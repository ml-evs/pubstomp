import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

with open("square.txt") as flines:
    square = [line.strip().split() for line in flines]


square = np.asarray([list(map(float,x)) for x in square])


sns.heatmap(square, vmin=0.9, vmax=1.0)

plt.show()