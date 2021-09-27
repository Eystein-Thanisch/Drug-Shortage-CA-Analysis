import sqlite3
import json
import pip._vendor.requests
import os.path

from datetime import datetime, timedelta
from flask import render_template, request
from Drug_Shortage_CA_Analysis import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# NB: FIND A MORE SECURE WAY OF ACCESSING THIS BEFORE SUBMISSION!!!
auth_token = "02597e45864d4229bcb509e6db650f7a"

# Functions

def get_names():
    lists = []

    #Drugs
    drugs = []
    url = "https://health-products.canada.ca/api/drug/drugproduct"
    response = pip._vendor.requests.get(url)
    js = response.json()
    for x in range(len(js)):
        drug = {}
        din = js[x]["drug_identification_number"]
        dn = js[x]["brand_name"]
        drug = {"name" : dn, "code" : din}
        drugs.append(drug)
    lists.append(drugs)

    #Manufacturers
    manufacturers = []
    url = "https://health-products.canada.ca/api/drug/company"
    response = pip._vendor.requests.get(url)
    js = response.json()
    for x in range(len(js)):
        manufacturer = {}
        cc = js[x]["company_code"] 
        cn = js[x]["company_name"]
        manufacturer = {"name" : cn, "code" : cc}
        manufacturers.append(manufacturer)
    lists.append(manufacturers)

    #Ingredients
    ingredients = []
    url = "https://health-products.canada.ca/api/drug/activeingredient"
    response = pip._vendor.requests.get(url)
    js = response.json()
    names = []
    for x in range(len(js)):
        ing_name = js[x]["ingredient_name"]
        names.append(ing_name)
    # This method of de-duplicating a list is based on: https://www.w3schools.com/python/python_howto_remove_duplicates.asp
    names = list(dict.fromkeys(names))
    for y in range(len(names)):
        ingredient = {}
        ing_code = y
        ing_name = names[y]
        ingredient = {"name" : ing_name, "code" : ing_code}
        ingredients.append(ingredient)
    lists.append(ingredients)
    return lists

def get_summary(subj, type, term):
    if subj == 0:
        data = []
        dict1 = {}
        dict2 = {}

        # Drug Details
        base_url = "https://health-products.canada.ca/api/drug/drugproduct"
        url = base_url + "/?din=" + term
        response = pip._vendor.requests.get(url)
        js = response.json()
        code = js[0]["drug_code"]
        dict2["name"] = js[0]["brand_name"]
        dict2["class"] = js[0]["class_name"]
        dict2["manufacturer"] = js[0]["company_name"]

        # Active Ingredients
        base_url = "https://health-products.canada.ca/api/drug/activeingredient"
        url = base_url + "/?id=" + str(code)
        response = pip._vendor.requests.get(url)
        js = response.json()
        l = len(js)
        ingredients = []
        for x in range(l):
            dict3 = {}
            ingredient = js[x]["ingredient_name"]
            dict3["name"] = ingredient
            ingredients.append(dict3)
        dict2["ingredients"] = ingredients
        dict1["drug_details"] = dict2

        # Current Status
        dict2 = {}
        base_url = "https://health-products.canada.ca/api/drug/status"
        url = base_url + "/?id=" + str(code)
        response = pip._vendor.requests.get(url)
        js = response.json()
        dict2["status"] = js["status"]
        dict2["since"] = js["history_date"]
        dict2["marketed"] = js["original_market_date"]
        dict1["drug_status"] = dict2

        # Shortage History
        dict2 = {}
        base_url = "https://www.drugshortagescanada.ca/api/v1"
        url = base_url + "/search?din=" + term
        header = {"auth-token" : auth_token}
        response = pip._vendor.requests.get(url, headers = header)
        js = response.json()
        if js["total"] == 0:
            dict2["shortages"] = 0
        else:
            dict2["shortages"] = 1
        dict1["shortage_info"] = dict2
        data.append(dict1)
        return data
    elif subj == 1:
        return
    elif subj == 2:
        return
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

@app.route('/summary', methods=["GET", "POST"])
def summary():
    if request.method == "POST":
        lists = []
        query = {}
        subj = int(request.form.get("subject"))
        type = int(request.form.get("type"))
        term = request.form.get("term")
        query["subj"] = int(request.form.get("subject"))
        query["type"] = int(request.form.get("type"))
        query["term"] = request.form.get("term")
        lists.append(query)
        response = get_summary(subj, type, term)
        lists.append(response)
        print(lists)
        return render_template('summarized.html', lists=lists)
    else:
        lists = get_names()
        return render_template('summaries.html', lists=lists)
