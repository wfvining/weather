import sys
import json
import numpy
import scipy

first = lambda x: x[0]

# State
vector_type = 'snow'
temperature = []
precipitation = []
snow_depth = []
dew_point = []
fog = []
rain = []
snow = []
hail = []
thunder = []
tornado = []

def reset_state():
    temperature = []
    precipitation = []
    snow_depth = []
    dew_point = []
    fog = []
    rain = []
    snow = []
    hail = []
    thunder = []
    tornado = []

def record_observations(observations):
    day = observations['day']
    year = observations['year']
    date = year * 1000 + day
    temperature.append((date, observations['temp']))
    precipitation.append((date, observations['precipitation']))
    snow_depth.append((date, observations['snow_depth']))
    dew_point.append((date, observations['dew_point']))
    fog.append((date, observations['fog']))
    rain.append((date, observations['rain']))
    snow.append((date, observations['snow']))
    thunder.append((date, observations['thunder']))
    hail.append((date, observations['hail']))
    tornado.append((date, observations['tornado']))

def get_blocks(size, data):
    b1 = 0
    b2 = size
    b3 = 2 * size
    while len(data[b3:b3+size]) == size:
        yield (data[b1:b2], data[b2:b3], data[b3:b3+size])
        b1 = b2
        b2 = b3
        b3 = b3 + size

def make_block_generators(temp, precip, snow_depth, dew_point,
                          fog, rain, snow, hail, thunder, tornado):
    temp_blocks   = get_blocks(30, temp)
    precip_blocks = get_blocks(30, precip)
    snow_depth_blocks = get_blocks(30, snow_depth)
    dew_point_blocks = get_blocks(30, dew_point)
    fog_blocks = get_blocks(30, fog)
    rain_blocks = get_blocks(30, rain)
    snow_blocks = get_blocks(30, snow)
    hail_blocks = get_blocks(30, hail)
    thunder_blocks = get_blocks(30, thunder)
    tornado_blocks = get_blocks(30, tornado)
    return {'temp':temp_blocks,
            'precip':precip_blocks,
            'snow_depth':snow_depth_blocks,
            'dew_point':dew_point_blocks,
            'fog':fog_blocks,
            'snow':snow_blocks,
            'rain':rain_blocks,
            'hail':hail_blocks,
            'thunder':thunder_blocks,
            'tornado':tornado_blocks}

def count_days(dv):
    count = 0
    for x in dv:
        if x == 1:
            count += 1
    return count

def longest_run(dv):
    longest_run = 0
    current_run = 0
    for x in dv:
        if x == 0:
            if current_run > longest_run:
                longest_run = current_run
            current_run = 0
        else:
            current_run += 1
    return longest_run

def make_weather_events(fog, hail, thunder, snow, rain, tornado):
    hail = [count_days(hail), longest_run(hail)]
    fog  = [count_days(fog), longest_run(fog)]
    thunder = [count_days(thunder), longest_run(thunder)]
    snow = [count_days(snow), longest_run(snow)]
    rain = [count_days(rain), longest_run(rain)]
    tornado = [count_days(tornado), longest_run(tornado)]
    return hail + fog + rain + thunder + rain + snow + tornado

def get_vector(feature, block_generator):
    b1, b2, b3 = next(block_generator[feature])
    return b1 + b2

# I'm not really sure that I'm handling stop iteration in the correct way here.
def make_snow_vectors(lat_lon, block_generators):
    for s1, s2, s3 in block_generators['snow_depth']:
        snowpack = numpy.mean(s3)
        snow_features = s1 + s2

        temp_vector = get_vector('temp', block_generators)
        precip_vector = get_vector('precip', block_generators)
        dewpoint_vector = get_vevtor('dew_point', block_generators)
        fog_vector = get_vector('fog', block_generators)
        rain_vector = get_vector('rain', block_generators)
        snowday_vector = get_vector('snow', block_generators)
        hail_vector = get_vector('hail', block_generators)
        thunder_vector = get_vector('thunder', block_generators)
        tornado_vector = get_vector('tornado', block_generastors)

        all_features = (snow_features + temp_vector + precip_vector
                        + dewpoint_vector + fog_vector + rain_vector
                        + hail_vector + snowday_vector + thunder_vector
                        + tornado_vector)
        weather_events_vector = make_weather_events(fog_vector,
                                                    hail_vector,
                                                    thunder_vector,
                                                    snowday_vector,
                                                    rain_vector,
                                                    tornado_vector)
        all_features = all_features + weather_events_vector
        svm_string = str(snowpack) + '\t'
        for (i, val) in enumerate(all_features):
            if val != 0:
                svm_string = svm_string + str(i+1) + ':' + str(val) + ' '
        lat, lon = lat_lon.split(',')
        print(svm_string+str(len(all_features)+1)+':'+lat
              +' '+str(len(all_features)+2)+':'+lon)
            
def output_vectors(lat_lon, temp, precip, snow_depth, dew_point,
                   fog, rain, snow, hail, thunder, tornado):
    """All vectors are assumed to be sorted by. They are lists of tupples
       where the first element is the day and the second the value.
    """
    snd = lambda (x, y): y
    block_generators = make_block_generators(map(snd, temp),
                                             map(snd, precip),
                                             map(snd, snow_depth),
                                             map(snd, dew_point),
                                             map(snd, fog),
                                             map(snd, rain),
                                             map(snd, snow),
                                             map(snd, hail),
                                             map(snd, thunder),
                                             map(snd, tornado))
    if   vector_type == 'snow':
        make_snow_vectors(lat_lon, block_generators)
    elif vector_type == 'rain':
        make_rain_vector(lat_lon, block_generators)
    elif vector_type == 'temp':
        make_temp_vector(lat_lon, block_generators)
    elif vector_type == 'snow_days':
        make_snow_days_vector(lat_lon, block_generators)

if __name__ == '__main__':
    vector_type = sys.argv[1]
    # read all data for a lat/lon in 30 day chunks.
    # read the next 30 days and compute the average rainfall,
    #      the maximum rainfall
    #      the average snow pack
    #      the maximum snow pack
    #      the number of snow days
    lat_lon, observation = sys.stdin.readline().split('\t')
    observations = json.loads(observation)
    record_observations(observations)
    
    for line in sys.stdin:
        key, observations = line.split('\t')
        observations = json.loads(observations)
        if key != lat_lon:
            output_vectors(lat_lon,
                           sorted(temperature, key=first),
                           sorted(precipitation, key=first),
                           sorted(snow_depth, key=first),
                           sorted(dew_point, key=first),
                           sorted(fog, key=first),
                           sorted(rain, key=first),
                           sorted(snow, key=first),
                           sorted(hail, key=first),
                           sorted(thunder, key=first),
                           sorted(tornado, key=first))
            reset_state()
        record_observations(observations)
        
