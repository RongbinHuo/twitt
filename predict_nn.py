import numpy as np
import cPickle as pickle
from math import sqrt
import sys, getopt
import MySQLdb
from gold_news import share
import time
from collections import Counter
from pybrain.datasets.supervised import SupervisedDataSet as SDS

def main(argv):
    today_date = time.strftime("%Y-%m-%d")
    myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com", port=3306, user="root", passwd="12345678",  db="twit")
    cHandler = myDB.cursor()
    select_query = """SELECT id, text, link, create_at FROM gold_news WHERE create_at >= '%s'""" % today_date
    cHandler.execute(select_query)
    results = cHandler.fetchall()
    current_score = Counter()
    share.retrieve_dic()
    for row in results:
        link = row[2]
        if 'www.kitco.com' in link:
            content_ary = share.parse_kitco_content(share.retrieve_content(link))
            tmp = share.final_score(share.scoring_article(content_ary))
            current_score.update(tmp)
    model_file = '/home/ec2-user/twitt/model/neural_network.pkl'
    net = pickle.load( open( model_file, 'rb' ))
    new_ary = [p[1] for p in current_score.items()]
    print net.activate(new_ary)[0]

if __name__ == "__main__":
   main(sys.argv)