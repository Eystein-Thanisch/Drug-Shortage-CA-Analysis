import sqlite3
import json
import pip._vendor.requests
import os.path

from datetime import datetime
from flask import render_template, request
from Drug_Shortage_CA_Analysis import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Functions
def update_names():
    db_path = os.path.join(BASE_DIR, "dpd_search_terms.db")
    con = sqlite3.connect(db_path)
    lists = []

    # Load drug names
    drugs = []
    url = "https://health-products.canada.ca/api/drug/drugproduct"
    response = pip._vendor.requests.get(url)
    js = response.json()
    db_now = con.execute("SELECT drug_code,updated FROM drug_names")
    drcs = {}
    for r in db_now:
        drcs[r[0]] = r[1]
    for x in range(len(js)):
        drug = {}
        din = js[x]["drug_identification_number"]
        dn = js[x]["brand_name"]
        drug = {"name" : dn, "code" : din}
        drugs.append(drug)
        drc = js[x]["drug_code"]
        ud = js[x]["last_update_date"] 
        if drc in drcs:
            if drcs[drc] != ud:
                var_list = [drc, din, dn, ud]
                con.execute("INSERT INTO drug_names (drug_code, din, name, updated) VALUES (?,?,?,?)", var_list)
            else:
                continue
        else:
            continue
    lists.append(drugs)
        
    # Load manufacturer names
    manufacturers = []
    url = "https://health-products.canada.ca/api/drug/company"
    response = pip._vendor.requests.get(url)
    js = response.json()
    db_now = con.execute("SELECT company_id FROM manufacturer_names")
    ccs = []
    for r in db_now:
        ccs.append(r[0])
    for x in range(len(js)):
        manufacturer = {}
        cc = js[x]["company_code"] 
        cn = js[x]["company_name"]
        manufacturer = {"name" : cn, "code" : cc}
        manufacturers.append(manufacturer)
        if cc in ccs:
            continue
        else:
            var_list = [cc, cn]
            con.execute("INSERT INTO manufacturer_names (company_id, name) VALUES (?,?)", var_list)
    lists.append(manufacturers)

    # Load ingredients
    ingredients = []
    url = "https://www.drugshortagescanada.ca/api/v1/search"
    # TO DO: Move the auth-token to the environment before submission!
    auth_header = {'auth-token' : '02597e45864d4229bcb509e6db650f7a'}
    response = pip._vendor.requests.get(url, headers = auth_header)
    total_js = response.json()
    js = total_js["data"]
    for x in range(len(js)):
        for y in range(len(js[x]["drug"]["drug_ingredients"])):
            ingredient = {}
            ing_code = js[x]["drug"]["drug_ingredients"][y]["ingredient"]["ingredient_code"]
            ing_name = js[x]["drug"]["drug_ingredients"][y]["ingredient"]["en_name"]
            ingredient = {"name" : ing_name, "code" : ing_code}
            ingredients.append(ingredient)
    db_now = con.execute("SELECT ingredient_code FROM ingredient_names")
    db_codes = []
    for r in db_now:
        db_codes.append(r[0])
    these_codes = []
    for x in range(len(ingredients)):
        name = ingredients[x]["name"]
        code = ingredients[x]["code"]
        if code in db_codes or code in these_codes:
            continue
        else:
            these_codes.append(code)
            var_list = [name, code]
            con.execute("INSERT INTO ingredient_names (name, ingredient_code) VALUES (?,?)", var_list)
    con.commit()
    con.close()
    lists.append(ingredients)
    return lists


# Routes

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/summary')
def summary():
    if request.method == "POST":
        return render_template('to_do.html')
    else:
        lists = update_names()
        return render_template('summaries.html', lists=lists)
