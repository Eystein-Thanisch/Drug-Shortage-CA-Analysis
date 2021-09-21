import sqlite3

class my_class(object):
    con = sqlite3.connect("dpd_search_terms.db")
    con.execute("CREATE TABLE drug_names (drug_code NUMERIC, din VARCHAR(8), name TEXT, PRIMARY KEY (drug_code))")
    con.execute("CREATE TABLE manufacturer_names (company_id NUMERIC, name TEXT, PRIMARY KEY (company_id))")
    con.execute("CREATE TABLE ingredient_names (drug_code NUMERIC, name TEXT)")
    con.commit()
    con.close()
    pass


