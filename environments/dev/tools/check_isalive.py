import urllib2, urllib, datetime

hosts = ["http://www.friendfund.com", "http://friendfund.com", "https://www.friendfund.com"]

for host in hosts:
	try:
		a = urllib2.urlopen(host).read()
	except urllib2.HTTPError,e: 
		from turbomail import Message
		from turbomail.control import interface
		config = {"mail.on":True,"mail.transport":"smtp","mail.smtp.server":"smtp.strato.de","mail.smtp.username":"cahoots@quotsy.com","mail.smtp.password":"Popov2010","mail.smtp.tls":True}
		interface.start(config)
		msg = Message("whitefall_1@dev.friendfund.de", ["martin@friendfund.com", "errors@friendfund.com"], "HTTP_SERVER_STATE: ALARM")
		msg.plain = '%s\n\n\n%s' % (host, e.fp.read())
		msg.send()
		interface.stop(force=True)
		print "ERROR IN HOST", host
	except urllib2.URLError, e:
		from turbomail import Message
		from turbomail.control import interface
		config = {"mail.on":True,"mail.transport":"smtp","mail.smtp.server":"smtp.strato.de","mail.smtp.username":"cahoots@quotsy.com","mail.smtp.password":"Popov2010","mail.smtp.tls":True}
		interface.start(config)
		msg = Message("whitefall_1@dev.friendfund.de", ["martin@friendfund.com", "errors@friendfund.com"], "HTTP_SERVER_STATE: ALARM")
		msg.plain = '%s\n\n\n%s' % (host, 'URL UNREACHABLE')
		msg.send()
		interface.stop(force=True)
		print "ERROR IN HOST", host
	else:
		print host, "is_alive"
	

if datetime.datetime.now().minute == 1:
	from turbomail import Message
	from turbomail.control import interface
	config = {"mail.on":True,"mail.transport":"smtp","mail.smtp.server":"smtp.strato.de","mail.smtp.username":"cahoots@quotsy.com","mail.smtp.password":"Popov2010","mail.smtp.tls":True}
	interface.start(config)
	msg = Message("whitefall_1@dev.friendfund.de", "martin@friendfund.com", "HTTP_SERVERS_STATE: OK")
	msg.plain = '%s\n\n\nCheck completed, no Errors' % ('\n'.join(hosts))
	msg.send()
	interface.stop(force=True)
	print "ALL GOOD on ALL HOSTS", hosts