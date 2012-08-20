if(!dojo._hasResource["friendfund.NetworkFriendSelector"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["friendfund.NetworkFriendSelector"] = true;
dojo.provide("friendfund.NetworkFriendSelector");
dojo.provide("friendfund.FriendTypeAhead");
dojo.require("friendfund.EmailFriendSelector");
dojo.require("ff.t");
dojo.require("ff.io");

dojo.declare("friendfund.NetworkFriendPanel", friendfund._Selector, {
	constructor : function(args){
		dojo.mixin(this, args);
	}
	,draw : function(){
		ff.io.xhrPost(this.base_url+'/' + this.network, {}, dojo.hitch(this, "onLoad"));
	}
	,onLoad : function(data){
		dojo.place(data.html, this.ref_node, "only");
		dojo.style(this.ref_node, 'display', 'Block');
	}
	,destroy : function(){
		dojo.forEach(this._listener_locals, dojo.disconnect);
		this._listener_locals = [];
	}
	,select : function(evt){
		var target = ff.t.findParent(evt.target, "invitee_row");
		if(target){
			return this.onSelect(target, evt);
		}
	}
});

dojo.declare("friendfund.DataProvider", friendfund.NetworkFriendPanel, {
	_selected : {}
	,constructor : function(args){
		dojo.mixin(this, args);
		this._rendering = false;
		this._current_display_idx = 0;
		this._fully_loaded = false;
		this._search_index = {};

	}
	,addToSearchIndex: function(ud){
		ud["dom_id"] = this.network+"_"+ud.network_id;
		var s, entry, i, j, k, tmp, keys = {};
		s = ud.name.split(' ').concat([ud.name]);
		for(i=0;i<s.length;i++){entry=s[i];for(j=0;j<=entry.length;j++){k=entry.substr(0,j).toLowerCase();keys[k]=true}}
		for(k in keys){
			tmp = this._search_index[k]||[];
			if(tmp.push){tmp.push(ud);this._search_index[k] = tmp;}
		}
		if(this.current_filter.length&&keys[this.current_filter]){
			this.renderUserAndPlace(ud);
		}
	}
	,_addPage : function(friends, is_complete){
		var i, ud;
		for(i=0;i<friends.length;i++){
			ud = friends[i];
			this.addToSearchIndex(ud);
		}
		this._fully_loaded = is_complete;
	}
	,renderSlice:function(size, show_more){
		var render = ff.t.render
			, template = this.friends_template
			, sel = this._selected
			, mutuals = this.mutuals
			, si = this._search_index[this.current_filter||""] || []
			, eligibles = []
			, result = []
			, len = si.length, i;
		for(i=this._current_display_idx;i<len;i++){
			if(!sel[si[i].dom_id]&&(!mutuals||mutuals&&si[i].mutual_with)){
				eligibles.push(si[i]);
			}
			if(eligibles.length<=size){this._current_display_idx++;}
		}
		len = eligibles.length>size?size:eligibles.length;
		for(i=0;i<len;i++){result.push(render(template, eligibles[i]));}
		if(show_more){result.push( "<li id=\"loading_placeholder_"+this.network+"\" class=\"clear\">&nbsp;</li>" )}
		return result;
	}
	,getFirstPage:function(){
		this._current_display_idx = 0;
		return this.renderSlice(this._page_size, true);
	}
	,getNextPage:function(){
		return this.renderSlice(this._page_size);
	}
	,hasMoreFriends:function(){
		return !this._fully_loaded || this._current_display_idx<this._search_index[this.current_filter||""].length;
	}
	,reRender : function(){
		var page = this.getFirstPage();
		if(page.length){dojo.place(page.join(""), this.friendlist, "only");this.onResultsFound()}else{delete dojo.query("*", this.friendlist).orphan();this.onNoResultsFound();}
	}
	,onResultsFound : function(){}
	,onNoResultsFound : function(){}
	,_checkScrollingState : function(evt){
		friendlist_loader = dojo.byId("loading_placeholder_"+this.network);
		if(!friendlist_loader){return;}
		var pos = dojo.position(friendlist_loader);
		if(pos.y < this.friendlist_box){
			if(this.hasMoreFriends()){
				dojo.place(this.getNextPage().join(""), friendlist_loader, "before");
			}
		}
	}
	,renderUserAndPlace:function(udata){
		dojo.place(ff.t.render(this.friends_template, udata), this.friendlist, "last");
	}
	,addLoad : function(data){
		if(data.friends){
			this._addPage(data.friends, data.is_complete);
			if(!data.is_complete){
				ff.io.xhrPost(this.base_url+'/ext_' + this.network, {offset:data.offset}, dojo.hitch(this, "addLoad"));
			}
		}
	}
	,draw : function(){
		if(this.rootNode){
			dojo.removeClass(this.rootNode, "hidden");
			this.connect();
		} else {
			if (!this.is_selected() || this._is_loading !== true){
				this._is_loading = true;
				{var l=dojo.query("#networkinviter_"+this.network); if(l.length){l.orphan();}}
				this.rootNode = dojo.create("DIV", {"id":("networkinviter_"+this.network)});
				dojo.byId(this.ref_node).appendChild(this.rootNode);
				dojo.place(this._loader, this.rootNode, "only");
				ff.io.xhrPost(this.base_url+'/' + this.network, {}, dojo.hitch(this, "onLoad"));
			}
		}
	}

});


dojo.declare("friendfund.NetworkFriendSelector", friendfund.DataProvider, {
	rootNode : null
	,_is_loading : false
	,_page_size : 20
	,current_filter : ""
	,constructor : function(args){
		dojo.mixin(this, args);
		if(this.invited_node){
			this.invited_node = dojo.isString(this.invited_node) && dojo.byId(this.invited_node) || this.invited_node;
		} else {this.invited_node=null;}
		
		/* since selector is outside of refnode, and does not get rerendered, this can get out of sync */
		_is_selected_decider = ".methodselector.ajaxlink.selected[_type="+this.network+"]";
		this.lazyReRender = ff.t.debounce(dojo.hitch(this, "reRender"), 200, false);
		this.checkScrollingState = ff.t.debounce(dojo.hitch(this, "_checkScrollingState"), 100, false);
	}
	,is_selected : function(){
		return dojo.query(this._is_selected_decider, this.container).length > 0;
	}
	,connect:function(){}
	,undraw : function(){
		if(this.rootNode){dojo.addClass(this.rootNode, "hidden");}
		else {var l=dojo.query("#networkinviter_"+this.network); if(l.length){l.orphan();}}
		dojo.forEach(this._listener_locals, dojo.disconnect);
		this._listener_locals = [];
	}
	,onLoad : function(data){
		var _t = this;
		_t._is_loading = false;
		dojo.place(data.html, _t.rootNode, "only");
		if(data.success){
			
			_t.friendlist = dojo.byId("friend_list_"+_t.network);
			_t.friendlist_box = dojo.position(_t.friendlist.parentNode);
			_t.friendlist_box = _t.friendlist_box.h*2 + _t.friendlist_box.y;
			var toggler = dojo.byId("toggle_mutuals_"+_t.network);
			if(toggler){
				dojo.connect(toggler, "onclick", _t, "toggle_mutuals");
				_t.mutuals = toggler.checked;;
			} else {_t.mutuals = false;}
			
			_t.friends_template = data.template;
			_t._addPage(data.friends, data.is_complete);
			_t.reRender()
			
			_t.filterNode = dojo.byId("filter_"+_t.network);
			dojo.connect(_t.friendlist, "onclick", _t, "select");
			dojo.connect(_t.filterNode, "onkeyup", _t, "filter");
			ff.w.parseDefaultsInputs(_t.ref_node);
			dojo.connect(_t.friendlist.parentNode, "onscroll", this.checkScrollingState);
			if(!data.is_complete){ff.io.xhrPost(_t.base_url+'/ext_' + _t.network, {offset:data.offset}, dojo.hitch(_t, "addLoad"));}
		} else {
			dojo.query("a.facebookBtn", _t.rootNode).forEach(function(elem){
				level = parseInt(dojo.attr(elem, "_level"), 10);
				dojo.connect(elem, "onclick", dojo.hitch(_t.auth_provider, "doFBLogin", {level:level,success:dojo.hitch(_t, "draw")}));
			});
			dojo.query("a.twitterBtn", _t.rootNode).forEach(function(elem){
				level = parseInt(dojo.attr(elem, "_level"), 10);
				dojo.connect(elem, "onclick", dojo.hitch(_t.auth_provider, "doTWLogin", {level:level,success:dojo.hitch(_t, "draw")}));
			});
			 _t.rootNode = null;
		}
	}
	/* ================= BEGIN selectors ========================= */
	/* ================= SELECT inherited ======================== */
	,onSelect : function(elem, evt){
		this.checkScrollingState();
		dojo.query("p.inviterTwo", this.global_invited_node).addClass("hidden");
		this.inviteAppendNode(elem);
		var el = dojo.byId("invitedCounter");
		el.innerHTML = parseInt(el.innerHTML,10)+1;
	}
	,inviteAppendNode : function(elem){
		var _t = this;
		dojo.query(elem).orphan().forEach(function(elem){
			dojo.place(elem, _t.invited_node, "last");
			_t._selected[elem.id] = true;
		});
	}
	,uninviteAppendNode : function(elem){
		delete this._selected[elem.id];
		this.lazyReRender();
	}
	,unSelect : function(target){
		var _t = this;
		dojo.query(target).orphan().forEach(function(elem){
			_t.uninviteAppendNode(elem);
			var ctr = dojo.byId("invitedCounter");
			var newctr = parseInt(ctr.innerHTML,10)-1;
			ctr.innerHTML = newctr;
			if(newctr === 0){
				dojo.query("p.inviterTwo", _t.global_invited_node).removeClass("hidden");
			}
		});
	}
	/* ================= END selectors ========================= */
	,toggle_mutuals: function(evt) {
		this.mutuals = evt.target.checked;
		this.lazyReRender();
	}
	,filter : function(evt){
		if(evt.keyCode==27){this.filterNode.value="";this.current_filter="";}else if(evt.keyCode<45&&evt.keyCode!=8){return;}
		this.current_filter = this.filterNode.value.toLowerCase();
		this.lazyReRender();
	}
});


dojo.declare("friendfund.FriendTypeAhead", friendfund.DataProvider, {
	rootNode : null
	,_is_loading : false
	,_page_size : 5
	,current_filter : ""
	,_has_results : false
	,selectedValueNode : "selectedReceiver"
	,constructor : function(args){
		dojo.mixin(this, args);
		/* since selector is outside of refnode, and does not get rerendered, this can get out of sync */
		this._is_selected_decider = ".methodselector.ajaxlink.selected[_type="+this.network+"]";
		this.lazyReRender = ff.t.debounce(dojo.hitch(this, "reRender"), 100, false);
		this.mutuals = false;
		this.selectedValueNode = dojo.byId(this.selectedValueNode);
		this.checkScrollingState = ff.t.debounce(dojo.hitch(this, "_checkScrollingState"), 100, false);
	}
	,is_selected : function(){
		return dojo.query(this._is_selected_decider, this.container).length > 0;
	},connect : function(){
		this._listener_locals.push(dojo.connect(this.friendlist, "onclick", this, "select"));
		this._listener_locals.push(dojo.connect(this.filterNode, "onkeyup", this, "filter"));
		this._listener_locals.push(dojo.connect(window, "onclick", this, "onHideSelector"));
		this._listener_locals.push(dojo.connect(this.filterNode, "onfocus", this, "onShowSelector"));
		this._listener_locals.push(dojo.connect(this.friendlist.parentNode, "onscroll", this.checkScrollingState));
	}
	,onHideSelector:function(evt){
		if(!ff.t.findParent(evt.target, "typeAheadSelector")){
			this.hideSelector()
		};
	}
	,hideSelector:function(){
		var pn = ff.t.findParent(this.friendlist, "friendsList");
		dojo.addClass(pn, "hidden");
	}
	,onShowSelector:function(evt){
		evt.target.select();
		this.reRender();
		var tmp = dojo.position(this.friendlist.parentNode);
		this.friendlist_box = this.friendlist_box || tmp.y+tmp.h*1.5;
	}
	,showSelector:function(){
		if(this._has_results){
			var pn = ff.t.findParent(this.friendlist, "friendsList");
			dojo.removeClass(pn, "hidden");
		}
	}
	,undraw : function(){
		if(this.rootNode){dojo.addClass(this.rootNode, "hidden");}
		else {var l=dojo.query("#networkinviter_"+this.network); if(l.length){l.orphan();}}
		dojo.forEach(this._listener_locals, dojo.disconnect);
		this._listener_locals = [];
	}
	,onLoad : function(data){
		var _t = this;
		_t._is_loading = false;
		dojo.place(data.html, _t.rootNode, "only");
		if(data.success){
			_t.friendlist = dojo.byId("friend_list_"+_t.network);
			_t.friends_template = data.template;
			_t._addPage(data.friends, data.is_complete);
			_t.filterNode = dojo.byId("filter_"+_t.network);

			ff.w.parseDefaultsInputs(_t.ref_node);
			_t.connect();
			if(!data.is_complete){ff.io.xhrPost(_t.base_url+'/ext_' + _t.network, {offset:data.offset}, dojo.hitch(_t, "addLoad"));}
		} else {
			dojo.query("a.facebookBtn", _t.rootNode).forEach(function(elem){
				level = parseInt(dojo.attr(elem, "_level"), 10);
				dojo.connect(elem, "onclick", dojo.hitch(_t.auth_provider, "doFBLogin", {level:level,success:dojo.hitch(_t, "draw")}));
			});
			dojo.query("a.twitterBtn", _t.rootNode).forEach(function(elem){
				level = parseInt(dojo.attr(elem, "_level"), 10);
				dojo.connect(elem, "onclick", dojo.hitch(_t.auth_provider, "doTWLogin", {level:level,success:dojo.hitch(_t, "draw")}));
			});
			 _t.rootNode = null;
		}
	}
	/* ================= BEGIN selectors ========================= */
	/* ================= SELECT inherited ======================== */
	,onResultsFound : function(){
		this._has_results = true;
		this.showSelector();
	}
	,onNoResultsFound : function(){
		this._has_results = false;
		this.hideSelector();
	}
	,onSelect : function(elem, evt){
		this.inviteAppendNode(elem);
	}
	,inviteAppendNode : function(elem){
		var _t = this;
		var pn = ff.t.findParent(_t.friendlist, "typeAheadSelector");
		dojo.query("img.smallProfPic", pn).orphan();
		dojo.query("img", elem).forEach(function(n){
			var newn = dojo.create("IMG", {src:n.src, className:"smallProfPic"});
			dojo.place(newn, pn, "first");
		});
		var values = dojo.query("input", elem);
		if(values.length){_t.selectedValueNode.value = values[0].value;}
		_t.filterNode.value = dojo.query("p", elem).attr("innerHTML").join("");
		_t.current_filter = _t.filterNode.value.toLowerCase();
		dojo.query(_t.filterNode).removeClass("default").addClass("selected");
		_t.reRender();
		_t.onNoResultsFound();
	}
	,uninviteAppendNode : function(elem){}
	,unSelect : function(target){}
	/* ================= END selectors ========================= */
	,filter : function(evt){
		if(evt.keyCode==27){this.filterNode.value="";this.current_filter="";}else if(evt.keyCode<45&&evt.keyCode!=8){return;}
		this.current_filter = this.filterNode.value.toLowerCase();
		this.lazyReRender();
	}
});

}
