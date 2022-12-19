import requests
import json
import os
from subprocess import run


class thingy:
    def __init__(self):
        self.config = {}
        self.config['plugins'] = []
        # Windows style filenames
        self.read_configfile('conf\\opensemanticsearch-etl')
        self.read_configfile('conf\\opensemanticsearch-enhancer-rdf')
        self.read_configfile('conf\\opensemanticsearch-connector-files')

        # Linux style filenames
        self.read_configfile('/etc/etl/config')
        self.read_configfile('/etc/opensemanticsearch/etl')
        self.read_configfile('/etc/opensemanticsearch/etl-webadmin')
        self.read_configfile('/etc/opensemanticsearch/etl-custom')
        self.read_configfile('/etc/opensemanticsearch/enhancer-rdf')
        self.read_configfile('/etc/opensemanticsearch/facets')
        self.read_configfile('/etc/opensemanticsearch/connector-files')
        self.read_configfile('/etc/opensemanticsearch/connector-files-custom')

    def read_configfile(self, configfile):
        result = False

        if os.path.isfile(configfile):
            config = self.config
            file = open(configfile, "r")
            exec(file.read(), locals())
            file.close()
            self.config = config

            result = True


def mapping_reverse(value, mappings=None):
    if mappings is None:
        mappings = {}

    max_match_len = -1

    # check all mappings for matching and use the best
    for map_from, map_to in mappings.items():

        # map from matching value?
        if value.startswith(map_to):

            # if from string longer (deeper path), this is the better matching
            match_len = len(map_to)

            if match_len > max_match_len:
                max_match_len = match_len
                best_match_map_from = map_from
                best_match_map_to = map_to

    # if there is a match, replace first occurance of value with reverse mapping
    if max_match_len >= 0:
        value = value.replace(best_match_map_to, best_match_map_from, 1)

    return value


host = "solr"

host_string = f"http://{host}:8983/solr/opensemanticsearch/select?"

query = f'http://{host}:8983/solr/opensemanticsearch/query?q=-orig_filepath_s:*&fl=id,&rows=100000000'

fish = requests.request("GET", query)
response = json.loads(fish.content.decode())
documents = response['response']['docs']

conf_getter = thingy()

print(len(documents))
for d in documents:
    try:
        doc_id = d['id']
        file_name = mapping_reverse(doc_id, mappings=conf_getter.config['mappings'])
        cmd = [f"python3", f"/usr/lib/python3/dist-packages/opensemanticetl/etl_file.py", "--force", file_name]
        run(cmd)
    except Exception as e:
        raise e
