import matplotlib.pyplot as plt
import numpy as np
from pybrain.datasets.supervised import SupervisedDataSet as SDS

train_file = '../data/train_data.csv'


train = np.loadtxt( train_file, delimiter = ',' )

x_train = train[:,0:-1]
y_train = train[:,-1]
y_train = y_train.reshape( -1, 1 )


input_size = x_train.shape[1]
target_size = y_train.shape[1]

ds = SDS( input_size, target_size )
ds.setField( 'input', x_train )
ds.setField( 'target', y_train )

x_plot = []
for x in x_train:
	x_plot.append(x[0])

y_plot = []
for y in y_train:
	y_plot.append(y[0])

n=0
m=0
c=0
n1=0
m1=0
for inp, tar in ds:
	c = c+1
	if inp[1] > 0.2 and tar[0] > 0:
		n=n+1
	if inp[1] < -0.2 and tar[0] < 0:
		m=m+1
	if inp[1] > 0.2 and tar[0] < 0:
		n1=n1+1
	if inp[1] < -0.2 and tar[0] > 1.0:
		m1=m1+1
print 'Test result, total {} records, {} is correct and {} is wrong. Perce {}'.format(c,n+m, n1+m1, float(n+m)/float(n+m+n1+m1))

plt.plot(x_plot,y_plot)


plt.show()