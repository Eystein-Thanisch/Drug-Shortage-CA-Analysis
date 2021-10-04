import sqlite3

con = sqlite3.connect("data\dpd_codes.db")
cur = con.cursor()
#cur.execute("SELECT * FROM shortages")
#shortages = cur.fetchall()
#for s in shortages:
ingredients = cur.execute("SELECT ingredient_name FROM ingredients WHERE used_in = ?", (78819,)).fetchall()
print(ingredients)




