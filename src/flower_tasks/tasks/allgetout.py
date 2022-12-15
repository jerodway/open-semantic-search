import os
import time
from celery import Celery
from kombu import Queue, Exchange


from etl_delete import Delete

broker = 'amqp://localhost'
if os.getenv('OPEN_SEMANTIC_ETL_MQ_BROKER'):
    broker = os.getenv('OPEN_SEMANTIC_ETL_MQ_BROKER')

app = Celery('etl.tasks', broker=broker)

app.conf.task_queues = [Queue('open_semantic_etl_tasks', Exchange(
    'open_semantic_etl_tasks'), routing_key='open_semantic_etl_tasks', queue_arguments={'x-max-priority': 100})]

app.conf.worker_max_tasks_per_child = 1
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True


# Max parallel tasks (Default: Use as many parallel ETL tasks as CPUs available).
# Warning: Some tools called by ETL plugins use multithreading, too,
# so used CPUs/threads can be more than that setting!

if os.getenv('OPEN_SEMANTIC_ETL_CONCURRENCY'):
    app.conf.worker_concurrency = int(os.getenv('OPEN_SEMANTIC_ETL_CONCURRENCY'))

etl_delete = Delete()

if __name__ == "__main__":

    app.worker_main(['worker'])