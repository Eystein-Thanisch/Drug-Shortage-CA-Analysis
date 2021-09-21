import sqlite3
import json

from datetime import datetime
from flask import render_template, request
from Drug_Shortage_CA_Analysis import app

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
        con = sqlite3.connect("drug_names.db")
        url = "https://health-products.canada.ca/api/drug/drugproduct"
        response = requests.get(url)
        js = response.json()
        for x in range(len(js)):
            din = js[x]["drug_identification_number"]
        con.close()
        return render_template('summaries.html')
