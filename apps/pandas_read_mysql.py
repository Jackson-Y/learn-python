# -*- coding: utf-8 -*-
import pandas as pd
import pymysql

conn = pymysql.connect(host='192.168.106.231', \
               user='root',password='cnkidras', \
               db='psmc',charset='utf8', use_unicode=True)

sql = 'select GroupName from psmc_user_study_group limit 20'
df = pd.read_sql(sql, con=conn)
print(df.head())

df.to_csv("data.csv")
conn.close()
