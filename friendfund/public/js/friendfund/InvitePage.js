dojo.provide("friendfund.InvitePage");

dojo.declare("friendfund.InvitePage", null, {
	selector : null,
	_listener_locals : [],
	_widget_locals: [],
	submitting : false,
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.selector = new friendfund.CompoundFriendSelector({
								container : "lowerbody_container",
								ref_node: "inviter",
								invited_node_suffix : "_invitees",
								inviter_node : "friend_list",
								base_url : _t.base_url ,
								mutuals : true,
								global_invited_node : _t.invited_node,
								avail_selectors : {'facebook':true, 'twitter':true, 'email':true}
							});
		_t._widget_locals.push(_t.selector);
		dojo.connect(dojo.byId("invite_submitter"), "onclick", dojo.hitch(null, _t.prepareSubmit, _t));
		_t.selector.draw(_t.method);
	},
	prepareSubmit : function(_t, evt){
		if(_t.submitting){return false;}
		_t.submitting = true;
		var results = dojo.query("div.invitee_row", _t.invited_node);
		
		if(results.length && (!dojo.byId("PendingSelectorSelector") || !dojo.hasClass("PendingNominator", "hidden"))){
			dojo.forEach(_t._widget_locals, function(item){item.destroy(item);});
			_t._widget_locals = [];
			_t.receiver_selectors = {};
			var invitees = [];
			dojo.query("div.invitee_row.selectable", _t.invited_node).forEach(
				function(elem, i){
					var params = {};
					dojo.forEach(dojo.attr(elem, "_search_keys").split(","), 
								function(key){params[key.substring(1)]=dojo.attr(elem, key);}
							);
					invitees.push(params);
				});
			invitees = {"invitees":invitees};
			dojo.place(dojo.create("textarea", {name:"invitees", style:"display:none",value:dojo.toJson(invitees)}), dojo.byId('invitees'), "last");
			dojo.byId('invitees').submit();
		} else if(!results.length){
			_t.submitting = false;
			var node = dojo.byId("inviters_panel_tooltip");
			dojo.removeClass(node, "hidden");
			dojo.style(node, "opacity", "1");
			dojo.fadeOut({node:node ,duration: 5000}).play();
			return false;
		} else {
			_t.submitting = false;
			var node = dojo.byId("inviters_selector_tooltip");
			dojo.removeClass(node, "hidden");
			dojo.style(node, "opacity", "1");
			dojo.fadeOut({node:node ,duration: 5000}).play();
			return false;
		}
 	}
});











