import sqlite3
import pandas as pd
import csv

data = pd.read_csv("flipkart_usable_database.csv",)

conn = sqlite3.connect("easyshop.db")
db = conn.cursor()
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
data.to_sql("items", conn, if_exists="append",index=False)
# count = 0
# for row in data.values:
#     try :
#         db.execute("INSERT INTO items VALUES(?)",(row[1:]))
#     except :
#         count += 1
#         pass
#
#print(count)

conn.commit()
conn.close()
