import requests
import json
from celery import Celery
from kombu import Queue, Exchange

host = "solr"

host_string = f"http://{host}:8983/solr/opensemanticsearch/update?commit=true"

headers = {'Content-Type': "application/json"}

broker = f'amqp://guest:guest@{host}:5672'

app = Celery('etl.tasks', broker=broker)
app.conf.task_queues = [Queue('open_semantic_etl_tasks', Exchange(
    'open_semantic_etl_tasks'), routing_key='open_semantic_etl_tasks', queue_arguments={'x-max-priority': 100})]


with open(r"open-semantic-search\src\open-semantic-etl\etc\opensemanticsearch\blacklist\tikaextraction\blacklist-fieldname", 'r') as h:
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

            r = app.send_task('etl.post_solr', kwargs={'string_to_send': string_to_send}, queue="open_semantic_etl_tasks", routing_key="open_semantic_etl_tasks" )

