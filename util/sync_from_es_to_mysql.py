import MySQLdb
from elasticsearch import Elasticsearch

myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com",port=3306,user="root",passwd="12345678",db="twit")
cHandler = myDB.cursor()
es = Elasticsearch()
res=es.search(index='stocks',doc_type='Amazon', body={"query":{"filtered":{"filter":{"exists":{"field": "current_quote"}}}}})
insert_query = """INSERT INTO ratings (company_id, created_at, rating, polarity, subjectivity, message, current_price) VALUES (%s,%s,%s,%s,%s,%s,%s)"""


total_records = res["hits"]["total"]

res=es.search(index='stocks',doc_type='Amazon', body={ "size": total_records, "query":{"filtered":{"filter":{"exists":{"field": "current_quote"}}}},"sort": [{"created_at": "asc"}]})

if total_records < 30000:
    dataset = res["hits"]["hits"]
    for data_h in dataset:
        print "asd"
        data = data_h['_source']
        stock_quote = float(data["current_quote"])
        polarity = float(data["polarity"])
        scoring = float(data["scoring"])
        message = data["message"].encode('utf-8').strip()
        subjectivity = float(data["subjectivity"])
        company_id = 1
        created_at = data["created_at"]
        cHandler.execute(insert_query,(1, created_at, scoring,polarity,subjectivity, message, stock_quote))

myDB.commit()
myDB.close()
