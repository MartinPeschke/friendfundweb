from friendfund.lib.helpers import get_upload_pic_name, get_upload_pic_name_ext, get_user_picture
from friendfund.lib.urlnormalize import normalize as urlnormalize
from friendfund.model.async.ecard_render import ECard, ECardUser, SetPoolECardsProc, GetPoolECardsProc
from friendfund.services.photo_renderer import retrieve_tmp_image
from friendfund.services import config, get_dbm\
		, upload_uimg_folder\
		, upload_pimg_folder\
		, upload_prodimg_folder\
		, upload_tmp\
		, IMAGEMAGICKROOT

BACKGROUND_FORMAT = (960,540)
SINGLE_ENTRY = (320,180)
SINGLE_ENTRY_PIC = (150,150)
SINGLE_ENTRY_MESSAGE = (150,150)

CONNECTION_NAME = 'jobs'


def render_tile(tmp_profile_picture):
	"""
		mogrify 
	"""
	pass


def remote_ecard_render(pool_url):
	dbm = get_dbm(CONNECTION_NAME)
	ecards = dbm.get(GetPoolECardsProc, p_url = pool_url)
	for ecard in ecards:
		for user in ecard:
			profile_pic_url = get_user_picture(user.profile_picture_url, "PROFILE_M", site_root = config['site_root_url'])
			tmp_profile_picture = retrieve_tmp_image(profile_pic_url)
			
		
		
	return 'ack'

remote_ecard_render('UC0xMTI5OQ~~')