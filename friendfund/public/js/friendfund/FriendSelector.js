dojo.provide("friendfund.CompoundFriendSelector");
dojo.require("friendfund.NetworkFriendSelector");
dojo.require("friendfund.EmailFriendSelector");
dojo.require("ff.t");
dojo.require("ff.io");

dojo.declare("friendfund.CompoundFriendSelector", null, {
	_widget_locals : [],
	_listener_locals : [],
	selectors : {},
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		if(args.avail_selectors.facebook === true){
			_t.selectors.facebook = new friendfund.NetworkFriendSelector(
						{	container : _t.container
							,auth_provider : _t.auth_provider
							,ref_node: _t.ref_node
							,invited_node : "network"+_t.invited_node_suffix
							,global_invited_node : _t.global_invited_node
							,base_url : _t.base_url
							,network : "facebook"
						});
		}
		if(args.avail_selectors.twitter === true){
			_t.selectors.twitter = new friendfund.NetworkFriendSelector(
						{	container : _t.container
							,auth_provider : _t.auth_provider
							,ref_node: _t.ref_node
							,invited_node : "network"+_t.invited_node_suffix
							,global_invited_node : _t.global_invited_node
							,base_url : _t.base_url
							,network : "twitter"
						});
		}
		if(args.avail_selectors.email === true){
			_t.selectors.email = new friendfund.EmailFriendSelector(
						{	ref_node: _t.ref_node
							,auth_provider : _t.auth_provider
							,invited_node : "network"+_t.invited_node_suffix
							,global_invited_node : _t.global_invited_node
							,base_url : _t.base_url
							,network : "email"
						});
		}
		if(args.avail_selectors.yourself === true){
			_t.selectors.yourself = new friendfund.YourselfSelector(
				{base_url : _t.base_url, ref_node: "receiver_selector_container"}
			);
		}
		
		
		
		for(var sel in _t.selectors){
			var s = _t.selectors[sel];
			if(_t.selectors.hasOwnProperty(sel)&&_t.selectors[sel]){
				if(_t.onSelect){s.onSelect = dojo.hitch(s, _t.onSelect);}
				if(_t.unSelect){s.unSelect = dojo.hitch(s, _t.unSelect);}
				_t._widget_locals.push(s);
			}
		}
		
		if(_t.invited_node_suffix){
			_t._listener_locals.push(dojo.connect(dojo.byId(_t.global_invited_node), "onclick", _t, "unselect"));
		}
		var removeall = dojo.byId("removeall");
		if(removeall){
			_t._listener_locals.push(dojo.connect(removeall, "onclick", _t, "removeAll"));
		}

	},removeAll : function(){
		var _t = this;
		dojo.query(".invitee_row.selectable", _t.global_invited_node).forEach(function(elem){
			_t.selectors[dojo.attr(elem, "_network")].unSelect(elem);
		});
	},unselect : function(evt){
		var target = ff.t.findParent(evt.target, "invitee_row");
		if(!target||!dojo.hasClass(target, "selectable")){return;}
		this.selectors[dojo.attr(target, "_network")].unSelect(target);
	},destroy : function(){
		dojo.forEach(this._listener_locals, dojo.disconnect);
		this._listener_locals = [];
		dojo.forEach(this._widget_locals, function(item){item.destroy();});
		this._widget_locals = [];
	},switchMethod : function(evt){
		var _t = this;
		if(dojo.hasClass(_t, "selected")){return;}
		dojo.query(".ajaxlink.selected", _t.container).forEach(function(elem){
			dojo.removeClass(elem, "selected");
			var selector = _t.selectors[dojo.attr(elem, "_type")];
			if(selector){selector.undraw();}
		});
		dojo.addClass(evt.target, "selected");
		var selector = _t.selectors[dojo.attr(evt.target, "_type")];
		if(selector){selector.draw();}
	},
	draw : function(selector){
		var _t = this;
		_t.selectors[selector].draw();
		dojo.query(".ajaxlink", _t.container).forEach(
			function(elem){_t._listener_locals.push(dojo.connect(elem, "onclick", _t, "switchMethod"));}
		);
		
	}
});












