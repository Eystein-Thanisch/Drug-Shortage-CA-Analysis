import sqlite3

con = sqlite3.connect("\\data\\dpd_codes.db")
cur = con.cursor()
code = 18136
cur.execute("SELECT reason,started FROM shortages WHERE drug_code = ?", (code,))
data = cur.fetchall()
print(data)