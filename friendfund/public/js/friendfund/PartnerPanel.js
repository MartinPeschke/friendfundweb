dojo.provide("friendfund.PartnerPanel");

dojo.declare("friendfund.PartnerPanel", null, {
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.connect();
		_t.load_receiver();
	},
	connect : function(){
		var _t = this;
		dojo.connect(dojo.byId("productSelector"), "onchange", dojo.hitch(_t, _t.swapProduct));
		dojo.connect(dojo.byId("occasionSelector"), "onchange", dojo.hitch(_t, _t.swapOccasionName));
		dojo.connect(dojo.byId("occasionTyper"), "onkeyup", dojo.hitch(_t, _t.changeOccasionName));
	},
	changeOccasionName : function(evt){
		if(evt.target.value){
			dojo.byId(dojo.attr(evt.target, "_target")).value = evt.target.value;
			dojo.addClass("selectedOccasion", "filled");
		} else {
			var fake_evt = {target:dojo.byId("occasionSelector")};
			this.swapOccasionName(fake_evt);
		}
	},
	swapOccasionName : function(evt){
		var selected_occasion = evt.target.options[evt.target.selectedIndex];
		dojo.byId(dojo.attr(evt.target, "_target")).value = selected_occasion.value;
		dojo.addClass("selectedOccasion", "filled");
	},
	updateOccasionDate : function(params){
		if(params.date){dojo.byId("occasion_date").value = datePickerController.printFormattedDate(params.date,"Y-ds-m-ds-d",false)}
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
								onSelect : function(ctx, params, elem, evt){
									_t.selector.removeAll(_t.selector);
									ctx.inviteAppendNode(ctx, elem);
									dojo.addClass(_t.invited_node, "filled");
									return true;
								},
								unSelect : function(ctx, target){
									dojo.query('#'+target.id, ctx.invited_node).orphan().forEach(dojo.hitch(null, ctx.uninviteAppendNode, ctx));
									dojo.removeClass(_t.invited_node, "filled");
								}
								
							});
		_t.selector.draw(_t.method);
	}
});