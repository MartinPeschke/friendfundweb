import pyodbc, os, ConfigParser, celery, pylibmc

from DBUtils.PersistentDB import PersistentDB
from celeryconfig import CELERY_ADDITIONAL_CONFIG
from celery.log import setup_logger
from mako.lookup import TemplateLookup

from friendfund.model import common

IMAGEMAGICKROOT ='/usr/local/bin'
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_root = os.path.join(os.getcwd(), 'data')
log = setup_logger(loglevel=0)

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def getRecAttr(obj, attr):
    tmp = obj
    for a in attr.split('.'):
        tmp = getattr(tmp, a)
    return callable(tmp) and tmp() or tmp

def getRecDictKey(d, k):
	tmp = d
	for a in k.split('.'):
		try:
			tmp = tmp.get(a, None)
		except AttributeError, e:
			return None
		if not tmp: break
	return tmp


def get_config(configname):
	_config = ConfigParser.ConfigParser({'here':os.getcwd()})
	_config.read(configname)
	_config = dict(_config.items('app:main'))
	return _config


def get_db_pool(app_conf, conn_name):
	return PersistentDB(
				pyodbc
				,driver=app_conf['%s.connectstring.driver' % conn_name]
				,server=app_conf['%s.connectstring.server' % conn_name]
				,instance=app_conf['%s.connectstring.instance' % conn_name]
				,database=app_conf['%s.connectstring.database' % conn_name]
				,port=app_conf['%s.connectstring.port' % conn_name]
				,tds_version=app_conf['%s.connectstring.tds_version' % conn_name]
				,uid=app_conf['%s.connectstring.uid' % conn_name]
				,pwd=app_conf['%s.connectstring.pwd' % conn_name]
				,client_charset=app_conf['%s.connectstring.client_charset' % conn_name]
				,autocommit=True
			)


_dbmanagers = {}
_caches = {}
config = get_config(CELERY_ADDITIONAL_CONFIG)

def _create_cm(connection_name):
	cache = pylibmc.Client(config['memcached.cache.url'].split(';'), binary=True)
	cache.behaviors = {"tcp_nodelay": True, "ketama": True}
	cache_pool = pylibmc.ThreadMappedPool(cache)
	return cache_pool
def get_cm(connection_name):
	return _caches.setdefault(connection_name, _create_cm(connection_name))

def _create_dbm(connection_name):
	dbpool = get_db_pool(config, connection_name)
	cm = get_cm(connection_name)
	return common.DBManager(dbpool, cm, log)

def get_dbm(connection_name):
	dbm = _dbmanagers.get(connection_name, None)
	if not dbm:
		_dbmanagers[connection_name] = _create_dbm(connection_name)
	return _dbmanagers[connection_name]

upload_tmp = os.path.join(data_root, 'tmp')
upload_uimg_folder = os.path.join(data_root, 's', 'user')
upload_pimg_folder = os.path.join(data_root, 's', 'pool')
upload_prodimg_folder = os.path.join(data_root, 's', 'product')
if not os.path.exists(upload_tmp):
	os.makedirs(upload_tmp)