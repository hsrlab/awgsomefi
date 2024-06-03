import json
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

with open("glitch_histogram2.json", 'r') as f:
    info = json.load(f)

with open("alternative_lowscan.json", 'r') as f:
    info = json.load(f)

#with open("newglitch_lowscan.json", 'r') as f:
#    info = json.load(f)

hists = []

for k, v in info.items():
    histogram = np.bincount(np.asarray(v)[:, 0], minlength=256)
    print(histogram)
    hists.append(histogram)

final = defaultdict(lambda: defaultdict(int))

for histogram, t in zip(hists, info.keys()):
    for i, leakedcount in enumerate(histogram):
        if leakedcount != 0 and i != 0:
            final[i][t.split(".")[0]] = leakedcount



for v, f in final.items():
    lists = sorted(f.items())
    xs, ys = zip(*lists)
    xs = [int(a)/10**6 for a in xs]
    diff = xs[-1] + xs[-1] - xs[-2]
    xs.append(float(diff))
    plt.stairs(ys, xs, label=v, fill=False)
    print(xs)

plt.xlabel("Glitch Trigger Delay", fontsize=18, fontweight='bold')
plt.legend()
plt.tight_layout()
plt.show()
