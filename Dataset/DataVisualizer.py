import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

class DataVisualizer():
    def __init__(self, dataset):
        self.dataset = dataset
        self.dfroute = pd.read_csv("%s/routes.csv"%dataset, encoding='gbk') # already sorted
        self.dfstop = pd.read_csv("%s/stops.csv"%dataset, encoding='gbk')
        self.dftrip = pd.read_csv("%s/trips.csv"%dataset, encoding='gbk')
        self.dfstoptime = pd.read_csv("%s/stop_times.csv"%dataset, encoding='gbk')
        
    def plot_basemap(self, ax, radius=0.17):
        dfstopfull = pd.read_csv("TransitRoutesFull/stops.csv", encoding='gbk')
        ax.plot(dfstopfull.stop_lon, dfstopfull.stop_lat, "ko", markersize=0.1)
        bjcenter = (116.38, 39.90)
        ax.scatter(bjcenter[0], bjcenter[1], marker='*', c='r', s=100)
        ax.set_xlim(bjcenter[0]-radius, bjcenter[0]+radius)
        ax.set_ylim(bjcenter[1]-radius, bjcenter[1]+radius)
        return ax
    
    def plot_routes(self, ax):
        route_names = self.dfroute["route_name"].to_list()
        select_trips = self.dftrip.groupby("route_id").head(1)["trip_id"].to_list()
        for i,trip_id in enumerate(select_trips):
            dfcur = self.dfstoptime[self.dfstoptime["trip_id"]==trip_id]
            dfcur = dfcur.merge(self.dfstop[["stop_id", "stop_lon", "stop_lat"]], how='left')
            ax.plot(dfcur.stop_lon, dfcur.stop_lat, '-o', markersize=2.5, label=route_names[i])

    def getTimeString(self,seconds):
        days,remainder=divmod(seconds,24*3600)
        hours,remainder=divmod(remainder,3600)
        minutes,seconds=divmod(remainder,60)
        s='{:02}:{:02}'.format(int(hours),int(minutes))
        return s

    def plot_time_space_network(self, ax, route_id):
        mpl.rcParams['font.sans-serif'] = ['SimHei']
        sid2sname = {row.stop_id:row.stop_name for row in self.dfstop.itertuples()}
        route_name = self.dfroute[self.dfroute["route_id"]==route_id]["route_name"].to_list()[0]
        dftrip = self.dftrip[self.dftrip["route_id"]==route_id]
        dftrip = dftrip.merge(self.dfstoptime, how='left')
        bus_count = 0
        for bus_id, dfcur in dftrip.groupby("bus_id"):
            dfcur = dfcur.sort_values(by="arrival_time")
            stop_ids = dfcur.drop_duplicates(subset=['stop_id'])['stop_id'].to_list()
            if bus_count % 11 == 0:
                ax.plot(dfcur.arrival_time, dfcur.stop_id, '-o', markersize=2.5, label=bus_id, alpha = 0.8)
            bus_count += 1
        ax.set_yticks(range(len(stop_ids)))
        ax.set_yticklabels([sid2sname[sid] for sid in stop_ids])
        time_stamps = [i*3600 for i in range(6,26)]
        ax.set_xticks(time_stamps)
        ax.set_xticklabels([self.getTimeString(t) for t in time_stamps])
        ax.tick_params(axis='x', labelrotation = 45)
        ax.legend()

def plot_routes_on_basemap_summary():
    fig, axes = plt.subplots(2, 3, figsize=(18,12), dpi=200)
    topk_lst = list(range(10, 70, 10))
    for i, ax in enumerate(axes.flat):
        dv = DataVisualizer("TransitRoutesTop%d"%topk_lst[i])
        dv.plot_basemap(ax)
        dv.plot_routes(ax)
        ax.set_title("TransitRoutesTop%d"%topk_lst[i])
        if i < 3:
            ax.legend(ncol=5)   
    plt.tight_layout()
    if not os.path.exists("Visualization"):
        os.makedirs("Visualization")
    plt.savefig("Visualization/RoutesSummary.png")

def plot_time_space_network_summary(route_ids):
    fig, axes = plt.subplots(2, 2, figsize=(20,10), dpi=200)
    dv = DataVisualizer("TransitRoutesFull")
    rid2rname = {row.route_id:row.route_name for row in dv.dfroute.itertuples()}
    for i, ax in enumerate(axes.flat):
        dv.plot_time_space_network(ax, route_ids[i])
        ax.set_title(rid2rname[route_ids[i]]+"路公交车")

    plt.tight_layout()
    if not os.path.exists("Visualization"):
        os.makedirs("Visualization")
    plt.savefig("Visualization/TimeSpaceSummary.png")

if __name__ == "__main__":
    plot_routes_on_basemap_summary()
    # plot_time_space_network_summary(["R0001", "R0002", "R0009", "R0011"])





