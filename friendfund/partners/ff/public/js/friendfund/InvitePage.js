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
								container : _t.container,
								ref_node: "inviter",
								invited_node_suffix : "_invitees",
								inviter_node : "friend_list",
								base_url : _t.base_url ,
								mutuals : _t.mutuals,
								global_invited_node : _t.invited_node,
								avail_selectors : {'facebook':true, 'twitter':true, 'email':true}
							});
		_t._widget_locals.push(_t.selector);
		dojo.connect(dojo.byId("invite_submitter"), "onclick", dojo.hitch(null, _t.prepareSubmit, _t));
		dojo.connect(document, "onclick", dojo.hitch(null, _t.loadPreviewPopup, _t, _t.method));
		_t.selector.draw(_t.method);
	},
	loadPreviewPopup : function(_t, method, evt){
		if(dojo.hasClass(evt.target, "message_preview")){
			params = dojo.formToObject("invitees");
			params.method = dojo.attr(evt.target, "_method");
			xhrPost(dojo.attr(evt.target, "_href"), params);
		}
	}, 
	get_invitee_json : function(_t, method){
		var invitees = [], submittingNodes;
		if(method){
			submittingNodes = dojo.query(".invitee_row.selectable.network_"+method, _t.invited_node);
		} else {
			submittingNodes = dojo.query(".invitee_row.selectable", _t.invited_node);
		}
		dojo.forEach(submittingNodes, function(elem, i){
				var params = {};
				dojo.forEach(dojo.attr(elem, "_search_keys").split(","), 
							function(key){params[key.substring(1)]=dojo.attr(elem, key);}
						);
				invitees.push(params);
			});
		return {"invitees":invitees};
	},
	prepareSubmit : function(_t, evt){
		onSubmitCleaner(_t.target_form); 
		var node;
		if(_t.submitting){return false;}
		_t.submitting = true;
		var results = dojo.query(".invitee_row", _t.invited_node);
		
		dojo.forEach(_t._widget_locals, function(item){item.destroy(item);});
		_t._widget_locals = [];
		_t.receiver_selectors = {};

		invitees = _t.get_invitee_json(_t);
		dojo.place(dojo.create("textarea", {name:_t.target_form, style:"display:none",value: dojo.toJson(invitees)}), dojo.byId('invitees'), "last");
		dojo.byId('invitees').submit();
 	}
});











