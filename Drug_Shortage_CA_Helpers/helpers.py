import requests

auth_token = "02597e45864d4229bcb509e6db650f7a"

def get_company_data():
    url = "https://health-products.canada.ca/api/drug/company"
    response = requests.get(url)
    company_data = response.json()
    values = []
    codes = set()
    for datum in company_data:
        if datum["company_code"] not in codes:
            codes.add(datum["company_code"])
            details = (datum["company_code"], datum["company_name"], datum["country_name"])
            values.append(details)
    return values

def get_drug_data():
    url = "https://health-products.canada.ca/api/drug/drugproduct"
    response = requests.get(url)
    drug_data = response.json()
    values = []
    codes = set()
    for datum in drug_data:
        code = datum["drug_code"]
        if code not in codes:
            codes.add(code)
            owner = datum["company_name"]
            din = datum["drug_identification_number"]
            class_name = datum["class_name"]
            details = (code, datum["brand_name"], owner, din, class_name)
            values.append(details)
    return values

def get_drug_status():
    url = "https://health-products.canada.ca/api/drug/status"
    response = requests.get(url)
    status_data = response.json()
    values = []
    for datum in status_data:
        drug_code = datum["drug_code"]
        status = datum["status"]
        values.append((status, drug_code))
    return values

def get_drug_ingredients():
    url = "https://health-products.canada.ca/api/drug/activeingredient"
    response = requests.get(url)
    ing_data = response.json()
    values = []
    for datum in ing_data:
        name = datum["ingredient_name"]
        used_in = datum["drug_code"]
        details = (name, used_in)
        values.append(details)
    return values

def get_shortage_data(shortage_status: str):

    if shortage_status == "active":
        param = "filter_status=active_confirmed&"
    elif shortage_status == "anticipated":
        param = "filter_status=anticipated_shortage&"
    elif shortage_status == "discontinued":
        param = "filter_status=discontinued"
    else:
        param = ""

    base_url = f"https://www.drugshortagescanada.ca/api/v1/search?{param}limit=50"
    header = {"auth-token": auth_token}
    response = requests.get(base_url, headers=header)
    reports = response.json()
    if "error" in reports:
        raise Exception(reports["error"]["en"])
    p = reports["total_pages"]
    o = 0
    values = []
    for x in range(p):
        url = base_url + "&offset=" + str(o)
        o = o + 50
        response = requests.get(url, headers=header)
        reports = response.json()
        data = reports["data"]
        for report in data:
            report_id = report["id"]
            try:
                drug_code = report["drug"]["drug_code"]
            except:
                drug_code = report["drug"]["din"]
            din = report["drug"]["din"]
            try:
                company_code = report["drug"]["company"]["company_code"]
            except:
                company_code = "no_code"
            status = report["status"]
            reason = report.get("shortage_reason", report.get("discontinuance_reason", {})).get("en_reason", None)
            started = report.get("anticipated_start_date", report.get("discontinuation_date", report.get("anticipated_discontinuation_date", None)))
            details = (drug_code, company_code, reason, started, report_id, din, status)
            values.append(details)
    return values

def get_active_shortage_data():
    values = get_shortage_data(shortage_status="active")
    return [val[:-1] for val in values]

def get_anticipated_shortage_data():
    values = get_shortage_data(shortage_status="anticipated")
    return [val[:-1] for val in values]

def get_discontinuation_data():
    values = get_shortage_data(shortage_status="discontinued")
    return [val[:-1] for val in values]