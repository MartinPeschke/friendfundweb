"""Pylons environment configuration"""
import os, logging

from mako.lookup import TemplateLookup
from pylons.configuration import PylonsConfig
from pylons.error import handle_mako_error

import friendfund.lib.app_globals as app_globals
import friendfund.lib.helpers
from friendfund.config.routing import make_map

log = logging.getLogger(__name__)

def load_environment(global_conf, app_conf):
	"""Configure the Pylons environment via the ``pylons.config``
	object
	"""
	config = PylonsConfig()

	# Pylons paths
	root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	paths = dict(root=root,
				 controllers=os.path.join(root, 'controllers'),
				 static_files=os.path.join(root, 'public'),
				 templates			=[os.path.join(root, path) for path in global_conf['templates'].split(';')],
				 merchant_templates	=[os.path.join(root, path) for path in global_conf['merchant_templates'].split(';')],
				 freeform_templates	=[os.path.join(root, path) for path in global_conf['freeform_templates'].split(';')],
				 uploads=os.path.join(app_conf['cache_dir'], 'uploads'))
	log.info("loaded templates from, %s", str([os.path.join(root, path) for path in global_conf['templates'].split(';')]))
	# Initialize config with the basic options
	config.init_app(global_conf, app_conf, package='friendfund', paths=paths)

	config['routes.map'] = make_map(config)
	config['pylons.app_globals'] = app_globals.Globals(config)
	config['pylons.h'] = friendfund.lib.helpers

	# Setup cache object as early as possible
	import pylons
	pylons.cache._push_object(config['pylons.app_globals'].cache)

	# Create the Mako TemplateLookup, with the default auto-escaping
	config['pylons.app_globals'].mako_lookup = TemplateLookup(
		directories=paths['templates'],
		filesystem_checks=config['debug'],
		error_handler=handle_mako_error,
		module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
		input_encoding='utf-8', default_filters=['escape'],
		imports=['from webhelpers.html import escape','from xml.sax.saxutils import quoteattr'])
	# Create the Mako TemplateLookup, with the default auto-escaping
	config['pylons.app_globals'].merchant_mako_lookup = TemplateLookup(
		directories=paths['merchant_templates'],
		filesystem_checks=config['debug'],
		error_handler=handle_mako_error,
		module_directory=os.path.join(app_conf['cache_dir'], 'merchant_templates'),
		input_encoding='utf-8', default_filters=['escape'],
		imports=['from webhelpers.html import escape','from xml.sax.saxutils import quoteattr'])
	# Create the Mako TemplateLookup, with the default auto-escaping
	config['pylons.app_globals'].freeform_mako_lookup = TemplateLookup(
		directories=paths['freeform_templates'],
		filesystem_checks=config['debug'],
		error_handler=handle_mako_error,
		module_directory=os.path.join(app_conf['cache_dir'], 'freeform_templates'),
		input_encoding='utf-8', default_filters=['escape'],
		imports=['from webhelpers.html import escape','from xml.sax.saxutils import quoteattr'])

	# CONFIGURATION OPTIONS HERE (note: all config options will override
	# any Pylons config options)

	return config
