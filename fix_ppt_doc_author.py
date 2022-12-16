import requests
import json
from unidecode import unidecode

host = "localhost"

host_string = f"http://{host}:8983/solr/opensemanticsearch/update?commit=true"

headers = {'Content-Type': "application/json"}

list_of_file_extensions = ["pptx",
                           "ppt",
                           "docx",
                           "doc"
                           ]

for extension in list_of_file_extensions:
    query = f'http://{host}:8983/solr/opensemanticsearch/query?q=filename_extension_s:"{extension}"&sort=file_modified_dt desc&fl=id,author_ss,meta_last-author_ss&rows=100000000'

    fish = requests.request("GET", query)
    response = json.loads(fish.content.decode())

    documents = response['response']['docs']

    for doc in documents:
        id_name = doc['id']
        id_name = id_name.replace(':', '\:')

        old_author = doc.get("author_ss", None)
        new_author = doc.get('meta_last-author_ss', None)

        if new_author is not None:
            str_na = [f'"{unidecode(x)}"' for x in new_author]
            str_na = ", ".join(str_na)
            str_na.replace("'", r"\'")

            string_to_send = '[{{"id":"{}","author_ss":{{"set":[{}]}}}}]'.format(id_name, str_na)

            resp = requests.request("POST", url=host_string, headers=headers, data=string_to_send.encode())
            if not resp:
                print(f"problem changing {old_author} to {new_author} in {id_name}")

