import md5, uuid, os
from friendfund.lib.notifications.messages import ErrorMessage

from pylons import tmpl_context, session as websession
from pylons.i18n import _
from friendfund.lib.helpers import FriendFundFormEncodeState
from friendfund.model.authuser import User, OtherUserData, TwitterUserHasEmailProc, CreateEmailUserProc, WebLoginUserByEmail, DisconnectAccountProc
from friendfund.model.myprofile import GetMyProfileProc
from friendfund.model.common import SProcWarningMessage
from friendfund.model.forms.user import SignupForm, LoginForm
from friendfund.tasks.celerytasks.photo_renderer import remote_save_image
from friendfund.services import static_service as statics

class UserService(object):
    """
        This is shared between all threads, do not stick state in here!
    """
    def __init__(self, config, dbm, statics_service):
        self.ulpath = config['pylons.paths']['uploads']
        self.statics_service = statics_service
        self.dbm = dbm
        if not os.path.exists(self.ulpath):
            os.makedirs(self.ulpath)


    def login_or_consolidate(self, user_data, remote_task):
        user = tmpl_context.user
        if not bool(user.u_id):
            if not user_data.get('email'):
                if user_data['network'].lower() != 'twitter':
                    raise Exception("NOT_IMPLEMENTED")
                twemailproc = self.dbm.get(TwitterUserHasEmailProc, network_id = user_data['network_id'])
                if not twemailproc.default_email:
                    tmpl_context.user = User(user_data_temp = user_data, name = user_data['name'])
                    tmpl_context.user.set_network(user_data['network'],
                                                  network_id = user_data['network_id'],
                                                  access_token = user_data['access_token']
                    )
                    return (False, None)
                else:
                    user_data['email'] = twemailproc.default_email
            user = self.dbm.get(User
                                ,network = user_data['network']
                                ,network_id = user_data['network_id']
                                ,email = user_data['email']
                                ,locale=websession['lang']
                                ,name = user_data['name'])
            user_data['u_id'] = user.u_id
            user.set_profile_picture_url(user_data['profile_picture_url'])
            remote_task.delay(user_data)
            user.network = user_data['network']
            user.network_id = user_data['network_id']
        else:
            user_data['u_id'] = user.u_id
            suppl_user = OtherUserData(**user_data)
            try:
                additional_user_data = self.dbm.call(suppl_user, User)
                remote_task.delay(user_data)
            except SProcWarningMessage, e:
                user.set_network(user_data['network'])
                return (False, _(u"LOGIN_ACCOUNTS_CANNOT_BE_CONSOLIDATED_WARNING"))
            user.has_activity = False
        user.set_network(user_data['network'],
                         network_id = user_data['network_id'],
                         access_token = user_data['access_token'],
                         access_token_secret = user_data.get('access_token_secret'),
                         screen_name = user_data.get('screen_name')
        )
        tmpl_context.user = user
        return (True, None)

    def signup_email_user(self, values):
        schema = SignupForm()
        form_result = schema.to_python(values, state = FriendFundFormEncodeState)
        user_data = form_result
        user_data['network'] = 'EMAIL'
        user_data['locale']=websession['lang']
        user = self.dbm.call(CreateEmailUserProc(**user_data), User)
        user.set_network('email',
                         network_id =  user.default_email,
                         access_token = None,
                         access_token_secret = None
        )
        user.network = 'email'
        return user

    def login_email_user(self, values):
        schema = LoginForm()
        form_result = schema.to_python(values, state = FriendFundFormEncodeState)
        user_data = form_result
        user_data['network'] = 'email'
        user_data['locale'] = websession['lang']
        user = self.dbm.call(WebLoginUserByEmail(**user_data), User)
        user.set_network('email',
                         network_id = user.default_email,
                         access_token = None,
                         access_token_secret = None
        )
        user.network = 'email'
        return user

    def save_email_user_picture(self, user_data, picture):
        user_data['profile_picture_url'] = statics.new_tokenized_name()
        tmpname, ext = os.path.splitext(picture.filename)
        tmpname = os.path.join(self.ulpath,
                               '%s%s' % (md5.new(str(uuid.uuid4())).hexdigest(), ext))
        outf = open(tmpname, 'wb')
        outf.write(picture.file.read())
        outf.close()
        remote_save_image.delay(user_data['email'], tmpname, user_data['profile_picture_url'])
        return user_data['profile_picture_url']

    def disconnect(self, user, network, network_id, email = None):
        try:
            profile = self.dbm.get(GetMyProfileProc, u_id = user.u_id)
            if not (network in profile.profiles and profile.profiles[network].network_id == network_id):
                tmpl_context.messages.append(ErrorMessage(_("FF_Cannot remove this network, you do not own it!")))
                raise Exception("NOT_CORRECT_USER_TO_DISCONNECT")
            suppl_details = self.dbm.get(DisconnectAccountProc, u_id = user.u_id, network = network, network_id = network_id)
            user.set_network(network)
            user.rem_perm_network(network)
            suppl_details = dict([(k,v) for k,v in suppl_details.to_map().items() if v])
            user.from_map(suppl_details, override = True)
            user.set_network(suppl_details)
        except SProcWarningMessage, e:
            tmpl_context.messages.append(ErrorMessage(_("FF_Cannot remove last network, please connect differently first!")))