from yahoo_finance import Share
import json
from elasticsearch import Elasticsearch
import time
from datetime import datetime, tzinfo
import pytz
import numpy as np

date_now = int(time.time())
date_passed_72_hours =  int(time.time()) - 72*60*60
es = Elasticsearch()
yahoo = Share('AMZN')
# res = es.search(index='stocks',doc_type='Amazon', body={ "size": 0, "aggs": { "count_by_type": { "terms": { "field": '_type'}}}})
res = es.search(index='stocks',doc_type='Amazon', body={ "size": 0, "aggs": { "avg_grade": { "avg": { "field": 'scoring'}}}})
avg_score_all_data = res["aggregations"]["avg_grade"]["value"]
stock_year_high = float(yahoo.get_year_high())
stock_year_low = float(yahoo.get_year_low())
# res = es.search(index='stocks',doc_type='Amazon', body={ "size": 0, "aggs": { "min_time": { "min": { "field": 'created_at'}}}})
# min_timestamp = res["aggregations"]["min_time"]["value"]
# res = es.search(index='stocks',doc_type='Amazon', body={ "size": 0, "aggs": { "max_time": { "max": { "field": 'created_at'}}}})
# max_timestamp = res["aggregations"]["max_time"]["value"]

dataset = np.genfromtxt("./data/quote_data.csv", dtype=None, delimiter=',') 
original_quote = dataset[0][1]
for data in dataset:
	tmp_timestamp = data[0]
	time_range_start = tmp_timestamp - 60*30
	time_range_end = tmp_timestamp - 60*20
	res = es.search(index='stocks',doc_type='Amazon', body={ "size": 0, "query": { "range": { "created_at": { "gte": time_range_start, "lte": time_range_end}}}, 
		  "aggs": { "avg_grade": { "avg": { "field": 'scoring'}}}})
	score_range_avg = res["aggregations"]["avg_grade"]["value"]
	res = es.search(index='stocks',doc_type='Amazon', body={ "size": 0, "query": { "range": { "created_at": {"lte": time_range_start}}}, 
		  "aggs": { "avg_grade": { "avg": { "field": 'scoring'}}}})
	score_range_avg_pre = avg_score_all_data if res["aggregations"]["avg_grade"]["value"] == None else res["aggregations"]["avg_grade"]["value"]
	quote_data = data[1]
	quote_data_year_percent = (stock_year_high - quote_data)/(quote_data - stock_year_low)
	quote_data_increase = quote_data_year_percent * (quote_data-original_quote)/original_quote
	scoring_increase_overall = (score_range_avg-avg_score_all_data)/avg_score_all_data
	scoring_increase_than_pre = (score_range_avg-score_range_avg_pre)/score_range_avg_pre
	if score_range_avg > 0:
		train_data = quote_data_increase, quote_data_year_percent, scoring_increase_overall, scoring_increase_than_pre, quote_data_increase
		train_arry = np.array(train_data)
		with open(r'./data/train_data.csv', 'a') as f:
			f.write(",".join(map(str, train_arry))+'\n')

	original_quote = quote_data




# res = es.search(index='stocks',doc_type='Amazon', body={ "size": 3000, "query": { "range": { "created_at": { "gte": date_passed_72_hours, "lte": date_now}}}})
# res["hits"]["hits"]
# res = es.search(index='stocks',doc_type='Amazon', body={ "size": 3000, "query": { "range": { "created_at": { "gte": date_passed_72_hours, "lte": date_now}}}, 
# 		  "aggs": { "avg_grade": { "avg": { "field": 'scoring'}}}})