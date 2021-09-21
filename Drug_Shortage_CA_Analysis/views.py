import helpers

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
    db_path = os.path.join(BASE_DIR, "dpd_search_terms.db")
    if request.method == "POST":
        return render_template('to_do.html')
    else:
        update_names()
        return render_template('summaries.html')
