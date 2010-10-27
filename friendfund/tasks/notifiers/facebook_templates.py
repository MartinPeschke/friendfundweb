# -*- coding: utf-8 -*-
from string import Template
FF_SLOGAN = 'Friendfund is the easy way for you and your friends to organise group gifts!'


#to print a $ in a message, use $$

STANDARD_PARAMS = {'description':Template(FF_SLOGAN),"picture":Template(u"${ROOT_URL}/static/imgs/fb_stream_publish_logo.png")}
TEMPLATES = {"INVITE":{
					 "public":{
						 "message":Template(u"${description}")
						,"link":   Template(u"${ROOT_URL}/pool/${up_url}")
						,"name":   Template(u"Friend Fund for ${receiver}")
					}
					,"secret":{
						"message":Template(u"A Friend Fund for a Friend of yours has been opened, the admin wants this pool to remain secret, see it at www.friendfund.com")
						,"link"   :Template(u"${ROOT_URL}/pool/${up_url}")
						,"name"   :Template(u"Friend Fund for a friend of yours")
					}
				},
			"CONTRIBUTION_FEED":{
					 "public":{
						 "message":Template(u"${name} has chipped in for ${receiver}'s ${product}")
						,"link":   Template(u"${ROOT_URL}/pool/${p_url}")
						,"name":   Template(u"Friend Fund for ${receiver}")
					}
					,"secret":{
						 "message":Template(u"A Friend Fund for a Friend of yours has been opened, the admin wants this pool to remain secret, see it at www.friendfund.com")
						,"link"   :Template(u"${ROOT_URL}/pool/${p_url}")
						,"name"   :Template(u"Friend Fund for a friend of yours")
					}
				},
			"ASK_RECEIVER":{
					 "public":{
						 "message":Template(u"${admin} had created a gift pool for you, can you help out for your ${product}?")
						,"link":   Template(u"${ROOT_URL}/pool/${p_url}")
						,"name":   Template(u"Friend Fund for ${receiver}")
					}
					,"secret":{
						 "message":Template(u"${admin} had created a gift pool for you, can you help out for your ${product}?")
						,"link"   :Template(u"${ROOT_URL}/pool/${p_url}")
						,"name"   :Template(u"Friend Fund for a friend of yours")
					}
				},
			"REMIND_INVITEES":{
					 "public":{
						 "message":Template(u"${admin} is still in urgent need of your support, see if you can help out and chip in for ${receiver}'s ${product}")
						,"link":   Template(u"${ROOT_URL}/pool/${p_url}")
						,"name":   Template(u"Friend Fund for ${receiver}")
					}
					,"secret":{
						 "message":Template(u"A Friend Fund for a Friend of yours needs help, the admin wants this pool to remain secret, see it at www.friendfund.com")
						,"link"   :Template(u"${ROOT_URL}/pool/${p_url}")
						,"name"   :Template(u"Friend Fund for a friend of yours")
					}
				},
			"ASK_CONTRIBUTORS_TO_INVITE":{
					 "public":{
						 "message":Template(u"${admin} is in urgent need of your support, so help out and and to invite more friends to ${receiver}'s ${product} pool at friendfund.com")
						,"link":   Template(u"${ROOT_URL}/pool/${p_url}")
						,"name":   Template(u"Friend Fund for ${receiver}")
					}
					,"secret":{
						 "message":Template(u"A Friend Fund for a Friend of yours needs help, the admin wants this pool to remain secret, see it at www.friendfund.com")
						,"link"   :Template(u"${ROOT_URL}/pool/${p_url}")
						,"name"   :Template(u"Friend Fund for a friend of yours")
					}
				},
			"POOL_FUNDED_FEED":{
					 "public":{
						 "message":Template(u"${receiver}'s gift pool has reached its target and the ${product} is on its ways. Thanks to those who chipped in!")
						,"link":   Template(u"${ROOT_URL}/pool/${p_url}")
						,"name":   Template(u"Friend Fund for ${receiver}")
					}
					,"secret":{
						 "message":Template(u"A secret gift pool has reached it target come and see who has chipped in. Check it at www.friendfund.com")
						,"link"   :Template(u"${ROOT_URL}/pool/${p_url}")
						,"name"   :Template(u"Friend Fund for a friend of yours")
					}
				}
			}