import logging, Image, os, urllib2, StringIO, uuid, md5, subprocess, urlparse, cgi, re, time
from collections import deque
from celery.decorators import task

from friendfund.lib import helpers as h
from friendfund.lib.urlnormalize import normalize as urlnormalize
from friendfund.model import db_access
from friendfund.model.async.profile_picture_render import AddRenderedProfilePictureProc
from friendfund.model.async.product_picture_render import AddRenderedProductPictureProc
from friendfund.model.async.pool_picture_render import PoolPictureUsersProc, AddRenderedPoolPictureProc
from friendfund.tasks import config, get_dbm\
		, upload_uimg_folder\
		, upload_pimg_folder\
		, upload_prodimg_folder\
		, upload_tmp\
		, IMAGEMAGICKROOT

CONNECTION_NAME = 'jobs'
from celery.log import setup_logger
log = setup_logger(loglevel=0)



PROFILE_PIC_FORMATS = [('RA', (120,120))
					,('POOL', (140,140))
					,('PROFILE_S', (50,50))
					,('PROFILE_M', (75,75))
					,('MYPROFILE', (90,90))
					,('RESULT', (205,205))]

PRODUCT_PIC_FORMATS = [('RA', (161,120)), ('POOL', (140,140)), ('MYPOOLS', (153,114))]
POOL_PIC_FORMATS = [('RA', (161,120), (4, 12)), ('MYPOOLS', (120,79), (3, 6))]

class UnexpectedFileNameFormat(Exception):
	pass

def try_locate_sub_image_url(url):
	"""
		Tries to guess a sub URL for the source image for e.g. Swarovski
		http://dynpng.nonstoppartner.net/resize/
				?height=70
				&image=http%3A%2F%2Fwww.swarovski.com%2Fis-bin%2Fintershop.static%2FWFS%2FSCO-Media-Site%2F-%2F-%2Fpublicimages%2FCG%2FB2C%2FPROD%2F240%2F10001W240.jpg
				&width=70
		
		via filter_picture_urls( get_first_elem_from_list( parse_qs( urlparse ) ) )
	"""
		
	pic_ext_matcher = re.compile('.*(\.jpg|\.png|\.gif|\.tga|\.bmp|\.jpeg).*')
	potential_subimages = filter(lambda x:'http' in x and pic_ext_matcher.match(x), 
						map(lambda x: isinstance(x, list) and len(x) and x[0] or x, cgi.parse_qs(urlparse.urlparse(url)[4]).values()))
	if potential_subimages:
		return potential_subimages[0]
	else:
		return None

def retrieve_tmp_image(source_url, try_locate_sub_url = False):
	alt_url = try_locate_sub_image_url(source_url)
	source = try_locate_sub_url and alt_url or source_url
	try:
		resp = urllib2.urlopen(urlnormalize(source))
	except urllib2.HTTPError, e:
		log.error("Could not load Picture fom this URL: %s" % source)
		return None
	try:
		extension = resp.url.rsplit('.',1)[1]
		if not (2<len(extension)<5):
			extension = None
	except IndexError, e:
		log.warning(UnexpectedFileNameFormat("Could not Find a suitable File Name Extension in URL: %s" % resp.url))
		extension = None
	tmpfname = os.path.join(upload_tmp, os.extsep.join(filter(None, [str(uuid.uuid4()), extension])))
	tmpf = open(tmpfname, 'wb')
	tmpf.write(resp.read())
	tmpf.close()
	return tmpfname

def crop_resize_original(sizes, fit_full_image = False, gravity = "Center"):
	if fit_full_image:
		resize_parameter = '%sx%s'
	else:
		resize_parameter = '%sx%s^'
		procs = deque()
	for fname_src, fname_dest, target_w, target_h in sizes:
		crop_command = []
		crop_command.extend([os.path.join(IMAGEMAGICKROOT, 'convert'), str(fname_src),\
							'-resize',resize_parameter % (target_w, target_h),\
							'-gravity', gravity, '-filter','Lanczos',\
							'-background', 'white', '-extent', '%sx%s' % (target_w, target_h), \
							str(fname_dest)])
		procs.append(subprocess.Popen(crop_command, shell = False, stdout = None, stderr = subprocess.STDOUT))
	for p in procs:
		p.wait()
	return 1

@task
def remote_save_image(email, tmpfname, newfname):
	dbm = get_dbm(CONNECTION_NAME)
	newurl = newfname  # '/23/a1/23a1a-wefkj-hqwfok-jqwfr'
	filepath, filename = os.path.split(newfname)
	newpath = os.path.join(upload_uimg_folder, filepath)
	if not os.path.exists(newpath):
		os.makedirs(newpath)
	try:
		sizes = deque()
		for name_ext, (target_w,target_h) in PROFILE_PIC_FORMATS:
			newfname = os.extsep.join(['_'.join([filename, name_ext]), 'jpg'])
			newfname = os.path.join(newpath, newfname)
			sizes.append((tmpfname, newfname, target_w,target_h))
		crop_resize_original(sizes)
		try:
			dbm.set(AddRenderedProfilePictureProc(network = 'EMAIL', email = email, profile_picture_url=newurl))
		except db_access.SProcException, e:
			log.error(str(e))
		return 'ack'
	finally:
		os.unlink(tmpfname)

@task
def remote_product_picture_render(pool_url, picture_url):
	dbm = get_dbm(CONNECTION_NAME)
	newfname = h.get_upload_pic_name(str(uuid.uuid4()))
	newurl = newfname  # '23/a1/23a1a-wefkj-hqwfok-jqwfr'
	filepath, filename = os.path.split(newfname)
	newpath = os.path.join(upload_prodimg_folder, filepath)
	if not os.path.exists(newpath):
		os.makedirs(newpath)
	tmpfname = retrieve_tmp_image(picture_url, try_locate_sub_url = True)
	if tmpfname:
		try:
			sizes = deque()
			for name_ext, (target_w,target_h) in PRODUCT_PIC_FORMATS:
				newfname = os.extsep.join(['_'.join([filename, name_ext]), 'jpg'])
				newfname = os.path.join(newpath, newfname)
				sizes.append((tmpfname, newfname, target_w,target_h))
			crop_resize_original(sizes)
			try:
				dbm.set(AddRenderedProductPictureProc(p_url = pool_url, product_picture_url=newurl))
			except db_access.SProcException, e:
				log.error(str(e))
		finally:
			os.unlink(tmpfname)
	return newurl
	
	
@task
def remote_profile_picture_render(userlist):
	start = time.time()
	dbm = get_dbm(CONNECTION_NAME)
	dltime = 0
	rendertime = 0
	for network, network_id, picture_url in userlist:
		if not network_id:
			log.error("RECEIVED NO NETWORK_ID (%s,%s,%s)", network, network_id, picture_url)
			continue
		if h.url_is_local(picture_url):
			log.warning("Tried rendering local picture %s:%s:%s" % (network, network_id, picture_url))
		else:
			newfname = h.get_upload_pic_name(md5.new(picture_url).hexdigest())
			newurl = newfname  # '/23/a1/23a1a-wefkj-hqwfok-jqwfr'
			filepath, filename = os.path.split(newfname)
			newpath = os.path.join(upload_uimg_folder, filepath)
			
			# overload preventer, but cant be used now, as add pool invitees overwrites picture urls with remote
			try:
				name_ext = PROFILE_PIC_FORMATS[0][0]
				newfname = os.extsep.join(['_'.join([filename, name_ext]), 'jpg'])
				newfname = os.path.join(newpath, newfname)
				if ((time.time() - os.stat(newfname).st_ctime)/3600) < 24:
					log.info("aborting rendering of %s, it was rendered within last 24hrs", newfname)
					return 'ack'
			except OSError, e: pass
			
			if not os.path.exists(newpath):
				os.makedirs(newpath)
			dltime = time.time()
			tmpfname = retrieve_tmp_image(picture_url)
			dltime = time.time() - dltime
			if tmpfname:
				try:
					sizes = deque()
					for name_ext, (target_w,target_h) in PROFILE_PIC_FORMATS:
						newfname = os.extsep.join(['_'.join([filename, name_ext]), 'jpg'])
						newfname = os.path.join(newpath, newfname)
						sizes.append((tmpfname, newfname, target_w,target_h))
					rendertime = time.time()
					crop_resize_original(sizes, gravity = 'North')
					rendertime = time.time() - rendertime
					try:
						dbm.set(AddRenderedProfilePictureProc(network = network, network_id = network_id, profile_picture_url=newurl))
					except db_access.SProcException, e:
						log.error(str(e))
				finally:
					os.unlink(tmpfname)
	return 'ack[ttl:%.4fs, dl:%.4fs, rdr: %.4fs]' % (time.time() - start, dltime, rendertime)

@task
def remote_pool_picture_render(pool_url):
	dbm = get_dbm(CONNECTION_NAME)
	newfname = h.get_upload_pic_name(md5.new(pool_url).hexdigest())
	newurl = newfname
	basepath,fname = os.path.split(newfname)
	newfpath = os.path.join(upload_pimg_folder, basepath)
	if not os.path.exists(newfpath):
		os.makedirs(newfpath)
	try:
		pool_users = dbm.get(PoolPictureUsersProc, p_url = pool_url)
	except db_access.SProcException, e:
		log.error(str(e))
	else:
		ppic = {}
		for name, (target_w, target_h), (panels_w, panels_no) in POOL_PIC_FORMATS:
			ppic[name] = {'image':Image.new("RGBA", (target_w, target_h), (255,255,255,0))\
						,'target_w':target_w\
						,'target_h':target_h\
						,'panels_w'  :panels_w\
						,'panels_no' :panels_no}
		
		for i, user in enumerate(pool_users.users):
			profile_pic_url = h.get_user_picture(user.profile_picture_url, "PROFILE_S", site_root = config['site_root_url'])
			try:
				tmpfile = StringIO.StringIO(urllib2.urlopen(profile_pic_url).read())
			except urllib2.HTTPError, e:
				log.error("ERROR in pool picture Render, Pic Download Broke, %s, %s", profile_pic_url, str(e))
				continue
			tmp = Image.open(tmpfile)
			width,height = tmp.size
			shrinkfac = (width >= height) and float(38)/width or float(38)/height
			width, height = int(width*shrinkfac), int(height*shrinkfac)
			tmp = tmp.resize( (width, height), Image.ANTIALIAS )
			tmp = tmp.crop((0,0,38,38))
			for name, pic in ppic.iteritems():
				if pic['panels_no'] > i:
					pic['image'].paste(tmp, ((i%pic['panels_w'])*41, (i/pic['panels_w'])*41))
		for name, (target_w, target_h), (panels_w, no_panels) in POOL_PIC_FORMATS:
			newfname = os.extsep.join([('%s_%s' % (fname, name)), 'png'])
			ppic[name]['image'].save(os.path.join(newfpath, newfname))
			del ppic[name]
		dbm.set(AddRenderedPoolPictureProc(p_url = pool_url, pool_picture_url = newurl))
	return 'ack'