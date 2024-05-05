import requests

def get_company_data():
    url = "https://health-products.canada.ca/api/drug/company"
    response = requests.get(url)
    company_data = response.json()
    values = []
    codes = set()
    for datum in company_data:
        if datum["company_code"] not in codes:
            codes.add(datum["company_code"])
            details = (datum["company_code"], datum["company_name"])
            values.append(details)
    return values