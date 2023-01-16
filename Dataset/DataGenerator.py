import os
import pandas as pd
from collections import defaultdict
from utils import TravelHelper

config = \
{
    "DISPINTERVAL": 10*60,       # dispatching interval is 10 mins
    "STARTTIME": 6.5*3600,       # bus operating start time 06:30
    "ENDTIME": 23.5*3600,        # bus operating end time 06:30
    "BUSPERROUTE": 30,           # average number of buses per route
    "BUSAVGSPEED": 40*1000/3600, # average speed of bus is 40km/h
    "TRIPOFFSET": 4*60,          # time offset of each trip is 4min
    "BREAKTIME": 10*60           # break time for driver after each trip is 10min 
}

def get_stop_table(in_file, out_file):
    df = pd.read_csv("External/%s.csv"%in_file, encoding="gbk")
    df = df.drop_duplicates(subset=['stop_name'])
    dfstops = df[["stop_name", "stop_lon", "stop_lat", "stop_full_name"]]
    dfstops.insert(0, "stop_id", ["S%04d"%(i+1) for i in range(len(dfstops))])
    dfstops.to_csv("%s/stops.csv"%out_file, index=None, encoding="gbk")
    print("------------Finish generating stops.csv------------")

def get_route_table(in_file, out_file):
    df = pd.read_csv("External/%s.csv"%in_file, encoding="gbk")
    resd_routes = defaultdict(list)
    routes = set(df["route_name"])
    print(len(routes))
    num_route, char_route = [], []
    for route in routes:
        if route.isnumeric():
            num_route.append(int(route))
        else:
            char_route.append(route)
    
    resd_routes["route_id"] = ["R%04d"%(i+1) for i in range(len(routes))]
    resd_routes["route_name"] = sorted(num_route) + sorted(char_route)
    dfroutes = pd.DataFrame(resd_routes, index=None)
    dfroutes.to_csv("%s/routes.csv"%out_file, index=None, encoding="gbk")
    print("------------Finish generating routes.csv------------")

def get_trip_and_stop_time_table(in_file, out_file):
    df = pd.read_csv("External/%s.csv"%in_file, encoding='gbk')
    df = df[["route_name", "direction", "stop_seq", "stop_name"]]
    dfstop = pd.read_csv("%s/stops.csv"%out_file, encoding='gbk')
    dfroute = pd.read_csv("%s/routes.csv"%out_file, encoding='gbk')
    th = TravelHelper(config, dfstop)
    busid, tripid = 1, 1
    resd_trip, resd_stime = defaultdict(list), defaultdict(list)

    # iterate through each route
    for route_name, dfcur in df.groupby("route_name"):
        dfcur = dfcur.merge(dfstop[["stop_id", "stop_name"]], how="left")
        dfcur = dfcur.merge(dfroute, how="left")[["route_id", "direction", "stop_seq", "stop_id"]]
        route_id = dfcur["route_id"].to_list()[0]
        dfzero, dfone = dfcur[dfcur["direction"]==0], dfcur[dfcur["direction"]==1]
        seq2sid_zero = {row.stop_seq:row.stop_id for row in dfzero.itertuples()}
        seq2sid_one = {row.stop_seq:row.stop_id for row in dfone.itertuples()}
        seq2sid_lst = [seq2sid_zero, seq2sid_one]
        # reject the route if single direction
        if len(seq2sid_zero)==0 or len(seq2sid_one)==0:
            continue

        # iterate through each bus on the route
        for i in range(config["BUSPERROUTE"]):
            # flag indicates the initial direction of current bus
            flag = 1 if i % 2 == 0 else 0
            # initially takes zero direction
            cur_time = config["STARTTIME"] + i * config["DISPINTERVAL"] // 2 
            sid2time = {}
            # the bus begins multiple trips
            while cur_time < config["ENDTIME"]:
                cur_seq = 1
                # the bus is running a single trip
                while cur_seq < max(seq2sid_lst[1-flag]):
                    cur_sid = seq2sid_lst[1-flag][cur_seq]
                    sid2time[cur_sid] = cur_time
                    next_sid = seq2sid_lst[1-flag][cur_seq+1]
                    cur_time += th.get_travel_time(cur_sid, next_sid)
                    cur_seq += 1
                
                # last stop arrival time 
                sid2time[seq2sid_lst[1-flag][cur_seq]] = cur_time
                # prepare trip table
                resd_trip["trip_id"].append("T%06d"%(tripid))
                resd_trip["route_id"].append(route_id)
                resd_trip["direction_id"].append(1-flag)
                resd_trip["bus_id"].append("B%05d"%(busid))
                print("Prepare trip ", "T%06d"%(tripid), "in route", route_id)
                # prepare stop_time table
                for seq, sid in seq2sid_lst[1-flag].items():
                    resd_stime["trip_id"].append("T%06d"%(tripid))
                    resd_stime["stop_id"].append(sid)
                    resd_stime["stop_seq"].append(seq)
                    resd_stime["arrival_time"].append(sid2time[sid])
                    resd_stime["time_string"].append(th.getTimeString(sid2time[sid]))
                
                # variable updation
                cur_time += config["BREAKTIME"]
                flag = 1 - flag
                tripid += 1
            busid += 1

    dftrip = pd.DataFrame(resd_trip, index=None)
    dftrip.to_csv("%s/trips.csv"%out_file, index=None, encoding="gbk")
    print("------------Finish generating trips.csv------------")
    dfstime = pd.DataFrame(resd_stime, index=None)
    dfstime.to_csv("%s/stop_times.csv"%out_file, index=None, encoding="gbk")
    print("------------Finish generating stop_times.csv------------")

def get_transit_routes_top(in_file, out_file, num_routes = 10):
    dfroute = pd.read_csv("%s/routes.csv"%in_file, encoding='gbk')
    dfstoptime = pd.read_csv("%s/stop_times.csv"%in_file, encoding='gbk')
    dfstop = pd.read_csv("%s/stops.csv"%in_file, encoding='gbk')
    dftrip = pd.read_csv("%s/trips.csv"%in_file, encoding='gbk').sort_values(by=["route_id","trip_id"])

    select_rid = []
    dftrip_new = pd.DataFrame(columns=dftrip.columns)
    for i, (rid, dft) in enumerate(dftrip.groupby("route_id")):
        if i < num_routes:
            dftrip_new = dftrip_new.append(dft)
            select_rid.append(rid)

    dfroute_new = dfroute[dfroute["route_id"].isin(select_rid)]
    select_trip = dftrip_new["trip_id"].to_list()
    dfstoptime_new = dfstoptime[dfstoptime["trip_id"].isin(select_trip)]
    select_stop = dfstoptime_new["stop_id"]
    dfstop_new = dfstop[dfstop["stop_id"].isin(select_stop)]
    if not os.path.exists(out_file):
        os.makedirs(out_file)
        
    dfstop_new.to_csv("%s/stops.csv"%out_file, index=None, encoding="gbk")
    dfroute_new.to_csv("%s/routes.csv"%out_file, index=None, encoding="gbk")
    dftrip_new.to_csv("%s/trips.csv"%out_file, index=None, encoding="gbk")
    dfstoptime_new.to_csv("%s/stop_times.csv"%out_file, index=None, encoding="gbk")
    print("------------Finish generating %s dataset------------"%out_file)

if __name__ == "__main__":
    # get_stop_table("BeijingTransit", "TransitRoutesFull")
    # get_route_table("BeijingTransit", "TransitRoutesFull")
    # get_trip_and_stop_time_table("BeijingTransit", "TransitRoutesFull")
    for k in range(10, 70, 10):
        get_transit_routes_top("TransitRoutesFull", "TransitRoutesTop%d"%k, k)



