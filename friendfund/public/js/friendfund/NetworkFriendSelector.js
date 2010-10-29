dojo.provide("friendfund.NetworkFriendSelector");

dojo.require("dojo.NodeList-traverse");

dojo.declare("friendfund.NetworkFriendSelector", null, {
	_listener_locals : []
	,constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.ref_node = dojo.isString(_t.ref_node) && dojo.byId(_t.ref_node) || _t.ref_node;
		if(_t.invited_node){
			_t.invited_node = dojo.isString(_t.invited_node) && dojo.byId(_t.invited_node) || _t.invited_node;
			_t._listener_locals.push(dojo.connect(dojo.byId(_t.invited_node), "onclick", dojo.hitch(null, _t.unselect, _t)));
		} else {_t.invited_node=null;}
		
		
		/* since selector is outside of refnode, and does not get rerendered, this can get out of sync */
		_t._is_selected_decider = "a.methodselector.ajaxlink.selected[_type="+_t.network+"]";
	},is_selected:function(_t){
		return dojo.query(_t._is_selected_decider, _t.container).length > 0;
	},draw : function(){
		var _t = this;
		if (!_t.is_selected(_t) || _t.is_loading != true){
			_t.is_loading = true;
			xhrPost(_t.base_url+'/' + _t.network, {}, dojo.hitch(null, _t.onLoad, _t));
		}
	},onLoad : function(_t, data){
		_t.is_loading = false;
		if (_t.is_selected(_t)){
			dojo.place(data.html, _t.ref_node, "only");
			dojo.style(_t.ref_node, 'display', 'Block');
			var filter_box = dojo.byId("fb_filter");
			_t._listener_locals.push(dojo.connect(filter_box, "onkeyup", dojo.hitch(null, _t.filter, _t)));
			var addall = dojo.byId("inviteall");
			if(addall){_t._listener_locals.push(dojo.connect(addall, "onclick", dojo.hitch(null, _t.addall, _t)));}
			_t._listener_locals.push(dojo.connect(dojo.byId("friend_list"), "onclick", dojo.hitch(null, _t.select, _t)));
			
			parseDefaultsInputs(_t.ref_node);
			var toggler = dojo.byId("toggle_mutuals");
			if(toggler)_t._listener_locals.push(dojo.connect(toggler, "onchange", dojo.hitch(null, _t.toggle_mutuals, _t)));
			if(!data.is_complete){
				xhrPost(_t.base_url+'_ext/' + _t.network, {offset:data.offset}, dojo.hitch(null, _t.addLoad, _t));
			}
		}
	}, addLoad : function(_t, data){
		if (_t.is_selected(_t)){
			dojo.place(data.html, dojo.byId("friend_list"), "last");
			if(!data.is_complete){
				xhrPost(_t.base_url+'_ext/' + _t.network, {offset:data.offset}, dojo.hitch(null, _t.addLoad, _t));
			}
		}
	},unload : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
	}
	
	/* ================= BEGIN selectors ========================= */
	,select : function(_t, evt){
		if(dojo.hasClass(evt.target, "invitee_row") && dojo.hasClass(evt.target, "selectable")){
			var elem = evt.target;
		} else {
			var elem = dojo.query(evt.target).parents(".invitee_row.selectable")[0];
			if(elem==null)return;
		}
		return _t.onSelect(dojo.attr(elem, 'networkid'), dojo.attr(elem, 'networkname'), dojo.attr(elem, 'pos'), elem, evt);
	},unselect : function(_t, evt){
		if(dojo.hasClass(evt.target, "invitee_row") && dojo.hasClass(evt.target, "selectable")){
			var elem = evt.target;
		} else {
			var elem = dojo.query(evt.target).parents(".invitee_row.selectable")[0];
		}
		dojo.query('#'+elem.id, _t.invited_node).orphan().forEach(function(elem){
				if(dojo.hasClass(_t.inviter_node, _t.network)){
					if(_t.mutuals == true && dojo.hasClass(elem, 'nonmutual')){dojo.addClass(elem, "hidden")}
					dojo.place(elem, _t.inviter_node, "last");
				}
				xhrPost(_t.base_url+'/rem', 
						{network:dojo.attr(elem, 'network'), networkid:dojo.attr(elem, 'networkid')});
			});
	}
	,onSelect : function(networkid, name, pos, elem, evt){
		var _t = this;
		dojo.query('#'+elem.id, _t.inviter_node).orphan().forEach(function(elem){
			dojo.place(elem, _t.invited_node, "last");
			var keys = dojo.attr(elem, '_keys').split(",");
			var params = {};
			dojo.forEach(keys, function(key){params["invitee."+key] = dojo.attr(elem, key);});
			xhrPost(_t.base_url+'/add', params);
		});
	/* ================= END selectors ========================= */
	},addall : function(_t, evt){
		dojo.hitch(_t, _t.onSelect, dojo.attr(this, 'networkid'), dojo.attr(this, 'networkname'), dojo.attr(this, 'pos'), this, evt);
		var userlist={};
		var i = 0;
		var selector = "div.selectable.invitee_row";
		if(_t.mutuals == true)selector = "div.selectable.mutual.invitee_row";
		dojo.query(selector, _t.inviter_node).orphan().forEach(function(elem){
			dojo.place(elem, _t.invited_node, "last");
			var keys = dojo.attr(elem, '_keys').split(",");
			dojo.forEach(keys, function(key){userlist["userlist-"+i+"."+key] = dojo.attr(elem, key);});
			i++;
		});
		console.log(userlist, userlist.length);
		if(userlist!={}){
			userlist["network"] = _t.network;
			xhrPost(_t.base_url+'/addall',userlist);
		}
	},toggle_mutuals: function(_t) {
		if(_t.mutuals == true){
			_t.mutuals=false;
			dojo.query("div.nonmutual.invitee_row[networkname]", _t.inviter_node).removeClass("hidden");
		} else {
			_t.mutuals=true;
			dojo.query("div.nonmutual.invitee_row[networkname]", _t.inviter_node).addClass("hidden");
		}
	},filter : function(_t, evt){
		var st = this.value.toLowerCase();
		
		var selector = "div.invitee_row[networkname]";
		if(_t.mutuals == true){selector = "div.mutual.invitee_row[networkname]";}
		dojo.query(selector, _t.inviter_node).forEach(
			function(elem){
				var tokens = dojo.attr(elem, "networkname").split(" ");
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
