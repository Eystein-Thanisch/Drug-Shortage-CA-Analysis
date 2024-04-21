import sqlite3


class my_class(object):
    con = sqlite3.connect("dpd_search_terms.db")
    con.execute(
        "CREATE TABLE drug_names (id INTEGER, drug_code INTEGER, din VARCHAR(8), name TEXT, updated DATE)"
    )
    # con.execute("CREATE TABLE manufacturer_names (company_id NUMERIC, name TEXT, updated DATE, PRIMARY KEY (company_id))")
    # con.execute("CREATE TABLE ingredient_names (drug_code NUMERIC, name TEXT, updated DATE)")
    con.commit()
    con.close()
    pass
