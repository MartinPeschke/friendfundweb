dojo.provide("friendfund.EmailFriendSelector");

dojo.declare("friendfund.EmailFriendSelector", null, {
	_listener_locals : []
	,constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.ref_node = dojo.isString(_t.ref_node) && dojo.byId(_t.ref_node) || _t.ref_node;
		_t.invited_node = dojo.isString(_t.invited_node) && dojo.byId(_t.invited_node) || _t.invited_node || 'asrgwergstgbkjhqwgejgvawsrgasrgsegsegfevswjhverg';
		dojo.query(".selectable.invitee_row", _t.invited_node).onclick(dojo.hitch(null, _t.select, _t));
	},
	draw : function(){
		var _t = this;
		loadElement(_t.base_url+'/email', _t.ref_node, {}, dojo.hitch(null, _t.onLoad, _t));
	},
	onLoad : function(_t){
		_listener_locals.push(dojo.connect(dojo.byId("emailsubmitter"), "onclick", dojo.hitch(null, _t.select, _t)));
	},destroy : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
	},
	select : function(_t, evt){
		if(dojo.query('#'+this.id, _t.invited_node).length > 0){
			dojo.query('#'+this.id, _t.invited_node).orphan();
			xhrPost(_t.base_url+"/rem", {network:dojo.attr(this, 'network'), networkid:dojo.attr(this, 'networkid')});
		} else {
			var tab = dojo.byId("email_email");
			if(tab != null && tab.value.length > 0)
				xhrFormPost(_t.base_url+"/add", "emailinviter", dojo.hitch(null, _t.onSelect, _t));
		}
		evt.stopPropagation();
		evt.preventDefault();
		return false;
	},
	onSelect : function(_t, data){
		if(data.success===true){
			dojo.place(data.html, _t.invited_node, "only");
			dojo.query("input[type=text]", "emailinviter").attr("value", "");
			dojo.query(".selectable.invitee_row", _t.invited_node).onclick(dojo.hitch(null, _t.select, _t));
		} else {
			dojo.place(data.message, dojo.byId("email_inviter_error"), "only");
		}
	}
});
