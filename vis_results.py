from utils import read_data
import matplotlib.pyplot as plt

data = read_data()

for key, val in data.items()[-4:]:
    plt.plot([d[4] for d in val], [d[5]-d[4] for d in val],
             '.', label=str(key), alpha=0.5)
    # plt.plot(sorted([d[5]-d[4] for d in val]),
    #          #'.',
    #          label=str(key), alpha=0.5)

plt.legend()
plt.show()
