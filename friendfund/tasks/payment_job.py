"""
FriendFund Payment Service, the only commandline argument should be the paster config file.
i.e. invoke as: python friendfund/tasks/payment_job.py -f development.ini
"""
import logging, time, sys, getopt, os, ZSI
from lxml import etree
from xml.sax.saxutils import quoteattr
from friendfund.model.mapper import DBMapper
from friendfund.model.db_access import execute_query
from friendfund.tasks import get_db_pool, get_config, Usage
from friendfund.lib.payment.adyengateway import AdyenPaymentGateway, get_contribution_from_adyen_result

import logging, logging.config
logging.config.fileConfig("notifier_logging.conf")
log = logging.getLogger(__name__)

CONNECTION_NAME = 'job'
set_CONNECTION_NAME = 'pool'


def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		opts, args = getopt.getopt(sys.argv[1:], "f:h", ["help", "file"])
		opts = dict(opts)
		if '-f' not in opts:
			raise Usage("Missing Option -f")
	except getopt.error, msg:
		 raise Usage(msg)
	except Usage, err:
		print >>sys.stderr, err.msg
		print >>sys.stderr, "for help use --help"
		return 2
	
	configname = opts['-f']
	config = get_config(configname)
	dbpool = get_db_pool(config, CONNECTION_NAME)
	dbset = get_db_pool(config, set_CONNECTION_NAME)
	ROOT_URL = config['site_root_url']
	debug = config['debug'].lower() == 'true'
	gateway = AdyenPaymentGateway(url = config['adyen.location'],
					user = config['adyen.user'],
					password = config['adyen.password'],
					merchantAccount = config['adyen.merchantaccount'])
	
	log.info( 'DEBUG: %s for %s (%s)', debug, CONNECTION_NAME, gateway)
	while 1:
		conn = dbpool.connection()
		cur = conn.cursor()
		res = cur.execute('exec job.get_recurring_payment;')
		res = res.fetchone()[0]
		cur.close()
		conn.commit()
		conn.close()
		log.info ( res )
		contributions = etree.fromstring(res)
		contrib_set = [c for c in contributions.findall('CONTRIBUTION') if c.get("contribution_ref")]
		###		<CONTRIBUTION 
		###		shopper_ref="3708AF13-7FBB-494C-B65B-F0BF5DE5C299" 
		###		shopper_email="test201@friendfund.com" 
		###		contribution_ref="0850DA3E-58E0-4D4C-9DCD-D0B44C00C13F" 
		###		recurring_transaction_total="24489" 
		###		currency_code="EUR" />
		if contrib_set:
			log.info( 'RECEIVED %s, %s', len(contrib_set), 'Contributions' )
			for contrib in contrib_set:
				if not (contrib.get('shopper_ref') and contrib.get('shopper_email') and contrib.get('contribution_ref') and contrib.get('recurring_transaction_total') and contrib.get('currency_code')):
					log.error("CONTRIBUTION_INCOMPLETE_RECURRING_DETAILS %s" % (contrib.attrib))
				else:
					log.info("RECURRING_CONTRIBUTION %s", contrib.attrib)
					try:
						payment_result = gateway.use_last_recurring(contrib.get('contribution_ref'), 
										int(contrib.get('recurring_transaction_total')),
										contrib.get('currency_code'), 
										contrib.get('shopper_email'), 
										contrib.get('shopper_ref'), 
										selectedRecurringDetailReference = 'LATEST')
						notice = get_contribution_from_adyen_result(contrib.get('contribution_ref'), payment_result)
						result, cur = execute_query(dbset, log, 'exec %s ?;' % notice._set_proc, DBMapper.toDB(notice))
					except ZSI.FaultException, e:
						log.error("ADYEN_SOAP_ERROR: %s" % e)
		else:
			time.sleep(2)

if __name__ == "__main__":
    sys.exit(main())