import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
from elasticsearch import Elasticsearch
import time
from datetime import datetime, tzinfo
import pytz
import MySQLdb
from googlefinance import getQuotes

# import twitter keys and tokens
from config import *

es = Elasticsearch()
company = 'NUGT'
stock = "$NUGT"
myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com",port=3306,user="root",passwd="12345678",db="twit")
cHandler = myDB.cursor()
insert_query = """INSERT INTO ratings (company_id, created_at, rating, polarity, subjectivity, message, current_price) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
class TweetStreamListener(StreamListener):
	# on success
    def on_data(self, data):

    	dict_data = json.loads(data)
        if 'text' in dict_data:
            tweet = TextBlob(dict_data["text"])
    	    # print tweet.sentiment.polarity
            if tweet.sentiment.polarity < 0:
                sentiment = "negative"
            elif tweet.sentiment.polarity == 0:
                sentiment = "neutral"
            else:
                sentiment = "positive"
            stock_quote = str(getQuotes('AMZN')[0]['LastTradePrice'])

            print sentiment
        
            # time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(dict_data["created_at"],'%a %b %d %H:%M:%S +0000 %Y'))
            time_stamp = datetime.strptime(dict_data["created_at"],'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            p='%Y-%m-%d %H:%M:%S'
            epoch = int(time.mktime(time.strptime(time_stamp,p)))
            scoring =  (1-tweet.sentiment.subjectivity)*tweet.sentiment.polarity

            es.index(index="stocks",
                 doc_type="NUGT",
                 body={"company": dict_data["user"]["screen_name"],
                       "created_at": epoch,
                       "message": dict_data["text"],
                       "polarity": tweet.sentiment.polarity,
                       "subjectivity": tweet.sentiment.subjectivity,
                       "sentiment": sentiment,
                       "scoring": scoring,
                       "current_quote": stock_quote})
            cHandler.execute(insert_query,(2, epoch, scoring, tweet.sentiment.polarity, tweet.sentiment.subjectivity, message, stock_quote))
        return True

    # on failure
    def on_error(self, status):
        print status

if __name__ == '__main__':

    # create instance of the tweepy tweet stream listener
    listener = TweetStreamListener()

    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # create instance of the tweepy stream
    stream = Stream(auth, listener)
    try:
        # search twitter for "congress" keyword
        stream.filter(track=[stock])
    except Exception, e:
        pass
