import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv("output/polHist.csv", header= None)
data.drop_duplicates(subset= None, inplace= True)
start = 15000
last1 = start + 500
last2 = start + 50
slicedX1 = data[0][start:last1]
slicedY1 = data[1][start:last1]
slicedX2 = data[0][start:last2]
slicedY2 = data[1][start:last2]
plt.figure(figsize= (12, 7))
plt.plot(slicedX1, slicedY1)
plt.plot(slicedX1, slicedY1, "gx")
plt.title("Active RBM-Policy vs Cycles: snap taken at steady state")
plt.legend(["0 => Open-Page \n1 => Closed-Page"])
plt.figure(figsize= (12, 7))
plt.plot(slicedX2, slicedY2)
plt.plot(slicedX2, slicedY2, "gx")
plt.title("Transition between RBM Policies")
plt.legend(["0 => Open-Page \n1 => Closed-Page"])
plt.show()
