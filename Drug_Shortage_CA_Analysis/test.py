import pip._vendor.requests
import json

class my_class(object):
   con = sqlite3.connect(db_path)
   url = "https://health-products.canada.ca/api/drug/drugproduct"
   response = pip._vendor.requests.get(url)
   js = response.json()
   for x in range(len(js)):
       drc = js[x]["drug_code"]
       din = js[x]["drug_identification_number"]
       dn = js[x]["brand_name"]
       ud = js[x]["last_update_date"]
       var_list = [drc, din, dn, ud]
       con.execute("INSERT INTO drug_names (drug_code, din, name, updated) VALUES (?,?,?,?)", var_list)
   pass




