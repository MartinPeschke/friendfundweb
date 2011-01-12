print "IMPORTING GADTEST"
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_USER = "rabbitmquser"
BROKER_PASSWORD = "rabbitmqpassword"
BROKER_VHOST = "rabbitmqvhost"
CELERY_RESULT_BACKEND = "amqp"
CELERY_IMPORTS = ("friendfund.tasks.fb", 
					"friendfund.tasks.twitter",
					"friendfund.tasks.photo_renderer",
					"friendfund.tasks.ecard_renderer")
 
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
CELERY_ADDITIONAL_CONFIG="development.ini"



# If you're doing mostly I/O you can have more processes,
# but if mostly spending CPU, try to keep it close to the
# number of CPUs on your machine. If not set, the number of CPUs/cores
# available will be used.
CELERYD_CONCURRENCY = 4

CELERYD_LOG_FILE = "logs/celeryd_dev_gad.log"
CELERYD_LOG_LEVEL = "DEBUG"
