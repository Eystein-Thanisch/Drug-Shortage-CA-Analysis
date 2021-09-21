import pip._vendor.requests
import json

class my_class(object):
    url = "https://www.drugshortagescanada.ca/api/v1/shortages/145824"
    request_headers = {"auth-token" : "02597e45864d4229bcb509e6db650f7a"}
    response = pip._vendor.requests.get(url, headers=request_headers)
    js = response.json()
    print(js)




