words_dic = {}
file_name = 'gold_news/conflict_words.txt'

with open(file_name) as f:
  for line in f:
    (key, val) = line.split(':')
    words_dic[key.strip()] = float(val.strip())
