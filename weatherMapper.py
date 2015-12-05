"""First step mapper
   Extract the relevant fields for each observation
"""
import sys
import cPickle
import json
from datetime import datetime

def get_station_id(line):
    return (int(line[0:6]), int(line[7:12]))

# return a datetime object
def get_date(line):
    date_string = line[14:22]
    date = datetime.strptime(date_string, "%Y%m%d")
    return date

def get_temp(line):
    return float(line[24:30])

def get_dewpoint(line):
    return float(line[35:41])

def get_slp(line):
    return float(line[46:52])

def get_stp(line):
    return float(line[57:63])

def get_visibility(line):
    return float(line[68:73])

def get_windspeed(line):
    return float(line[78:83])

def get_maxspd(line):
    return float(line[88:93])

def get_gust(line):
    return float(line[95:100])

def get_maxtemp(line):
    return float(line[102:108])

def get_mintemp(line):
    return float(line[110:116])

def get_precipitation(line):
    precip_str = line[118:123]
    if precip_str == "99.99":
        return 0.0
    else:
        return float(precip_str)

def get_snowdepth(line):
    sndp_str = line[125:130]
    if sndp_str == '999.9':
        return 0.0
    else:
        return float(sndp_str)

# Booleans indicating the occurenc of a weather event
def had_fog(line):
    return int(line[132:133])
def had_rain(line):
    return int(line[133:134])
def had_snow(line):
    return int(line[134:135])
def had_hail(line):
    return int(line[135:136])
def had_thunder(line):
    return int(line[136:137])
def had_tornado(line):
    return int(line[137:138])

def year(date):
    return date.timetuple().tm_year

def month(date):
    return date.timetuple().tm_month

def day(date):
    return date.timetuple().tm_yday

def output(key, val):
    print('\t'.join([str(key), json.dumps(val)]))

# the reducer should get a list of values for each field for each for
# each station.  It will take the list and do spline (or maybe linear)
# interpolation on it to get a full set of data for the year.
if __name__ == '__main__':
    stnFile = open('station_index.p', 'r')
    station_index = cPickle.load(stnFile)
    for observation in sys.stdin:
        date = get_date(observation)
        station_id = get_station_id(observation)
        station = station_index[station_id]
        key = (station_id, year(date))
        val = {'lat':station['lat'], 'lon':station['lon'],
               'day':day(date),
               'temp':get_temp(observation),
               'dew_point':get_dewpoint(observation),
               'precipitation':get_precipitation(observation),
               'snow_depth':get_snowdepth(observation),
               'fog':had_fog(observation),
               'rain':had_rain(observation),
               'snow':had_snow(observation),
               'hail':had_hail(observation),
               'thunder':had_thunder(observation),
               'tornado':had_tornado(observation)}
        output(key, val)
               
