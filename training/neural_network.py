import numpy as np
import cPickle as pickle
from math import sqrt
from pybrain.datasets.supervised import SupervisedDataSet as SDS
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import TanhLayer
from pybrain.structure.modules   import SoftmaxLayer

train_file = '../data/train_data.csv'
validation_file = '../data/validation.csv'
output_model_file = '../model/model.pkl'

hidden_size = 30
epochs = 600


train = np.loadtxt( train_file, delimiter = ',' )
validation = np.loadtxt( validation_file, delimiter = ',' )
train = np.vstack(( train, validation ))
x_train = train[:,0:-1]
y_train = train[:,-1]
y_train = y_train.reshape( -1, 1 )

input_size = x_train.shape[1]
target_size = y_train.shape[1]

ds = SDS( input_size, target_size )
ds.setField( 'input', x_train )
ds.setField( 'target', y_train )

net = buildNetwork( input_size, hidden_size, target_size, bias = True )
trainer = BackpropTrainer( net, ds, verbose=True)

print "training for {} epochs...".format( epochs )

# for inp, tar in ds:
#     print [net.activate(inp), tar]

# trainer.trainUntilConvergence(maxEpochs=1000, continueEpochs=10, validationProportion=0.1)

for inp, tar in ds:
    print [net.activate(inp), tar]

for i in range( epochs ):
	mse = trainer.train()
	rmse = sqrt( mse )
	print "training RMSE, epoch {}: {}".format( i + 1, rmse )

pickle.dump( net, open( output_model_file, 'wb' ))


n=0
m=0
c=0
n1=0
m1=0
for inp, tar in ds:
	c = c+1
	if net.activate(inp)[0] >0.2 and tar[0] == 1.0:
		n=n+1
	if net.activate(inp)[0] <-0.1 and tar[0] == -1.0:
		m=m+1
	if net.activate(inp)[0] >0.2 and tar[0] == -1.0:
		n1=n1+1
	if net.activate(inp)[0] <-0.1 and tar[0] == 1.0:
		m1=m1+1


n=0
m=0
c=0
n1=0
m1=0
for inp, tar in ds:
	c = c+1
	if net.activate(inp)[0] > 0 and tar[0] == 1.0:
		n=n+1
	if net.activate(inp)[0] < 0 and tar[0] == -1.0:
		m=m+1
	if net.activate(inp)[0] > 0 and tar[0] == -1.0:
		n1=n1+1
	if net.activate(inp)[0] < 0 and tar[0] == 1.0:
		m1=m1+1