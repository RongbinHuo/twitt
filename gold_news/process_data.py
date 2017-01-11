import datetime
import ast
import MySQLdb

file_name = './gold_news/words_count_with_date.txt'
thefile = open(file_name, 'r')
processed_data = {}
count = 0
for line in thefile:
    count = count+1
    dt = datetime.datetime.strptime(line.split(":")[0].strip(),'%Y-%m-%d')
    next_day = dt + datetime.timedelta(days=1)
    myDB = MySQLdb.connect(host="rongbin.cdpxz2jepyxw.us-east-1.rds.amazonaws.com", port=3306, user="root", passwd="12345678", db="twit")
    cHandler = myDB.cursor()
    select_query = """SELECT close, open FROM dust_price WHERE date = '%s' """ % (next_day.strftime('%Y-%m-%d %H:%M:%S'))
    cHandler.execute(select_query)
    results = cHandler.fetchall()
    count = 0
    while len(results) == 0 and count < 5:
        count = count+1
        next_day = next_day + datetime.timedelta(days=1)
        select_query = """SELECT close, open FROM dust_price WHERE date = '%s' """ % (next_day.strftime('%Y-%m-%d %H:%M:%S'))
        cHandler.execute(select_query)
        results = cHandler.fetchall()
    close_price = 0
    open_price = 0
    if len(results) >0:
        close_price = results[0][0]
        open_price = results[0][1]
    ary  = line.split(":")[1].strip()
    testarray = ast.literal_eval(ary)
    new_ary = [p[1] for p in testarray]
    processed_data[dt] = []
    processed_data[dt].append(new_ary)
    if open_price == 0:
        processed_data[dt].append(0.0)
    else:
        processed_data[dt].append((close_price - open_price)/open_price)
print processed_data

processed_file = '../gold_news/processed_data.txt'
thefile = open(processed_file, 'w')
for item in processed_data:
  thefile.write("%s\n" % str(item).strip()+" : "+str(list(processed_data[item])))