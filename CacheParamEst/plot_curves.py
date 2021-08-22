import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as scp

# Plotting Block Size Estimation Plot
file1 = "acc_lat.txt"
fptr = open(file1)
data = np.loadtxt(fptr, delimiter= ",")
X = data[:, 0]; Y = data[:, 1]
y_min = np.min(Y);
thresh = y_min*1.4
x_peaks, y_peaks = scp.find_peaks(Y, height= thresh)
y_peaks = y_peaks["peak_heights"]

plt.figure(figsize=(8, 4))
plt.plot(X, Y)
plt.plot(x_peaks, y_peaks, "ro")
for i_x, i_y in zip(x_peaks, y_peaks):
    plt.text(i_x, i_y, "({})".format(i_x))
plt.title("Access Time vs Byte Position relative to starting addr")
plt.ylabel("# Cycles elapsed")
plt.xlabel("Byte Position relative to starting addr")

# Set Associativity Estimation Plot
file2 = "set_lat.txt"
fptr2 = open(file2)
data = np.loadtxt(fptr2, delimiter= ",")
X = data[:, 0]; Y = data[:, 1]
z = Y - np.min(Y); X  = X+1
delta = z[1:] - z[0:-1]
estimate = np.argsort(delta)[-1] + 1
z = z[1:]    # first entry is noisy
plt.figure(figsize=(8, 4))
plt.plot(X, Y)
plt.title(r'Access Latencies for Blocks Mapped to the same Set')
plt.ylabel("# Cycles elapsed")
plt.xlabel("Index corr to Order in which the Block is Accessed")
plt.figure(figsize=(8, 4))
plt.axvline(estimate + 1)
plt.text(estimate, z[estimate - 1], "[{}]".format(estimate))
plt.plot(X[1:], z, "ro")
plt.title("Miss Penalty for Blocks relative to the fastest access")
plt.show()
