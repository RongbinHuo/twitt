import numpy as np
import cPickle as pickle

from math import sqrt

import sys, getopt


def main(argv):
	scoring_increase_overall = sys.argv[1]
	scoring_increase_than_pre = sys.argv[2]
	quote_data_year_percent = sys.argv[3]
	quote_data_day_percent = sys.argv[4]
	model_file = sys.argv[5]

	# model_file = 'model/model.pkl'
	clf = pickle.load( open( model_file, 'rb' ))

	p = clf.predict_proba([[scoring_increase_overall,scoring_increase_than_pre,quote_data_year_percent,quote_data_day_percent]])
	negative_per = p[0][0]
	positive_per = p[0][2]
	# sys.exit(p)
	# return p
	if positive_per >= negative_per:
		print positive_per
	else:
		print 0.0-float(negative_per)

if __name__ == "__main__":
   main(sys.argv)
