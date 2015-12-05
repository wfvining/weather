import json
import sys
from scipy.interpolate import interp1d
import numpy

undefined_values = {'temp':9999.9,
                    'precipitation':99.99,
                    'dew_point':9999.9,
                    'snow_depth':999.9,
                    'fog':None,
                    'rain':None,
                    'snow':None,
                    'thunder':None,
                    'hail':None,
                    'tornado':None}

weather_features = ['temp', 'precipitation', 'dew_point', 'snow_depth',
                    'fog', 'rain', 'snow', 'thunder', 'hail', 'tornado']

data_threshold = 200

def new_values():
    return {'temp':[],
            'temp_days':[],
            'precipitation':[],
            'precipitation_days':[],
            'dew_point':[],
            'dew_point_days':[],
            'snow_depth':[],
            'snow_depth_days':[],
            'fog':[],
            'fog_days':[],
            'rain':[],
            'rain_days':[],
            'snow':[],
            'snow_days':[],
            'hail':[],
            'hail_days':[],
            'thunder':[],
            'thunder_days':[],
            'tornado':[],
            'tornado_days':[]}

def append_value(fieldName, fields, values_dict):
    values_dict[fieldName].append(fields[fieldName])
    values_dict[fieldName+'_days'].append(fields['day'])

def add_value(fieldName, fields, values_dict):
    if undefined_values[fieldName] is None:
        append_value(fieldName, fields, values_dict)
    elif fields[fieldName] != undefined_values[fieldName]:
        append_value(fieldName, fields, values_dict)

def interpolate_data(fieldName, values, fill):
    return interp1d(values[fieldName+'_days'],
                    values[fieldName],
                    bounds_error=False,
                    fill_value=fill)
        
def interpolate(values_dict):
    # use the min value for temperature since the days outside the
    # interpolation range are probably in the winter.
    temp_interp   = interpolate_data('temp', values_dict,
                                     min(values_dict['temp']))
    # use average precipitation
    precip_interp = interpolate_data('precipitation', values_dict,
                                     numpy.mean(values_dict['precipitation']))
    # use min for dew point
    dew_point_interp = interpolate_data('dew_point', values_dict,
                                        min(values_dict['dew_point']))
    # use the max for snow depth
    snow_depth_interp = interpolate_data('snow_depth', values_dict,
                                         max(values_dict['snow_depth']))
    days = range(1, 366)
    values_dict['temp'] = list(temp_interp(days))
    values_dict['precipitation'] = list(precip_interp(days))
    values_dict['dew_point'] = list(dew_point_interp(days))
    values_dict['snow_depth'] = list(snow_depth_interp(days))

def sort_with(idxs, vals):
    return [x for i, x in sorted(zip(idxs, vals), key=lambda pair:pair[0])]
    
# there are a couple ways to do this... just fill in with 0s or
# ... fill with the same distribution as is already present in the
# data.
# I'm using the strategey where I fill everything with zeroes
def fill_boolean_features(values_dict):
    # rain_days is the same as all other days sets for boolean features.
    known_days = values_dict['rain_days']
    rain = values_dict['rain']
    snow = values_dict['snow']
    fog  = values_dict['fog']
    hail = values_dict['hail']
    thunder = values_dict['thunder']
    tornado = values_dict['tornado']
    for d in range(1, 366):
        if d not in known_days:
            known_days.append(d)
            rain.append(0)
            snow.append(0)
            fog.append(0)
            hail.append(0)
            thunder.append(0)
            tornado.append(0)
    values_dict['rain'] = sort_with(known_days, rain)
    values_dict['snow'] = sort_with(known_days, snow)
    values_dict['hail'] = sort_with(known_days, hail)
    values_dict['fog']  = sort_with(known_days, fog)
    values_dict['thunder'] = sort_with(known_days, thunder)
    values_dict['tornado'] = sort_with(known_days, tornado)        

def enough_data(values):
    return all([len(data) > data_threshold for data in [values['temp'],
                                                        values['precipitation'],
                                                        values['dew_point'],
                                                        values['snow_depth']]])

def output(year, values_dict, lat, lon):
    key_prefix = ','.join([str(lat), str(lon), str(year)])
    for day in range(1, 366):
        key = key_prefix + str(day)
        val = { feat:values_dict[feat][day-1] for feat in weather_features }
        print('\t'.join([key, json.dumps(val)]))    

# for each station/year:
# 1. combine all temperatures into a list
#    - remove undefined values (9999.9)
# 2. use linear (or cubic spline) interpolation to estimate a value
#    for missing days
#
# 3. Repeat for precipitation, dew_point, and snow_depth

if __name__ == '__main__':
    station = None
    year = None
    values_dict = {}
    latitude = 0.0
    longitude = 0.0
    for line in sys.stdin:
        key, value = line.split('\t')
        stn, wban, y = key.split(',')
        station_id = stn+wban
        fields = json.loads(value)

        if station is None:
            station = station_id
            year = y[0:-1] # janky parsing for extra parens from map phase
            values_dict = new_values()
            latitude = fields['lat']
            longitude = fields['lon']
        elif station != station_id:
            if enough_data(values_dict):
                try:
                    interpolate(values_dict)
                    fill_boolean_features(values_dict)
                    output(year, values_dict, latitude, longitude)
                except(LinAlgError):
                    pass
            station = station_id
            year = y[0:-1]
            values_dict = new_values()
            latitude = fields['lat']
            longitude = fields['lon']
        # add the next values to the list...
        add_value('temp', fields, values_dict)
        add_value('dew_point', fields, values_dict)
        add_value('precipitation', fields, values_dict)
        add_value('snow_depth', fields, values_dict)
        add_value('fog', fields, values_dict)
        add_value('rain', fields, values_dict)
        add_value('snow', fields, values_dict)
        add_value('hail', fields, values_dict)
        add_value('thunder', fields, values_dict)
        add_value('tornado', fields, values_dict)
