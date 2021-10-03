import sqlite3
import requests
import json
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class my_class(object):
   con = sqlite3.connect("dpd_codes.db")
   cur = con.cursor()
   url = "https://health-products.canada.ca/api/drug/company"
   response = requests.get(url)
   company_data = response.json()
   codes = []
   for datum in company_data:
       code = datum["company_code"]
       print(cur.execute("SELECT * FROM companies WHERE company_code = ?", code))
       if code in codes:
           continue
       else:
           codes.append(code)
           values = (datum["company_code"], datum["company_name"])
           cur.execute("INSERT INTO companies (company_code, company_name) VALUES(?, ?)", values)
   con.commit()
   con.close
   pass




