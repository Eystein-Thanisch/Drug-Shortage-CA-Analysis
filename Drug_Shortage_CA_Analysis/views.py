import sqlite3
import json
import pip._vendor.requests
import os.path

from datetime import datetime, timedelta
from flask import render_template, request
from Drug_Shortage_CA_Analysis import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    for x in range(len(js)):
        ingredient = {}
        ing_code = x
        ing_name = js[x]["ingredient_name"]
        ingredient = {"name" : ing_name, "code" : ing_code}
        ingredients.append(ingredient)
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
        lists = get_names()
        return render_template('summaries.html', lists=lists)
