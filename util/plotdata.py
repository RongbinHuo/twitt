import matplotlib.pyplot as plt
import numpy as np

train_file = '../data/train_data.csv'


train = np.loadtxt( train_file, delimiter = ',' )

x_train = train[:,0:-1]
y_train = train[:,-1]
y_train = y_train.reshape( -1, 1 )

x_plot = []
for x in x_train:
	x_plot.append(x[1])

y_plot = []
for y in y_train:
	y_plot.append(y[0])

plt.plot(x_plot,y_plot)

plt.show()