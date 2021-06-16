import numpy as np

from scipy.interpolate import interp1d
from matplotlib import pyplot as plt

filename = "/home/amelia/Documents/ferrofluids/sm-magnet-dec13.csv"

distance = float(input("Distance in mm: "))

dist, field = [], []

with open(filename) as f:
    for line in f:
        dist.append(float(line.split(",")[0]))
        field.append(float(line.split(",")[1])/10000)

f = interp1d(dist, field, 'cubic')

xnew = np.arange(dist[0], dist[-1], 0.1)

ynew = f(xnew)   # use interpolation function returned by `interp1d`

plt.plot(dist, field, 'o', xnew, ynew, '-')
plt.title("Magnetic field on axis (December 13 2019)")
plt.xlabel("Distance (mm)")
plt.ylabel("Magnetic Field on-axis (T)")
plt.show()

field_at_x = f(distance)

print("Field at {}mm is {} T".format(distance, field_at_x))
