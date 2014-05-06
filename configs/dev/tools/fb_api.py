import urllib, urllib2, os, sys, pyodbc, ConfigParser, simplejson, pprint

def get_config(configname):
	_config = ConfigParser.ConfigParser({'here':__file__})
	_config.read(configname)
	_config = dict(_config.items('app:main'))
	return _config



def get_access_token(app_conf):
	app_id = app_conf['fbappid']
	appsecret = app_conf['fbapisecret']
	print app_id, appsecret
	query = "https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (app_id, appsecret)
	a = urllib2.urlopen(query)
	token = a.read().split('=')[1]
	return app_id, token
def make_query(query):
	try:
		print query
		result = simplejson.load(urllib2.urlopen(query))
		pprint.pprint(result)
		return result
	except urllib2.HTTPError, e:
		print e.fp.read()

def main(app_id, token, command, args):
	if command == 'create_user':
		response = make_query("https://graph.facebook.com/%s/accounts/test-users?installed=false&permissions=email&method=post&access_token=%s"%(app_id, token))
	elif command == 'list_users':
		response = make_query("https://graph.facebook.com/%s/accounts/test-users?access_token=%s"%(app_id, token))
	elif command == "make_friend":
		users = make_query("https://graph.facebook.com/%s/accounts/test-users?access_token=%s"%(app_id, token))['data']
		token1, token2 = None, None
		for i, user in enumerate(users):
			if user['id']==args[0]:
				token1 = user['access_token']
			if user['id']==args[1]:
				token2 = user['access_token']
			if token1 and token2: break
		make_query("https://graph.facebook.com/%s/friends/%s?access_token=%s&method=post" % (args[0], args[1], token1))
		make_query("https://graph.facebook.com/%s/friends/%s?access_token=%s&method=post" % (args[1], args[0], token2))
	else:
		print "unknown command"

if __name__ == "__main__":
	argv = sys.argv
	if len(argv) < 3: print >>sys.stderr, "Need at least some DB Environment name, i.e. dev, test or beta"
	environment = argv[1]
	command = argv[2]
	args = argv[3:]
	app_id, token = get_access_token(get_config(environment))
	sys.exit(main(app_id, token, command, args))