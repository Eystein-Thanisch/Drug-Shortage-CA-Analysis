import sqlite3

con = sqlite3.connect("data\dpd_codes.db")
cur = con.cursor()
#cur.execute("SELECT * FROM shortages")
#shortages = cur.fetchall()
#for s in shortages:
drug = cur.execute("SELECT drug_name FROM drugs WHERE din = ?", ('02150204',)).fetchall()
print(drug)




