# -*- coding: utf-8 -*-
from string import Template


#to print a $ in a message, use $$

STANDARD_PARAMS = {}
TEMPLATES = {'INVITE':{ 
					 "public":Template(u"@${screen_name}:${admin} invites you to a gift pool for ${receiver}'s ${occasion} gift at ")
					,"secret":Template(u"@${screen_name}:${admin} invites you to a gift pool on friendfund at ")
					,"url":Template(u"${ROOT_URL}/pool/${up_url}")
				},
			'CONTRIBUTION_FEED':{
					 "public":Template(u"@${screen_name} has just chipped into a gift pool, join in the fund raising at ")
					,"secret":Template(u"@${screen_name} has just chipped into a gift pool, join in the fund raising at ")
					,"url":Template(u"${ROOT_URL}/pool/${up_url}")
				},
			'REMIND_INVITEES':{
					 "public":Template(u"@${screen_name}:${admin} invites you to help out for ${receiver}'s ${product} at ")
					,"secret":Template(u"@${screen_name}:${admin} invites you to help out for a friends gift pool at ")
					,"url":Template(u"${ROOT_URL}/pool/${p_url}")
				},
			'ASK_RECEIVER':{
					 "public":Template(u"@${screen_name}:${admin} invites you to help out and chip in for your gift at ")
					,"secret":Template(u"@${screen_name}:${admin} invites you to help out and chip in for your gift at ")
					,"url":Template(u"${ROOT_URL}/pool/${p_url}")
				},
			'ASK_CONTRIBUTORS_TO_INVITE':{
					 "public":Template(u"@${screen_name}:${admin} invites you to invite more for ${receiver}'s ${product} at ")
					,"secret":Template(u"@${screen_name}:${admin} invites you to invite more for a friends gift pool at ")
					,"url":Template(u"${ROOT_URL}/pool/${p_url}")
				},
			'FRIEND_SELECTOR':{
					 "public":Template(u"@${screen_name}:I nominated you to choose the gift for ${receiver}, pick it at ")
					,"secret":Template(u"@${screen_name}:I nominated you to choose the gift for a friend's gift pool at ")
					,"url":Template(u"${ROOT_URL}/pool/${up_url}")
				}
			}
