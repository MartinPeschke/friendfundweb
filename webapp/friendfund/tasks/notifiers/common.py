import mako, os
from mako.lookup import TemplateLookup
from friendfund.tasks import data_root

class InvalidAccessTokenException(Exception):
	pass
class MissingTemplateException(Exception):
	pass

	
	
def get_parent(folder, levels):
	if levels == 0: return os.path.abspath(folder)
	else: return get_parent(os.path.dirname(folder), levels-1)
	
root = get_parent(__file__, 3)
tmpl_lookup = TemplateLookup(directories=[os.path.join(root, 'templates','messaging')]
		, module_directory=os.path.join(data_root, 'templates','messaging')
		, output_encoding='utf-8'
		, input_encoding='utf-8'
		)


def get_template(locale, file_no, log):
	try:
		return tmpl_lookup.get_template('/messages_%s/msg_%s.txt' % (locale, file_no))
	except mako.exceptions.TopLevelLookupException, e:
		log.warning( "WARNING Template not Found for (/messages_%s/msg_%s.txt)" , locale, file_no )
		try:
			return tmpl_lookup.get_template('/messages/msg_%s.txt' % (file_no))
		except mako.exceptions.TopLevelLookupException, e:
			log.error( "ERROR Template not Found for (%s) or (%s)" , (('/messages_%s/msg_%s.txt' % (locale, file_no)), ('/messages/msg_%s.txt' % file_no)) )
			raise MissingTemplateException(e)
