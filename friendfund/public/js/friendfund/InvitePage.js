dojo.provide("friendfund.InvitePage");

dojo.declare("friendfund.InvitePage", null, {
	selector : null,
	submitting : false,
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.parse_links(_t);
		dojo.connect(dojo.byId("invite_submitter"), "onclick", dojo.hitch(null, _t.prepareSubmit, _t));
		_t.selector = {};
		_t.selector.facebook = new friendfund.NetworkFriendSelector(
							{
								ref_node: "inviter"
								, container : "lowerbody_container"
								, invited_node : "fb_invitees"
								, inviter_node : "friend_list"
								, base_url : _t.base_url 
								, network : "facebook"
								, mutuals : true
							});
		_t.selector.twitter = new friendfund.NetworkFriendSelector(
							{
								ref_node: "inviter"
								, container : "lowerbody_container"
								, invited_node : "twitter_invitees"
								, inviter_node : "friend_list"
								, base_url :  _t.base_url 
								, network : "twitter"
							});
		_t.selector.email = new friendfund.EmailFriendSelector(
						{
							ref_node: "inviter"
							, container : "lowerbody_container"
							, invited_node : "mail_invitees"
							, inviter_node : "friend_list"
							, base_url :  _t.base_url 
						});
	}, 
	parse_links : function(_t) {
		dojo.query("a.ajaxlink",  _t.container).onclick(
			function(evt){
				dojo.query("a.ajaxlink.selected", _t.container).removeClass("selected");
				dojo.addClass(this, "selected");
				_t.selector[dojo.attr(this, "_type")].draw();
			});
	},
	prepareSubmit : function(_t, evt){
		if(_t.submitting){return false};
		_t.submitting = true;
		var results = dojo.query("div.invitee_row", _t.invited_node);
		if(results.length){
			dojo.query("div.invitee_row.selectable", _t.invited_node).forEach(
				function(elem, i){
					var network = dojo.attr(elem, "network");
					var fieldname = (network == "email"?".email":".network_id");
					
					dojo.place(dojo.create("input", {name:"invitees-"+i+fieldname, type:"hidden",value:dojo.attr(elem, "networkid")}), elem, "last");
					dojo.place(dojo.create("input", {name:"invitees-"+i+".network", type:"hidden",value:network}), elem, "last");
					dojo.place(dojo.create("input", {name:"invitees-"+i+".notification_method", type:"hidden",value:dojo.attr(elem, "notification_method")}), elem, "last");
					dojo.place(dojo.create("input", {name:"invitees-"+i+".name", type:"hidden",value:dojo.attr(elem, "networkname")}), elem, "last");
					if(dojo.attr(elem, "profile_picture_url") != null)
						dojo.place(dojo.create("input", {name:"invitees-"+i+".profile_picture_url", type:"hidden",value:dojo.attr(elem, "profile_picture_url")}), elem, "last");
					if(dojo.attr(elem, "large_profile_picture_url") != null)
						dojo.place(dojo.create("input", {name:"invitees-"+i+".large_profile_picture_url", type:"hidden",value:dojo.attr(elem, "large_profile_picture_url")}), elem, "last");
					if(dojo.attr(elem, "screenname") != null)
						dojo.place(dojo.create("input", {name:"invitees-"+i+".screen_name", type:"hidden",value:dojo.attr(elem, "screenname")}), elem, "last");
				});
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