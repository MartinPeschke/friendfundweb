dojo.provide("friendfund.NetworkFriendSelector");

dojo.require("dojo.NodeList-traverse");

dojo.declare("friendfund.NetworkFriendSelector", null, {
	_listener_locals : []
	,_backup_node : null
	,_prev_node : []
	,_to_append_nodes : []
	,_backup_reloader : null
	,constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.ref_node = dojo.isString(_t.ref_node) && dojo.byId(_t.ref_node) || _t.ref_node;
		if(_t.invited_node){
			_t.invited_node = dojo.isString(_t.invited_node) && dojo.byId(_t.invited_node) || _t.invited_node;
		} else {_t.invited_node=null;}
		
		/* since selector is outside of refnode, and does not get rerendered, this can get out of sync */
		_t._is_selected_decider = "a.methodselector.ajaxlink.selected[_type="+_t.network+"]";
	},is_selected:function(_t){
		return dojo.query(_t._is_selected_decider, _t.container).length > 0;
	},draw : function(){
		var _t = this;
		page_reloader = dojo.hitch(_t, _t.draw);
		if(_t._backup_node !=  null){
			_t.onLoad(_t, {html:_t._backup_node, is_complete:true});
			_t._to_append_nodes.forEach(function(elem){
				if(_t.mutuals == true && dojo.hasClass(elem, 'nonmutual')){dojo.addClass(elem, "hidden")}
				dojo.place(elem, _t.inviter_node, "last");
			});
			_t._to_append_nodes = [];
			_t._backup_node = null;
		} else if (!_t.is_selected(_t) || _t.is_loading != true){
			_t.is_loading = true;
			xhrPost(_t.base_url+'/' + _t.network, {}, dojo.hitch(null, _t.onLoad, _t));
			_t.backup_reloader = page_reloader;
		}
	},undraw : function(){
		var _t = this;
		dojo.query("#networkinviter_"+this.network).orphan().forEach(function(item){_t._backup_node = item});
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		page_reloader = _t.backup_reloader;
		_t._prev_node.forEach(function(elems){dojo.place(elems,_t.ref_node, "only");});
		_t._prev_node = [];
	},onLoad : function(_t, data){
		_t.is_loading = false;
		if (_t.is_selected(_t)){
			dojo.query("*",_t.ref_node).orphan().forEach(_t._prev_node.push);
			dojo.place(data.html, _t.ref_node, "only");
			dojo.style(_t.ref_node, 'display', 'Block');
			var filter_box = dojo.byId("fb_filter");
			_t._listener_locals.push(dojo.connect(filter_box, "onkeyup", dojo.hitch(null, _t.filter, _t, _t.inviter_node)));
			var addall = dojo.byId("inviteall");
			if(addall){_t._listener_locals.push(dojo.connect(addall, "onclick", dojo.hitch(null, _t.addall, _t)));}
			_t._listener_locals.push(dojo.connect(dojo.byId("friend_list"), "onclick", dojo.hitch(null, _t.select, _t)));
			
			parseDefaultsInputs(_t.ref_node);
			var toggler = dojo.byId("toggle_mutuals");
			if(toggler)_t._listener_locals.push(dojo.connect(toggler, "onchange", dojo.hitch(null, _t.toggle_mutuals, _t)));
			
			if(!data.is_complete){
				xhrPost(_t.base_url+'/ext_' + _t.network, {offset:data.offset}, dojo.hitch(null, _t.addLoad, _t), "Get");
			}
		}
	},addLoad : function(_t, data){
		if(_t._backup_node !=  null){
			_t._to_append_nodes.push(data.html);
		} else {
		
			dojo.place(data.html, dojo.byId("friend_list"), "last");
		}
		if(!data.is_complete){
			xhrPost(_t.base_url+'/ext_' + _t.network, {offset:data.offset}, dojo.hitch(null, _t.addLoad, _t), "Get");
		}
		if (_t.is_selected(_t)){
			if(!dojo.hasClass("fb_filter", 'default'))_t.filter(_t, _t.inviter_node, null);
		}
	},destroy : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		page_reloader = _t.backup_reloader;
		_t._backup_node = null;
		_t._prev_node = [];
	}
	
	/* ================= BEGIN selectors ========================= */
	,select : function(_t, evt){
		if(dojo.hasClass(evt.target, "invitee_row") && dojo.hasClass(evt.target, "selectable")){
			var target = evt.target;
		} else {
			var target = dojo.query(evt.target).parents(".invitee_row.selectable")[0];
			if(target==null)return;
		}
		var params = {}
		dojo.forEach(dojo.attr(target, "_search_keys").split(","), 
					function(key){params[key.substring(1)]=dojo.attr(target, key)}
				);
		return _t.onSelect(params, target, evt);
	}
	,onSelect : function(params, elem, evt){
		var _t = this;
		dojo.query('#'+elem.id, _t.inviter_node).orphan().forEach(function(elem){
			dojo.place(elem, _t.invited_node, "last");
		});
	},
	unSelect : function(_t, target){
		dojo.query('#'+target.id, _t.invited_node).orphan().forEach(function(elem){
			if(_t._backup_node){
				_t._to_append_nodes.push(target);
			} else {
				if(_t.mutuals == true && dojo.hasClass(elem, 'nonmutual')){dojo.addClass(elem, "hidden")}
				dojo.place(elem, _t.inviter_node, "last");
			}
		});

	/* ================= END selectors ========================= */
	},addall : function(_t, evt){
		var selector = "div.selectable.invitee_row";
		if(_t.mutuals == true)selector = "div.selectable.mutual.invitee_row";
		dojo.query(selector, _t.inviter_node).orphan().forEach(function(elem){
			dojo.place(elem, _t.invited_node, "last");
		});
	},toggle_mutuals: function(_t) {
		if(_t.mutuals == true){
			_t.mutuals=false;
			dojo.query("div.nonmutual.invitee_row[_search_keys]", _t.inviter_node).removeClass("hidden");
		} else {
			_t.mutuals=true;
			dojo.query("div.nonmutual.invitee_row[_search_keys]", _t.inviter_node).addClass("hidden");
		}
	},filter : function(_t, refnode, evt){
		var st = dojo.byId("fb_filter").value.toLowerCase();
		var selector = "div.invitee_row[_search_keys]";
		if(_t.mutuals == true){selector = "div.mutual.invitee_row[_search_keys]";}
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
