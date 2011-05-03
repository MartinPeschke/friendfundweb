dojo.provide("friendfund.PartnerPanel");

dojo.declare("friendfund.PartnerPanel", null, {
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.triedSubmitting = false;
		_t.target_form = dojo.isString(_t.target_form) && dojo.byId(_t.target_form) || _t.target_form;
		_t.connect();
		_t.load_receiver();
	},
	connect : function(){
		var _t = this;
		if(dojo.byId("productSelector")){dojo.connect(dojo.byId("productSelector"), "onchange", dojo.hitch(_t, _t.swapProduct));}
		if(dojo.byId("occasionSelector")){dojo.connect(dojo.byId("occasionSelector"), "onchange", dojo.hitch(_t, _t.swapOccasionName));}
		dojo.connect(dojo.byId("occasionTyper"), "onkeyup", dojo.hitch(_t, _t.changeOccasionName));
	},
	changeOccasionName : function(evt){
		var _t = this;
		if(evt.target.value){
			dojo.byId(dojo.attr(evt.target, "_target")).value = evt.target.value;
		} else {
			var fake_evt = {target:dojo.byId("occasionSelector")};
			this.swapOccasionName(fake_evt);
		}
		_t.check_occasion_name();
	},
	swapOccasionName : function(evt){
		var _t = this;
		var selected_occasion = evt.target.options[evt.target.selectedIndex];
		dojo.byId(dojo.attr(evt.target, "_name_target")).value = selected_occasion.value;
		dojo.byId(dojo.attr(evt.target, "_key_target")).value = dojo.attr(selected_occasion, "key");
		_t.check_occasion_name();
	},
	swapProduct : function(evt){
		var selected_product = evt.target.options[evt.target.selectedIndex];
		dojo.query(".selectedProduct", "productArea").removeClass("selectedProduct").addClass("hidden");
		dojo.query("#product_"+dojo.attr(selected_product, "_guid")).addClass("selectedProduct").removeClass("hidden");
	},
	load_receiver : function(){
		var _t = this;
		_t.selector = new friendfund.CompoundFriendSelector({
								container : _t.container,
								ref_node: "inviter",
								invited_node_suffix : "_invitees",
								inviter_node : "friend_list",
								base_url : _t.base_url ,
								mutuals : _t.mutuals,
								global_invited_node : _t.invited_node,
								avail_selectors : {'facebook':true, 'twitter':true, 'email':true},
								onSelect : function(ctx, elem, evt){
									_t.selector.removeAll(_t.selector);
									ctx.inviteAppendNode(ctx, elem);
									dojo.addClass(_t.invited_node, "filled");
									_t.check_receiver();
									return true;
								},
								unSelect : function(ctx, target){
									dojo.query('#'+target.id, ctx.invited_node).orphan().forEach(dojo.hitch(null, ctx.uninviteAppendNode, ctx));
									dojo.removeClass(_t.invited_node, "filled");
								}
								
							});
		_t.selector.draw(_t.method);
	},
	submit : function(url, level, evt){
		var _t = this;
		onSubmitCleaner(_t.target_form); 
		if(_t.submitting){return false;}
		_t.submitting = true;
		return doLogin({level:level, cb:dojo.hitch(null, _t._submit, _t, url), failcb:function(){_t.submitting = false}});
 	},_submit:function(url){
		var _t = this;
		dojo.query("input[type=submit]").attr("disabled","disabled");
		_t.target_form.action = url;
		_t.target_form.onsubmit = function(){};
		_t.target_form.submit();
	},
	
	
	
	
	checkCompleteness : function(){
		var _t = this;
		var a = _t.check_receiver(), b = _t.check_occasion_name();
		return a&&b&&c;
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
		var parental = findParent(oname, "generalBoxIframe");
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