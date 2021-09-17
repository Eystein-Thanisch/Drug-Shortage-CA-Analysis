"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)

import Drug_Shortage_CA_Analysis.views
