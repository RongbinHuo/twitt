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
from sets import Set
from nltk.corpus import sentiwordnet as swn
import nltk

word_count={}
conflict_words = Set()

positive_words = ["gold", "yellow metal", "inflation", "fear", "CPI", "emerging markets", "euro", "imbalances", "oil", "demand",
 "Global Crisis", "Government Reserves", "Chinese economy", "Australian", "British", "pound", "silver", "sterling", "China", "brexit", "trump", "european", "yen", "risk", "bond", "mining", "weakness", "crash"]

negative_words = ["u.s.", "interest", "rates", "dollar", "US debt", "imbalances", "financial repression", "US economy", "Central Bank", "equity market", "hike", "greenback", "clinton", "data", "employment", "yellen"]
def retrieve_content(link):
  try:
    soup = BeautifulSoup(urllib2.urlopen(link).read())
    if soup.find("div", {"itemprop": "articleBody"}) is not None:
      content = soup.find("div", {"itemprop": "articleBody"}).getText()
    else:
      count=""
    return str(content)
  except:
    return ""

def parse_kitco_content(content):
  sent_ary = []
  sent_tokenize = nltk.data.load('tokenizers/punkt/english.pickle')
  sent_ary = sent_tokenize.tokenize(content)
  for se in sent_ary:
    if to_discard(se): sent_ary.remove(se)
  for se in sent_ary:
  	if '*' in se and se.startswith('*'):
  		sent_ary.remove(se)
  		sent_ary.extend(parse_headline(se))
  return sent_ary

def to_discard(sent):
  total_size  = float(len(sent))
  useful_size = float(len(re.sub('[^a-zA-Z0-9-_*,.%]', '', sent)))
  if useful_size/total_size <0.5:
    return True
  else:
    return False

def special_match(strg, search=re.compile(r'[^a-z0-9.]').search):
  return not bool(search(strg))

def parse_headline(sent):
  return sent.split('*')[1:]

def count_words(sent):
  global word_count
  words_ary = word_tokenize(sent)
  tagged_words = pos_tag(words_ary)
  propernouns = [word.lower() for word,pos in tagged_words if pos == 'NNP' or pos == 'NN']
  counts_counter = Counter(propernouns)
  word_count_counter = Counter(word_count)
  word_count = dict(counts_counter+word_count_counter)

def retrieve_conflict_words(sent):
  global conflict_words
  words_ary = word_tokenize(sent)
  tagged_words=nltk.pos_tag(words_ary)
  for word,pos in tagged_words:
    if pos == 'JJ':
      blob_scoring = TextBlob(word).sentiment.polarity
      synsets_scoring_entry = list(swn.senti_synsets(word,'a'))
      if len(synsets_scoring_entry) == 0:
        synsets_scoring = 0
      else:
        synsets_scoring = synsets_scoring_entry[0].pos_score() - synsets_scoring_entry[0].neg_score()
      if ((blob_scoring ==0 and synsets_scoring ==0) or (blob_scoring * synsets_scoring <0)) and special_match(word):
        conflict_words.add(word)
    if pos == 'VB':
      blob_scoring = TextBlob(word).sentiment.polarity
      synsets_scoring_entry = list(swn.senti_synsets(word,'v'))
      if len(synsets_scoring_entry) == 0:
        synsets_scoring = 0
      else:
        synsets_scoring = synsets_scoring_entry[0].pos_score() - synsets_scoring_entry[0].neg_score()
      if ((blob_scoring ==0 and synsets_scoring ==0) or (blob_scoring * synsets_scoring <0)) and special_match(word):
        conflict_words.add(word)
    if pos == 'RB':
      blob_scoring = TextBlob(word).sentiment.polarity
      synsets_scoring_entry = list(swn.senti_synsets(word,'r'))
      if len(synsets_scoring_entry) == 0:
        synsets_scoring = 0
      else:
        synsets_scoring = synsets_scoring_entry[0].pos_score() - synsets_scoring_entry[0].neg_score()
      if ((blob_scoring ==0 and synsets_scoring ==0) or (blob_scoring * synsets_scoring <0)) and special_match(word):
        conflict_words.add(word)


myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com", port=3306, user="root", passwd="12345678", db="twit")
cHandler = myDB.cursor()
select_query = """SELECT id, text, link FROM gold_news """
cHandler.execute(select_query)
results = cHandler.fetchall()

# Count words frequency in the documents
for row in results:
  link = row[2]
  if 'www.kitco.com' in link:
    print link
    content_ary = parse_kitco_content(retrieve_content(link))
    for c in content_ary:
      if not to_discard(c):
        count_words(c)
print 'Count words done!'

# Checking conflict words and words with no scoring
for row in results:
  link = row[2]
  if 'www.kitco.com' in link:
    print link
    content_ary = parse_kitco_content(retrieve_content(link))
    for c in content_ary:
      retrieve_conflict_words(c)
    print conflict_words

words_list = list(conflict_words)
file_name = '../gold_news/conflict_words.txt'
thefile = open(file_name, 'w')
for item in words_list:
  thefile.write("%s\n" % item)










