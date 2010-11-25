"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
#from routes import Mapper
from friendfund.lib.routes_middleware import VersionedMapper as Mapper

CONNECT_METHODS = 'twitter|facebook|email|yourself'
purlpattern = '[.0-9a-zA-Z~_-]+'
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
	
	map.connect('get_pool', '/pool/{pool_url}', controller='pool', action='index', requirements={'pool_url': purlpattern})
	map.connect('pool_action', '/pool/{pool_url}/{action}', controller='pool', requirements={'pool_url': purlpattern})
	map.connect('chipin', '/chipin/{pool_url}', controller='contribution', action="chipin", requirements={'pool_url': purlpattern})
	map.connect('chipin_fixed', '/chipin/{pool_url}/fixed', controller='contribution', action="chipin_fixed", requirements={'pool_url': purlpattern})
	map.connect('contribution', '/chipin/{pool_url}/{action}', controller='contribution', requirements={'pool_url': purlpattern})
	
	map.connect('/invite/friends', controller='invite', action='friends')
	
	map.connect('invite', '/invite/{pool_url}/{method}', controller='invite', action='method', requirements={'pool_url': purlpattern, 'method':CONNECT_METHODS})
	map.connect('invite', '/invite/{pool_url}/ext_{method}', controller='invite', action='get_extension', requirements={'pool_url': purlpattern, 'method':CONNECT_METHODS})
	map.connect('/myfriends/{method}', controller='myfriends', action='method', requirements={'method':CONNECT_METHODS})
	map.connect('/myfriends/ext_{method}', controller='myfriends', action='get_extension', requirements={'method':CONNECT_METHODS})
	map.connect('getfriends', '/myfriends/get/{pmethod}', controller='myfriends', action='get', requirements={'method':CONNECT_METHODS})
	map.connect('invite_index', '/invite/{pool_url}', controller='invite', action='display', requirements={'pool_url': purlpattern})
	map.connect('invite_action', '/invite/{pool_url}/{action}', controller='invite', requirements={'pool_url': purlpattern})

	map.connect('mybadges', '/mybadges/panel/{badge_name}', controller="mybadges", action="panel")
	map.connect('/myprofile/{action}/{token}', controller="myprofile")
	map.connect('/{controller}/{pool_url}/{action}', controller='pool', requirements={'pool_url': purlpattern})
	map.connect('/{controller}/{action}')
	map.connect('/{controller}/{action}/{id}')
	
	map.connect('ctrlpoolindex', '/{controller}/{pool_url}', action='index')
	map.connect('controller', '/{controller}', action='index')
	map.connect('index', '/{action}', controller='index')
	map.connect('home', '/', controller='index', action='index')
	return map
