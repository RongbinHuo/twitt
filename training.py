import numpy as np
import cPickle as pickle
from math import sqrt
from pybrain.datasets.supervised import SupervisedDataSet as SDS
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer


train_file = 'data/train.csv'
validation_file = 'data/validation.csv'
output_model_file = 'model/model.pkl'

hidden_size = 100
epochs = 600

