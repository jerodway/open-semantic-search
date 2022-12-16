import requests
import json
from unidecode import unidecode

host = "localhost"

host_string = f"http://{host}:8983/solr/opensemanticsearch/select?"

headers = {'Content-Type': "application/json"}

# https://yonik.com/json-facet-api/#JSON_Facet_Syntax
json_facet = "{author:{type:terms, field:author_ss, limit:1000000000}}"

query = f'http://{host}:8983/solr/opensemanticsearch/query?q=*:*&rows=0&wt=json&facet=true&json.facet={json_facet}&facet.limit=10000000'

fish = requests.request("GET", query)
response = json.loads(fish.content.decode())

auth_buckets = response['facets']['author']['buckets']

with open('authors.csv', 'w') as handle:
    for b in auth_buckets:
        name = b['val']
        count = b['count']

        handle.write(f'"{unidecode(name)}",{count}\n')

        print(f"{name}\t{count}")
