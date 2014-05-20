BROKER_URL = "amqp://rabbitmquser:rabbitmqpassword@127.0.0.1:5672/rabbitmqvhost"
CELERY_RESULT_BACKEND = "amqp"

CELERYD_SOFT_TASK_TIME_LIMIT=480
CELERYD_TASK_TIME_LIMIT=490

CELERY_STORE_ERRORS_EVEN_IF_IGNORED = False
CELERY_IGNORE_RESULT = True
CELERY_DISABLE_RATE_LIMITS = True

CELERY_QUEUES = {"default_dev": {"exchange": "celeryevent_dev",
                                 "binding_key": "celeryevent_dev_dev",
                                 "routing_key": "celeryevent_dev_dev"}}

CELERY_DEFAULT_QUEUE = "default_dev"

CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DEFAULT_EXCHANGE = "celeryevent_dev"
CELERY_DEFAULT_ROUTING_KEY = "celeryevent_dev_dev"

CELERY_EVENT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

CELERY_ADDITIONAL_CONFIG="code/config.ini"


# If you're doing mostly I/O you can have more processes,
# but if mostly spending CPU, try to keep it close to the
# number of CPUs on your machine. If not set, the number of CPUs/cores
# available will be used.
CELERYD_CONCURRENCY = 2



# sudo rabbitmqctl add_user rabbitmquser rabbitmqpassword
# sudo rabbitmqctl add_vhost rabbitmqvhost
# sudo rabbitmqctl set_permissions -p rabbitmqvhost rabbitmquser ".*" ".*" ".*"