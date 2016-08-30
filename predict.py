import numpy as np
import cPickle as pickle

from math import sqrt

import sys, getopt


def main(argv):
	scoring_increase_overall = sys.argv[1]
	scoring_increase_than_pre = sys.argv[2]
	model_file = sys.argv[3]

	# model_file = 'model/model.pkl'
	net = pickle.load( open( model_file, 'rb' ))

	p = net.activate([scoring_increase_overall,scoring_increase_than_pre])[0]

	# sys.exit(p)
	# return p
	print p

if __name__ == "__main__":
   main(sys.argv)
