import sqlite3
import json
import pip._vendor.requests
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def update_names():
    con = sqlite3.connect(db_path)

    # Load drug names
    url = "https://health-products.canada.ca/api/drug/drugproduct"
    response = pip._vendor.requests.get(url)
    js = response.json()
    db_now = con.execute("SELECT drug_code,updated FROM drug_names")
    drcs = {}
    for r in db_now:
        drcs[r[0]] = r[1]
    for x in range(len(js)):
        drc = js[x]["drug_code"]
        ud = js[x]["last_update_date"] 
        if drc in drcs:
            if drcs[drc] != ud:
                din = js[x]["drug_identification_number"]
                dn = js[x]["brand_name"]
                var_list = [drc, din, dn, ud]
                con.execute("INSERT INTO drug_names (drug_code, din, name, updated) VALUES (?,?,?,?)", var_list)
            else:
                continue
        else:
            continue
        
    # Load manufacturer names
    url = "https://health-products.canada.ca/api/drug/company"
    response = pip._vendor.requests.get(url)
    js = response.json()
    db_now = con.execute("SELECT company_id FROM manufacturer_names")
    ccs = []
    for r in db_now:
        ccs.append(r[0])
    for x in range(len(js)):
        cc = js[x]["company_code"] 
        if cc in ccs:
            continue
        else:
            cn = js[x]["company_name"]
            var_list = [cc, cn]
            con.execute("INSERT INTO manufacturer_names (company_id, name) VALUES (?,?)", var_list)

    # Load ingredients
    url = "https://health-products.canada.ca/api/drug/activeingredient"
    response = pip._vendor.requests.get(url)
    js = response.json()
    db_now = con.execute("SELECT name FROM ingredient_names")
    db_names = []
    for r in db_now:
        db_names.append(r[0])
    these_names = []
    for x in range(len(js)):
        name = js[x]["ingredient_name"]
        if name in db_names or name in these_names:
            continue
        else:
            these_names.append(name)
            con.execute("INSERT INTO ingredient_names (name) VALUES (?)", (name,))
    con.commit()
    con.close()