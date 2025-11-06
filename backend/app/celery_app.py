import os

from celery import Celery
from kombu import Exchange, Queue

from .tasks import cleanup_expired_reservations

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://rabbit:rabbit@rabbitmq:5672/')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

celery = Celery('gift_registry', broker=RABBITMQ_URL, backend=REDIS_URL)

celery.conf.update(
    accept_content=['json'],
    task_serializer='json',
    result_serializer='json',
    timezone='UTC',
    task_acks_late=True,
    worker_max_tasks_per_child=100,
)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # call cleanup every 60 seconds
    sender.add_periodic_task(60.0, cleanup_expired_reservations.s(), name="cleanup expired reservations every 60s")

celery.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default', durable=True),
)
