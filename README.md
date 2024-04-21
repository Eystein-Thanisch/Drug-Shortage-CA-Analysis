# Drug Shortage Canada: Analysis (DSCA)

#### Video Demo:

View a short demo of DSCA [here](https://youtu.be/SYDqVUg2Y0s).

#### Description

##### Motivation
Drug Shortage Canada: Analysis (DSCA) offers basic analysis and visualizations of the latest data from [Drug Shortages Canada](https://www.drugshortagescanada.ca), supported by data from 
the [Drug Product Database](https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/drug-product-database). It aims to provide contextual and historical information 
related to medicine shortages that will help trace the underlying cause and anticipate how the situation will develop.

Medicine shortages constitute a complex global problem, with obvious impacts on patient care. Causes can include high demand straining manufacturing or distribution capacity, low demand causing 
providers to discontinue products, regulatory obstacles, or extraneous disruptions to the supply chain. The resulting shortages have most impact in the Global South, where governments and 
healthcare providers have less purchasing power and less access to market intelligence. However, the problem is most easily studied in the Global North, where more data is typically available, 
often thanks to mandatory reporting systems like [Drug Shortages Canada](https://www.drugshortagescanada.ca). Furthermore, in such countries, shortages are the exception rather than the rule, 
meaning that newly emerging shortage situations are more readily identifiable.

[Drug Shortages Canada](https://www.drugshortagescanada.ca) and the [Drug Product Database](https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/drug-product-database) 
already offer sophisticated search functionality on their own sites, but their focus is on returning lists of individual shortage reports and product profiles. The present app supplements this 
information by visualizing the relevant products, ingredients, and companies as network graphs (built and visualized via [Pyvis](https://pyvis.readthedocs.io/en/latest/)). These network graphs 
can reveal whether an individual shortage is potentially part of a wider trend and, if so, what might merit further investigation to better understand that trend. For example, it might turn out 
that the product owner has reported a string of shortages recently citing "Business reasons", in which case the shortage may be due to a change in strategy on their part. Alternatively, a number 
of products using the same active ingredient may have gone into shortage, suggesting that there might be problems sourcing this ingredient. The app does not provide any definite answers, but it 
provides some useful materials for thinking about the problem.

##### Functionality
Data is provided by DSCA in three different ways:
- The **Dashboard**, on the DSCA homepage, presents key data from the most recent 20 shortage reports, live from [Drug Shortages Canada's](https://www.drugshortagescanada.ca) API, along with links to the reports themselves.
- **Summary** will return a brief factfile on the user-specified drug, company, or active ingredient, including some headline figures on their history of involvement in shortages.
- Network graphs: **Entity Network*** will return an interactive network graph centred on the user-specified drug, company, or active ingredient, plus its neighbours in the network to a depth of 2, while **Shortages Network** will return an interactive network graph showing all drugs currently in shortage, plus their active ingredients and owners. Each report on the <strong>Dashboard</strong> can also be visualized as a network graph centred on the product.
Most of this data (the exception being the contents of the **Dashboard**) is not live from the [Drug Shortages Canada](https://www.drugshortagescanada.ca) and 
[Drug Product Database](https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/drug-product-database) APIs; it has been cached in a database to facilitate relatively 
swift retrieval and to ensure compliance with the [Drug Product Database](https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/drug-product-database) API's call limit. This
database can be refreshed at any time by the web app administrator. When it was last refreshed is shown on the homepage.

##### Technical Details
DCSA is a [Flask](https://flask.palletsprojects.com/en/2.0.x/) application. It was built initially in Visual Studio Code, using the provided Flask Web Project template, although some alterations had to be made when moving the application to the CS50 IDE 
for submission. The application also makes use of a combination of API calls (via [requests](https://docs.python-requests.org/en/latest/)) and a [SQLite](https://www.sqlite.org/index.html) database for obtaining data in response to user queries. Its webpages are rendered using a combination 
of HTML and [Jinja](https://jinja.palletsprojects.com/en/3.0.x/), with some use of [Bootstrap](https://getbootstrap.com/) and some bespoke JavaScript and JQuery functions, as well as [Select2](https://select2.org/). The network visualizations are built and 
rendered in [Pyvis](https://pyvis.readthedocs.io/en/latest/).

Under the hood, the application is created in \_\_init\_\_.py, although most of the application's core functions are found in views.py, as are the application's various routes. These core functions retrieve data from either the APIs 
or the SQLite database (data/dpd\_codes.db) in response to user queries and package it as JSON payloads, which are then used by either Jinja or Pyvis to present the information to the user via the application in a curated manner. Two further functions are 
found in db\_update.py. These comprehensively update the SQLite database from the APIs and provide a timestamp showing when the update occurred. db\_update.py cannot be triggered by the user; it has to be run from the 
command line by the application administrator. This is because it takes about 5 minutes for db\_update.py to update the database and there was no way of building that process into the application without
severely impacting user satisfaction. If DSCA is ever turned into a public application, the database will hopefully be kept updated regularly by the server on a separate thread. 

##### Warnings and Disclaimers
Large quantities of data can be returned by many queries and generating visualizations thereof can take some time. Demanding queries can sometimes be predicted (e.g. if the query results are 
going to include a commonly used ingredient or a major drug company) and sometimes not. The point of DSCA is to provide as much information as possible within the bounds of useability without 
making any assumptions about what is going to be relevant to any given situation, meaning that demanding payloads of data are unavoidable.

DSCA's query results are based on the data as received from the APIs and taken at face value. That is, no attempt has been made to interpret or link together entities beyond the network graphs 
themselves. For example, some large pharmaceutical ventures will consist of multiple companies that appear as separate in the data (e.g. "PFIZER CANADA ULC" v. "PFIZER CONSUMER HEALTHCARE A 
DIVISION OF PFIZER CANADA ULC"). In practice, they will likely coordinate their business activities, but they must be treated as separate companies for the purposes of querying the data. Active 
ingredients are not uniquely identified in the [Drug Product Database](https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/drug-product-database), meaning that 
they must be identified by the names provided. Some of these names seem to be referring to the same ingredient (e.g. "PENICILLIN G POTASSIUM" v. "PENICILLIN G (PENICILLIN G POTASSIUM)"), but, 
as this cannot be assumed programmtically across the data, they must necessarily be treated as separate for the purposes of queries.

Finally, to reiterate the disclaimer on the homepage, this web app is for academic research only and should not be used to make any sort of commercial or medical decision. Consult a medical 
professional on all matters relating to your own or someone else's medication.

##### Further Reading
In order to understand the data presented by DSCA, the information provided by [Drug Shortages Canada](https://www.drugshortagescanada.ca) and the 
[Drug Product Database](https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/drug-product-database) should be studied closely. Otherwise, data from 
[Drug Shortages Canada](https://www.drugshortagescanada.ca) has been used in a number of academic and journalistic investigations. These might provide a good introduction to the kind of 
issues that DSCA could be used to explore. For example:

- '[Role of Canadian pharmacists in managing drug shortage concerns amid the COVID-19 pandemic](https://doi.org/10.1177/1715163520929387)' (publ. 29/05/2020)
- '[One quarter of prescription drugs in Canada may be in short supply](https://www.sciencedaily.com/releases/2020/09/200901085306.htm)' (publ. 01/09/2020)
- '[Wasp Venom Can Save Lives. But the Supply Chain Is Shaky](https://undark.org/2020/11/16/wasp-venom-shaky-supply-chain/)' (publ. 11/16/2020)

Documentation for the key technologies used in DSCA:

- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [Pyvis](https://pyvis.readthedocs.io/en/latest/)
- [Select2](https://select2.org/)
- [SQLite](https://www.sqlite.org/index.html)

#### Get Started

To run DSC locally,

- Clone the repo to your machine
- Set up a Python Virtual environment: `python -m venv .venv`
- Install the required packages: `pip install -r requirements.txt`
- Run the app: `python runserver.py`