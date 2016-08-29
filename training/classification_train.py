from pybrain.datasets            import ClassificationDataSet
from pybrain.utilities           import percentError
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules   import SoftmaxLayer
import numpy as np
import cPickle as pickle
from math import sqrt

train_file = 'data/train_data.csv'
validation_file = 'data/validation.csv'
output_model_file = 'model/classification_model.pkl'

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

alldata = ClassificationDataSet(input_size, target_size, nb_classes=2)

alldata.setField( 'input', x_train )
alldata.setField( 'target', y_train )

tstdata, trndata = alldata.splitWithProportion( 0.15 )

trndata._convertToOneOfMany( )
tstdata._convertToOneOfMany( )

fnn = buildNetwork( trndata.indim, 5, trndata.outdim, outclass=SoftmaxLayer )

trainer = BackpropTrainer( fnn, dataset=trndata, momentum=0.1, verbose=True, weightdecay=0.01)

for i in range( epochs ):
	mse = trainer.train()
	rmse = sqrt( mse )
	print "training RMSE, epoch {}: {}".format( i + 1, rmse )

for inp, tar in alldata:
    print [fnn.activate(inp), tar]