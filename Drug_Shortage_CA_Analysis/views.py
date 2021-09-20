import sqlite3

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
        con.execute("CREATE TABLE drug_names (din NUMERIC, name TEXT)")
        con.execute("CREATE TABLE manufacturer_names (company_id NUMERIC, name TEXT)")
        con.execute("CREATE TABLE ingredient_names (atc_id NUMERIC, name TEXT)")
        con.close()
        return render_template('summaries.html')
