import pandas as pd
from haversine import haversine, Unit

class TravelHelper:
    def __init__(self, config, dfstop):
        self.config = config
        self.sid2pos = {row.stop_id:(row.stop_lat, row.stop_lon) for row in dfstop.itertuples()}
        self.sid2name = {row.stop_id:row.stop_name for row in dfstop.itertuples()}

    def get_travel_time(self, sid, nextsid):
        frompos, topos = self.sid2pos[sid], self.sid2pos[nextsid]
        dist = haversine(frompos, topos, unit=Unit.METERS)
        return round(dist/self.config["BUSAVGSPEED"]) + self.config["TRIPOFFSET"]
    
    def getTimeString(self,seconds):
        days,remainder=divmod(seconds,24*3600)
        hours,remainder=divmod(remainder,3600)
        minutes,seconds=divmod(remainder,60)
        s='{:02}:{:02}'.format(int(hours),int(minutes))
        if days>0:
            s+=" (+%d)"%days
        return s
    
    def print_trip_scheudule(self, sid2time):
        resd = {}
        for sid, time in sid2time.items():
            sname = self.sid2name[sid]
            timestr = self.getTimeString(time)
            resd[sname] = timestr
        print(resd)