import requests
import json

host = "localhost"

host_string = f"http://{host}:8983/solr/opensemanticsearch/update?commit=true"
body_string = '[{"id":"{}","currency_ss":{"set":[]},"currency_ss_uri_ss":{"set":[]},"currency_ss_preflabel_and_uri_ss":{"set":[]},"currency_ss_taxonomy0_ss":{"set":[]},"money_ss":{"set":[]}}]'

headers = {'Content-Type': "application/json"}

list_of_file_extensions = ["pptx",
                           "ppt",
                           ]

for extension in list_of_file_extensions:
    query = f'http://{host}:8983/solr/opensemanticsearch/query?q=filename_extension_s:"{extension}"&fl=id,author_ss,&rows=100000000'

    fish = requests.request("GET", query)
    response = json.loads(fish.content.decode())

    documents = response['response']['docs']

    for doc in documents:
        id_name = doc['id']
        id_name = id_name.replace(':', '\:')

        new_title = doc["path_basename_s"]

        string_to_send = '[{{"id":"{}","title_txt":{{"set":"{}"}}}}]'.format(id_name, new_title)

        resp = requests.request("POST", url=host_string, headers=headers, data=string_to_send.encode())
        if not resp:
            print(f"problem putting {new_title} in for from {id_name}")
