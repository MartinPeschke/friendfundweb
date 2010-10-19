"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

CONNECT_METHODS = 'twitter|facebook|email|yourself'

def make_map(config):
	"""Create, configure and return the routes Mapper"""
	map = Mapper(directory=config['pylons.paths']['controllers'],
				 always_scan=config['debug'])
	map.minimization = False

	# The ErrorController route (handles 404/500 error pages); it should
	# likely stay at the top, ensuring it can always be resolved
	map.connect('/error/{action}', controller='error')
	map.connect('/error/{action}/{id}', controller='error')

	# CUSTOM ROUTES HERE
	map.connect('/pool/start', controller='pool', action='reset')
	map.connect('/pool/create', controller='pool', action='create')
	map.connect('get_pool', '/pool/{pool_url}', controller='pool', action='index', requirements={'pool_url': '[0-9a-zA-Z.~_-]+'})
	map.connect('chipin', '/pool/{pool_url}/chipin', controller='contribution', action="chipin", requirements={'pool_url': '[0-9a-zA-Z.~_-]+'})
	map.connect('chipin_fixed', '/pool/{pool_url}/chipin_fixed', controller='contribution', action="chipin_fixed", requirements={'pool_url': '[0-9a-zA-Z.~_-]+'})
	map.connect('pool_action', '/pool/{pool_url}/{action}', controller='pool', requirements={'pool_url': '[0-9a-zA-Z.~_-]+'})
	
	map.connect('/invite/friends', controller='invite', action='friends')
	
	map.connect('invite', '/invite/{pool_url}/{method}', controller='invite', action='method', requirements={'pool_url': '[0-9a-zA-Z.~_-]+', 'method':CONNECT_METHODS})
	map.connect('invite_index', '/invite/{pool_url}', controller='invite', action='display', requirements={'pool_url': '[0-9a-zA-Z.~_-]+'})
	map.connect('invite_action', '/invite/{pool_url}/{action}', controller='invite', requirements={'pool_url': '[0-9a-zA-Z.~_-]+'})
	map.connect('/receiver/{method}', controller='receiver', action='method', requirements={'method':CONNECT_METHODS})
	map.connect('/mybadges/panel/{badge_name}', controller="mybadges", action="panel")
	map.connect('/myprofile/{action}/{token}', controller="myprofile")
	map.connect('/{controller}/{pool_url}/{action}', controller='pool', requirements={'pool_url': '[0-9a-zA-Z.~_-]+'})
	map.connect('/{controller}/{action}')
	map.connect('/{controller}/{action}/{id}')
	
	map.connect('ctrlpoolindex', '/{controller}/{pool_url}', action='index')
	map.connect('controller', '/{controller}', action='index')
	map.connect('index', '/{action}', controller='index')
	map.connect('home', '/', controller='index', action='index')
	return map
