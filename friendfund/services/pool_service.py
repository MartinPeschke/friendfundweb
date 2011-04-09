import md5, uuid, os, formencode, logging
log = logging.getLogger(__name__)

from pylons import app_globals, tmpl_context, request, session as websession
from pylons.i18n import _
from friendfund.lib import helpers as h
from friendfund.lib.i18n import friendfund_formencode_gettext
from friendfund.model.forms.pool import PoolCreateForm, PoolPartnerIFrameForm
from friendfund.model.pool import Pool, AddInviteesProc, PoolInvitee, PoolUser, Occasion, JoinPoolProc
from friendfund.model.product import Product, DisplayProduct
from friendfund.tasks.photo_renderer import remote_profile_picture_render, render_product_pictures, save_product_image, remote_product_picture_render, remote_pool_picture_render

class MissingPermissionsException(Exception):pass
class MissingPoolException(Exception):pass
class MissingProductException(Exception):pass
class MissingOccasionException(Exception):pass
class MissingReceiverException(Exception):pass
class MissingAmountException(MissingProductException):pass

class PoolService(object):
	"""
		This is shared between all threads, do not stick state in here!
	"""
	def __init__(self, config):
		self.config = config
		self.ulpath = config['pylons.paths']['uploads']
		if not os.path.exists(self.ulpath):
			os.makedirs(self.ulpath)
	
	def _post_process(self, pool):
		admin = PoolInvitee.fromUser(tmpl_context.user)
		admin.is_admin = True
		pool.participants.append(admin)
		pool.merchant_domain = request.merchant.domain
		app_globals.dbm.set(pool, merge = True, cache=False)
		if pool.product and pool.product.has_picture():
			remote_product_picture_render.apply_async(args=[pool.p_url, pool.product.picture])
		remote_pool_picture_render.apply_async(args=[pool.p_url])
		return pool
	
	def create_free_form(self):
		tmpl_context._ = friendfund_formencode_gettext
		tmpl_context.request = request
		pool_map = formencode.variabledecode.variable_decode(request.params)
		pool_schema = PoolCreateForm().to_python(pool_map, state = tmpl_context)
		
		pool = Pool(title = pool_schema['title'],
				description = pool_schema['description'],
				currency = pool_schema['currency'],
				settlementOption = pool_schema['settlementOption']
			)
		
		so = request.merchant.map[pool.settlementOption]
		so_values = pool_map.get(pool.settlementOption)
		for rf in so.required_fields:
			if rf.persistence_attribute:
				setattr(pool, rf.persistence_attribute, so_values.get(rf.name))
			else:
				log.error("POOLCREATE, REQUIRED FIELD has no PERSISTENCE_ATTRIBUTE")
		
		amount = pool_schema.pop("amount")
		if so_values and 'charge_through' in so_values:
			amount = (1+so.fee)*amount
		pool.set_amount_float(amount)
		pool.occasion = Occasion(key="EVENT_OTHER", date=pool_schema['date'])
		
		if h.contains_one_ne(pool_schema, ["tracking_link", "product_picture"]):
			pool.product = Product(name = pool_schema.get("product_name"), 
									description = pool_schema.get("product_description"),
									tracking_link = pool_schema.get("tracking_link"),
									picture = pool_schema.get("product_picture") )
		else:
			pool.product = Product(picture = h.get_default_product_picture_token())
		
		
		receiver = PoolInvitee.fromUser(tmpl_context.user)
		receiver.is_receiver = True
		pool.participants.append(receiver)
		return self._post_process(pool)
	
	def create_group_gift_from_iframe(self, product, receiver):
		tmpl_context._ = friendfund_formencode_gettext
		tmpl_context.request = request
		pool_map = formencode.variabledecode.variable_decode(request.params)
		pool_schema = PoolPartnerIFrameForm().to_python(pool_map, state = tmpl_context)
		pool = Pool(settlementOption = request.merchant.settlement_options[0].name)
		pool.set_product(product)
		pool.occasion = Occasion(key=pool_schema['occasion_key'], date=pool_schema['date'], name = pool_schema['occasion_name'])
		
		receiver.is_receiver = True
		pool.participants.append(receiver)
		return self._post_process(pool)
	
	def create_group_gift(self):
		pool = websession.get('pool')
		if pool is None:
			raise MissingPoolException()
		elif pool.product is None:
			raise MissingProductException()
		elif pool.occasion is None:
			raise MissingOccasionException()
		elif pool.receiver is None:
			raise MissingReceiverException()
		#### Setting up the Pool for initial Persisting
		pool.participants.append(admin)
		locals = {"admin_name":admin.name, "receiver_name" : pool.receiver.name, "occasion_name":pool.occasion.get_display_name()}
		pool.description = (_("INVITE_PAGE_DEFAULT_MSG_%(admin_name)s has created a Friend Fund for %(receiver_name)s's %(occasion_name)s. Come and chip in!")%locals)
		remote_profile_picture_render.delay([(pu.network, pu.network_id, pu.large_profile_picture_url or pu.profile_picture_url) for pu in pool.participants])
		pool.settlementOption = request.merchant.settlement_options[0].name
		return self._post_process(pool)
	
	
	
	def invite_myself(self, pool_url, user):
		app_globals.dbm.get(JoinPoolProc, u_id = user.u_id, p_url = pool_url)
		app_globals.dbm.expire(Pool(p_url = pool_url))

	def save_pool_picture(self, picture):
		picture_url = h.get_upload_pic_name(str(uuid.uuid4()))
		tmpname, ext = os.path.splitext(picture.filename)
		tmpname = os.path.join(self.ulpath \
			, '%s%s' % (md5.new(str(uuid.uuid4())).hexdigest(), ext))
		outf = open(tmpname, 'wb')
		outf.write(picture.file.read())
		outf.close()
		newurl = render_product_pictures(picture_url, tmpname)
		return picture_url
	
	def save_pool_picture_sync(self, picture, type):
		picture_url = h.get_upload_pic_name(str(uuid.uuid4()))
		tmpname, ext = os.path.splitext(picture.filename)
		tmpname = os.path.join(self.ulpath \
			, '%s%s' % (md5.new(str(uuid.uuid4())).hexdigest(), ext))
		outf = open(tmpname, 'wb')
		outf.write(picture.file.read())
		outf.close()
		newurl = save_product_image(picture_url, tmpname, type)
		return newurl