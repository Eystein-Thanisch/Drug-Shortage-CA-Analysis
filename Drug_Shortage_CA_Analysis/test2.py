import sqlite3

con = sqlite3.connect("dpd_codes.db")
cur = con.cursor()
code = 14412
cur.execute("SELECT company_name FROM companies WHERE company_code = ?", (code,))
data = cur.fetchall()
name = data[0][0]
print(name)