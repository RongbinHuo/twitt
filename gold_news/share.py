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
from nltk.corpus import wordnet as wn
import nltk

positive_words = set()
negative_words = set()
all_words_ary = []
words_dic = {}

def retrieve_content(link):
  try:
    req = urllib2.Request(link, headers={ 'User-Agent': 'Mozilla/5.0' })
    soup = BeautifulSoup(urllib2.urlopen(req).read())
    if 'www.kitco.com' in link:
      if soup.find("div", {"itemprop": "articleBody"}) is not None:
        content = soup.find("div", {"itemprop": "articleBody"}).getText()
      else:
        count=""
      return str(content)
    elif 'www.investing.com' in link:
      if soup.find("div", {"class" : "arial_14 clear WYSIWYG newsPage"}) is not None:
        content = soup.find("div", {"class" : "arial_14 clear WYSIWYG newsPage"}).getText()
      else:
        content=""
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
    
def retrieve_dic():
  global positive_words
  global negative_words
  global words_dic
  global all_words_ary
  conflict_words_file_name = '/home/ec2-user/twitt/gold_news/conflict_words.txt'

  with open(conflict_words_file_name) as f:
    for line in f:
      (key, val) = line.split(':')
      words_dic[key.strip().lower()] = float(val.strip())

  positive_words_file_name = '/home/ec2-user/twitt/gold_news/positive_factor.txt'
  with open(positive_words_file_name) as f:
    for line in f:
      word_ary = line.split(",")
      for w in word_ary:
        positive_words.add(w.strip().lower())

  negative_words_file_name = '/home/ec2-user/twitt/gold_news/negative_factor.txt'

  with open(negative_words_file_name) as f:
    for line in f:
      word_ary = line.split(",")
      for w in word_ary:
        negative_words.add(w.strip().lower())
  
  for w in positive_words:
    all_words_ary.append(w.strip())
  for w in negative_words:
    all_words_ary.append(w.strip())
        
def valid_sentence(sentence):
  global positive_words
  global negative_words
  is_valid = False
  for w in positive_words:
    if w.lower() in sentence.lower():
      is_valid = True
  for w in negative_words:
    if w.lower() in sentence.lower():
      is_valid = True
  return is_valid

def final_score(score_words):
  global positive_words
  global negative_words
  all_valued_words = positive_words | negative_words
  all_valued_words_counter = Counter(all_valued_words)
  all_valued_words_counter = Counter({x:0 for x in all_valued_words_counter})
  all_valued_words_counter.update(Counter(score_words))
  return all_valued_words_counter

def retrieve_useful_words(sentence):
  global positive_words
  global negative_words
  word_ary = []
  for w in positive_words:
    if w in sentence.lower():
      word_ary.append(w)
  for w in negative_words:
    if w in sentence.lower():
      word_ary.append(w)
  return word_ary

def special_match(strg, search=re.compile(r'[^a-z0-9.]').search):
  return not bool(search(strg))

def get_closer_word(word_ary_in_sent, word, word_ary):
  closer_word = ''
  min_distance = len(word_ary_in_sent)
  for w in word_ary:
    for ow in word_ary_in_sent:
      if w in ow:
        if abs(word_ary_in_sent.index(word) - word_ary_in_sent.index(ow)) < min_distance:
          closer_word = w
          min_distance = abs(word_ary_in_sent.index(word) - word_ary_in_sent.index(ow))
  return closer_word

def score(word, pos):
  global words_dic
  if pos == 'JJ':
    blob_scoring = TextBlob(word).sentiment.polarity
    synsets_scoring_entry = list(swn.senti_synsets(word,'a'))
    if len(synsets_scoring_entry) == 0:
      synsets_scoring = 0
    else:
      synsets_scoring = synsets_scoring_entry[0].pos_score() - synsets_scoring_entry[0].neg_score()
    if word in words_dic:
      return words_dic[word]
    else:
      return float(blob_scoring + synsets_scoring)/2

  if pos == 'VB':
    blob_scoring = TextBlob(word).sentiment.polarity
    synsets_scoring_entry = list(swn.senti_synsets(word,'v'))
    if len(synsets_scoring_entry) == 0:
      synsets_scoring = 0
    else:
      synsets_scoring = synsets_scoring_entry[0].pos_score() - synsets_scoring_entry[0].neg_score()
    if word in words_dic:
      return words_dic[word]
    else:
      return float(blob_scoring + synsets_scoring)/2

  if pos == 'RB':
    blob_scoring = TextBlob(word).sentiment.polarity
    synsets_scoring_entry = list(swn.senti_synsets(word,'r'))
    if len(synsets_scoring_entry) == 0:
      synsets_scoring = 0
    else:
      synsets_scoring = synsets_scoring_entry[0].pos_score() - synsets_scoring_entry[0].neg_score()
    if word in words_dic:
      return words_dic[word]
    else:
      return float(blob_scoring + synsets_scoring)/2
  return 0.0

def analyze_sentence(sentence, word_ary):
  global words_dic
  word_score = {}
  words_ary = word_tokenize(sentence)
  words_ary = [str(wn.morphy(w.lower())) for w in words_ary]
  tagged_words = nltk.pos_tag(words_ary)
  for w in word_ary:
    word_score[w] = 0.0
  if len(words_ary) == 1:
    for word,pos in tagged_words:
      word_score[word_ary[0]] = word_score[word_ary[0]] + score(word,pos)
  else:
    for word,pos in tagged_words:
      closest_word = get_closer_word(words_ary, word, word_ary)
      if closest_word:
          word_score[closest_word] = word_score[closest_word] + score(word,pos)
  return word_score

def scoring_sentence(sentence):
  sent_words = {}
  total = Counter()
  if valid_sentence(sentence):
    word_ary = retrieve_useful_words(sentence)
    total.update(Counter(analyze_sentence(sentence, word_ary)))
  return dict(total)

def scoring_article(content_ary):
  total = Counter()
  for sent in content_ary:
    total.update(Counter(scoring_sentence(sent)))
  return dict(total)
    