#coding: utf8
import datetime
import time
import os
from Util import *
import MySQLdb
from conf.dbconf import dbconf


pos_dir = "/tmp/OnesideDolphin/YesterdayPosition/"
now = datetime.datetime.now()
tag = get_minutes_to_closemarket(now.strftime("%H:%M:%S"))

#if tag != -1 and tag != 241 and tag != 120.5:
if True:
    g_conn = MySQLdb.connect(host = dbconf['HOST'], user = dbconf['USER'], passwd = dbconf['PASSWORD'], db = dbconf['NAME'], charset = 'utf8')
    g_cur = g_conn.cursor()

    all_time_delta = []
    for f in os.listdir(pos_dir):
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(pos_dir + f))
        delta = now - mtime
        all_time_delta.append(int(delta.seconds))

    stockid = candidate_stock_pairs[0].split("_")[0]

    sql = "select max(time) from dolphin_stockmetadata where date='" + str(now.date()) + "' and stockid='" + stockid + "'"
    g_cur.execute(sql)
    res = g_cur.fetchall()
    if len(res) > 0 and len(res[0]) > 0:
        data_up_time = res[0][0]
        up_time = now - now.replace(hour=0).replace(minute=0).replace(second=0)
        delta = up_time - data_up_time
        seconds = delta.days*24*3600 + delta.seconds
        if seconds > 120:
            print "warning!!!", seconds
            os.system("curl http://127.0.0.1:8082/dolphin/stop_all/")
            time.sleep(3)
            os.system("curl http://127.0.0.1:8082/dolphin/init/")
            time.sleep(20)
            os.system("curl http://127.0.0.1:8082/dolphin/start_all/")

    if max(all_time_delta) < 60:
        print datetime.datetime.now(), "warning!!!", delta.seconds

    g_cur.close()
    g_conn.close()