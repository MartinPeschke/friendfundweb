from datetime import date
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping
_ = lambda x:x
ALLBADGES = 	[   
					 ('BADGE_BEST_FRIEND'	,True,True	,'BEST_FRIEND'	
						,_(u'BADGE_DESCRIPTION_You\'ve been awarded the Best Friend Badge for creating a pool for your friend. They\'ll surely love you.'))
					,('BADGE_BIG_SPENDER'	,False,False,'BIG_SPENDER'	,
						_(u'BADGE_DESCRIPTION_You\'ve been awarded the Big Spender Badge for chipping in more than &euro;50.00 to one pool.'))
					,('BADGE_PHILANTHROPIST',False,True	,'PHILANTHROPIST',
						_(u'BADGE_DESCRIPTION_You have a heart of gold. You\'ve been awarded the Philanthropist Badge for chipping in to two or more pools.'))
					,('BADGE_FANATIC'		,False,False,'FANATIC'		,
						_(u'BADGE_DESCRIPTION_Nice one! You\'ve been awarded the Fanatic Badge for chipping in to the same pool two times or more.'))
					,('BADGE_TEAM_PLAYER'	,False,False,'TEAM_PLAYER'	,
						_(u'BADGE_DESCRIPTION_You\'ve been awarded the Team Player Badge for sending out two or more invites. There\'s no "I" in "Team"!'))
					,('BADGE_ACTIVIST'		,True,True	,'ACTIVIST'		,
						_(u'BADGE_DESCRIPTION_You\'ve been awarded the Activist Badge for inviting 20 or more people to one pool. Go you.'))
					,('BADGE_PATRON'		,False,False,'PATRON'		,
						_(u'BADGE_DESCRIPTION_High five! You\'ve been awarded the Patron Badge for contributing &euro;100.00 or more to the same pool.'))
					,('BADGE_SOUL_MATE'		,False,False,'SOUL_MATE'	,
						_(u'BADGE_DESCRIPTION_You\'ve been awarded the Soul Mate Badge for creating two pools for the same person. Awww.'))
					,('BADGE_DREAMER'		,True,True,  'DREAMER'		,
						_(u'BADGE_DESCRIPTION_You\'ve been awarded the Dreamer Badge for requesting one gift for yourself. Because you\'re worth it!'))
					,('BADGE_CONNOISSEUR'	,False,True, 'CONNOISSEUR'	,
						_(u'BADGE_DESCRIPTION_Hmmm, impressive! You\'ve been awarded the Connoisseur Badge for requesting a gift of &euro;100.00 and over.'))
					,('BADGE_DIVA'			,False,False,'DIVA'			,
						_(u'BADGE_DESCRIPTION_You\'ve been awarded the Diva Badge for requesting 3 or more gifts for yourself. You\'re fabulous!'))
					,('BADGE_MYSTERY'		,False,False,'MYSTERY'		,
						_(u'BADGE_DESCRIPTION_MYSTERY_...'))
					,('BADGE_BADGE1'		,False,False,'BADGE1'		,'')
					,('BADGE_BADGE2'		,False,False,'BADGE2'		,'')
					,('BADGE_BADGE3'		,False,False,'BADGE3'		,'')]
ALLBADGES_DICT = dict([(k,{'has_outline':v, 'has_badge':u, 'description':w, "badge_url":x}) for k,v,u,x,w in ALLBADGES ])

from pylons.i18n import _

class Badge(DBMappedObject):
	_set_root = _get_root = 'BADGE'
	_unique_keys = ['name']
	_keys = [ GenericAttrib(str,'name','name')
			, GenericAttrib(str,'badge_url','badge_url')
			, GenericAttrib(date,'award_date','award_date')
			, GenericAttrib(unicode,'profile_picture_url','profile_picture_url')
			, GenericAttrib(unicode, 'friend_name', 'friend_name') 
			]
	def get_display_description(self):
		return _(ALLBADGES_DICT.get(self.name).get("description"))
	
	def get_display_name(self):
		return _(self.name)
	display_name = property(get_display_name)
	def get_badge_picture(self, type="small"):
		return h.get_badge_picture(self.badge_url, type)
	def get_profile_pic(self, type="RA"):
		return h.get_user_picture(self.profile_picture_url, type)

class GetMyBadgesProc(DBMappedObject):
	"""
		exec [app].[get_my_badges] '<MY_BADGES u_id="4514"/>'
	"""
	_set_root = 'MY_BADGES'
	_get_root = None
	_set_proc = _get_proc = "app.get_my_badges"
	_unique_keys = ['u_id', 'badges']
	_keys = [	GenericAttrib(int,'u_id','u_id'),
				DBMapper(Badge, 'badges', 'BADGE', is_list = True)
			]
	def fromDB(self, xml):
		last_badge = len(self.badges) and self.badges[0]
		if last_badge:
			details = ALLBADGES_DICT.get(last_badge.name, {})
			setattr(last_badge, "details", details)
		setattr(self, "last_awarded", last_badge)
		self.badge_map = dict((k.name, k) for k in self.badges)
	all_badges = ALLBADGES

class UserFriend(DBMappedObject):
	_cachable = False
	_unique_keys = ['network', 'network_id']
	_set_proc = _get_proc = None
	_set_root = _get_root = "USER_FRIEND"
	_keys = [	 GenericAttrib(str, 'network', 'network'), GenericAttrib(str, 'network_id', 'id') ]

class GetFriendsBadgesProc(DBMappedObject):
	"""
		 [app].[get_friend_badges] '<USER u_id ="12"> 
		<USERFRIEND network = "FACEBOOK" id="14500754" /> 
		<USERFRIEND network = "FACEBOOK" id="14500754" /> 
		<USERFRIEND network = "FACEBOOK" id="14500754" /> 
		<USERFRIEND network = "FACEBOOK" id="14500754" /> 
		</USER>' 
	"""
	_cachable = False
	_unique_keys = ['u_id']
	_get_proc = _set_proc = "app.get_friend_badges"
	_set_root = "USER"
	_get_root = None
	_keys = [	 GenericAttrib(int, 'u_id', 'u_id')
				,DBMapper(UserFriend, 'friends', 'USER_FRIEND', is_list = True)
				,DBMapper(Badge, 'badges', 'BADGE', is_list = True)
			]