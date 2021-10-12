import json
import requests
import os.path
import sqlite3

from datetime import datetime, timezone
from flask import render_template, request, send_file
from pyvis.network import Network
from Drug_Shortage_CA_Analysis import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# NB: FIND A MORE SECURE WAY OF ACCESSING THIS BEFORE SUBMISSION!!!
auth_token = "02597e45864d4229bcb509e6db650f7a"

def update_database():
   con = sqlite3.connect(BASE_DIR + "\\data\dpd_codes.db")
   cur = con.cursor()

   # Companies
   cur.execute("DELETE FROM companies")
   url = "https://health-products.canada.ca/api/drug/company"
   response = requests.get(url)
   company_data = response.json()
   values = []
   codes = set()
   for datum in company_data:
       if datum["company_code"] not in codes:
           codes.add(datum["company_code"])
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
   codes = set()
   for datum in drug_data:
       code = datum["drug_code"]
       if code not in codes:
           codes.add(code)
           owner = datum["company_name"]
           din = datum["drug_identification_number"]
           cur.execute("SELECT company_code FROM companies WHERE company_name = ?", (owner,))
           ccode = cur.fetchall()[0][0]
           details = (code, datum["brand_name"], ccode, din)
           values.append(details)
   cur.executemany("INSERT INTO drugs (drug_code, drug_name, owner, din) VALUES(?, ?, ?, ?)", values)
   con.commit()

   # Drug Status
   url = "https://health-products.canada.ca/api/drug/status"
   response = requests.get(url)
   status_data = response.json()
   for datum in status_data:
       drug_code = datum["drug_code"]
       status = datum["status"]
       details = (status, drug_code)
       cur.execute("UPDATE drugs SET status = ? WHERE drug_code = ?", details)
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
       o = o + 50
       response = requests.get(url, headers = header)
       reports = response.json()
       if "error" in reports:
           error_text = reports["error"]["en"]
           return render_template("error.html", text = error_text)
       data = reports["data"]
       for report in data:
           report_id = report["id"]
           try:
               drug_code = report["drug"]["drug_code"]
           except:
               drug_code = report["drug"]["din"]
           din = report["drug"]["din"]
           try:
               company_code = report["drug"]["company"]["company_code"]
           except:
               company_code = "no_code"
           reason = report["shortage_reason"]["en_reason"]
           started = ""
           try:
               started = report["actual_start_date"]
           except:
               started = report["anticipated_start_date"]
           details = (drug_code, company_code, reason, started, report_id, din)
           values.append(details)
   cur.executemany("INSERT INTO shortages (drug_code, company_code, reason, started, report_id, din) VALUES (?, ?, ?, ?, ?, ?)", values)
   con.commit()

   # Anticipated Shortages
   cur.execute("DELETE FROM anticipated_shortages")
   base_url = "https://www.drugshortagescanada.ca/api/v1/search?filter_status=anticipated_shortage&limit=50"
   header = {"auth-token" : auth_token}
   response = requests.get(base_url, headers = header)
   reports = response.json()
   if "error" in reports:
       error_text = reports["error"]["en"]
       return render_template("error.html", text = error_text)
   p = reports["total_pages"]
   o = 0
   values = []
   for x in range(p):
       url = base_url + "&offset=" + str(o)
       o = o + 50
       response = requests.get(url, headers = header)
       reports = response.json()
       data = reports["data"]
       for report in data:
           report_id = report["id"]
           try:
               drug_code = report["drug"]["drug_code"]
           except:
               drug_code = report["drug"]["din"]
           din = report["drug"]["din"]
           try:
               company_code = report["drug"]["company"]["company_code"]
           except:
               company_code = "no_code"
           reason = report["shortage_reason"]["en_reason"]
           started = report["anticipated_start_date"]
           details = (drug_code, company_code, reason, started, report_id, din)
           values.append(details)
   cur.executemany("INSERT INTO anticipated_shortages (drug_code, company_code, reason, started, report_id, din) VALUES (?, ?, ?, ?, ?, ?)", values)
   con.commit()

   # Discontinuations
   cur.execute("DELETE FROM discontinuations")
   base_url = "https://www.drugshortagescanada.ca/api/v1/search?filter_status=discontinued&limit=50"
   header = {"auth-token" : auth_token}
   response = requests.get(base_url, headers = header)
   reports = response.json()
   if "error" in reports:
       error_text = reports["error"]["en"]
       return render_template("error.html", text = error_text)
   p = reports["total_pages"]
   o = 0
   values = []
   for x in range(p):
       url = base_url + "&offset=" + str(o)
       o = o + 50
       response = requests.get(url, headers = header)
       reports = response.json()
       data = reports["data"]
       for report in data:
           report_id = report["id"]
           try:
               drug_code = report["drug"]["drug_code"]
           except:
               drug_code = report["drug"]["din"]
           din = report["drug"]["din"]
           try:
               company_code = report["drug"]["company"]["company_code"]
           except:
               company_code = "no_code"
           reason = report["discontinuance_reason"]["en_reason"]
           started = ""
           try:
               started = report["discontinuation_date"]
           except:
               started = report["anticipated_discontinuation_date"]
           details = (drug_code, company_code, reason, started, report_id, din)
           values.append(details)
   cur.executemany("INSERT INTO discontinuations (drug_code, company_code, reason, started, report_id, din) VALUES (?, ?, ?, ?, ?, ?)", values)
   con.commit()

   con.close
   return

def get_names():
    lists = []

    #Drugs
    drugs = []
    con = sqlite3.connect(BASE_DIR + "\\data\dpd_codes.db")
    cur = con.cursor()
    cur.execute("SELECT drug_code,drug_name,din,company_name FROM d_and_c")
    drug_data = cur.fetchall()
    for d in drug_data:
        drug = {}
        drug_code = d[0]
        din = d[2]
        drug_name = d[1]
        owner = d[3]
        drug = {"name" : drug_name, "code" : din, "company" : owner}
        drugs.append(drug)
    lists.append(drugs)

    #Manufacturers
    companies = []
    con = sqlite3.connect(BASE_DIR + "\\data\dpd_codes.db")
    cur = con.cursor()
    cur.execute("SELECT company_code,company_name FROM companies")
    comps = cur.fetchall()
    for comp in comps:
        company = {}
        cc = comp[0] 
        cn = comp[1]
        company = {"name" : cn, "code" : cc}
        companies.append(company)
    lists.append(companies)

    #Ingredients
    names = set()
    con = sqlite3.connect(BASE_DIR + "\\data\dpd_codes.db")
    cur = con.cursor()
    cur.execute("SELECT ingredient_name FROM ingredients")
    ings = cur.fetchall()
    for ing in ings:
        names.add(ing[0])
    counter = 0
    ingredients = []
    for name in names:
        counter += 1
        ingredient = {}
        ing_code = counter
        ing_name = name
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
        dict2["company"] = js[0]["company_name"]

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
                try:
                    dict2["latest_start"] = reports["data"][0]["actual_start_date"].rpartition("T")[0]
                except:
                    dict2["latest_start"] = reports["data"][0]["anticipated_start_date"].rpartition("T")[0]
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
        if "error" in reports:
            dict2["report_count"] = "unavailable"
            dict2["active_reports"] = "unavailable"
        else:
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
        companies = []
        for x in range(len(drugs)):
            code = drugs[x]
            base_url = "https://health-products.canada.ca/api/drug/drugproduct"
            url = base_url + "/?id=" + str(code)
            response = requests.get(url)
            js = response.json()
            company = js["company_name"]
            if company not in companies:
                companies.append(company)
        dict2["company_count"] = len(companies)
        dict1["ingredient_details"] = dict2

        # Shortage Details
        dict2 = {}
        base_url = "https://www.drugshortagescanada.ca/api/v1"
        url = base_url + "/search?orderby=updated_date&order=desc&filter_status=resolved&term=" + name
        header = {"auth-token" : auth_token}
        response = requests.get(url, headers = header)
        reports = response.json()
        if "error" in reports:
            dict2["report_count"] = "unavailable"
            dict2["active_reports"] = "unavailable"
        else:
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
    if "error" in js:
        data.append("error")
        return data
    reports = js["data"]
    for x in range(20):
        dict = {}
        dict["id"] = reports[x]["id"]
        dict["url"] = "https://www.drugshortagescanada.ca/shortage/" + str(reports[x]["id"])
        updated_date = reports[x]["updated_date"]
        dt_object = datetime.strptime(updated_date, "%Y-%m-%dT%H:%M:%S-04:00")
        ts = round(dt_object.timestamp() * 1000)
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%m/%d/%Y %H:%M:%S")
        dict["date"] = dt
        dict["event"] = reports[x]["status"]
        dict["drug"] = reports[x]["drug"]["brand_name"]
        dict["din"] = reports[x]["drug"]["din"]
        dict["company"] = reports[x]["drug"]["company"]["name"]
        dict["code"] = reports[x]["drug"]["company"]["company_code"]
        data.append(dict)
    return data

def get_graph_report(id):
    subj = 0
    base_url = "https://www.drugshortagescanada.ca/api/v1/shortages/"
    url = base_url + str(id)
    header = {"auth-token" : auth_token}
    response = requests.get(url, headers = header)
    report = response.json()
    din = report["drug"]["din"]
    get_graph_entity(subj,type,din)
    return

def get_graph_all():
    # Create network
    net = Network("800px", "100%")

    # Get report data
    con = sqlite3.connect(BASE_DIR + "\\data\dpd_codes.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM shortages")
    shortages = cur.fetchall()

    # Build network
    for s in shortages:
        drug_code = s[1]
        if isinstance(drug_code, str):
            drug_code = cur.execute("SELECT drug_code FROM drugs WHERE din = ?", (drug_code,)).fetchall()[0][0]
        company_code = s[2]
        reason = s[3]
        started = s[4]
        report_id = s[5]
        din = s[6]
        drug_name = cur.execute("SELECT drug_name FROM drugs WHERE drug_code = ?", (drug_code,)).fetchall()[0][0]
        company_name = cur.execute("SELECT company_name FROM companies WHERE company_code = ?", (company_code,)).fetchall()[0][0]
        net.add_node(drug_code, label = drug_name, title = str(din) + "<br/>" + reason + "<br/>From " + started + "<br/>Report " + str(report_id), color = "#e30e38", shape = "diamond")
        net.add_node(company_code, label = company_name, color = "#5380cf", shape = "square")
        net.add_edge(company_code, drug_code)
        ingredients = cur.execute("SELECT ingredient_name FROM ingredients WHERE used_in = ?", (drug_code,)).fetchall()
        for ingredient in ingredients:
            ing_name = ingredient[0]
            net.add_node(ing_name, label = ing_name, color = "#d0d624", shape = "triangle")
            net.add_edge(drug_code, ing_name)

    # Save visualized network graph
    os.chdir(BASE_DIR + "\\templates")
    net.show_buttons(filter_=['physics'])
    net.save_graph('shortages_graph.html')
    os.chdir(BASE_DIR)
    con.close()
    return

def get_graph_entity(subj,type,id):
    # Create network
    net = Network("800px", "100%")

    # Connect to database
    con = sqlite3.connect(BASE_DIR + "\\data\\dpd_codes.db")
    cur = con.cursor()

    # Get shortage list
    cur.execute("SELECT * FROM shortages")
    shortages = cur.fetchall()
    shortage_list = {}
    for s in shortages:
        shortage_list[s[1]] = {}
        shortage_list[s[1]]["reason"] = s[3]
        shortage_list[s[1]]["started"] = s[4]

    # Get anticipated shortages list
    cur.execute("SELECT * FROM anticipated_shortages")
    ant_shortages = cur.fetchall()
    ant_shortage_list = {}
    for a_s in ant_shortages:
        ant_shortage_list[a_s[1]] = {}
        ant_shortage_list[a_s[1]]["reason"] = a_s[3]
        ant_shortage_list[a_s[1]]["started"] = a_s[4]

    # Get discontinuations list
    cur.execute("SELECT * FROM discontinuations")
    discontinuations = cur.fetchall()
    discontinuation_list = {}
    for d in discontinuations:
        discontinuation_list[d[1]] = {}
        discontinuation_list[d[1]]["reason"] = d[3]
        discontinuation_list[d[1]]["started"] = d[4]

    # Determine what is being searched for:
    # Drug
    if subj == 0:
        # Drug node
        cur.execute("SELECT * FROM drugs WHERE din = ?", (id,))
        drug_data = cur.fetchall()
        drug_code = drug_data[0][1]
        start_drug = drug_code
        drug_name = drug_data[0][2]
        din = id
        company = drug_data[0][3]
        status = drug_data[0][5]
        start_company = company
        title = din
        color = ""
        drug_nodes = set()
        drug_nodes.add(start_drug)
        if drug_code in shortage_list:
            reason = shortage_list[drug_code]["reason"]
            started = shortage_list[drug_code]["started"]
            color = "#e30e38"
            title = title + "<br/>" + reason + "<br/>From " + started
        elif drug_code in ant_shortage_list:
            reason = ant_shortage_list[drug_code]["reason"]
            started = ant_shortage_list[drug_code]["started"]
            color = "#cf8702"
            title = title + "<br/>" + reason + "<br/>From " + started
        elif drug_code in discontinuation_list or "CANCELLED" in status:
            try:
                reason = discontinuation_list[drug_code]["reason"]
                started = discontinuation_list[drug_code]["started"]
            except:
                reason = status
                started = "[unavailable]"
            color = "#abaaa7"
            title = title + "<br/>" + reason + "<br/>From " + started
        else:
            color = "#89d624"
        net.add_node(drug_code, label = drug_name, title = title, color = color, size = 100, mass = 100, shape = "diamond")

        # Company node
        company_name = cur.execute("SELECT company_name FROM companies WHERE company_code = ?", (company,)).fetchall()[0][0]
        net.add_node(company, label = company_name, color = "#5380cf", size = 100, mass = 100, shape = "square")
        net.add_edge(company, drug_code)

        # Ingredient nodes
        ingredient_nodes = set()
        ingredients = cur.execute("SELECT ingredient_name FROM ingredients WHERE used_in = ?", (drug_code,)).fetchall()
        for ingredient in ingredients:
            ing_name = ingredient[0]
            ingredient_nodes.add(ing_name)
            net.add_node(ing_name, label = ing_name, color = "#d0d624", size = 100, mass = 100, shape = "triangle")
            net.add_edge(drug_code, ing_name)
            
        # Ingredient links
        for ingredient in ingredients:
            ing_name = ingredient[0]
            ing_links = cur.execute("SELECT used_in FROM ingredients WHERE ingredient_name = ?", (ing_name,)).fetchall()
            for ing in ing_links:
                drug_code = ing[0]
                if drug_code not in drug_nodes:
                    drug_nodes.add(drug_code)
                    cur.execute("SELECT * FROM drugs WHERE drug_code = ?", (drug_code,))
                    drug_data = cur.fetchall()
                    drug_code = drug_data[0][1]
                    start_drug = drug_code
                    drug_name = drug_data[0][2]
                    din = drug_data[0][4]
                    status = drug_data[0][5]
                    company = drug_data[0][3]
                    title = din
                    color = ""
                    if drug_code in shortage_list:
                        reason = shortage_list[drug_code]["reason"]
                        started = shortage_list[drug_code]["started"]
                        color = "#e30e38"
                        title = title + "<br/>" + reason + "<br/>From " + started
                    elif drug_code in ant_shortage_list:
                        reason = ant_shortage_list[drug_code]["reason"]
                        started = ant_shortage_list[drug_code]["started"]
                        color = "#cf8702"
                        title = title + "<br/>" + reason + "<br/>From " + started
                    elif drug_code in discontinuation_list or "CANCELLED" in status:
                        try:
                            reason = discontinuation_list[drug_code]["reason"]
                            started = discontinuation_list[drug_code]["started"]
                        except:
                            reason = status
                            started = "[unavailable]"
                        color = "#abaaa7"
                        title = title + "<br/>" + reason + "<br/>From " + started
                    else:
                        color = "#89d624"
                    net.add_node(drug_code, label = drug_name, title = title, color = color, shape = "diamond")

                    company_name = cur.execute("SELECT company_name FROM companies WHERE company_code = ?", (company,)).fetchall()[0][0]
                    net.add_node(company, label = company_name, color = "#5380cf", shape = "square")
                    net.add_edge(company, drug_code)

                    ingredients = cur.execute("SELECT ingredient_name FROM ingredients WHERE used_in = ?", (drug_code,)).fetchall()
                    for ingredient in ingredients:
                        ing_name = ingredient[0]
                        if ing_name not in ingredient_nodes:
                            ingredient_nodes.add(ing_name)
                            net.add_node(ing_name, label = ing_name, color = "#d0d624", shape = "triangle")
                        net.add_edge(drug_code, ing_name)

        # Company links
        cur.execute("SELECT * FROM drugs WHERE owner = ?", (start_company,))
        drug_data = cur.fetchall()
        for drug in drug_data:
            drug_code = drug[1]
            if drug_code not in drug_nodes:
                drug_name = drug[2]
                din = drug[4]
                company = drug[3]
                status = drug[5]
                title = din
                color = ""
                if drug_code in shortage_list:
                    reason = shortage_list[drug_code]["reason"]
                    started = shortage_list[drug_code]["started"]
                    color = "#e30e38"
                    title = title + "<br/>" + reason + "<br/>From " + started
                elif drug_code in ant_shortage_list:
                    reason = ant_shortage_list[drug_code]["reason"]
                    started = ant_shortage_list[drug_code]["started"]
                    color = "#cf8702"
                    title = title + "<br/>" + reason + "<br/>From " + started
                elif drug_code in discontinuation_list or "CANCELLED" in status:
                    try:
                        reason = discontinuation_list[drug_code]["reason"]
                        started = discontinuation_list[drug_code]["started"]
                    except:
                        reason = status
                        started = "[unavailable]"
                    color = "#abaaa7"
                    title = title + "<br/>" + reason + "<br/>From " + started
                else:
                    color = "#89d624"
                net.add_node(drug_code, label = drug_name, title = title, color = color, shape = "diamond")
                net.add_edge(start_company, drug_code)
                ingredients = cur.execute("SELECT ingredient_name FROM ingredients WHERE used_in = ?", (drug_code,)).fetchall()
                for ingredient in ingredients:
                    ing_name = ingredient[0]
                    if ing_name not in ingredient_nodes:
                        ingredient_nodes.add(ing_name)
                        net.add_node(ing_name, label = ing_name, color = "#d0d624", shape = "triangle")
                    net.add_edge(drug_code, ing_name)

    # Company
    elif subj == 1:

        # Company Node
        cur.execute("SELECT * FROM companies WHERE company_code = ?", (id,))
        company_data = cur.fetchall()
        company = id
        company_name = company_data[0][2]
        net.add_node(company, label = company_name, color = "#5380cf", size = 100, mass = 100, shape = "square")

        # Drugs Nodes
        cur.execute("SELECT * FROM drugs WHERE owner = ?", (company,))
        drug_data = cur.fetchall()
        for drug in drug_data:
            drug_code = drug[1]
            drug_name = drug[2]
            din = drug[4]
            status = drug[5]
            title = din
            color = ""
            if drug_code in shortage_list:
                reason = shortage_list[drug_code]["reason"]
                started = shortage_list[drug_code]["started"]
                color = "#e30e38"
                title = title + "<br/>" + reason + "<br/>From " + started
            elif drug_code in ant_shortage_list:
                reason = ant_shortage_list[drug_code]["reason"]
                started = ant_shortage_list[drug_code]["started"]
                color = "#cf8702"
                title = title + "<br/>" + reason + "<br/>From " + started
            elif drug_code in discontinuation_list or "CANCELLED" in status:
                try:
                    reason = discontinuation_list[drug_code]["reason"]
                    started = discontinuation_list[drug_code]["started"]
                except:
                    reason = status
                    started = "[unavailable]"
                color = "#abaaa7"
                title = title + "<br/>" + reason + "<br/>From " + started
            else:
                color = "#89d624"
            net.add_node(drug_code, label = drug_name, title = title, color = color, shape = "diamond")
            net.add_edge(company, drug_code)

            # Ingredient nodes
            ingredients = cur.execute("SELECT ingredient_name FROM ingredients WHERE used_in = ?", (drug_code,)).fetchall()
            for ingredient in ingredients:
                ing_name = ingredient[0]
                net.add_node(ing_name, label = ing_name, color = "#d0d624", shape = "triangle")
                net.add_edge(drug_code, ing_name)

    # Ingredient
    elif subj == 2:
        ingredient_nodes = set()

        # Ingredient node
        ingredient_nodes.add(id)
        net.add_node(id, label = id, color = "#d0d624", size = 100, mass = 100, shape = "triangle")

        # Drug nodes
        cur.execute("SELECT used_in FROM ingredients WHERE ingredient_name = ?", (id,))
        drug_links = cur.fetchall()
        for link in drug_links:
            drug_code = link[0]
            cur.execute("SELECT * FROM drugs WHERE drug_code = ?", (drug_code,))
            drug_data = cur.fetchall()
            for drug in drug_data:
                drug_name = drug[2]
                din = drug[4]
                company = drug[3]
                status = drug[5]
                title = din
                color = ""
                if drug_code in shortage_list:
                    reason = shortage_list[drug_code]["reason"]
                    started = shortage_list[drug_code]["started"]
                    color = "#e30e38"
                    title = title + "<br/>" + reason + "<br/>From " + started
                elif drug_code in ant_shortage_list:
                    reason = ant_shortage_list[drug_code]["reason"]
                    started = ant_shortage_list[drug_code]["started"]
                    color = "#cf8702"
                    title = title + "<br/>" + reason + "<br/>From " + started
                elif drug_code in discontinuation_list or "CANCELLED" in status:
                    try:
                        reason = discontinuation_list[drug_code]["reason"]
                        started = discontinuation_list[drug_code]["started"]
                    except:
                        reason = status
                        started = "[unavailable]"
                    color = "#abaaa7"
                    title = title + "<br/>" + reason + "<br/>From " + started
                else:
                    color = "#89d624"
                net.add_node(drug_code, label = drug_name, title = title, color = color, shape = "diamond")
                net.add_edge(drug_code, id)

                # Company nodes
                company_name = cur.execute("SELECT company_name FROM companies WHERE company_code = ?", (company,)).fetchall()[0][0]
                net.add_node(company, label = company_name, color = "#5380cf", shape = "square")
                net.add_edge(company, drug_code)

                # Ingredient links
                ingredients = cur.execute("SELECT ingredient_name FROM ingredients WHERE used_in = ?", (drug_code,)).fetchall()
                for ingredient in ingredients:
                    ing_name = ingredient[0]
                    if ing_name not in ingredient_nodes:
                        net.add_node(ing_name, label = ing_name, color = "#d0d624", shape = "triangle")
                    net.add_edge(drug_code, ing_name)

    # Save visualized network graph
    net.set_edge_smooth('dynamic')
    os.chdir(BASE_DIR + "\\templates")
    net.show_buttons(filter_=['physics'])
    net.save_graph('shortages_graph.html')
    os.chdir(BASE_DIR)
    con.close()
    return

def update_dbdt():
    ts = round(datetime.utcnow().timestamp() * 1000)
    con = sqlite3.connect(BASE_DIR + "\\data\dpd_codes.db")
    cur = con.cursor()
    cur.execute("INSERT INTO updates (update_timestamp) VALUES(?)", (ts,))
    con.commit()
    con.close()
    return

def get_last_update():
    con = sqlite3.connect(BASE_DIR + "\\data\dpd_codes.db")
    cur = con.cursor()
    ts = cur.execute("SELECT MAX(update_timestamp) FROM updates").fetchall()[0][0]
    dt = datetime.fromtimestamp(ts / 1000).strftime("%m/%d/%Y %H:%M:%S")
    return dt

# Routes
@app.route('/', methods=["GET", "POST"])
@app.route('/home')
def home():
    if request.method == "POST":
        update_database()
        update_dbdt()
    update = {}
    last_update = get_last_update()
    lists = get_updates()
    update["last_update"] = last_update
    return render_template(
            'index.html', lists = lists, update=update,
            title='Home Page',
            year=datetime.now().year,
    )

@app.route('/visualize', methods=["GET", "POST"])
def visualize():
    if request.method == "POST":
        id = request.form.get("submit")
        what = int(request.form.get("what"))
        if what < 3:
            subj = int(request.form.get("subject"))
            type = int(request.form.get("type"))
            id = request.form.get("term")
            get_graph_entity(subj,type,id)
        elif what == 3:
            get_graph_report(id)
        elif what == 4:
            get_graph_all()
        else:
            return render_template('to_do.html')
        details = (what, id)
        # This Stack Overflow answer was used to understand how to disable Jinja caching: https://stackoverflow.com/a/43200326/9022913
        app.jinja_env.cache = {}
        return render_template('visualized.html', details = details,
            year=datetime.now().year,)
    else:
        lists = get_names()
        return render_template("visualize.html", lists = lists,
            year=datetime.now().year,)

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
        app.jinja_env.cache = {}
        return render_template('summarized.html', lists=lists,
            year=datetime.now().year,)
    else:
        lists = get_names()
        return render_template('summaries.html', lists=lists,
            year=datetime.now().year,)