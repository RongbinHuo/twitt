from textblob import TextBlob
import MySQLdb
from BeautifulSoup import BeautifulSoup


positive_words = set()
negative_words = set()
words_dic = {}

def retrieve_dic():
  global positive_words
  global negative_words
  global words_dic
  conflict_words_file_name = 'gold_news/conflict_words.txt'

  with open(conflict_words_file_name) as f:
    for line in f:
      (key, val) = line.split(':')
      words_dic[key.strip()] = float(val.strip())

  positive_words_file_name = 'gold_news/positive_factor.txt'

  with open(positive_words_file_name) as f:
    for line in f:
      word_ary = line.split(",")
      for w in word_ary:
        positive_words.add(w.strip())

  negative_words_file_name = 'gold_news/negative_factor.txt'

  with open(negative_words_file_name) as f:
    for line in f:
      word_ary = line.split(",")
      for w in word_ary:
        negative_words.add(w.strip())


myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com", port=3306, user="root", passwd="12345678", db="twit")
retrieve_dic()
cHandler = myDB.cursor()
select_query = """SELECT id, text, link FROM gold_news """
cHandler.execute(select_query)
results = cHandler.fetchall()

for row in results:
  link = row[2]
  if 'www.kitco.com' in link:
    print link
    
