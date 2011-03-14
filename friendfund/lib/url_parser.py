import urlparse
from itertools import imap, ifilter
from BeautifulSoup import BeautifulSoup
from ordereddict import OrderedDict

def absolutize_img_src(rel_base, abs_base):
	def inner(url):
		if url.startswith('http'):
			return url
		elif url.startswith('/'):
			return '%s%s' % (abs_base, url)
		elif not url.startswith('.'):
			return '%s/%s' % (abs_base, url)
		else:
			return '%s%s' % (rel_base, url)
	return inner

def filter_pictures(img_src):
	return isinstance(img_src, basestring) and img_src[-4:].lower() in ('.jpg','.png','.gif')

def extract_imgs_from_soup(img):
	attr_map = dict(img.attrs)
	width_filter = ('width' not in attr_map) or (int(filter(lambda x: x.isdigit(), attr_map['width']))>49)
	height_filter = ('height' not in attr_map) or (int(filter(lambda x: x.isdigit(), attr_map['height']))>49)
	return width_filter and height_filter and img.get('src') or None

def get_title_descr_imgs(query, product_page):
	content_type = product_page.headers.get("Content-Type")
	
	if content_type and 'image' in content_type.lower():
		return None, None, [query]
	if not content_type or 'html' in content_type.lower():
		soup = BeautifulSoup(product_page.read())
		params = dict((t.get('name').lower(), t.get('content')) for t in soup.findAll('meta') if t.get('name'))
		descr = params.get("description", params.get("og:description"))
		if not descr:
			descr = soup.find('h1') or soup.find('h2') or soup.find('h3') or soup.find('h4')
			if descr:
				descr = descr.text
			else: 
				descr = None
		name = soup.find('title')
		name = name and name.text or params.get("og:title")
		if not (name or descr):
			return None, None, None
		else:
			if params.get("og:image"):
				img_collection = [params.get("og:image")]
			else:
				img_rels = soup.findAll('link')
				def_images = filter(lambda x: x.get('rel') == "image_src", img_rels)
				if def_images:
					img_collection = filter(bool, map(lambda x: x.get('href'),  def_images))
				else:
					scheme, domain, path, query_str, fragment = urlparse.urlsplit(query)
					abs_base = urlparse.urlunparse((scheme, domain, '','','',''))
					rel_base = urlparse.urlunparse((scheme, domain,'%s/' % path.rsplit('/', 1)[0],'','',''))
					img_collection = list(imap(absolutize_img_src(rel_base, abs_base), ifilter(filter_pictures, imap(extract_imgs_from_soup, soup.findAll("img")))))
					#### remove duplicates
					imgs = OrderedDict((a, True) for a in img_collection)
					img_collection = imgs.keys()
			return name, descr, img_collection