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
