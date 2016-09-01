from yahoo_finance import Share
import json
from elasticsearch import Elasticsearch
import time
from datetime import datetime, tzinfo
import pytz
import numpy as np

date_now = int(time.time())
date_passed_48_hours =  int(time.time()) - 72*60*60
es = Elasticsearch()
yahoo = Share('AMZN')
res = es.search(index='stocks',doc_type='Amazon', body={ "size": 0, "aggs": { "avg_grade": { "avg": { "field": 'scoring'}}}})
avg_score_all_data = res["aggregations"]["avg_grade"]["value"]
stock_year_high = float(yahoo.get_year_high())
stock_year_low = float(yahoo.get_year_low())

res = es.search(index='stocks',doc_type='Amazon', body={ "size": 3000, "query": { "range": { "created_at": { "gte": date_passed_48_hours, "lte": date_now}}}})
original_quote = float(res["hits"]["hits"][0][u'_source'][u'current_quote'])
dataset = res["hits"]["hits"]
for data in dataset:
	utc_epoch = data[u'_source'][u'created_at']
	dt = dt.fromtimestamp(utc_epoch)
	y_m_d = dt.strftime('%Y-%m-%d')
	stock_day_range_high = yahoo.get_historical(y_m_d,y_m_d)[0]['High']
	stock_day_range_low = yahoo.get_historical(y_m_d,y_m_d)[0]['Low']
	time_range_start = utc_epoch - 60*60*3
	time_range_end = utc_epoch - 60*60*2
	res = es.search(index='stocks',doc_type='Amazon', body={ "size": 0, "query": { "range": { "created_at": { "gte": time_range_start, "lte": time_range_end}}}, 
		  "aggs": { "avg_grade": { "avg": { "field": 'scoring'}}}})
	score_range_avg = res["aggregations"]["avg_grade"]["value"]
	res = es.search(index='stocks',doc_type='Amazon', body={ "size": 0, "query": { "range": { "created_at": {"lte": time_range_start}}}, 
		  "aggs": { "avg_grade": { "avg": { "field": 'scoring'}}}})
	score_range_avg_pre = res["aggregations"]["avg_grade"]["value"]
	quote_data = float(data[u'_source'][u'current_quote'])
	quote_data_year_percent = (quote_data - stock_year_low)/(stock_year_high - quote_data)
	quote_data_increase = (quote_data - original_quote)/original_quote
	quote_data_day_percent = (quote_data - stock_day_range_low)/(stock_day_range_high - quote_data)
	symbol = 0
	if quote_data_increase >0:
		symbol = 1
	if quote_data_increase <0:
		symbol = -1
	if score_range_avg > 0 and score_range_avg !=None and score_range_avg_pre !=None:
		scoring_increase_overall = (score_range_avg-avg_score_all_data)/avg_score_all_data
		scoring_increase_than_pre = (score_range_avg-score_range_avg_pre)/score_range_avg_pre
		train_data = scoring_increase_overall, scoring_increase_than_pre, quote_data_year_percent, quote_data_day_percent, symbol
		train_arry = np.array(train_data)
		with open(r'../data/train_data.csv', 'a') as f:
			f.write(",".join(map(str, train_arry))+'\n')

	original_quote = quote_data




# res = es.search(index='stocks',doc_type='Amazon', body={ "size": 3000, "query": { "range": { "created_at": { "gte": date_passed_72_hours, "lte": date_now}}}})
# res["hits"]["hits"]
# res = es.search(index='stocks',doc_type='Amazon', body={ "size": 3000, "query": { "range": { "created_at": { "gte": date_passed_72_hours, "lte": date_now}}}, 
# 		  "aggs": { "avg_grade": { "avg": { "field": 'scoring'}}}})