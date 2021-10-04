import json
import requests
import os.path
import sqlite3

from datetime import datetime
from flask import render_template, request, send_file
from pyvis.network import Network
from Drug_Shortage_CA_Analysis import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# NB: FIND A MORE SECURE WAY OF ACCESSING THIS BEFORE SUBMISSION!!!
auth_token = "02597e45864d4229bcb509e6db650f7a"

def update_database():
   con = sqlite3.connect("Drug_Shortage_CA_Analysis\data\dpd_codes.db")
   cur = con.cursor()

   # Companies
   cur.execute("DELETE FROM companies")
   url = "https://health-products.canada.ca/api/drug/company"
   response = requests.get(url)
   company_data = response.json()
   values = []
   codes = []
   for datum in company_data:
       if datum["company_code"] not in codes:
           codes.append(datum["company_code"])
           details = (datum["company_code"], datum["company_name"])
           values.append(details)
   cur.executemany("INSERT INTO companies (company_code, company_name) VALUES(?, ?)", values)
   con.commit()

   # Drugs
   cur.execute("DELETE FROM drugs")
   url = "https://health-products.canada.ca/api/drug/drugproduct"
   response = requests.get(url)
   drug_data = response.json()
   values = []
   codes = []
   for datum in drug_data:
       code = datum["drug_code"]
       if code not in codes:
           codes.append(code)
           owner = datum["company_name"]
           cur.execute("SELECT company_code FROM companies WHERE company_name = ?", (owner,))
           ccode = cur.fetchall()[0][0]
           details = (code, datum["brand_name"], ccode)
           values.append(details)
   cur.executemany("INSERT INTO drugs (drug_code, drug_name, owner) VALUES(?, ?, ?)", values)
   con.commit()

   # Ingredients
   cur.execute("DELETE FROM ingredients")
   url = "https://health-products.canada.ca/api/drug/activeingredient"
   response = requests.get(url)
   ing_data = response.json()
   values = []
   for datum in ing_data:
       name = datum["ingredient_name"]
       used_in = datum["drug_code"]
       details = (name, used_in)
       values.append(details)
   cur.executemany("INSERT INTO ingredients (ingredient_name, used_in) VALUES(?, ?)", values)
   con.commit()

   # Shortages
   cur.execute("DELETE FROM shortages")
   base_url = "https://www.drugshortagescanada.ca/api/v1/search?filter_status=active_confirmed&limit=50"
   header = {"auth-token" : auth_token}
   response = requests.get(base_url, headers = header)
   reports = response.json()
   p = reports["total_pages"]
   o = 0
   values = []
   for x in range(p):
       url = base_url + "&offset=" + str(o)
       response = requests.get(url, headers = header)
       reports = response.json()
       data = reports["data"]
       for report in data:
           report_id = report["id"]
           drug_code = 0
           try:
               drug_code = report["drug"]["drug_code"]
           except:
               drug_code = report["drug"]["din"]
           finally:
               drug_code = 0
           company_code = report["drug"]["company"]["company_code"]
           reason = report["shortage_reason"]["en_reason"]
           started = ""
           try:
               started = report["actual_start_date"]
           except:
               started = report["anticipated_start_date"]
           finally:
               started = "nd"
           details = (drug_code, company_code, reason, started, report_id)
           values.append(details)
   cur.executemany("INSERT INTO shortages (drug_code, company_code, reason, started, report_id) VALUES (?, ?, ?, ?, ?)", values)
   o = o + 50
   con.commit()

   con.close
   return

def get_names():
    lists = []

    #Drugs
    drugs = []
    url = "https://health-products.canada.ca/api/drug/drugproduct"
    response = requests.get(url)
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
    response = requests.get(url)
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
    response = requests.get(url)
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
        response = requests.get(url)
        js = response.json()
        code = js[0]["drug_code"]
        dict2["name"] = js[0]["brand_name"]
        dict2["class"] = js[0]["class_name"]
        dict2["manufacturer"] = js[0]["company_name"]

        # Active Ingredients
        base_url = "https://health-products.canada.ca/api/drug/activeingredient"
        url = base_url + "/?id=" + str(code)
        response = requests.get(url)
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
        response = requests.get(url)
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
        response = requests.get(url, headers = header)
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
        response = requests.get(url, headers = header)
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
        response = requests.get(url)
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
        response = requests.get(url)
        js = response.json()
        counter = 0
        for x in range(len(js)):
            if js[x]["company_name"] == name:
                counter = counter + 1
        dict2["drug_count"] = counter
        base_url = "https://www.drugshortagescanada.ca/api/v1"
        url = base_url + "/search?orderby=updated_date&order=desc&filter_status=resolved&term=" + name
        header = {"auth-token" : auth_token}
        response = requests.get(url, headers = header)
        reports = response.json()
        resolved = reports["total"]
        url = base_url + "/search?orderby=updated_date&order=desc&filter_status=active_confirmed&term=" + name
        response = requests.get(url, headers = header)
        reports = response.json()
        active = reports["total"]
        dict2["report_count"] = resolved + active
        dict2["active_reports"] = active

        dict1["drugs_marketed"] = dict2
        data.append(dict1)

        return data
    elif subj == 2:
        data = []
        dict1 = {}
        dict2 = {}

        # Ingredient Details
        name = term
        dict2["name"] = name

        base_url = "https://health-products.canada.ca/api/drug/activeingredient"
        url = base_url + "/?ingredientname=" + term
        response = requests.get(url)
        js = response.json()
        counter = 0
        drugs = []
        for x in range(len(js)):
           counter = counter + 1
           drug_code = js[x]["drug_code"]
           drugs.append(drug_code)
        dict2["drug_count"] = counter
        manufacturers = []
        for x in range(len(drugs)):
            code = drugs[x]
            base_url = "https://health-products.canada.ca/api/drug/drugproduct"
            url = base_url + "/?id=" + str(code)
            response = requests.get(url)
            js = response.json()
            manufacturer = js["company_name"]
            if manufacturer not in manufacturers:
                manufacturers.append(manufacturer)
        dict2["manufacturer_count"] = len(manufacturers)
        dict1["ingredient_details"] = dict2

        # Shortage Details
        dict2 = {}
        base_url = "https://www.drugshortagescanada.ca/api/v1"
        url = base_url + "/search?orderby=updated_date&order=desc&filter_status=resolved&term=" + name
        header = {"auth-token" : auth_token}
        response = requests.get(url, headers = header)
        reports = response.json()
        resolved = reports["total"]
        url = base_url + "/search?orderby=updated_date&order=desc&filter_status=active_confirmed&term=" + name
        response = requests.get(url, headers = header)
        reports = response.json()
        active = reports["total"]
        dict2["report_count"] = resolved + active
        dict2["active_reports"] = active
        dict1["shortage_details"] = dict2

        data.append(dict1)

        return data

def get_updates():
    data = []
    base_url = "https://www.drugshortagescanada.ca/api/v1"
    url = base_url + "/search?orderby=updated_date&order=desc&limit=20"
    header = {"auth-token" : auth_token}
    response = requests.get(url, headers = header)
    js = response.json()
    reports = js["data"]
    for x in range(20):
        dict = {}
        dict["id"] = reports[x]["id"]
        dict["url"] = "https://www.drugshortagescanada.ca/shortage/" + str(reports[x]["id"])
        dict["date"] = reports[x]["updated_date"]
        dict["event"] = reports[x]["status"]
        dict["drug"] = reports[x]["drug"]["brand_name"]
        dict["din"] = reports[x]["drug"]["din"]
        dict["company"] = reports[x]["drug"]["company"]["name"]
        dict["code"] = reports[x]["drug"]["company"]["company_code"]
        data.append(dict)
    return data

def get_graph(id):
    # Get Report Data
    base_url = "https://www.drugshortagescanada.ca/api/v1/shortages/"
    url = base_url + str(id)
    header = {"auth-token" : auth_token}
    response = requests.get(url, headers = header)
    report = response.json()
    drug_name = report["drug"]["brand_name"]
    drug = report["drug"]["drug_code"]
    company_name = report["drug"]["company"]["name"]
    company = report["drug"]["company"]["company_code"]
    ingredients = []
    l = len(report["drug"]["drug_ingredients"])
    for x in range(l):
        name = report["drug"]["drug_ingredients"][x]["ingredient"]["en_name"]
        ingredients.append(name)

    # Build Initial Network
    net = Network()
    net.add_node(drug, label = drug_name, color = "#ddaafa", shape = "diamond")
    net.add_node(company, label = company_name, color = "#5380cf", shape = "square")
    l = len(ingredients)
    for x in range(l):
        net.add_node(ingredients[x], label = ingredients[x], color = "#cf538a", shape = "triangle")
    net.add_edge(company, drug)
    for x in range(l):
        net.add_edge(drug, ingredients[x])
    
    # Ingredient links
    for x in range(l):
        base_url = "https://health-products.canada.ca/api/drug/activeingredient"
        url = base_url + "/?ingredientname=" + ingredients[x]
        response = requests.get(url)
        ings = response.json()
        for y in ings:
            drug = y["drug_code"]
            base_url = "https://health-products.canada.ca/api/drug/drugproduct"
            url = base_url + "/?id=" + str(drug)
            response = requests.get(url)
            drug_data = response.json()
            drug_name = drug_data["brand_name"]
            net.add_node(drug, label = drug_name, color = "#ddaafa", shape = "diamond")
            net.add_edge(drug, ingredients[x])

    # Save Visualized Network Graph
    os.chdir(BASE_DIR + "\\templates")
    net.show_buttons(filter_=['physics'])
    net.save_graph('shortages_graph.html')
    os.chdir(BASE_DIR)
    return

def get_graph_all():
    # Create network
    net = Network("1000px", "1000px")

    # Get report data
    con = sqlite3.connect("Drug_Shortage_CA_Analysis\data\dpd_codes.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM shortages")
    shortages = cur.fetchall()

    # Build network
    for s in shortages:
        drug_code = s[1]
        company_code = s[2]
        reason = s[3]
        started = s[4]
        report_id = s[5]
        if drug_code != 0:
            drug_name = cur.execute("SELECT drug_name FROM drugs WHERE drug_code = ?", (drug_code,)).fetchall()[0][0]
            company_name = cur.execute("SELECT company_name FROM companies WHERE company_code = ?", (company_code,)).fetchall()[0][0]
            net.add_node(drug_code, label = drug_name, title = reason + "<br/>From " + started + "<br/>Report " + str(report_id), color = "#e30e38", shape = "diamond")
            net.add_node(company_code, label = company_name, color = "#5380cf", shape = "square")
            net.add_edge(company_code, drug_code)
            ingredients = cur.execute("SELECT ingredient_name FROM ingredients WHERE used_in = ?", (drug_code,)).fetchall()
            for ingredient in ingredients:
                ing_name = ingredient[0]
                net.add_node(ing_name, label = ing_name, color = "#a9d927", shape = "triangle")
                net.add_edge(drug_code, ing_name)

    # Save visualized network graph
    os.chdir(BASE_DIR + "\\templates")
    net.show_buttons(filter_=['physics'])
    net.save_graph('shortages_graph.html')
    os.chdir(BASE_DIR)
    return

# Routes
@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    lists = get_updates()
    update_database()
    return render_template(
        'index.html', lists = lists,
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/visualize', methods=["GET", "POST"])
def visualize():
    if request.method == "POST":
        id = request.form.get("submit")
        get_graph(id)
        return render_template('visualized.html')

@app.route('/visualize_all', methods=["GET", "POST"])
def visualize_all():
    if request.method == "POST":
        get_graph_all()
        return render_template('visualized.html')

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
