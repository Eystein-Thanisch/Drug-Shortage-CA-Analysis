import sqlite3
import requests
import json
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class my_class(object):
   con = sqlite3.connect("dpd_codes.db")
   cur = con.cursor()

   # Companies
   url = "https://health-products.canada.ca/api/drug/company"
   response = requests.get(url)
   company_data = response.json()
   codes = []
   for datum in company_data:
       code = datum["company_code"]
       cur.execute("SELECT * FROM companies WHERE company_code = ?", (code,))
       if len(cur.fetchall()) > 0:
           continue
       if code in codes:
           continue
       else:
           codes.append(code)
           values = (datum["company_code"], datum["company_name"])
           cur.execute("INSERT INTO companies (company_code, company_name) VALUES(?, ?)", values)
   con.commit()

   # Drugs
   url = "https://health-products.canada.ca/api/drug/drugproduct"
   response = requests.get(url)
   drug_data = response.json()
   codes = []
   for datum in drug_data:
       code = datum["drug_code"]
       cur.execute("SELECT * FROM drugs WHERE drug_code = ?", (code,))
       if len(cur.fetchall()) > 0:
           continue
       if code in codes:
           continue
       else:
           codes.append(code)
           owner = datum["company_name"]
           cur.execute("SELECT company_code FROM companies WHERE company_name = ?", (owner,))
           ccode_data = cur.fetchall()
           ccode = ccode_data[0][0]
           values = (datum["drug_code"], datum["brand_name"], ccode)
           cur.execute("INSERT INTO drugs (drug_code, drug_name, owner) VALUES(?, ?, ?)", values)
   con.commit()

   # Ingredients
   url = "https://health-products.canada.ca/api/drug/activeingredient"
   response = requests.get(url)
   ing_data = response.json()
   names = []
   for datum in ing_data:
       name = datum["ingredient_name"]
       cur.execute("SELECT * FROM ingredients WHERE ingredient_name = ?", (name,))
       if len(cur.fetchall()) > 0:
           continue
       if name in names:
           continue
       else:
           names.append(name)
           used_in = datum["drug_code"]
           values = (name, used_in)
           cur.execute("INSERT INTO ingredients (ingredient_name, used_in) VALUES(?, ?)", values)
   con.commit()
   con.close
   pass




