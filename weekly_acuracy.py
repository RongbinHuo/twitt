import numpy as np
import cPickle as pickle
import datetime
from math import sqrt
import sys, getopt
import MySQLdb
from gold_news import share
import time
from collections import Counter
from pybrain.datasets.supervised import SupervisedDataSet as SDS

def main(argv):
    myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com", port=3306, user="root", passwd="12345678",  db="twit")
    cHandler = myDB.cursor()
    share.retrieve_dic()
    dt = datetime.datetime.now()
    start_date = dt - datetime.timedelta(days=20)
    wrong_number = 0
    correct_number = 0
    for i in range(20):
        tmp_date = (start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        dow = int((start_date + datetime.timedelta(days=i)).strftime("%w"))
        if dow < 1 or dow > 4:
            continue
        select_query = """SELECT id, text, link, create_at FROM gold_news WHERE DATE(create_at) = '%s'""" % tmp_date
        cHandler.execute(select_query)
        results = cHandler.fetchall()
        current_score = Counter()
        for row in results:
            link = row[2]
            if 'www.kitco.com' in link:
                content_ary = share.parse_kitco_content(share.retrieve_content(link))
                tmp = share.final_score(share.scoring_article(content_ary))
                current_score.update(tmp)
        model_file = '/home/ec2-user/twitt/model/neural_network_v2.pkl'
        net = pickle.load( open( model_file, 'rb' ))
        new_ary = [p[1] for p in sorted(current_score.items())]
        predicted_value = net.activate(new_ary)[0]
        tmp_date_plus = (start_date + datetime.timedelta(days=i+1)).strftime("%Y-%m-%d")
        select_query_dust_price = select_query = """SELECT close, open FROM dust_price WHERE DATE(date) = '%s' """ % tmp_date_plus
        cHandler.execute(select_query_dust_price)
        results_dust_price = cHandler.fetchall()
        actual_value = 0
        if len(results_dust_price) == 0:
            actual_value = 0.0
        else:
            actual_value = (results_dust_price[0][0] - results_dust_price[0][1])/results_dust_price[0][1]
        if actual_value * predicted_value > 0:
            correct_number = correct_number + 1
        elif actual_value * predicted_value < 0:
            wrong_number = wrong_number + 1
    acuracy = correct_number/float(correct_number+wrong_number)
    print acuracy

if __name__ == "__main__":
   main(sys.argv)