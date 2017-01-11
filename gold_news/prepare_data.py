from textblob import TextBlob
from nltk.corpus import wordnet as wn
import MySQLdb
import re
from collections import Counter
from BeautifulSoup import BeautifulSoup
import share
from nltk.tokenize import sent_tokenize, word_tokenize
from textblob import TextBlob
from nltk.tag import pos_tag
from nltk.corpus import sentiwordnet as swn
import nltk


positive_words = set()
negative_words = set()
all_words_ary = []
words_dic = {}
news_vector = {}

def retrieve_dic():
  global positive_words
  global negative_words
  global words_dic
  global all_words_ary
  conflict_words_file_name = '../gold_news/conflict_words.txt'

  with open(conflict_words_file_name) as f:
    for line in f:
      (key, val) = line.split(':')
      words_dic[key.strip().lower()] = float(val.strip())

  positive_words_file_name = '../gold_news/positive_factor.txt'

  with open(positive_words_file_name) as f:
    for line in f:
      word_ary = line.split(",")
      for w in word_ary:
        positive_words.add(w.strip().lower())

  negative_words_file_name = '../gold_news/negative_factor.txt'

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
#   final_s = 0.0
#   for sw in score_words:
#     if sw in positive_words:
#       final_s = final_s+score_words[sw]
#     else:
#       final_s = final_s-score_words[sw]
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
  if len(word_ary) == 1:
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


myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com", port=3306, user="root", passwd="12345678", db="twit")
retrieve_dic()
cHandler = myDB.cursor()
select_query = """SELECT id, text, link, create_at FROM gold_news """
cHandler.execute(select_query)
results = cHandler.fetchall()

date_range = {}
count = 0
for row in results:
    count = count+1
    link = row[2]
    time = row[3]
    if 'www.kitco.com' in link:
        print count
        content_ary = share.parse_kitco_content(share.retrieve_content(link))
        current_score = final_score(scoring_article(content_ary))
        if time.date() not in date_range:
            date_range[time.date()] = current_score
        else:
            date_range[time.date()].update(current_score)
print date_range


file_name = '../gold_news/words_count_with_date.txt'
thefile = open(file_name, 'w')
for item in date_range:
  thefile.write("%s\n" % str(item).strip()+" : "+str(list(date_range[item].items())))
