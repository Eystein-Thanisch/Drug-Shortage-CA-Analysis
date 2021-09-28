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
        manufacturer = js[x]["company_name"]
        drug = {"name" : dn, "code" : din, "manufacturer" : manufacturer}
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
        dict2 = {}

        # Latest Shortage/Discontinuation
        base_url = "https://www.drugshortagescanada.ca/api/v1"
        url = base_url + "/search?din=" + term + "&orderby=updated_date&order=desc"
        header = {"auth-token" : auth_token}
        response = pip._vendor.requests.get(url, headers = header)
        reports = response.json()
        in_shortage = False
        if reports["total"] == 0:
            dict2["total_shortages"] = 0
            dict2["total_discontinuations"] = 0
        else:
            dict2["report_id"] = reports["data"][0]["id"]
            if reports["data"][0]["status"] == "active_confirmed" or reports["data"][0]["status"] == "resolved":
                dict2["report_url"] = "https://www.drugshortagescanada.ca/shortage/" + str(dict2["report_id"])
                dict2["status"] = reports["data"][0]["status"]
                dict2["latest_start"] = reports["data"][0]["actual_start_date"].rpartition("T")[0]
                dict2["latest_reason"] = reports["data"][0]["shortage_reason"]["en_reason"]
                if reports["data"][0]["status"] == "resolved":
                    dict2["latest_resolved"] = True
                    dict2["resolved_date"] = reports["data"][0]["updated_date"].rpartition("T")[0]
                    dict2["latest_est_end"] = "N/A"
                else:
                    in_shortage = True
                    dict2["latest_resolved"] = False
                    dict2["latest_est_end"] = reports["data"][0]["estimated_end_date"].rpartition("T")[0]
            elif reports["data"][0]["status"] == "discontinued" or reports["data"][0]["status"] == "reversed":
                dict2["report_url"] = "https://www.drugshortagescanada.ca/discontinuance/" + str(dict2["report_id"])
                dict2["status"] = reports["data"][0]["status"]
                dict2["latest_start"] = reports["data"][0]["updated_date"].rpartition("T")[0]
                dict2["latest_reason"] = reports["data"][0]["discontinuance_reason"]["en_reason"]
                if reports["data"][0]["status"] == "reversed":
                    dict2["latest_reversed"] = True
                    dict2["reversed_date"] = reports["data"][0]["updated_date"].rpartition("T")[0]
                    dict2["latest_est_end"] = "N/A"
                else:
                    dict2["latest_reversed"] = False
                    dict2["latest_est_end"] = reports["data"][0]["updated_date"].rpartition("T")[0]
        
        # Total Shortages
        url = base_url + "/search?din=" + term + "&orderby=updated_date&order=desc&filter_status=resolved"    
        response = pip._vendor.requests.get(url, headers = header)
        shortages = response.json()
        if in_shortage:
            dict2["total_shortages"] = shortages["total"] + 1
        else:
            dict2["total_shortages"] = shortages["total"]
        
        # Append and Send
        dict1["shortage_info"] = dict2
        data.append(dict1)
        return data
    elif subj == 1:
        data = []
        dict1 = {}
        dict2 = {}

        # Company Details
        base_url = "https://health-products.canada.ca/api/drug/company"
        url = base_url + "/?id=" + term
        response = pip._vendor.requests.get(url)
        js = response.json()
        name = js["company_name"]
        dict2["name"] = name
        dict2["code"] = js["company_code"]
        dict2["location"] = js["city_name"] + ", " + js["province_name"] + ", " + js["country_name"]
        dict2["type"] = js["company_type"]
        dict1["company_details"] = dict2

        # Drugs Marketed
        dict2 = {}
        url = "https://health-products.canada.ca/api/drug/drugproduct"
        response = pip._vendor.requests.get(url)
        js = response.json()
        counter = 0
        for x in range(len(js)):
            if js[x]["company_name"] == name:
                counter = counter + 1
        dict2["drug_count"] = counter
        base_url = "https://www.drugshortagescanada.ca/api/v1"
        url = base_url + "/search?orderby=updated_date&order=desc&filter_status=resolved&term=" + name
        header = {"auth-token" : auth_token}
        response = pip._vendor.requests.get(url, headers = header)
        reports = response.json()
        resolved = reports["total"]
        url = base_url + "/search?orderby=updated_date&order=desc&filter_status=active_confirmed&term=" + name
        response = pip._vendor.requests.get(url, headers = header)
        reports = response.json()
        active = reports["total"]
        dict2["report_count"] = resolved + active

        dict1["drugs_marketed"] = dict2
        data.append(dict1)

        return data
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
