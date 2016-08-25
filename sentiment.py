import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
from elasticsearch import Elasticsearch
import time
from datetime import datetime

# import twitter keys and tokens
from config import *

es = Elasticsearch()
company = 'Amazon'
stock = "$AMZN"
class TweetStreamListener(StreamListener):
	# on success
    def on_data(self, data):

    	dict_data = json.loads(data)

    	tweet = TextBlob(dict_data["text"])

    	print tweet.sentiment.polarity

    	if tweet.sentiment.polarity < 0:
            sentiment = "negative"
        elif tweet.sentiment.polarity == 0:
            sentiment = "neutral"
        else:
            sentiment = "positive"

        print sentiment
        
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(dict_data["created_at"],'%a %b %d %H:%M:%S +0000 %Y'))
        scoring =  (1-tweet.sentiment.subjectivity)*tweet.sentiment.polarity

        es.index(index="stocks",
                 doc_type="Amazon",
                 body={"company": dict_data["user"]["screen_name"],
                       "created_at": time_stamp,
                       "message": dict_data["text"],
                       "polarity": tweet.sentiment.polarity,
                       "subjectivity": tweet.sentiment.subjectivity,
                       "sentiment": sentiment,
                       "scoring": scoring})

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

    # search twitter for "congress" keyword
    stream.filter(track=[company, stock])