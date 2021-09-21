import sqlite3
import json
import pip._vendor.requests
import os.path

from datetime import datetime
from flask import render_template, request
from Drug_Shortage_CA_Analysis import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    db_path = os.path.join(BASE_DIR, "dpd_search_terms.db")
    if request.method == "POST":
        return render_template('to_do.html')
    else:
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
        con.commit()
        con.close()
        return render_template('summaries.html')
