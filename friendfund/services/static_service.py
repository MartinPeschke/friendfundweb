import random, md5
import pylons

class StaticService(object):
	PROFILE_STATIC_ROOT = '/s/user'
	DEFAULT_USER_PICTURE_TOKEN = "DEFAULT_USER_PICTURE"
	def __init__(self, sites, secure_sites):
		self.sites = sites.split(";")
		self.sites_length = len(self.sites)
		
		self.secure_sites = secure_sites.split(";")
		self.secure_sites_length = len(self.secure_sites)
	
	def get_default_user_picture_token(self):
		return self.DEFAULT_USER_PICTURE_TOKEN
	def get_default_user_picture(self, type, secured = False):
		return self.get_user_picture(None, type, secured)
	
	def get_user_picture(self, url, type, secured = False, ext="jpg"):
		if url.startswith('http'):
			return url
		else:
			static_root = self.PROFILE_STATIC_ROOT
			if secured:
				site_root = self.secure_sites[ord(url[0])%self.secure_sites_length]
				protocol = "https://"
			else:
				site_root = self.sites[ord(url[0])%self.sites_length]
				protocol = "http://"
			
			if not site_root:
				protocol = ''
				site_root = ''
			
			if not isinstance(url, basestring) or not url or url == "DEFAULT_USER_PICTURE": 
				return '%(protocol)s%(site_root)s/static/imgs/default_user_PROFILE_M.png'%locals()
			elif isinstance(url, basestring):
				if url.startswith('/'):
					return '%(protocol)s%(site_root)s%(url)s'%locals()
				else:
					return ('%(protocol)s%(site_root)s%(static_root)s/%(url)s_%(type)s.%(ext)s'%locals())
			else:
				return None