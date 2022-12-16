import requests
import json
import os
import re


def is_in_lists(listfiles, value, match=None):

    result = False

    for listfile in listfiles:

        try:
            if is_in_list(filename=listfile, value=value, match=match):
                result = True
                break

        except BaseException as e:
            print("Exception while checking blacklist {}:".format(listfile))
            print(e.args[0])

    return result


#
# is a value in a textfile with a list
#
def is_in_list(filename, value, match=None):

    result = False
    listfile = open(filename)

    # search all the lines
    for line in listfile:
        line = line.strip()

        # ignore empty lines and comment lines (starting with #)
        if line and not line.startswith("#"):

            if match == 'prefix':
                if value.startswith(line):
                    result = True
            elif match == 'suffix':
                if value.endswith(line):
                    result = True
            elif match == 'regex':
                if re.search(line, value):
                    result = True

            else:
                if line == value:
                    result = True

            if result:

                # we dont have to check rest of list
                break

    listfile.close()

    return result


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

        self.config['blacklist'] = [
            "/etc/opensemanticsearch/blacklist/blacklist-url"]
        self.config['blacklist_prefix'] = [
            "/etc/opensemanticsearch/blacklist/blacklist-url-prefix"]
        self.config['blacklist_suffix'] = [
            "/etc/opensemanticsearch/blacklist/blacklist-url-suffix"]
        self.config['blacklist_regex'] = [
            "/etc/opensemanticsearch/blacklist/blacklist-url-regex"]
        self.config['whitelist'] = [
            "/etc/opensemanticsearch/blacklist/whitelist-url"]
        self.config['whitelist_prefix'] = [
            "/etc/opensemanticsearch/blacklist/whitelist-url-prefix"]
        self.config['whitelist_suffix'] = [
            "/etc/opensemanticsearch/blacklist/whitelist-url-suffix"]
        self.config['whitelist_regex'] = [
            "/etc/opensemanticsearch/blacklist/whitelist-url-regex"]
        self.config['blackest_list_regex'] = [
            '/etc/opensemanticsearch/blacklist/the_blackest_of_lists-url-regex']


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


if __name__ == "__main__":

    remove_blacklisted = True
    remove_non_existing = True

    host = "solr"

    headers = {'Content-Type': "application/json"}

    host_string = f"http://{host}:8983/solr/opensemanticsearch/update?commit=true"

    query = f'http://{host}:8983/solr/opensemanticsearch/query?q=*:*&fl=id,&rows=100000000'

    fish = requests.request("GET", query)
    response = json.loads(fish.content.decode())
    documents = response['response']['docs']

    conf_getter = thingy()

    print(len(documents))
    for d in documents:
        try:
            doc_id = d['id']
            file_name = mapping_reverse(doc_id, mappings=conf_getter.config['mappings'])

            remove = False

            # check if this document would violate any of the black lists
            if remove_blacklisted:
                blacklisted = False
                c = conf_getter.config

                if 'blackest_list_regex' in conf_getter.config:
                    if is_in_lists(listfiles=c['blackest_list_regex'], value=doc_id, match="regex"):
                        blacklisted = True

                if 'blacklist_prefix' in c:

                    if is_in_lists(listfiles=c['blacklist_prefix'], value=doc_id, match="prefix"):
                        blacklisted = True

                if not blacklisted and 'blacklist_suffix' in c:

                    if is_in_lists(listfiles=c['blacklist_suffix'], value=doc_id, match="suffix"):
                        blacklisted = True

                if not blacklisted and 'blacklist_regex' in c:

                    if is_in_lists(listfiles=c['blacklist_regex'], value=doc_id, match="regex"):
                        blacklisted = True

                if not blacklisted and 'blacklist' in c:

                    if is_in_lists(listfiles=c['blacklist'], value=doc_id):
                        blacklisted = True

                # check whitelists for URI, if blacklisted

                if blacklisted and 'whitelist_prefix' in c:
                    if is_in_lists(listfiles=c['whitelist_prefix'], value=doc_id, match="prefix"):
                        blacklisted = False

                if blacklisted and 'whitelist_suffix' in c:
                    if is_in_lists(listfiles=c['whitelist_suffix'], value=doc_id, match="suffix"):
                        blacklisted = False

                if blacklisted and 'whitelist_regex' in c:
                    if is_in_lists(listfiles=c['whitelist_regex'], value=doc_id, match="regex"):
                        blacklisted = False

                if blacklisted and 'whitelist' in c:
                    if is_in_lists(listfiles=c['whitelist'], value=doc_id):
                        blacklisted = False

                if blacklisted:
                    remove = True

            # check if the file still exists
            if remove_non_existing:
                if not os.path.exists(file_name):
                    remove = True

            # remove the doc
            if remove:
                print(f"removing {doc_id}")
                string_to_send = '{{"delete":{{"id":"{}"}}}}'.format(doc_id)
                print(string_to_send)
                resp = requests.request("POST", url=host_string, headers=headers, data=string_to_send.encode())

                print(resp.content)

        except Exception as e:
            print(e)
