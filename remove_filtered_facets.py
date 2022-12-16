import requests
import json
import time

host = "solr"

host_string = f"http://{host}:8983/solr/opensemanticsearch/update?commit=true"

headers = {'Content-Type': "application/json"}

list_of_facets_to_clear = ["currency_ss",
                           "currency_ss_uri_ss",
                           "currency_ss_preflabel_and_uri_ss",
                           "currency_ss_taxonomy0_ss",
                           "money_ss",
                           "hashtag_ss",
                           "law_code_ss",
                           "law_code_ss_uri_ss",
                           "law_code_ss_preflabel_and_uri_ss",
                           "law_code_ss_taxonomy0_ss",
                           ]

with open("/etc/opensemanticsearch/blacklist/tikaextraction/blacklist-fieldname", 'r') as h:
    list_of_facets_to_clear = h.readlines()

list_of_facets_to_clear = [x.strip() for x in list_of_facets_to_clear]
list_of_facets_to_clear = [x.replace(":", '_') for x in list_of_facets_to_clear]
list_of_facets_to_clear = [x.replace(" ", "_") + "_ss" for x in list_of_facets_to_clear]

print("going to try to remove: ")
for x in list_of_facets_to_clear:
    print(f"\t{x}")

for facet_to_clear in list_of_facets_to_clear:
    print(f"working on {facet_to_clear}")

    query = f"http://{host}:8983/solr/opensemanticsearch/query?q={facet_to_clear}:[*%20TO%20*]&fl=id&rows=100000000"

    fish = requests.request("GET", query)
    response = json.loads(fish.content.decode())

    if response:
        documents = response['response']['docs']
        print(f"{len(documents)} to process")
        for doc in documents:
            id_name = doc['id']
            id_name = id_name.replace(':', '\:')

            string_to_send = '[{{"id":"{}","{}":{{"set":[]}}}}]'.format(id_name, facet_to_clear)

            resp = requests.request("POST", url=host_string, headers=headers, data=string_to_send.encode())
            if not resp:
                print(f"problem removing {facet_to_clear} from {id_name}")
            time.sleep(0.25)
