import sqlite3

class my_class(object):
    con = sqlite3.connect("search_terms.db")
    con.execute("CREATE TABLE drug_names (din NUMERIC, name TEXT, PRIMARY KEY (din))")
    con.execute("CREATE TABLE manufacturer_names (company_id NUMERIC, name TEXT, PRIMARY KEY (company_id))")
    con.execute("CREATE TABLE ingredient_names (atc_id NUMERIC, name TEXT, PRIMARY KEY (atc_id))")
    con.commit()
    con.close()
    pass




