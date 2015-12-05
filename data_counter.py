import sys

if __name__ == '__main__':
    count = 1
    count_sum = 0
    num_locations = 0
    lat_lon, val = sys.stdin.readline().split('\t')
    for line in sys.stdin:
        ll, v = line.split('\t')
        if ll != lat_lon:
            lat_lon = ll
            count_sum += count
            num_locations += 1
            count = 1
        else:
            count += 1

    print(count_sum / num_locations)
            
            
