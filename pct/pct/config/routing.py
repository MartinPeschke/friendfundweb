"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    map.redirect('/', '/index/index/de/all/1')
    map.connect('controller_paged','/{controller}/{action}/{region}/{program}/{page}', requirements = {'region':'de|gb|us', 'page':'[0-9]+'})
    map.connect('controller_program','/{controller}/{action}/{region}/{program}', requirements = {'region':'de|gb|us'})
    map.connect('controller_region','/{controller}/{action}/{region}/', requirements = {'region':'de|gb|us'})
    map.connect('controller','/{controller}/{action}/{region}', requirements = {'region':'de|gb|us'})
    map.connect('home', '/', controller="index", action="index", region='de')

    return map
