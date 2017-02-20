import cPickle as pickle
import datetime
from math import sqrt
import sys, getopt
import MySQLdb
from gold_news import share
import time
from collections import Counter

def main(argv):
    dt = datetime.datetime.now()
    yesterday = dt - datetime.timedelta(days=5)
    yesterday_date = yesterday.strftime("%Y-%m-%d")
    myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com", port=3306, user="root", passwd="12345678",  db="twit")
    cHandler = myDB.cursor()
    select_query = """SELECT id, text, link, create_at FROM gold_news WHERE DATE(create_at) >= '%s'""" % yesterday_date
    cHandler.execute(select_query)
    results = cHandler.fetchall()
    share.retrieve_dic()
    for row in results:
        link = row[2]
        time = row[3]
        if 'www.kitco.com' in link or 'www.investing.com' in link or 'www.bulliondesk.com' in link:
            check_query = """SELECT * FROM news_detail WHERE link = '%s' """ % (link)
            cHandler.execute(check_query)
            results_check = cHandler.fetchall()
            if len(results_check) == 0:
                content = share.retrieve_content(link)
                if content and len(content)>0:
                    content = content.replace('"', '')
                    content = content.replace("'", "")
                    insert_query = """INSERT INTO news_detail (link, content, created_at) VALUES ('%s', '%s', '%s') """ % (link, content, time)
                    cHandler.execute(insert_query)
                    myDB.commit()
    cHandler.close()
    myDB.close()

if __name__ == "__main__":
   main(sys.argv)