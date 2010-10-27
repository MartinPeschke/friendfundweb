# -*- coding: utf-8 -*-
from string import Template


#to print a $ in a message, use $$

STANDARD_PARAMS = {}
TEMPLATES = {'INVITE':{ 
					 "public":Template(u"@${screen_name}:${admin} asks you to join a gift pool for ${receiver}'s [occasion] at ${ROOT_URL}/pool/${up_url}")
					,"secret":Template(u"@${screen_name}:${admin} asks you to a pool on friendfund. ${ROOT_URL}/pool/${up_url}")
				},
			'CONTRIBUTION_FEED':{
					 "public":Template(u"@${screen_name} has just chipped into a gift pool, join in the fund raising. ${ROOT_URL}/pool/${up_url}")
					,"secret":Template(u"@${screen_name} has just chipped into a gift pool, join in the fund raising. ${ROOT_URL}/pool/${up_url}")
				},
			'REMIND_INVITEES':{
					 "public":Template(u"@${screen_name}:${admin} asks you to help out for ${receiver}'s ${product} at ${ROOT_URL}/pool/${p_url}")
					,"secret":Template(u"@${screen_name}:${admin} asks you to help out for a friends gift pool at ${ROOT_URL}/pool/${p_url}")
				},
			'ASK_RECEIVER':{
					 "public":Template(u"@${screen_name}:${admin} asks you to help out and chip in for your gift at ${ROOT_URL}/pool/${p_url}")
					,"secret":Template(u"@${screen_name}:${admin} asks you to help out and chip in for your gift at ${ROOT_URL}/pool/${p_url}")
				},
			'ASK_CONTRIBUTORS_TO_INVITE':{
					 "public":Template(u"@${screen_name}:${admin} asks you to invite more for ${receiver}'s ${product} at ${ROOT_URL}/pool/${p_url}")
					,"secret":Template(u"@${screen_name}:${admin} asks you to invite more for a friends gift pool at ${ROOT_URL}/pool/${p_url}")
				},
			'ASK_CONTRIBUTORS_TO_INVITE':{
					 "public":Template(u"@${screen_name}:${admin} asks you to invite more for ${receiver}'s ${product} at ${ROOT_URL}/pool/${p_url}")
					,"secret":Template(u"@${screen_name}:${admin} asks you to invite more for a friends gift pool at ${ROOT_URL}/pool/${p_url}")
				}
			}
