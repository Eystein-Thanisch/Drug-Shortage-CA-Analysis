import sqlite3

con = sqlite3.connect("data\dpd_codes.db")
cur = con.cursor()
cur.execute("SELECT drug_code FROM shortages")
shortage_list = cur.fetchall()
print(3089 in shortage_list)




