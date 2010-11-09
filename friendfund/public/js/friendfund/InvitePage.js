dojo.provide("friendfund.InvitePage");

dojo.declare("friendfund.InvitePage", null, {
	selector : null,
	_listener_locals : [],
	_widget_list: [],
	submitting : false,
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.selector = {};
		_t.selector.facebook = new friendfund.NetworkFriendSelector(
							{
								ref_node: "inviter"
								, container : "lowerbody_container"
								, invited_node : "facebook_invitees"
								, inviter_node : "friend_list"
								, base_url : _t.base_url 
								, network : "facebook"
								, mutuals : true
							});
		_t._widget_list.push(_t.selector.facebook);
		_t.selector.twitter = new friendfund.NetworkFriendSelector(
							{
								ref_node: "inviter"
								, container : "lowerbody_container"
								, invited_node : "twitter_invitees"
								, inviter_node : "friend_list"
								, base_url :  _t.base_url 
								, network : "twitter"
							});
		_t._widget_list.push(_t.selector.twitter);
		_t.selector.email = new friendfund.EmailFriendSelector(
						{
							ref_node: "inviter"
							, container : "lowerbody_container"
							, invited_node : "email_invitees"
							, inviter_node : "friend_list"
							, base_url :  _t.base_url 
						});
		_t._widget_list.push(_t.selector.email);
		
		
		_t.parse_links(_t);
		dojo.connect(dojo.byId("invite_submitter"), "onclick", dojo.hitch(null, _t.prepareSubmit, _t));
		_t._listener_locals.push(dojo.connect(dojo.byId(_t.invited_node), "onclick", dojo.hitch(null, _t.unselect, _t)));

		
	},
	parse_links : function(_t) {
		dojo.query("a.ajaxlink",  _t.container).onclick(
			function(evt){
				var deselect = dojo.query("a.ajaxlink.selected", _t.container);
				if(deselect.length > 0){
					deselect = deselect[0];
					if(deselect == this)return;
					dojo.removeClass(deselect, "selected");
					if(dojo.attr(deselect, "_type") in _t.selector){
						var selector = _t.selector[dojo.attr(deselect, "_type")];
						selector.undraw(selector);
					}
				}
				dojo.addClass(this, "selected");
				_t.selector[dojo.attr(this, "_type")].draw();
			});
	},
	unselect : function(_t, evt){
		if(dojo.hasClass(evt.target, "invitee_row") && dojo.hasClass(evt.target, "selectable")){
			var target = evt.target;
		} else {
			var target = dojo.query(evt.target).parents(".invitee_row.selectable")[0];
			if(target==null)return;
		}
		var sel = _t.selector[dojo.attr(target, "_network")];
		sel.unSelect(sel, target);
	},
	prepareSubmit : function(_t, evt){
		if(_t.submitting){return false};
		_t.submitting = true;
		var results = dojo.query("div.invitee_row", _t.invited_node);
		if(results.length){
			dojo.forEach(_t._widget_list, function(item){item.destroy(item);});
			_t._widget_list = [];
			_t.receiver_selectors = {};
			var invitees = [];
			dojo.query("div.invitee_row.selectable", _t.invited_node).forEach(
				function(elem, i){
					var params = {}
					dojo.forEach(dojo.attr(elem, "_search_keys").split(","), 
								function(key){params[key.substring(1)]=dojo.attr(elem, key)}
							);
					invitees.push(params);
				});
			invitees = {"invitees":invitees}
			dojo.place(dojo.create("textarea", {name:"invitees", style:"display:none",value:dojo.toJson(invitees)}), dojo.byId('invitees'), "last");
			dojo.byId('invitees').submit();
		} else {
			_t.submitting = false;
			var node = dojo.byId("inviters_panel_tooltip");
			dojo.removeClass(node, "hidden");
			dojo.style(node, "opacity", "1");
			dojo.fadeOut({node:node ,duration: 5000}).play();
			return false;
		}
 	}
});