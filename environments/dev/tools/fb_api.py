import urllib2, os, sys, pyodbc, ConfigParser, simplejson, pprint

def get_config(configname):
	_config = ConfigParser.ConfigParser({'here':__file__})
	_config.read(configname)
	_config = dict(_config.items('app:main'))
	return _config



def get_access_token(app_conf):
	appid = app_conf['fbappid']
	appsecret = app_conf['fbapisecret']
	query = "https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (appid, appsecret)
	a = urllib2.urlopen(query)
	token = a.read().split('=')[1]
	return token, app_id


def main(token, app_id, command, args):
	if command == 'create_user':
		query = "https://graph.facebook.com/%s/accounts/test-users?installed=false&permissions=&method=post&access_token=%s"%(token, app_id)
		print query
		a = urllib2.urlopen(query)
		response = simplejson.load(a)
		pprint.pprint( response )
	elif command == 'get_users':
		"https://graph.facebook.com/%s/accounts/test-users?access_token=%s"%(token, app_id)
		print query
		a = urllib2.urlopen(query)
		response = simplejson.load(a)
		pprint.pprint( response )
	elif command == "make_friend":
		query = "https://graph.facebook.com/%s/friends/%s?method=post" % (args[0], args[1])
		print query
		pprint.pprint( urllib2.urlopen(query).read() )
		query = "https://graph.facebook.com/%s/friends/%s?method=post" % (args[0], args[1])
		print query
		pprint.pprint( urllib2.urlopen(query).read() )


if __name__ == "__main__":
	argv = sys.argv
	if len(argv) < 3: print >>sys.stderr, "Need at least some DB Environment name, i.e. dev, test or beta"
	environment = argv[1]
	command = argv[2]
	args = argv[3:]
	token, app_id = get_access_token(get_config(environment))
	sys.exit(main(token, app_id, command, args))