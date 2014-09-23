from collections import defaultdict
from itertools import combinations

from scipy import stats

from pprint import pprint
from utils import read_data


def choose_points(response_list):
    res = [d[5]-d[4] for d in response_list]
    return filter(lambda x: x > 5.5e5 and x < 1.4e6, res)


def analyze_data(data, p_threshold=0.05):
    """ combinatoric KS, add hits """
    data_roundup = defaultdict(int)
    for k1, k2 in combinations(data.keys(), 2):
        # DON'T EVER USE A SAMPLE SIZE THAT IS A MULTIPLE OF 100
        d, p = stats.ks_2samp(choose_points(data[k1]),
                              choose_points(data[k2]))
        print k1, k2, d, p
        if p < p_threshold:
            data_roundup[k1] += 1
            data_roundup[k2] += 1

    return dict(data_roundup)


data = read_data()

for k, v in data.items():
    print k, len(choose_points(v))


pprint(analyze_data(data, p_threshold=0.01))
