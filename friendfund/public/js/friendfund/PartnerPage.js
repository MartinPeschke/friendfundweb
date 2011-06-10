dojo.provide("friendfund.PartnerPage");

dojo.declare("friendfund.PartnerPage", null, {
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.triedSubmitting = false;
		_t.target_form = dojo.isString(_t.target_form) && dojo.byId(_t.target_form) || _t.target_form;
		_t.load_receiver();
	}
	,load_receiver : function(){
		var _t = this;
		_t.selector = new friendfund.CompoundFriendSelector({
								auth_provider : _t.auth_provider
								,container : _t.container
								,ref_node: "inviter"
								,inviter_node : "friend_list"
								,base_url : _t.base_url
								,avail_selectors : {'facebook':true, 'twitter':true, 'email':true}
								,networkSelector : friendfund.FriendTypeAhead
							});
		_t.selector.draw(_t.method);
	}
	,submit : function(url, level, evt){
		var _t = this;
		var complete = _t.checkCompleteness();
		if(!complete||_t.submitting){
			return false;
		} else {
			ff.t.onSubmitCleaner(_t.target_form);
			_t.submitting = true;
			return _t.auth_provider.checkLogin({level:level, success:dojo.hitch(_t, "_submit", url), fail:function(){_t.submitting = false}});
		};
 	}
	,_submit:function(url){
		var _t = this;
		dojo.query("input[type=submit]").attr("disabled","disabled");
		_t.target_form.action = url;
		_t.target_form.onsubmit = function(){};
		_t.target_form.submit();
	},
	
	
	
	
	checkCompleteness : function(){
		var _t = this;
		return _t.check_receiver()&&_t.check_occasion_name();
	},
	check_receiver : function(clean_only){
		if(dojo.query(".invitee_row", "network_invitees").length != 1){
			dojo.query(".errorHook", "receiverSelectorContainer").addClass("error");
			dojo.query(".errorMsgIframe", "selectedReceiverContainer").removeClass("hidden");
			return false;
		} else {
			dojo.query(".errorHook", "receiverSelectorContainer").removeClass("error");
			dojo.query(".errorMsgIframe", "selectedReceiverContainer").addClass("hidden");
			return true;
		}
	},
	check_occasion_name : function(clean_only){
		var oname = dojo.byId("occasion_name");
		var parental = ff.t.findParent(oname, "generalBoxIframe");
		if(!oname.value){
			dojo.query(".errorMsgIframe", parental).removeClass("hidden");
			dojo.query("#yourOccasionSelector,#occasionSelectorContainer").addClass("error");
			return false;
		} else {
			dojo.query(".errorMsgIframe", parental).addClass("hidden");
			dojo.query("#yourOccasionSelector,#occasionSelectorContainer").removeClass("error");
			return true;
		}
	}
});