import requests

host = "localhost"

host_string = f"http://{host}:8983/solr/opensemanticsearch/select?"

headers = {'Content-Type': "application/json"}

query = fr'http://{host}:8983/solr/opensemanticsearch/select?q=*:*&wt=csv&rows=0&facet'

fish = requests.request("GET", query)
all_fields_str = fish.text
all_fields = all_fields_str.split(',')

with open('field_list.txt', 'w') as handle:
    for f in all_fields:
        handle.write(f'{f}\n')
