dojo.provide("friendfund.NetworkFriendSelector");
dojo.provide("friendfund.YourselfSelector");
dojo.provide("friendfund.EmailFriendSelector");

dojo.require("dojo.NodeList-traverse");
dojo.require("dojo.NodeList-manipulate");

dojo.declare("friendfund._Selector", null, {
	_listener_locals : [],
	_loader : "<div style=\"margin: 0px auto;text-align:center;padding:30px;\"><div class=\"loading_animation\"><img src=\"/static/imgs/ajax-loader.gif\"></div></div>",
	draw: function(){console.log("NOT_IMPLEMENTED");},
	destoy: function(){console.log("NOT_IMPLEMENTED");}
});


dojo.declare("friendfund.YourselfSelector", friendfund._Selector, {
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.ref_node = dojo.isString(_t.ref_node) && dojo.byId(_t.ref_node) || _t.ref_node;
	},draw : function(_t){
		xhrPost("/myfriends/validate", {"invitee.network":"yourself"}, dojo.hitch(null, _t._onSelect, _t));
	},_onSelect : function(_t, data){
		if(data.success===true){
			_t.onSelect(_t, data, data.html, null);
		} else {
			dojo.place(data.html, _t.ref_node, "only");
		}
	},
	onSelect : function(_t, params, elem, evt){},
	undraw :function(){},
	destroy:function(){}
});


dojo.declare("friendfund.EmailFriendSelector", friendfund._Selector, {
	_listener_locals : [],
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.ref_node = dojo.isString(_t.ref_node) && dojo.byId(_t.ref_node) || _t.ref_node;
	},
	draw : function(_t){
		dojo.place(_t._loader, _t.ref_node, "only");
		loadElement(_t.base_url+'/email', _t.ref_node, {}, dojo.hitch(null, _t.onLoad, _t));
	},
	onLoad : function(_t){
		_t._listener_locals.push(dojo.connect(dojo.byId("emailsubmitter"), "onclick", dojo.hitch(null, _t.select, _t)));
		_t._listener_locals.push(dojo.connect(_t.ref_node, "onkeydown", dojo.hitch(_t, accessability, _t.select, function(){})));
	},
	undraw : function(_t){_t.destroy(_t);},
	destroy : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
	},
	select : function(_t, evt){
		var tab = dojo.byId("email_email");
		if(tab && tab.value.length > 0){
			xhrFormPost("/myfriends/validate", "emailinviter", dojo.hitch(null, _t._onSelect, _t));
		}
	},
	_onSelect : function(_t, data){
		if(data.success===true){
			_t.onSelect(_t, data, data.html, null);
		} else {
			dojo.place(data.message, dojo.byId("email_inviter_error"), "only");
		}
	},
	onSelect : function(_t, params, elem, evt){
		dojo.place(elem, _t.invited_node, "last");
		dojo.query("input[type=text]", "emailinviter").attr("value", "");
		dojo.query("#email_inviter_error", "emailinviter").orphan();
		
	},
	unSelect : function(_t, target){dojo.query('#'+target.id, _t.invited_node).orphan();}
});

dojo.declare("friendfund.NetworkFriendPanel", friendfund._Selector, {
	constructor : function(args){
		var _t = this;
		dojo.mixin(_t, args);
	},draw : function(_t){
		xhrPost(_t.base_url+'/' + _t.network, {}, dojo.hitch(null, _t.onLoad, _t));
	},onLoad : function(_t, data){
		dojo.place(data.html, _t.ref_node, "only");
		dojo.style(_t.ref_node, 'display', 'Block');
		_t._listener_locals.push(dojo.connect(dojo.byId("friend_list"), "onclick", dojo.hitch(null, _t.select, _t)));
	},destroy : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
	},select : function(_t, evt){
		if(!dojo.hasClass(evt.target,'invite')){return;}
		var target = dojo.query(evt.target).parents(".invitee_row.selectable")[0];
		if(!target){return;}
		var params = {};
		dojo.forEach(dojo.attr(target, "_search_keys").split(","), 
					function(key){params[key.substring(1)]=dojo.attr(target, key);}
				);
		return _t.onSelect(_t, params, target, evt);
	}
});



dojo.declare("friendfund.NetworkFriendSelector", friendfund.NetworkFriendPanel, {
	_backup_node : null,
	_to_append_nodes : [],
	_backup_reloader : null,
	constructor : function(args){
		var _t = this;
		dojo.mixin(_t, args);
		if(_t.invited_node){
			_t.invited_node = dojo.isString(_t.invited_node) && dojo.byId(_t.invited_node) || _t.invited_node;
		} else {_t.invited_node=null;}
		
		/* since selector is outside of refnode, and does not get rerendered, this can get out of sync */
		_t._is_selected_decider = "a.methodselector.ajaxlink.selected[_type="+_t.network+"]";
	},is_selected : function(_t){
		return dojo.query(_t._is_selected_decider, _t.container).length > 0;
	},draw : function(_t){
		_t.backup_reloader = page_reloader;
		page_reloader = dojo.hitch(_t, _t.draw, _t);
		_t.ref_node = dojo.isString(_t.ref_node) && dojo.byId(_t.ref_node) || _t.ref_node;
		dojo.place(_t._loader, _t.ref_node, "only");
		if(_t._backup_node){
			_t.onLoad(_t, {html:_t._backup_node, is_complete:true});
			while(_t._to_append_nodes.length){
				var e=_t._to_append_nodes.pop();
				if(_t.mutuals === true && dojo.hasClass(e, 'nonmutual')){dojo.addClass(e, "hidden");}
				dojo.place(e, _t.inviter_node, "last");
			}
			_t._backup_node = null;
		} else if (!_t.is_selected(_t) || _t.is_loading !== true){
			_t.is_loading = true;
			xhrPost(_t.base_url+'/' + _t.network, {}, dojo.hitch(null, _t.onLoad, _t));
		}
	},undraw : function(){
		var _t = this;
		dojo.query("#networkinviter_"+this.network).orphan().forEach(function(item){_t._backup_node = item;});
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		page_reloader = _t.backup_reloader;
	},onLoad : function(_t, data){
		_t.is_loading = false;
		if (_t.is_selected(_t)){
			dojo.place(data.html, _t.ref_node, "only");
			dojo.style(_t.ref_node, 'display', 'Block');
			var filter_box = dojo.byId("fb_filter");
			_t._listener_locals.push(dojo.connect(filter_box, "onkeyup", dojo.hitch(null, _t.filter, _t, _t.inviter_node)));
			var addall = dojo.byId("inviteall");
			if(addall){_t._listener_locals.push(dojo.connect(addall, "onclick", dojo.hitch(null, _t.addall, _t)));}
			_t._listener_locals.push(dojo.connect(dojo.byId("friend_list"), "onclick", dojo.hitch(null, _t.select, _t)));
			
			parseDefaultsInputs(_t.ref_node);
			var toggler = dojo.byId("toggle_mutuals");
			if(toggler){_t._listener_locals.push(dojo.connect(toggler, "onchange", dojo.hitch(null, _t.toggle_mutuals, _t)));}
			
			if(!data.is_complete){
				xhrPost(_t.base_url+'/ext_' + _t.network, {offset:data.offset}, dojo.hitch(null, _t.addLoad, _t), "Get");
			}
		}
	},addLoad : function(_t, data){
		if(_t._backup_node){
			_t._to_append_nodes.push(data.html);
		} else {
			dojo.place(data.html, dojo.byId("friend_list"), "last");
		}
		if(!data.is_complete){
			xhrPost(_t.base_url+'/ext_' + _t.network, {offset:data.offset}, dojo.hitch(null, _t.addLoad, _t), "Get");
		}
		if (_t.is_selected(_t)){
			if(!dojo.hasClass("fb_filter", 'default')){_t.filter(_t, _t.inviter_node, null);}
		}
	},
	/* ================= BEGIN selectors ========================= */
	/* ================= SELECT inherited ======================== */
	onSelect : function(_t, params, elem, evt){
		dojo.query('#'+elem.id, _t.inviter_node).orphan().forEach(function(elem){
			dojo.place(elem, _t.invited_node, "last");
		});
	},
	unSelect : function(_t, target){
		dojo.query('#'+target.id, _t.invited_node).orphan().forEach(function(elem){
			if(_t._backup_node){
				_t._to_append_nodes.push(target);
			} else {
				if(_t.mutuals === true && dojo.hasClass(elem, 'nonmutual')){dojo.addClass(elem, "hidden");}
				dojo.place(elem, _t.inviter_node, "last");
			}
		});
	},
	/* ================= END selectors ========================= */
	addall : function(_t, evt){
		var selector = "div.selectable.invitee_row";
		if(_t.mutuals === true){selector = "div.selectable.mutual.invitee_row";}
		dojo.query(selector, _t.inviter_node).orphan().forEach(function(elem){
			dojo.place(elem, _t.invited_node, "last");
		});
	},toggle_mutuals: function(_t) {
		if(_t.mutuals === true){
			_t.mutuals=false;
			dojo.query("div.nonmutual.invitee_row[_search_keys]", _t.inviter_node).removeClass("hidden");
		} else {
			_t.mutuals=true;
			dojo.query("div.nonmutual.invitee_row[_search_keys]", _t.inviter_node).addClass("hidden");
		}
	},filter : function(_t, refnode, evt){
		var st = dojo.byId("fb_filter").value.toLowerCase();
		var selector = "div.invitee_row[_search_keys]";
		if(_t.mutuals === true){selector = "div.mutual.invitee_row[_search_keys]";}
		dojo.query(selector, refnode).forEach(
			function(elem){
				var tokens = dojo.attr(elem, "_name").split(" ");
				if(dojo.some(tokens, function(token){return token.substring(0, st.length).toLowerCase() == st;})){
					dojo.addClass(elem, "selectable");
					dojo.removeClass(elem, "nonselectable");
				} else {
					dojo.removeClass(elem, "selectable");
					dojo.addClass(elem, "nonselectable");
				}
			}
		);
	}
});


dojo.declare("friendfund.CompoundFriendSelector", null, {
	_widget_locals : [],
	_listener_locals : [],
	selectors : {},
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		if(args.avail_selectors.facebook === true){
			_t.selectors.facebook = new friendfund.NetworkFriendSelector(
						{	container : _t.container,
							ref_node: _t.ref_node,
							inviter_node : _t.inviter_node,
							invited_node : "facebook"+_t.invited_node_suffix,
							base_url : _t.base_url,
							network : "facebook",
							mutuals : args.mutuals
						});
			if(_t.onSelect){_t.selectors.facebook.onSelect = _t.onSelect;}
		}
		if(args.avail_selectors.twitter === true){
			_t.selectors.twitter = new friendfund.NetworkFriendSelector(
						{	container : _t.container,
							ref_node: _t.ref_node,
							inviter_node : _t.inviter_node,
							invited_node : "twitter"+_t.invited_node_suffix,
							base_url : _t.base_url,
							network : "twitter"
						});
			if(_t.onSelect){_t.selectors.twitter.onSelect = _t.onSelect;}
		}
		if(args.avail_selectors.email === true){
			_t.selectors.email = new friendfund.EmailFriendSelector(
						{	ref_node: _t.ref_node,
							invited_node : "email"+_t.invited_node_suffix,
							base_url : _t.base_url
						});
			if(_t.onSelect){_t.selectors.email.onSelect = _t.onSelect;}
		}
		if(args.avail_selectors.yourself === true){
			_t.selectors.yourself = new friendfund.YourselfSelector(
						{	base_url : _t.base_url, ref_node: "receiver_selector_container"
						});
			if(_t.onSelect){_t.selectors.yourself.onSelect = _t.onSelect;}
		}
		for(var sel in _t.selectors){
			_t._widget_locals.push(_t.selectors[sel]);
		}
		if(_t.invited_node_suffix){
			_t._listener_locals.push(dojo.connect(dojo.byId(_t.global_invited_node), "onclick", dojo.hitch(null, _t.unselect, _t)));
		}
	},unselectPendingSelector : function(_t, selector, target, evt){
		dojo.removeClass("PendingPlaceHolder", "hidden");dojo.addClass("PendingNominator", "hidden");
		dojo.query(".invitee_row .pending.selected", _t.global_invited_node).removeClass("selected");
		dojo.attr(target, "_is_selector", "");
		dojo.attr("PendingSelectorSelector", {_network:"",_network_id:""});
	},makePendingSelector : function(_t, selector, target, evt){
		if(dojo.attr("PendingSelectorSelector", "_network")==dojo.attr(target, '_network')&&dojo.attr("PendingSelectorSelector", "_network_id")==dojo.attr(target, '_network_id'))
		{_t.unselectPendingSelector(_t, selector, target, evt);return;}
		
		dojo.attr("PendingSelectorSelector", {_network:dojo.attr(target, '_network'), _network_id:dojo.attr(target, '_network_id')});
		dojo.query("img", "PendingNominator").orphan();
		dojo.place(dojo.create("IMG", {src:dojo.attr(target, '_profile_picture_url')}), dojo.byId("PendingNominator"), "first");
		dojo.query("span.name", "PendingNominator").innerHTML(dojo.attr(target, '_name'));
		dojo.addClass("PendingPlaceHolder", "hidden");dojo.removeClass("PendingNominator", "hidden");
		dojo.query(".invitee_row[_is_selector=1]", _t.global_invited_node).attr("_is_selector", "");
		dojo.query(".invitee_row .pending.selected", _t.global_invited_node).removeClass("selected");
		dojo.addClass(evt.target, "selected");dojo.attr(target, "_is_selector", "1");
	},unselect : function(_t, evt){
		if(!(dojo.hasClass(evt.target,'pending') || dojo.hasClass(evt.target,'remove'))){return;}
		var target = dojo.query(evt.target).parents(".invitee_row.selectable")[0];
		if(!target){return;}
		var sel = _t.selectors[dojo.attr(target, "_network")];
		if(dojo.hasClass(evt.target,'pending')){
			_t.makePendingSelector(_t, sel, target, evt);
		}else{
			if(dojo.query(".pending.selected",target).length>0){_t.unselectPendingSelector(_t, sel, target, evt);}
			sel.unSelect(sel, target);
		}
	},destroy : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		dojo.forEach(_t._widget_locals, function(item){item.destroy(item);});
		_t._widget_locals = [];
	},switchMethod : function(_t, evt){
		var deselect = dojo.query("a.ajaxlink.selected", _t.container);
		if(deselect.length > 0){
			deselect = deselect[0];
			if(deselect === this){return;}
			dojo.removeClass(deselect, "selected");
			if(dojo.attr(deselect, "_type") in _t.selectors){
				var selector = _t.selectors[dojo.attr(deselect, "_type")];
				selector.undraw(selector);
			}
		}
		dojo.addClass(this, "selected");
		if(dojo.attr(this, "_type") in _t.selectors){
			_t.selectors[dojo.attr(this, "_type")].draw(_t.selectors[dojo.attr(this, "_type")]);
		}
	},
	draw : function(selector){
		var _t = this;
		_t.selectors[selector].draw(_t.selectors[selector]);
		dojo.query("a.ajaxlink", _t.container).forEach(
			function(elem){_t._listener_locals.push(dojo.connect(elem, "onclick", dojo.hitch(null, _t.switchMethod, _t)));}
		);
		
	}
});











