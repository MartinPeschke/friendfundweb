"""
	FriendFund Payment Service, the only commandline argument should be the paster config file.
	i.e. invoke as: python friendfund/tasks/payment_job.py -f development.ini

	runs exec job.get_payment_queue;
	and processes entries of following format

	--refund 
	<CONTRIBUTION queue_ref="B76F0C12-283E-49ED-90AE-2C091F15D72C" contribution_ref="C76C5165-517C-4014-861F-67D5A1F61499"> 
	  <REFUND /> 
	</CONTRIBUTION> 

	--capture 
	<CONTRIBUTION queue_ref="38A4D812-F792-4A82-B7D5-187C33E5E014" contribution_ref="B8A4A51C-1EB3-48B8-9D21-BFE6B1391B90"> 
	  <CAPTURE total="21" currency_code="EUR" /> 
	</CONTRIBUTION> 

	--recurring 
	<CONTRIBUTION queue_ref="EB8E6C5B-774F-4641-BD4C-0059161000E5" contribution_ref="801DEBDF-3365-410C-8983-1C9AB7F64C2F"> 
	  <RECURRING shopper_ref="DC21D163-6185-4697-BEE0-618DBA19DFFB" shopper_email="martin@per-4.com" recurring_transaction_total="509" currency_code="EUR" /> 
	</CONTRIBUTION> 
"""
import time
import sys
import getopt
from xml.sax.saxutils import quoteattr
from logging.config import fileConfig

import ZSI
from paste.exceptions import formatter, collector

from friendfund.model.mapper import DBMapper
from friendfund.model.db_access import execute_query
from friendfund.tasks import get_db_pool, get_config, Usage
from friendfund.lib.payment.adyengateway import AdyenPaymentGateway, get_contribution_from_adyen_result


CONNECTION_NAME = 'job'
set_CONNECTION_NAME = 'pool'

def send_report(exc_data, config, level):
    from turbomail import Message
    from turbomail.control import interface

    _config = {"mail.on":True
        ,"mail.transport":"smtp"
        ,"mail.smtp.server":config.get('smtp_server')
        ,"mail.smtp.username":config.get('smtp_username')
        ,"mail.smtp.password":config.get('smtp_password')
        ,"mail.smtp.tls":config.get('smtp_use_tls')
    }
    interface.start(_config)
    msg = Message(config.get('error_email_from'), [config.get('email_to')], "%s:PAYMENT QUEUE:%s" % (config.get('error_subject_prefix'), level))
    msg.plain = """%s <br/> %s""" % (formatter.format_text(exc_data), __name__)
    msg.html = """%s <br/> %s""" % (formatter.format_html(exc_data), __name__)
    msg.send()
    interface.stop(force=True)


def execute_cancel_or_refund(dbset, gateway, contrib):
    details = contrib.find("REFUND")
    if details is None \
            or contrib.get('contribution_ref') is None \
            or contrib.get('queue_ref') is None \
            or details.get('transaction_id') is None:
        log.error("INCOMPLETE_REFUND_DETAILS %s (%s)" % (contrib.attrib, details.attrib))
        raise AttributeError("INCOMPLETE_REFUND_DETAILS %s (%s)" % (contrib.attrib, details.attrib))
    else:
        log.info("PROCESSING_REFUND %s", details.get('transaction_id'))
        payment_result = gateway.cancel_or_refund(details.get('transaction_id'))
        log.info("REFUND_RESULT: %s", payment_result)

def execute_capture(dbset, gateway, contrib):
    details = contrib.find("CAPTURE")
    if details is None \
            or contrib.get('contribution_ref') is None \
            or contrib.get('queue_ref') is None \
            or details.get('total') is None \
            or details.get('currency_code') is None \
            or details.get('transaction_id') is None:
        raise AttributeError("INCOMPLETE_CAPTURE_DETAILS %s (%s)" % (contrib.attrib, details.attrib))
    else:
        log.info("PROCESSING_CAPTURE %s, %d, %s", details.get('transaction_id'),  int(details.get('total')),details.get('currency_code'))
        payment_result = gateway.capture(
            details.get('transaction_id'),
            int(details.get('total')),
            details.get('currency_code')
        )
        if payment_result['response'] != u'[capture-received]':
            raise ValueError("CAPTURE_INVALID_RECEIVE_RECEIPT, %s" % payment_result)
        else:
            log.info("CAPTURE_RESULT: %s", payment_result)


def execute_recurring(dbset, gateway, contrib):
    details = contrib.find("RECURRING")
    if (details is None
        or contrib.get('contribution_ref') is None
        or contrib.get('queue_ref') is None
        or details.get('shopper_ref') is None
        or details.get('shopper_email') is None
        or details.get('recurring_transaction_total') is None
        or details.get('currency_code') is None):
        raise AttributeError("INCOMPLETE_RECURRING_DETAILS %s (%s)" % (contrib.attrib, details.attrib))
    else:
        log.info("PROCESSING_RECURRING %s", contrib.get('contribution_ref'))
        payment_result = gateway.use_last_recurring(
            contrib.get('contribution_ref'),
            int(details.get('recurring_transaction_total')),
            details.get('currency_code'),
            details.get('shopper_email'),
            details.get('shopper_ref'),
            selectedRecurringDetailReference = 'LATEST'
        )
        log.info("RECURRING_RESULT: %s", payment_result)
        notice = get_contribution_from_adyen_result(contrib.get('contribution_ref'), payment_result)
        result, cur = execute_query(dbset, log, 'exec %s ?;' % notice._set_proc, DBMapper.toDB(notice))

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

    fileConfig(configname)
    log = logging.getLogger(__name__)

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
    try:
        while 1:
            contributions, cur = execute_query(dbpool, log, "exec job.get_payment_queue;")
            contrib_set = [c for c in contributions.findall('CONTRIBUTION') if c.get("contribution_ref") and c.get("queue_ref")]
            if contrib_set:
                log.info( 'RECEIVED %s, %s', len(contrib_set), 'Contributions' )
                for contrib in contrib_set:
                    try:
                        if contrib.find("REFUND") is not None:
                            execute_cancel_or_refund(dbset, gateway, contrib)
                        elif contrib.find("CAPTURE") is not None:
                            execute_capture(dbset, gateway, contrib)
                        elif contrib.find("RECURRING") is not None:
                            execute_recurring(dbset, gateway, contrib)
                    except Exception, e:
                        exc_data = collector.collect_exception(*sys.exc_info())
                        rep_err = send_report(exc_data, config, 'ERROR')

                        if isinstance(e, ZSI.FaultException):
                            log.error("ADYEN_SOAP_ERROR: %s" % e)
                        else: log.error(e)
                        xml = execute_query(dbpool, log, 'job.set_payment_queue ?;',
                                            '<CONTRIBUTION queue_ref=%s contribution_ref=%s status="0"/>' \
                                            %(quoteattr(contrib.get("queue_ref")), quoteattr(contrib.get("contribution_ref")))
                        )
                    ####raise
                    else:
                        xml = execute_query(dbpool, log, 'job.set_payment_queue ?;',
                                            '<CONTRIBUTION queue_ref=%s contribution_ref=%s status="1"/>' \
                                            %(quoteattr(contrib.get("queue_ref")), quoteattr(contrib.get("contribution_ref")))
                        )
            else:
                time.sleep(120)
    except:
        exc_data = collector.collect_exception(*sys.exc_info())
        rep_err = send_report(exc_data, config, 'SHUTTING DOWN')
        raise
if __name__ == "__main__":
    sys.exit(main())