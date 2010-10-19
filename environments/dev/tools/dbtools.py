import os, sys, pyodbc, ConfigParser

def get_config(configname):
	_config = ConfigParser.ConfigParser({'here':__file__})
	_config.read(configname)
	_config = dict(_config.items('app:main'))
	return _config
	
	
def update_keys(conn):
	from lxml import etree
	cur = conn.cursor()
	res = cur.execute('exec app.get_keys;')
	r = res.fetchone()[0]
	result = etree.fromstring(r)
	outf = open('%s/friendfund/resources/db_keys.py' % os.getcwd(), 'w')
	outf.write("from pylons.i18n import ugettext as _\n\n")
	outf.write("KEYS=[\n\t")
	out = outf.write('\n\t,'.join('_("%s")' % (k.replace('"', '\"')) for k in result.xpath('KEYS/@NAME')))
	outf.write("]")
	outf.close()
	conn.commit()
	cur.close()
	conn.close()




def get_db_connection(app_conf):
	return pyodbc.connect(driver=app_conf['pool.connectstring.driver']
			,server=app_conf['pool.connectstring.server']
			,instance=app_conf['pool.connectstring.instance']
			,database=app_conf['pool.connectstring.database']
			,port=app_conf['pool.connectstring.port']
			,tds_version=app_conf['pool.connectstring.tds_version']
			,uid=app_conf['pool.connectstring.uid']
			,pwd=app_conf['pool.connectstring.pwd']
			,client_charset=app_conf['pool.connectstring.client_charset'])

def main(conn, command, args):
	if command == 'clean':
		cur = conn.cursor()
		cur.execute('exec app.delete_data;')
		conn.commit()
		cur.close()
		conn.close()
		print "deleted data"
	elif command == 'expire':
		cur = conn.cursor()
		cur.execute('exec app.expire_pool ?', args[0])
		conn.commit()
		cur.close()
		conn.close()
		print "expired pool", args
	elif command == 'badges':
		cur = conn.cursor()
		cur.execute('exec app.delete_badges;')
		conn.commit()
		cur.close()
		conn.close()
		print "deleted badges"
	elif command == 'cleanqueue':
		cur = conn.cursor()
		cur.execute('exec app.delete_message_queue;')
		conn.commit()
		cur.close()
		conn.close()
		print "deleted msg queue"
	elif command == 'update_keys':
		update_keys(conn)
		print "db keys resources updates"
	else:
		print "unknown command"

if __name__ == "__main__":
	argv = sys.argv
	if len(argv) < 3: print >>sys.stderr, "Need at least some DB Environment name, i.e. dev, test or beta"
	environment = argv[1]
	command = argv[2]
	args = argv[3:]
	conn = get_db_connection(get_config(environment))
	sys.exit(main(conn, command, args))