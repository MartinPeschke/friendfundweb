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
		dojo.connect(document, "onclick", dojo.hitch(null, _t.loadPreviewPopup, _t, _t.method));
	},
	loadPreviewPopup : function(_t, method, evt){
		if(dojo.hasClass(evt.target, "message_preview")){
			dojo.query("input.addRefContent", _t.target_form).forEach(function(elem){elem.value = dojo.byId(dojo.attr(elem, "_source")).value;});
			params = dojo.formToObject(_t.target_form);
			params.method = dojo.attr(evt.target, "_method");
			ff.io.xhrPost(dojo.attr(evt.target, "_href"), params);
		}
	}, 
	prepareSubmit : function(_t, level, evt){
		ff.t.onSubmitCleaner(_t.target_form); 
		if(_t.submitting){return false;}
		_t.submitting = true;
		return doLogin({level:level, cb:dojo.hitch(null, _t._submit, _t), failcb:function(){_t.submitting = false}});
 	},_submit:function(_t){
		dojo.forEach(_t._widget_locals, function(item){item.destroy(item);});
		_t._widget_locals = [];
		_t.receiver_selectors = {};
		dojo.query("input.addRefContent", _t.target_form).forEach(function(elem){elem.value = dojo.byId(dojo.attr(elem, "_source")).value;});
		dojo.byId(_t.target_form).submit();
	}
});











