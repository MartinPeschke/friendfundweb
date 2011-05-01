# -*- coding: utf-8 -*-
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
import os, base64, uuid
from friendfund.lib.i18n import *
from friendfund.lib.tools import *
import itertools


def decode_unique_token(token):
	return uuid.UUID(bytes=base64.urlsafe_b64decode(token+'=='))
def get_unique_token():
	return base64.urlsafe_b64encode(uuid.uuid4().bytes).strip('=')
def get_wizard(mc, pd):
	return mc.get("wizard_pd_%s"%pd) or {}
def set_wizard(mc, pd, wizard):
	mc.set("wizard_pd_%s"%pd, wizard, 7200)




################## Picture Helpers #################

def pool_users_equal(user1, user2):
	### find at least one corresponding user network overlap
	if not (user1.networks and user2.networks):
		return False
	else:
		for network in user1.networks:
			if (user1.networks[network].network_id and user1.networks[network].network_id == user2.networks[network].network_id) \
				or (user1.networks[network].email and user1.networks[network].email == user2.networks['network'].email):
				return True
	return False
		
def users_equal(user1, user2):
	if not user1.network or not user1.network_id or not user2.network or not user2.network_id:
		return False
	return str(user1.network).lower() == str(user2.network).lower() and str(user1.network_id).lower() == str(user2.network_id).lower()

def create_pool_link(request, url):
	return request.merchant.type_is_group_gift and url("home", protocol="http") or url("pool_details", protocol="http", v=2)