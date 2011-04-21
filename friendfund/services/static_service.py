import os, md5, uuid

class IncorrectPictureTypeException(Exception):
	pass

PROFILE_STATIC_ROOT = '/s/user'
PRODUCT_STATIC_ROOT = '/s/product'
POOL_STATIC_ROOT = '/s/pool'
DEFAULT_USER_PICTURE_TOKEN = "DEFAULT_USER_PICTURE"
DEFAULT_PRODUCT_PICTURE_TOKEN = "DEFAULT_PRODUCT_PICTURE"

DEFAULT_PROFILE_KEY = "PROFILE_M"
PROFILE_PIC_FORMATS = {  'RA' : (120,120)
						,'POOL': (140,140)
						,'PROFILE_S': (50,50)
						,'PROFILE_M': (75,75)
						,'MYPROFILE': (90,90)
						,'RESULT': (205,205)
						}

PRODUCT_PIC_FORMATS = {'RA' : (161,120)
					,  'POOL': (140,140)
					,  'MYPOOLS': (153,114)
					,  'FF_POOLS': (190,150)
					,  'FF_POOL_PIC_S':(60,50)
					}

POOL_PIC_FORMATS = {
					 'RA': ((161,120), (4, 12))
					,'MYPOOLS': ((120,79), (3, 6))
					}

def tokenize_name(name):
	return os.path.join(name[0:2], name[2:4],name)
def tokenize_url(url):
	return tokenize_name(md5.new(url).hexdigest())
def new_tokenized_name():
	return tokenize_url(str(uuid.uuid4()))
def url_is_local(url):
	return not (isinstance(url, basestring) and url.startswith('http'))

class StaticService(object):
	def __init__(self, sites, secure_sites):
		self.sites = sites.split(";")
		self.sites_length = len(self.sites)
		
		self.secure_sites = secure_sites.split(";")
		self.secure_sites_length = len(self.secure_sites)
		
		self.allowed_product_types = PRODUCT_PIC_FORMATS.copy()
		self.allowed_product_types.update({"TMP":(1,1)})
		
	def get_site_root(self, url, secured = False):
		if secured:
			site_root = self.secure_sites[ord(url[0])%self.secure_sites_length]
			protocol = "https://"
		else:
			site_root = self.sites[ord(url[0])%self.sites_length]
			protocol = "http://"
		
		if not site_root:
			protocol = ''
			site_root = ''
		return "%s%s" %(protocol, site_root)
	
	def get_default_profile_pic_file_name(self, name, type='jpg'):
		return os.extsep.join(['_'.join([name, DEFAULT_PROFILE_KEY]), type])
	
	def get_default_user_picture(self, type, secured = False):
		site_root = self.get_site_root("1", secured)
		return '%(site_root)s/static/imgs/default_user_PROFILE_M.png'%locals()
	def get_user_picture(self, url, type, secured = False, ext="jpg"):
		if type not in PROFILE_PIC_FORMATS:
			raise IncorrectPictureTypeException("UnknownPictureType:%s"%type)
		if not url:
			return self.get_default_user_picture(type, secured)
		elif not isinstance(url, basestring) or url.startswith('http'):
			return url
		else:
			static_root = PROFILE_STATIC_ROOT
			site_root = self.get_site_root(url, secured)
			if url == DEFAULT_USER_PICTURE_TOKEN: 
				return self.get_default_user_picture(type, secured)
			elif url.startswith('/'):
				return '%(site_root)s%(url)s'%locals()
			else:
				return ('%(site_root)s%(static_root)s/%(url)s_%(type)s.%(ext)s'%locals())
	
	def get_default_product_picture(self, type, secured = False):
		site_root = self.get_site_root("2", secured)
		return '%(site_root)s/static/imgs/default_product_FF_POOL.png'%locals()
	def get_product_picture(self, url, type, ext="jpg", secured = False):
		if type not in self.allowed_product_types:
			raise IncorrectPictureTypeException("UnknownPictureType:%s"%type)
		elif not url:
			return self.get_default_product_picture(type, secured)
		elif not isinstance(url, basestring) or url.startswith('http'):
			return url
		else:
			static_root = PRODUCT_STATIC_ROOT
			site_root = self.get_site_root(url, secured)
			if url == DEFAULT_PRODUCT_PICTURE_TOKEN:
				return self.get_default_product_picture(type, secured)
			elif url.startswith('/'):
					return '%(site_root)s%(url)s'%locals()
			else:
				return '%(site_root)s%(static_root)s/%(url)s_%(type)s.%(ext)s'%locals()
	
	def get_pool_picture(self, url, type, ext="png", secured = False):
		if type not in POOL_PIC_FORMATS:
			raise IncorrectPictureTypeException("UnknownPictureType:%s"%type)
		if url.startswith('http'):
			return url
		else:
			static_root = POOL_STATIC_ROOT
			site_root = self.get_site_root(url, secured)
			return '%(site_root)s%(static_root)s/%(url)s_%(type)s.%(ext)s'%locals()
