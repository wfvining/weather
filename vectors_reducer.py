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

def record_observations(observations):
    day = observations['day']
    year = observations['year']
    date = year * 1000 + day
    temperature.append((date, observations['temp']))
    precipitation.append((date, observations['precipitation']))
    snow_deth.append((date, observations['snow_depth']))
    dew_point.append((date, observations['dew_point']))
    fog.append((date, observations['fog']))
    rain.append((date, observations['rain']))
    snow.append((date, observations['snow']))
    thunder.append((date, observations['thunder']))
    hail.append((date, observations['hail']))
    tornado.append((date, observateions['tornado']))

def get_blocks(num_blocks, size, data):
    blocks = [x * size for x in range(0, num_blocks)]
    while len(data[blocks[-1]:blocks[-1] + size]):
        yield [data[start:start + size] for start in blocks]
        blocks = [start + size for start in blocks]        

def make_block_generators(temp, precip, snow_depth, dew_point,
                          fog, rain, snow, hail, thunder, tornado):
    temp_blocks   = get_blocks(3, 30, temp)
    precip_blocks = get_blocks(3, 30, precip)
    snow_depth_blocks = get_blocks(3, 30, snow_depth)
    dew_point_blocks = get_blocks(3, 30, dew_point)
    fog_blocks = get_blocks(3, 30, fog)
    rain_blocks = get_blocks(3, 30, rain)
    snow_blocks = get_blocks(3, 30, snow)
    hail_blocks = get_blocks(3, 30, hail)
    thunder_blocks = get_blocks(3, 30, thunder)
    tornado_blocks = get_blocks(3, 30, tornado)
    return {'temp':temp_blocks,
            'precip':precip_blocks,
            'snow_depth':snow_depth_blocks,
            'dew_point':dew_point_blocks,
            'fog':fog_blocks,
            'rain':rain_blocks,
            'hail':hail_blocks,
            'thunder':thunder_blocks,
            'tornado':tornado_blocks}

def make_snow_vectors(lat_lon, block_generators):
    for s1, s2, s3 in block_generators['snow_depth']:
        snowpack = numpy.mean(s3)
        snow_features = s1 + s2
        features = [f1 + f2
                    for f1, f2, _ in [next(block_generators[feature])
                                      for fearure in block_generators.keys()]]
        all_features = snow_features
        for fv in features:
            all_features.append(fv)

        svm_string = str(snowpack) + '\t'
        for (i, val) in enumerate(all_features):
            svm_string = svm_string + str(i+1) + ':' + str(val) + ' '
        lat, lon = lat_lon.split(',')
        print(svm_string+str(len(all_features+1))+':'+lat
              +' '+str(len(all_features+2))+':'+lon)
            
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
    record_observations(observartion)
    
    for line in sys.stdin:
        key, observations = line.split('\t')
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
        