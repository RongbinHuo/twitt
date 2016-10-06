from textblob import TextBlob
import MySQLdb
import schedule


def job():
  myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com",port=3306,user="root",passwd="12345678",db="twit")
  cHandler = myDB.cursor()
  select_query = """SELECT id, text FROM gold_news where auto_scoring IS NULL"""
  insert_query = """UPDATE gold_news SET auto_scoring = %s WHERE id = %s"""
  cHandler.execute(select_query)
  news_with_id = {}
  news_with_scoring = {}
  results = cHandler.fetchall()
  for row in results:
    news_with_id[row[0]] = row[1].decode('utf-8').strip()
  
  for key in news_with_id:
    news_blob = TextBlob(news_with_id[key])
    news_with_scoring[key] = news_blob.sentiment.subjectivity
  
  
  for key in news_with_scoring:
    cHandler.execute(insert_query,(float(news_with_scoring[key]),key))

  myDB.commit()
  myDB.close()

schedule.every(3).hours.do(job)

while 1:
  schedule.run_pending()
