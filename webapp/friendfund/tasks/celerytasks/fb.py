import logging
import urllib
import urllib2
import os
from operator import itemgetter
from datetime import datetime

import simplejson
from poster.streaminghttp import register_openers
from poster.encode import multipart_encode
from celery.log import setup_logger

from friendfund.lib import fb_helper, helpers as h
from friendfund.lib.cache_helper import set_pages_to_cache
from friendfund.model import db_access
from friendfund.model.async.user_data import UserData, UserBirthday, UserBirthdayList
from friendfund.tasks import get_dbm, get_cm
from friendfund.tasks.celerytasks import app
from friendfund.tasks.celerytasks.photo_renderer import remote_profile_picture_render

log = logging.getLogger()

CONNECTION_NAME = 'async'

FRIENDS_QUERY = '?'.join([
    'https://graph.facebook.com/%s/friends',
    'fields=id,name,birthday,gender,email,locale&access_token=%s'
])


@app.task
def upload_picture_to_event(event_id, access_token, picture_url, trial_count = 0):
    if trial_count>2:
        log.error("TOO_MANY_ERRORS_FOR_EVENTS_MODIFY: gave up after %s", trial_count)
        return '[ack]'
    register_openers()
    try:
        fname, headers = urllib.urlretrieve(picture_url)
    except Exception, e:
        log.error(e)
        upload_picture_to_event(event_id, access_token, picture_url, trial_count = trial_count + 1)
    try:
        datagen, headers = multipart_encode({"eid":event_id, "access_token":access_token, "event_info":"{}", "[no name]":open(fname, "rb"), "format":"json"})
        req = urllib2.Request('https://api.facebook.com/method/events.edit', datagen, headers)
        try:
            log.info("FACEBOOK_EVENT_PICTURE_UPLOAD_RETURNED %s", urllib2.urlopen(req).read())
        except Exception, e:
            log.error(e.fp.read())
            upload_picture_to_event(event_id, access_token, picture_url, trial_count = trial_count + 1)
    finally:
        if fname: os.unlink(fname)


@app.task
def remote_persist_user(user_data):
    dbm = get_dbm(CONNECTION_NAME)
    user = UserData(**user_data)
    try:
        dbm.set(user)
    except db_access.SProcException, e:
        log.error(str(e))
    remote_profile_picture_render.delay(
        [(user_data['network'],
          user_data['network_id'],
          user_data['profile_picture_url'])])

    friends, is_complete, offset = fb_helper.get_friends_from_cache(log,  ####TODO: FUCKED
                                                                    get_cm(CONNECTION_NAME),
                                                                    user_data['network_id'],
                                                                    user_data['access_token']
    )
    if not friends:
        return 'ack'

    user_list = (UserBirthday(**data) for uid,data in friends.iteritems())
    users = UserBirthdayList(users = user_list, u_id = user_data['u_id'])
    try:
        dbm.set(users)
    except db_access.SProcException, e:
        log.error(str(e))
    return 'ack'

def get_email_from_permissions(fb_data):
    query = urllib.urlencode({'access_token':fb_data['access_token']})
    resp = urllib2.urlopen('https://graph.facebook.com/me?%s' % query)
    user_data = simplejson.loads(resp.read())
    return user_data['email']



def get_friend_list(method, logger, id, access_token, slice_size = 100):
    def package(elem):
        repr = {### Pool User Attributes, unusable for display
                'notification_method':method
        ,'network':'facebook'
        ,'network_id':elem["id"]
        ,'email':elem.get('email')
        ,'profile_picture_url':fb_helper.get_pic_url(elem['id'])
        ,'large_profile_picture_url':fb_helper.get_large_pic_url(elem['id'])
        ,'locale':elem.get('locale', "").lower()
        ,'name':elem['name']
        }

        dob = elem.get('birthday')
        if dob:
            try:
                dob = datetime.strptime(dob, "%m/%d/%Y")
            except ValueError, e:
                try:
                    dob = datetime.strptime(dob, "%m/%d")
                except ValueError, e:
                    logger.error( 'Facebook User Birthday: %s, %s', e , dob)
                    dob = None
            if dob:
                year = datetime.today().year
                doy = dob-datetime(dob.year,1,1)
                repr['dob'] = datetime(year, 1,1) + doy
                repr['dob_difference'] = (repr['dob'] - datetime.today()).days
                if repr['dob_difference'] < 2:
                    repr['dob'] = datetime(year + 1, 1,1) + doy
                    repr['dob_difference'] = (repr['dob'] - datetime.today()).days
        return (elem['id'], {
        'name':elem['name']
        ,'network_id':elem["id"]
        ,'profile_picture_url':fb_helper.get_pic_url(elem['id'])
        ,'minimal_repr': h.encode_minimal_repr(repr)
        })
    query = FRIENDS_QUERY % (id, access_token)
    data = simplejson.loads(urllib2.urlopen(query).read())['data']
    user_data = [ package(elem) for elem in sorted(data, key=itemgetter("name")) if 'name' in elem ]

    total = len(user_data)
    pagenumber = total/slice_size + bool(total%slice_size)

    for i in range(0, pagenumber):
        yield user_data[i*slice_size:(i+1)*slice_size], i+1 == pagenumber


@app.task
def set_friends_async(proto_key, id, access_token):
    cache_pool = get_cm(CONNECTION_NAME)
    dataprovider = get_friend_list('CREATE_EVENT', log, id, access_token)
    set_pages_to_cache(log, cache_pool, proto_key, dataprovider)

