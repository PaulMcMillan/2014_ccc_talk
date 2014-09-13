from collections import defaultdict

def read_data():
    data = defaultdict(list)
    with open('data/out.pcap.parsed') as f:
        for line in f:
            this = line.split(',')
            data[this[0]].append(map(long, this[1:]))
    return data
