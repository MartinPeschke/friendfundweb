# -*- coding: utf-8 -*-
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
import os, base64, uuid
from friendfund.lib.i18n import *
from friendfund.lib.tools import *
import itertools

POOL_STATIC_ROOT = '/s/pool'
PRODUCT_STATIC_ROOT = '/s/product'
ACTION_PIC_STATIC_ROOT = '/static/imgs'

def decode_unique_token(token):
	return uuid.UUID(bytes=base64.urlsafe_b64decode(token+'=='))
def get_unique_token():
	return base64.urlsafe_b64encode(uuid.uuid4().bytes).strip('=')
def get_wizard(mc, pd):
	return mc.get("wizard_pd_%s"%pd) or {}
def set_wizard(mc, pd, wizard):
	mc.set("wizard_pd_%s"%pd, wizard, 7200)

def get_upload_pic_name(name):
	return os.path.join(name[0:2], name[2:4],name)
def get_upload_pic_name_ext(name, ext="jpg"):
	return os.extsep.join([os.path.join(name[0:2], name[2:4],name), ext])


################## Picture Helpers #################

def get_action_picture(action, ext='png'):
	name = action.name
	static_root = ACTION_PIC_STATIC_ROOT
	return '%(static_root)s/icon-%(name)s.%(ext)s' % locals()

def get_pool_picture(pool_pic_url, type, ext="png"):
	if pool_pic_url:
		static_root = POOL_STATIC_ROOT
		return '%(static_root)s/%(pool_pic_url)s_%(type)s.%(ext)s'%locals()
	else: 
		return ''

def url_is_local(url):
	return not url.startswith('http')

def get_default_product_picture_token():
	return "DEFAULT_PRODUCT_PICTURE"
def get_product_picture(product_picture_url, type, ext="jpg", site_root = ''):
	static_root = PRODUCT_STATIC_ROOT
	if not isinstance(product_picture_url, basestring) or not product_picture_url or product_picture_url == 'DEFAULT_PRODUCT_PICTURE':
		return '%(site_root)s/static/imgs/default_product_FF_POOL.png'%locals()
	elif product_picture_url.startswith('http'):
		return product_picture_url
	elif product_picture_url.startswith('/'):
		return '%(site_root)s%(product_picture_url)s'%locals()
	else:
		return '%(site_root)s%(static_root)s/%(product_picture_url)s_%(type)s.%(ext)s'%locals()
			

def get_merchant_logo(name):
	return '/static/imgs/merch/%s' % name
def get_merchant_logo_url(request):
	return get_merchant_logo(request.merchant.logo_url)
	
def pool_users_equal(user1, user2):
	### find at least one coresponding user network overlap
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

