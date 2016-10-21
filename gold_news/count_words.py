from textblob import TextBlob
import MySQLdb
import re
import schedule
import urllib2
from BeautifulSoup import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
from textblob import TextBlob
from nltk.tag import pos_tag
from nltk.corpus import sentiwordnet as swn
import nltk
import gold_news.share


word_count={}
conflict_words = set()

positive_words = ["gold", "yellow metal", "inflation", "fear", "CPI", "emerging markets", "euro", "imbalances", "oil", "demand",
 "Global Crisis", "Government Reserves", "Chinese economy", "Australian", "British", "pound", "silver", "sterling", "China", "brexit", "trump", "european", "yen", "risk", "bond", "mining", "weakness", "crash"]

negative_words = ["u.s.", "interest", "rates", "dollar", "US debt", "imbalances", "financial repression", "US economy", "Central Bank", "equity market", "hike", "greenback", "clinton", "data", "employment", "yellen"]


myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com", port=3306, user="root", passwd="12345678", db="twit")
cHandler = myDB.cursor()
select_query = """SELECT id, text, link FROM gold_news """
cHandler.execute(select_query)
results = cHandler.fetchall()

# Count words frequency in the documents
# for row in results:
#   link = row[2]
#   if 'www.kitco.com' in link:
#     print link
#     content_ary = parse_kitco_content(retrieve_content(link))
#     for c in content_ary:
#       if not to_discard(c):
#         count_words(c)
# print 'Count words done!'

# Checking conflict words and words with no scoring
for row in results:
  link = row[2]
  if 'www.kitco.com' in link:
    print link
    content_ary = parse_kitco_content(retrieve_content(link))
    for c in content_ary:
      retrieve_conflict_words(c)

words_list = list(conflict_words)
file_name = '../gold_news/conflict_words.txt'
thefile = open(file_name, 'w')
for item in words_list:
  thefile.write("%s\n" % item)










