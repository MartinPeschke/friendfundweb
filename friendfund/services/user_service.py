import md5, uuid, osfrom pylons import app_globals, tmpl_context, session as websessionfrom pylons.i18n import _from friendfund.lib.helpers import get_upload_pic_name, FriendFundFormEncodeStatefrom friendfund.model.authuser import User, ANONUSER, OtherUserData, TwitterUserHasEmailProc, SetUserLocaleProc, CreateEmailUserProcfrom friendfund.model.common import SProcWarningMessagefrom friendfund.model.forms.user import SignupFormfrom friendfund.tasks.photo_renderer import remote_save_imageclass UserService(object):	"""		This is shared between all threads, do not stick state in here!	"""	def __init__(self, config):		self.ulpath = config['pylons.paths']['uploads']		if not os.path.exists(self.ulpath):			os.makedirs(self.ulpath)			def login_or_consolidate(self, user_data, remote_task):		user = tmpl_context.user		if not bool(user.u_id):			if not user_data.get('email'):				if user_data['network'].lower() != 'twitter':					raise Exception("NOT_IMPLEMENTED")				twemailproc = app_globals.dbm.get(TwitterUserHasEmailProc, network_id = user_data['network_id'])				if not twemailproc.default_email:					tmpl_context.user = User(user_data_temp = user_data, name = user_data['name'])					tmpl_context.user.set_network(user_data['network'], 							network_id = user_data['network_id'],							access_token = user_data['access_token'],							access_token_secret = user_data['access_token_secret']						)					return (False, None)				else:					user_data['email'] = twemailproc.default_email			user = app_globals.dbm.get(User						,network = user_data['network']						,network_id = user_data['network_id']						,email = user_data['email']						,name = user_data['name'])			user.network = user_data['network']			user.network_id = user_data['network_id']			user_data['u_id'] = user.u_id			user.profile_picture_url = user.profile_picture_url or user_data['profile_picture_url']			remote_task.delay(user_data)						app_globals.dbm.set(SetUserLocaleProc(locale=websession['lang'], u_id=user.u_id))		else:			user_data['u_id'] = user.u_id			suppl_user = OtherUserData(**user_data)			try:				additional_user_data = app_globals.dbm.call(suppl_user, User)				user.pools = additional_user_data.pools				remote_task.delay(user_data)			except SProcWarningMessage, e:				user.set_network(user_data['network'])				return (False, _(u"LOGIN_ACCOUNTS_CANNOT_BE_CONSOLIDATED_WARNING"))		user.set_network(user_data['network'], 							network_id = user_data['network_id'],							access_token = user_data['access_token'],							access_token_secret = user_data['access_token_secret']						)		if 'email' in user_data:			user.set_perm(user_data['network'], 'has_email', True)			user.set_perm(user_data['network'], 'email', user_data['email'])			user.default_email = user_data['email']		tmpl_context.user = user		return (True, None)		def signup_email_user(self, values):		schema = SignupForm()		form_result = schema.to_python(values, state = FriendFundFormEncodeState)		usermap = form_result		usermap['network'] = 'EMAIL'		user = app_globals.dbm.call(CreateEmailUserProc(**usermap), User)		user.set_network('email', 						network_id =  user.default_email,						access_token = None,						access_token_secret = None					)		user.network = 'email'		app_globals.dbm.set(SetUserLocaleProc(locale=websession['lang'], u_id=user.u_id))		return user				def save_email_user_picture(self, user_data, picture):		user_data['profile_picture_url'] = get_upload_pic_name(str(uuid.uuid4()))		tmpname, ext = os.path.splitext(picture.filename)		tmpname = os.path.join(self.ulpath \			, '%s%s' % (md5.new(str(uuid.uuid4())).hexdigest(), ext))		outf = open(tmpname, 'wb')		outf.write(picture.file.read())		outf.close()		remote_save_image.delay(user_data['email'], tmpname, user_data['profile_picture_url'])