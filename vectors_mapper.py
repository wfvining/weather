"""Mapper for extracting features vectors."""
import json
import sys

if __name__ == '__main__':
    for line in sys.stdin:
        input_key, input_value = line.split('\t')
        lat, lon, date = input_key.split(',')
        date = str.strip(date)
        observations = json.loads(input_value)
        observations['year'] = int(date[0:4])
        observations['day']  = int(date[4:])
        # really simple, pretty much an identy mapper.
        print('\t'.join([','.join([lat, lon]), json.dumps(observations)]))
