if(!dojo._hasResource["friendfund.PartnerPage"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["friendfund.PartnerPage"] = true;
dojo.provide("friendfund.PartnerPage");

dojo.declare("friendfund.PartnerPage", null, {
	connect : function(){
		dojo.connect(dojo.byId("occasionSelector"), "onchange", this, "swapOccasionName");
		dojo.connect(dojo.byId("occasionTyper"), "onkeyup", this, "changeOccasionName");
	},
	changeOccasionName : function(evt){
		if(evt.target.value){
			dojo.byId(dojo.attr(evt.target, "_target")).value = evt.target.value;
		} else {
			var fake_evt = {target:dojo.byId("occasionSelector")};
			this.swapOccasionName(fake_evt);
		}
		this.check_occasion_name();
	},
	swapOccasionName : function(evt){
		var selected_occasion = evt.target.options[evt.target.selectedIndex];
		dojo.byId(dojo.attr(evt.target, "_name_target")).value = selected_occasion.value;
		dojo.byId(dojo.attr(evt.target, "_key_target")).value = dojo.attr(selected_occasion, "key");
		this.check_occasion_name();
	},

	constructor: function(args){
		dojo.mixin(this, args);
		this.triedSubmitting = false;
		this.target_form = dojo.isString(this.target_form) && dojo.byId(this.target_form) || this.target_form;
		this.load_receiver();
		this.connect();
		dojo.byId("selectedReceiver").value = "";
	}
	,load_receiver : function(){
		this.selector = new friendfund.CompoundFriendSelector({
								auth_provider : this.auth_provider
								,container : this.container
								,ref_node: "inviter"
								,inviter_node : "friend_list"
								,base_url : this.base_url
								,avail_selectors : {'facebook':true, 'twitter':true, 'email':true}
								,networkSelector : friendfund.FriendTypeAhead
								,emailSelector : friendfund.EmailInPlaceSelector
							});
		this.selector.draw(this.method);
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

}
