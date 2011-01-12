BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_USER = "rmquser_live"
BROKER_PASSWORD = "rmqpw_liveHGasegoiAuhqfReo96r"
BROKER_VHOST = "rmqvhost_live_gad"
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

CELERY_EVENT_EXCHANGE_TYPE = "direct"
CELERY_EVENT_EXCHANGE = "celeryevent_gad_live"
CELERY_EVENT_ROUTING_KEY = "celeryevent_gad_live"

CELERY_QUEUES = {"default_queue": {"exchange": "celeryevent_gad_live",
				"exchange_type": "direct",
				"routing_key": "*"}}
CELERY_DEFAULT_QUEUE = "default_queue"


CELERY_EVENT_SERIALIZER = "json"

CELERY_ADDITIONAL_CONFIG="/opt/www/ff_gad_live/ariel_1_gad.ini"


# If you're doing mostly I/O you can have more processes,
# but if mostly spending CPU, try to keep it close to the
# number of CPUs on your machine. If not set, the number of CPUs/cores
# available will be used.
CELERYD_CONCURRENCY = 4

CELERYD_LOG_FILE = "logs/celeryd_gad_live.log"
CELERYD_LOG_LEVEL = "INFO"
