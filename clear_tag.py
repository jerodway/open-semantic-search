import requests
import json

host = "localhost"

host_string = f"http://{host}:8983/solr/opensemanticsearch/update?commit=true"

headers = {'Content-Type': "application/json"}

list_of_tags_to_remove = ["FRANK",
                           "JOE",
                           ]

for tag_to_remove in list_of_tags_to_remove:
    query = f'http://{host}:8983/solr/opensemanticsearch/query?q=tag_ss:"{tag_to_remove}"&fl=id,tag_ss&rows=100000000'

    fish = requests.request("GET", query)
    response = json.loads(fish.content.decode())

    documents = response['response']['docs']

    for doc in documents:
        id_name = doc['id']
        id_name = id_name.replace(':', '\:')

        tags = doc['tag_ss']
        tags.remove(tag_to_remove)
        str_tags = [f'"{x}"' for x in tags]
        str_tags = ", ".join(str_tags)

        string_to_send = '[{{"id":"{}","tag_ss":{{"set":[{}]}}}}]'.format(id_name, str_tags)

        resp = requests.request("POST", url=host_string, headers=headers, data=string_to_send.encode())
        if not resp:
            print(f"problem removing {tag_to_remove} from {id_name}")
