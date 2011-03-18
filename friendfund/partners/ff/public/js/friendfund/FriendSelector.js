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
		xhrPost(_t.base_url+"/validate", {"invitee.network":"yourself"}, dojo.hitch(null, _t._onSelect, _t));
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
	rootNode : null,
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.ref_node = dojo.isString(_t.ref_node) && dojo.byId(_t.ref_node) || _t.ref_node;
	},
	draw : function(_t){
		if(_t.rootNode){
			dojo.removeClass(_t.rootNode, "hidden");
			dojo.query("input[type=text]", _t.rootNode)[0].focus();
		} else {
			_t.rootNode = dojo.create("DIV", {"id":("networkinviter_"+_t.network)});
			dojo.byId(_t.ref_node).appendChild(_t.rootNode);
			dojo.place(_t._loader, _t.rootNode, "only");
			xhrPost(_t.base_url+'/' + _t.network, {}, dojo.hitch(null, _t.onLoad, _t));
		}
	},
	onLoad : function(_t, html){
		dojo.place(html, _t.rootNode, "only");
		_t._listener_locals.push(dojo.connect(_t.ref_node, "onclick", dojo.hitch(null, _t.selectClick, _t)));
		_t._listener_locals.push(dojo.connect(_t.ref_node, "onkeydown", dojo.hitch(_t, accessability, _t.select, function(){})));
		dojo.query("input[type=text]", _t.rootNode)[0].focus();
	},
	undraw : function(_t){
		dojo.addClass(_t.rootNode, "hidden");
	},
	destroy : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
	},
	selectClick : function(_t, evt){
		if(evt.target.id==="emailsubmitter"){_t.select(_t, evt);}
	},
	select : function(_t, evt){
		var tab = dojo.byId("email_email");
		if(tab && tab.value.length > 0){
			xhrFormPost(_t.base_url+"/validate", "emailinviter", dojo.hitch(null, _t._onSelect, _t));
		}
	},
	_onSelect : function(_t, data){
		if(data.success===true){
			_t.onSelect(_t, data, data.html, null);
			dojo.place(data.input_html, _t.rootNode, "only");
		} else {
			dojo.place(data.html, _t.rootNode, "only");
		}
		dojo.query("input[type=text]", _t.rootNode)[0].focus();
	},
	onSelect : function(_t, params, elem, evt){
		dojo.query("p.inviterTwo", _t.global_invited_node).addClass("hidden");
		dojo.place(elem, _t.invited_node, "last");
		dojo.query("input[type=text]", "emailinviter").attr("value", "");
		dojo.query("#email_inviter_error", "emailinviter").orphan();
		elem = dojo.byId("invitedCounter");
		elem.innerHTML = parseInt(elem.innerHTML)+1;
	},
	unSelect : function(_t, target){
		dojo.query('#'+target.id, _t.invited_node).orphan();
		elem = dojo.byId("invitedCounter");
		elem.innerHTML = parseInt(elem.innerHTML)-1;
	}
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
	},destroy : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
	},select : function(_t, evt){
		target = evt.target;
		if(!(dojo.hasClass(target, "invitee_row")&&dojo.hasClass(target,"selectable"))){
			var target = dojo.query(evt.target).parents(".invitee_row.selectable")[0];
			if(!target){return;}
		}
		var params = {};
		dojo.forEach(dojo.attr(target, "_search_keys").split(","), 
					function(key){params[key.substring(1)]=dojo.attr(target, key);}
				);
		return _t.onSelect(_t, params, target, evt);
	}
});



dojo.declare("friendfund.NetworkFriendSelector", friendfund.NetworkFriendPanel, {
	rootNode : null,
	is_loading : false,
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
		_t._is_selected_decider = ".methodselector.ajaxlink.selected[_type="+_t.network+"]";
	},is_selected : function(_t){
		return dojo.query(_t._is_selected_decider, _t.container).length > 0;
	},draw : function(_t){
		_t.backup_reloader = page_reloader;
		page_reloader = dojo.hitch(_t, _t.draw, _t);
		if(_t.rootNode){
			dojo.removeClass(_t.rootNode, "hidden");
		} else {
			if (!_t.is_selected(_t) || _t.is_loading !== true){
				_t.is_loading = true;
				dojo.query("#networkinviter_"+_t.network).orphan();
				_t.rootNode = dojo.create("DIV", {"id":("networkinviter_"+_t.network)});
				dojo.byId(_t.ref_node).appendChild(_t.rootNode);
				dojo.place(_t._loader, _t.rootNode, "only");
				var pv = dojo.query(".invitee_row[_network="+_t.network+"]", _t.invited_node).attr("_network_id");
				xhrPost(_t.base_url+'/' + _t.network, {pv:pv}, dojo.hitch(null, _t.onLoad, _t));
			}
		}
	},undraw : function(){
		var _t = this;
		if(_t.rootNode){dojo.addClass(_t.rootNode, "hidden");}
		else {dojo.query("#networkinviter_"+_t.network).orphan();}
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		page_reloader = _t.backup_reloader;
	},onLoad : function(_t, data){
		_t.is_loading = false;
		dojo.place(data.html, _t.rootNode, "only");
		if(data.success){
			_t.friendlist = dojo.byId("friend_list_"+_t.network);
			dojo.connect(_t.rootNode, "onclick", dojo.hitch(null, _t.select, _t));
			dojo.connect(dojo.byId("filter_"+_t.network), "onkeyup", dojo.hitch(null, _t.filter, _t, _t.friendlist));
			
			var addall = dojo.byId("inviteall_"+_t.network);
			if(addall){dojo.connect(addall, "onclick", dojo.hitch(null, _t.addall, _t));}
			
			parseDefaultsInputs(_t.ref_node);
			var toggler = dojo.byId("toggle_mutuals_"+_t.network);
			if(toggler){dojo.connect(toggler, "onchange", dojo.hitch(null, _t.toggle_mutuals, _t));}

			if(_t._to_append_nodes["length"]){
				_t._to_append_nodes.forEach(function(elt){
					_t.friendlist.appendChild(elt);
				});
				_t._to_append_nodes=[];
			}
			
			if(!data.is_complete){
				var pv = dojo.query(".invitee_row[_network="+_t.network+"]", _t.invited_node).attr("_network_id");
				xhrPost(_t.base_url+'/ext_' + _t.network, {offset:data.offset,pv:pv}, dojo.hitch(null, _t.addLoad, _t));
			}
		} else {
			 _t.rootNode = null;
		}
	},addLoad : function(_t, data){
		if(data.html!=""){dojo.place(data.html, _t.friendlist, "last");}
		if(!data.is_complete){
			var pv = dojo.query(".invitee_row[_network="+_t.network+"]", _t.invited_node).attr("_network_id");
			xhrPost(_t.base_url+'/ext_' + _t.network, {offset:data.offset,pv:pv}, dojo.hitch(null, _t.addLoad, _t));
		}
		if(!dojo.hasClass("filter_"+_t.network, 'default')){_t.filter(_t, _t.friendlist, null);}
	},
	/* ================= BEGIN selectors ========================= */
	/* ================= SELECT inherited ======================== */
	onSelect : function(_t, params, elem, evt){
		dojo.query("p.inviterTwo", _t.global_invited_node).addClass("hidden");
		dojo.query('#'+elem.id, _t.friendlist).orphan().forEach(function(elem){
			_t.inviteAppendNode(_t, elem);
		});
	},
	inviteAppendNode : function(_t, elem){
		dojo.place(elem, _t.invited_node, "last");
		elem = dojo.byId("invitedCounter");
		elem.innerHTML = parseInt(elem.innerHTML)+1;
	},
	uninviteAppendNode : function(_t, elem){
		if(_t.friendlist){
			if(_t.mutuals === true && dojo.hasClass(elem, 'nonmutual')){dojo.addClass(elem, "hidden");}
			var list = dojo.query(".invitee_row", _t.friendlist), pos = parseInt(dojo.attr(elem, "pos"));
			for(var i=0;i<list.length;i++){
				if(parseInt(dojo.attr(list[i], "pos"))>pos)break;
			}
			if(list.length&&i<list.length)dojo.place(elem, list[i], "before");
			else dojo.place(elem, _t.friendlist, "last");
		} else _t._to_append_nodes.push(elem);
	},
	unSelect : function(_t, target){
		dojo.query('#'+target.id, _t.invited_node).orphan().forEach(function(elem){
			_t.uninviteAppendNode(_t, elem);
			var ctr = dojo.byId("invitedCounter");
			var newctr = parseInt(ctr.innerHTML)-1
			ctr.innerHTML = newctr;
			if(newctr == 0){
				dojo.query("p.inviterTwo", _t.global_invited_node).removeClass("hidden");
			}
		});
	},
	/* ================= END selectors ========================= */
	addall : function(_t, evt){
		dojo.query("p.inviterTwo", _t.global_invited_node).addClass("hidden");
		var selector = ".selectable.invitee_row";
		if(_t.mutuals === true){selector = ".selectable.mutual.invitee_row";}
		dojo.query(selector, _t.friendlist).orphan().forEach(function(elem){
			_t.inviteAppendNode(_t, elem);
		});
	},toggle_mutuals: function(_t) {
		if(_t.mutuals === true){
			_t.mutuals=false;
			dojo.query(".nonmutual.invitee_row[_search_keys]", _t.friendlist).removeClass("hidden");
		} else {
			_t.mutuals=true;
			dojo.query(".nonmutual.invitee_row[_search_keys]", _t.friendlist).addClass("hidden");
		}
	},filter : function(_t, refnode, evt){
		var filter = dojo.byId("filter_"+_t.network);
		if(evt.keyCode==27){filter.value="";}
		var st = filter.value.toLowerCase();
		var selector = ".invitee_row[_search_keys]";
		if(_t.mutuals === true){selector = ".mutual.invitee_row[_search_keys]";}
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
							invited_node : "network"+_t.invited_node_suffix,
							global_invited_node : _t.invited_node,
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
							invited_node : "network"+_t.invited_node_suffix,
							global_invited_node : _t.invited_node,
							base_url : _t.base_url,
							network : "twitter"
						});
			if(_t.onSelect){_t.selectors.twitter.onSelect = _t.onSelect;}
		}
		if(args.avail_selectors.email === true){
			_t.selectors.email = new friendfund.EmailFriendSelector(
						{	ref_node: _t.ref_node,
							invited_node : "network"+_t.invited_node_suffix,
							global_invited_node : _t.invited_node,
							base_url : _t.base_url,
							network : "email"
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
		var removeall = dojo.byId("removeall");
		if(removeall){
			_t._listener_locals.push(dojo.connect(removeall, "onclick", dojo.hitch(null, _t.removeAll, _t)));
		}

	},removeAll : function(_t, evt){
		dojo.query(".invitee_row.selectable", self.invited_node).forEach(function(elem){
			var sel = _t.selectors[dojo.attr(elem, "_network")];
			sel.unSelect(sel, elem);
		});
	},unselect : function(_t, evt){
		var target = dojo.query(evt.target).parents(".invitee_row.selectable")[0];
		if(!target){return;}
		var sel = _t.selectors[dojo.attr(target, "_network")];
		sel.unSelect(sel, target);
	},destroy : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		dojo.forEach(_t._widget_locals, function(item){item.destroy(item);});
		_t._widget_locals = [];
	},switchMethod : function(_t, evt){
		var deselect = dojo.query(".ajaxlink.selected", _t.container);
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
		dojo.query(".ajaxlink", _t.container).forEach(
			function(elem){_t._listener_locals.push(dojo.connect(elem, "onclick", dojo.hitch(null, _t.switchMethod, _t)));}
		);
		
	}
});












