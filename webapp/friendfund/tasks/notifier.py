"""
FriendFund Notification Service, the only commandline argument should be the paster config file.
i.e. invoke as: python friendfund/tasks/notifier.py -f development.ini
"""
import logging
import time
import sys
import getopt
import os
import gettext
from itertools import imap
from xml.sax.saxutils import quoteattr
from datetime import datetime, date
from decimal import Decimal

from babel.numbers import format_currency as fc
from babel.dates import format_date as fdate

from friendfund.lib import helpers as h
from friendfund.model import common
from friendfund.model.db_access import execute_query
from friendfund.model.globals import GetMerchantConfigProc
from friendfund.tasks import get_db_pool, get_config, Usage, STATICS_SERVICE
from friendfund.tasks.notifiers import email, facebook, twitter
from friendfund.tasks.notifiers.common import InvalidAccessTokenException, get_template, root


log = logging.getLogger(__name__)

transl = gettext.translation('friendfund', os.path.normpath(os.path.join(__file__, '..','..', 'i18n')), ['en', 'de', 'es'])
_ = transl.ugettext


log.info( os.path.join(root, 'templates','messaging') )
def empty_sender(name = None):
    def es(template, sndr_data, rcpt_data, template_data, config):
        log.warning( "%s_MESSAGING_IS_OFF", name )
        return "1"
    return es
def error_sender(name = None):
    def es(template, sndr_data, rcpt_data, template_data, config):
        raise Exception( "NOT_IMPLEMENTED_ERROR(%s)" % name)
    return es


def save_results(dbpool, messaging_results):
    #formatting children
    def format_child(element):
        mref, attribs = element
        def format_attrib(map):
            def f(key):
                return '%s=%s' % (key, quoteattr(map[key]))
            return f
        f = format_attrib(attribs)
        return "<MESSAGE message_ref=%s %s/>" % (quoteattr(mref), ' '.join(imap(f, attribs)))
    #assemble complete parameter xml
    status_update =  "<MESSAGES>%s</MESSAGES>" % ''.join(imap(format_child, messaging_results.iteritems()))
    execute_query(dbpool, log, "exec job.set_message_status ?;", status_update)

def pool_url(key, data_map, locale):
    return {key: "http://%s/pool/%s" % (data_map["merchant_domain"], data_map[key])}
def currency(key, data_map, locale):
    val = float(data_map[key]) / 100
    fnumber = Decimal('%.2f' % val)
    return {key: fc(fnumber, data_map['currency'], locale=locale)}
def firstname(key, data_map, locale):
    return {"firstname_%s"%key:data_map[key].split()[0], key:data_map[key]}
def date(key, data_map, locale):
    val = data_map[key]
    try:
        val =  datetime.strptime(val.rsplit('.',1)[0], '%Y-%m-%dT%H:%M:%S')
    except ValueError, e:
        val = datetime.strptime(val.split('T')[0], '%Y-%m-%d')
    if isinstance(val, datetime):
        return {key: fdate(val, format="long", locale=locale), "expiry_date_object":val}
    else:
        return {key: val}
def translate(key, data_map, locale):
    return {key: _(data_map[key])}

TRANSLATIONS = {"expiry_date": date, "chip_in_date": date, "target_amount":currency, "chip_in_amount":currency, "total_funded":currency, "invitee_name": firstname, "occasion":translate, "event_name":translate}

def localize(data_map, locale):
    result = {}
    for key in data_map:
        if key in TRANSLATIONS:
            updates = TRANSLATIONS[key](key, data_map, locale)
            result.update(updates)
        else:
            result[key] = data_map[key]
    return result


def setup_common_parameters(template_data, common_params, merchant_config):
    params = {}
    params.update(common_params)
    params["today"] = datetime.today().strftime("%d.%m.%Y")
    if "merchant_key" in template_data:
        merchant = merchant_config.merchants.key_map[template_data["merchant_key"]]
    else:
        merchant = merchant_config.merchants.default
    params['merchant_domain'] = merchant.domain
    params['merchant_logo_url'] = merchant.get_logo_url()
    params['merchant_name'] = merchant.name
    params['merchant_is_default'] = merchant.is_default

    return params


def poll_message_queue(config, debug, merchant_config, jobpool, available_langs, messengers, common_params):
    messaging_results = {}
    messages, cur = execute_query(jobpool, log, "exec job.get_unsent_messages;")
    msg_set = messages.findall('MESSAGE')
    if msg_set:
        log.info( 'RECEIVED %s, %s', len(msg_set), 'Messages' )
        for msg_data in msg_set:
            meta_data = msg_data.attrib
            sndr_data = msg_data.find("SENDER").attrib
            rcpt_data = msg_data.find("RECIPIENT").attrib
            template_data = dict( msg_data.find("TEMPLATE").attrib )
            template_data.update(setup_common_parameters(template_data, common_params, merchant_config))

            rcpts_data = [msg.attrib for msg in msg_data.find("TEMPLATE").findall("RECIPIENT")]
            ivts_data = [msg.attrib for msg in msg_data.find("TEMPLATE").findall("INVITEE")]
            print '-'*80
            if rcpts_data:
                template_data['recipients'] = rcpts_data
            if ivts_data:
                template_data['invitee_list']=ivts_data

            locale = h.negotiate_locale([meta_data.get('locale', "en_GB")], available_langs)
            try:
                file_no = meta_data['file_no']

                template_data = localize(template_data, locale)
                log.info ( 'TEMPLATE(file_no:%s), %s', file_no, template_data )
                template = get_template(locale, file_no, log)

                notification_method = meta_data.get('notification_method').lower()
                sender = messengers.get(notification_method, error_sender(notification_method))
                msg_id = sender(template, sndr_data, rcpt_data, template_data, config)
            except InvalidAccessTokenException, e:
                log.error( 'INVALID_ACCESS_TOKEN before SENDING: %s', str(e) )
                messaging_results[meta_data.get('message_ref')] = {'status':'INVALID_ACCESS_TOKEN', "note":str(e)[:254]}
            except email.UMSEmailUploadException, e:
                log.error( 'UMS_EMAIL_ERROR while SENDING: %s', str(e) )
                messaging_results[meta_data.get('message_ref')] = {'status':'FAILED', "note":str(e)[:254]}
            except Exception, e:
                log.error( 'ERROR while SENDING: %s (%s)', meta_data, str(e) )
                messaging_results[meta_data.get('message_ref')] = {'status':'FAILED', "note":str(e)[:254]}
            else:
                messaging_results[meta_data.get('message_ref')] = {'status':'SENT', "msg_id":msg_id}
        save_results(jobpool, messaging_results)

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
    jobpool = get_db_pool(config, "job")
    apppool = common.DBManager(get_db_pool(config, "pool"), None, log, STATICS_SERVICE)
    merchant_config = apppool.get(GetMerchantConfigProc)

    common_params = {"DEFAULT_BASE_URL":config['site_root_url'], "contact_url":"http://%s/content/contact"%config['site_root_url'], "learn_more_url":"http://%s/content/contact"%config['site_root_url']}

    debug = config['debug'].lower() == 'true'
    available_langs = config['available_locales'].lower().split(',')

    facebook_on = config['notification_fb'].lower() == 'on'
    twitter_on = config['notification_tw'].lower() == 'on'
    email_on = config['notification_email'].lower() == 'on'

    messengers = {}
    if facebook_on:
        messengers['create_event'] = facebook.create_event_invite
        messengers['stream_publish'] = facebook.send_stream_publish
    else:
        messengers['create_event'] = empty_sender("create_event")
        messengers['stream_publish'] = empty_sender('stream_publish')
    if twitter_on:
        messengers['tweet'] = twitter.send_tweet
        messengers['tweet_dm'] = empty_sender('tweet_dm')
    else:
        messengers['tweet'] = empty_sender('tweet')
        messengers['tweet_dm'] = empty_sender('tweet_dm')
    if email_on:
        messengers['email'] = email.send
    else:
        messengers['email'] = empty_sender('email')

    INTERVAL = 5
    if not debug:
        INTERVAL = INTERVAL*5
    log.info( 'DEBUG: %s for (fb:%s,tw:%s,email:%s), INTERVAL: %s', debug,  facebook_on, twitter_on, email_on, INTERVAL)
    log.info( "STARTING WITH %s", STATICS_SERVICE)

    while 1:
        poll_message_queue(config, debug, merchant_config, jobpool, available_langs, messengers, common_params)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    sys.exit(main())