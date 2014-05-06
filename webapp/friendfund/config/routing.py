"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
#from routes import Mapper
from friendfund.lib.routes_middleware import VersionedMapper as Mapper
from babel import parse_locale

CONNECT_METHODS = 'twitter|facebook|email|yourself'
purlpattern = '[.0-9a-zA-Z~_-]+'
languagespattern = "[a-zA-Z]{2}[_-][a-zA-Z]{2}"


def language_acceptor(environ, result):
    try:
        parse_locale(result.get("lang"))
        return True
    except:
        return False


def make_map(config):
    """Create, configure and return the routes Mapper"""
    route_map = Mapper(directory=config['pylons.paths']['controllers'], always_scan=config['debug'])
    route_map.minimization = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    route_map.connect('/error/{action}', controller='error')
    route_map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    route_map.connect('clean_session', '/pool/start', controller='pool', action='reset')
    route_map.connect('pool_create', '/pool/create', controller='pool', action='create')
    route_map.connect('pool_details', '/pool/details', controller='pool', action='details')
    route_map.connect('contribution_service', '/contribution/service', controller='payment_service', action='service')
    route_map.connect('get_pool', '/pool/{pool_url}', controller='pool', action='index',
                      requirements={'pool_url': purlpattern})
    route_map.connect('pool_action', '/pool/{pool_url}/{action}', controller='pool',
                      requirements={'pool_url': purlpattern})
    route_map.connect('pool_edit', '/pedit/{pool_url}/{action}', controller='pool_edit',
                      requirements={'pool_url': purlpattern})
    route_map.connect('pool_edit_index', '/pedit/{pool_url}', controller='pool_edit', action="index",
                      requirements={'pool_url': purlpattern})

    route_map.connect('settlement_fees', '/payment/settlement_fees', controller='payment', action="settlement_fees")
    route_map.connect('payment', '/payment/{pool_url}', controller='payment', action="index",
                      requirements={'pool_url': purlpattern})
    route_map.connect('payment_current', '/payment/{pool_url}/ret', controller='payment', action="ret",
                      requirements={'pool_url': purlpattern})
    route_map.redirect('/chipin/{pool_url:.*}', '/pool/{pool_url}', _redirect_code='301 Moved Permanently')
    route_map.connect('search_tab_extension', '/product/search_tab_extension', controller='product_query',
                      action="search_tab_extension")

    route_map.connect('/invite/friends', controller='invite', action='friends')
    route_map.connect('invite', '/invite/{pool_url}/{method}', controller='invite', action='method',
                      requirements={'pool_url': purlpattern, 'method': CONNECT_METHODS})
    route_map.connect('invite_ext', '/invite/{pool_url}/ext_{method}', controller='invite', action='get_extension',
                      requirements={'pool_url': purlpattern, 'method': CONNECT_METHODS})
    route_map.connect('invite_index', '/invite/{pool_url}', controller='invite', action='display',
                      requirements={'pool_url': purlpattern})
    route_map.connect('invite_action', '/invite/{pool_url}/{action}', controller='invite',
                      requirements={'pool_url': purlpattern})

    route_map.connect('/myfriends/{method}', controller='myfriends', action='method',
                      requirements={'method': CONNECT_METHODS})
    route_map.connect('/myfriends/ext_{method}', controller='myfriends', action='get_extension',
                      requirements={'method': CONNECT_METHODS})
    route_map.connect('getfriends', '/myfriends/get/{pmethod}', controller='myfriends', action='get',
                      requirements={'method': CONNECT_METHODS})

    route_map.connect('/myprofile/{action}/{token}', controller="myprofile")
    route_map.connect('/user/{action}/{token}', controller="myprofile")
    route_map.connect('/{controller}/{pool_url}/{action}', controller='pool', requirements={'pool_url': purlpattern})
    route_map.connect('/{controller}/{action}')
    route_map.connect('/{controller}/{action}/{id}')

    route_map.connect('edit', '/edit/{action}', controller='data_editor')
    route_map.connect('sitemap', '/sitemap.xml', controller='index', action="sitemap")

    route_map.connect('ctrlpoolindex', '/{controller}/{pool_url}', action='index')
    route_map.connect('controller', '/{controller}', action='index')
    route_map.connect('signup', '/login', controller='index', action="signup")
    route_map.connect('index', '/{action}', controller='index')
    route_map.connect('home', '/', controller='index', action='index')

    route_map.redirect('/{lang}/tips', '/{lang}/learn_more', _redirect_code='301 Moved Permanently',
                       conditions={'function': language_acceptor})
    route_map.connect('short_content', '/{lang}/{action}', controller='content',
                      conditions={'function': language_acceptor})
    route_map.redirect('/{lang}/content/{action}', '/{lang}/{action}', _redirect_code='301 Moved Permanently',
                       conditions={'function': language_acceptor})

    return route_map
