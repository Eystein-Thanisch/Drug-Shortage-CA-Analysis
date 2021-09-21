import pip._vendor.requests
import json

class my_class(object):
    url = "https://health-products.canada.ca/api/drug/drugproduct"
    #request_headers = {"auth-token" : "02597e45864d4229bcb509e6db650f7a"}
    response = pip._vendor.requests.get(url)
    js = response.json()
    for x in range(len(js)):
        c = js[x]["drug_code"]
        print(c)
        print(type(c))
    pass




