def get_graph(id):
    # Get Report Data
    base_url = "https://www.drugshortagescanada.ca/api/v1/shortages/"
    url = base_url + str(id)
    header = {"auth-token" : auth_token}
    response = requests.get(url, headers = header)
    report = response.json()
    drug_name = report["drug"]["brand_name"]
    drug = report["drug"]["drug_code"]
    company_name = report["drug"]["company"]["name"]
    company = report["drug"]["company"]["company_code"]
    ingredients = []
    l = len(report["drug"]["drug_ingredients"])
    for x in range(l):
        name = report["drug"]["drug_ingredients"][x]["ingredient"]["en_name"]
        ingredients.append(name)

    # Build Initial Network
    net = Network()
    net.add_node(drug, label = drug_name)
    net.add_node(company, label = company_name)
    l = len(ingredients)
    for x in range(l):
        net.add_node(ingredients[x], label = ingredients[x])
    net.add_edge(company, drug)
    for x in range(l):
        net.add_edge(drug, ingredients[x])
    net.show('mygraph.html')
    return
    
    # Ingredient Links
    drugs = []
    for x in range(l):
        base_url = "https://health-products.canada.ca/api/drug/activeingredient"
        url = base_url + "/?ingredientname=" + ingredients[x]
        response = requests.get(url)
        js = response.json()
        hits = len(js)
        for y in range(hits):
            drugs.append(hits[y]["drug_code"])
    for drug in drugs:
        base_url = "https://health-products.canada.ca/api/drug/drugproduct"
        url = base_url + "/drugproduct/?id=" + drug
        response = requests.get(url)
        js = response.json()
        name = js["brand_name"]
        company = js["company_name"]
        net.add_node(drug, label = name)
