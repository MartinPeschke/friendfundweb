/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/

if(!dojo._hasResource["friendfund.EmailFriendSelector"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["friendfund.EmailFriendSelector"] = true;
dojo.provide("friendfund.EmailFriendSelector");




dojo.declare("friendfund._Selector", null, {
	_listener_locals : [],
	_loader : "<div style=\"margin: 0px auto;text-align:center;padding:30px;\"><div class=\"loading_animation\"><img src=\"/static/imgs/ajax-loader.gif\"></div></div>",
	draw: function(){console.log("NOT_IMPLEMENTED");},
	destoy: function(){console.log("NOT_IMPLEMENTED");},
	uninviteAppendNode : function(elem){},
	inviteAppendNode : function(elem){}
});


dojo.declare("friendfund.YourselfSelector", friendfund._Selector, {
	constructor: function(args){
		dojo.mixin(this, args);
		this.ref_node = dojo.isString(this.ref_node) && dojo.byId(this.ref_node) || this.ref_node;
	},draw : function(){
		ff.io.xhrPost(this.base_url+"/validate", {"invitee.network":"yourself"}, dojo.hitch(this, "_onSelect"));
	},_onSelect : function(data){
		if(data.success===true){
			this.onSelect(data, data.html, null);
		} else {
			dojo.place(data.html, this.ref_node, "only");
		}
	},
	onSelect : function(params, elem, evt){},
	undraw :function(){},
	destroy:function(){}
});


dojo.declare("friendfund.EmailFriendSelector", friendfund._Selector, {
	_listener_locals : [],
	rootNode : null,
	constructor: function(args){
		dojo.mixin(this, args);
		this.ref_node = dojo.isString(this.ref_node) && dojo.byId(this.ref_node) || this.ref_node;
	},
	draw : function(){
		if(this.rootNode){
			dojo.removeClass(this.rootNode, "hidden");
			dojo.query("input[type=text]", this.rootNode)[0].focus();
		} else {
			this.rootNode = dojo.create("DIV", {"id":("networkinviter_"+this.network)});
			dojo.byId(this.ref_node).appendChild(this.rootNode);
			dojo.place(this._loader, this.rootNode, "only");
			ff.io.xhrPost(this.base_url+'/' + this.network, {}, dojo.hitch(this, "onLoad"));
		}
	},
	onLoad : function(html){
		dojo.place(html, this.rootNode, "only");
		this._listener_locals.push(dojo.connect(this.ref_node, "onclick", this, "selectClick"));
		this._listener_locals.push(dojo.connect(this.ref_node, "onkeydown", dojo.hitch(this, ff.t.accessability, dojo.hitch(this, "select"), function(){})));
		ff.w.parseDefaultsInputs(this.rootNode);
		dojo.query("input[type=text]",this.rootNode)[0].focus();
	},
	undraw : function(){
		dojo.addClass(this.rootNode, "hidden");
	},
	destroy : function(){
		dojo.forEach(this._listener_locals, dojo.disconnect);
		this._listener_locals = [];
	},
	selectClick : function(evt){
		if(evt.target.id==="emailsubmitter"){this.select(evt);}
	},
	select : function(evt){
		var tab = dojo.byId("email_email");
		if(tab && tab.value.length > 0){
			ff.io.xhrFormPost(this.base_url+"/validate", "emailinviter", dojo.hitch(this, "_onSelect"));
		}
	},
	_onSelect : function(data){
		if(data.success===true){
			this.onSelect(data.html, null);
			dojo.place(data.input_html, this.rootNode, "only");
		} else {
			dojo.place(data.html, this.rootNode, "only");
		}
		var input = dojo.query("input[type=text]", this.rootNode)[0];
		ff.w.parseDefaultsInputs(this.rootNode);
		if(input){input.focus();}
	},
	inviteAppendNode : function(elem){
		dojo.place(elem, this.invited_node, "last");
		dojo.query("input[type=text]", "emailinviter").attr("value", "");
		dojo.query("#email_inviter_error", "emailinviter").orphan();
	},
	onSelect : function(elem, evt){
		dojo.query("p.inviterTwo", this.global_invited_node).addClass("hidden");
		this.inviteAppendNode(elem);
		var el = dojo.byId("invitedCounter");
		el.innerHTML = parseInt(el.innerHTML,10)+1;

	},
	unSelect : function(target){
		dojo.query(target).orphan();
		elem = dojo.byId("invitedCounter");
		elem.innerHTML = parseInt(elem.innerHTML,10)-1;
	}
});

}

if(!dojo._hasResource["friendfund.NetworkFriendSelector"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["friendfund.NetworkFriendSelector"] = true;
dojo.provide("friendfund.NetworkFriendSelector");




dojo.declare("friendfund.NetworkFriendPanel", friendfund._Selector, {
	constructor : function(args){
		dojo.mixin(this, args);
	},draw : function(){
		ff.io.xhrPost(this.base_url+'/' + this.network, {}, dojo.hitch(this, "onLoad"));
	},onLoad : function(data){
		dojo.place(data.html, this.ref_node, "only");
		dojo.style(this.ref_node, 'display', 'Block');
	},destroy : function(){
		dojo.forEach(this._listener_locals, dojo.disconnect);
		this._listener_locals = [];
	},select : function(evt){
		var target = ff.t.findParent(evt.target, "invitee_row");
		if(target){
			this.checkScrollingState()
			return this.onSelect(target, evt);
		}
	}
});

dojo.declare("friendfund.DataProvider", friendfund.NetworkFriendPanel, {
	constructor : function(args){
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
		if(show_more){result.push( "<li id=\"loading_placeholder_"+this.network+"\">&nbsp;</li>" )}
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
		if(page.length){dojo.place(page.join(""), this.friendlist, "only");}else{delete dojo.query("*", this.friendlist).orphan();}
	}
	
	,_checkScrollingState : function(evt){
		friendlist_loader = dojo.byId("loading_placeholder_"+this.network);
		if(!friendlist_loader){return;}
		var pos = dojo.position(friendlist_loader);
		if(pos.y < friendlist_box){
			if(this.hasMoreFriends()){
				dojo.place(this.getNextPage().join(""), friendlist_loader, "before");
			}
		}
	}
});


dojo.declare("friendfund.NetworkFriendSelector", friendfund.DataProvider, {
	rootNode : null
	,_is_loading : false
	,_page_size : 20
	,current_filter : ""
	,_selected : {}
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
	,draw : function(){
		if(this.rootNode){
			dojo.removeClass(this.rootNode, "hidden");
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
			friendlist_box = dojo.position(_t.friendlist);
			friendlist_box = friendlist_box.h*2 + friendlist_box.y;
			_t.friends_template = data.template;
			var toggler = dojo.byId("toggle_mutuals_"+_t.network);
			if(toggler){
				dojo.connect(toggler, "onclick", _t, "toggle_mutuals");
				_t.mutuals = toggler.checked;;
			} else {_t.mutuals = false;}

			
			
			_t._addPage(data.friends, data.is_complete);
			_t.reRender()
			
			_t.filterNode = dojo.byId("filter_"+_t.network);
			dojo.connect(_t.friendlist, "onclick", _t, "select");
			dojo.connect(_t.filterNode, "onkeyup", _t, "filter");
			ff.w.parseDefaultsInputs(_t.ref_node);
			dojo.connect(_t.friendlist, "onscroll", this.checkScrollingState);
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
	,addLoad : function(data){
		if(!!data.friends){
			this._addPage(data.friends, data.is_complete);
		}
		if(!data.is_complete){
			ff.io.xhrPost(this.base_url+'/ext_' + this.network, {offset:data.offset}, dojo.hitch(this, "addLoad"));
		}
	}
	/* ================= BEGIN selectors ========================= */
	/* ================= SELECT inherited ======================== */
	,onSelect : function(elem, evt){
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
	,renderUserAndPlace:function(udata){
		dojo.place(ff.t.render(this.friends_template, udata), this.friendlist, "last");
	}
});

}

if(!dojo._hasResource["friendfund.CompoundFriendSelector"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["friendfund.CompoundFriendSelector"] = true;
dojo.provide("friendfund.CompoundFriendSelector");





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
		if(dojo.hasClass(evt.target, "selected")){return;}
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













}

if(!dojo._hasResource["friendfund.InvitePage"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["friendfund.InvitePage"] = true;
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
								auth_provider : _t.auth_provider
								,container : _t.container
								,ref_node: "inviter"
								,invited_node_suffix : "_invitees"
								,inviter_node : "friend_list"
								,base_url : _t.base_url
								,global_invited_node : _t.invited_node
								,avail_selectors : {'facebook':true, 'twitter':true, 'email':true}
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
		return _t.auth_provider.checkLogin({level:level, success:dojo.hitch(_t, "_submit"), fail:function(){_t.submitting = false}});
 	},_submit:function(){
		var _t = this;
		dojo.forEach(_t._widget_locals, function(item){item.destroy(item);});
		_t._widget_locals = [];
		_t.receiver_selectors = {};
		dojo.query("input.addRefContent", _t.target_form).forEach(function(elem){elem.value = dojo.byId(dojo.attr(elem, "_source")).value;});
		dojo.byId(_t.target_form).submit();
	}
});












}

if(!dojo._hasResource["friendfund.PartnerPanel"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["friendfund.PartnerPanel"] = true;
dojo.provide("friendfund.PartnerPanel");

dojo.declare("friendfund.PartnerPanel", null, {
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.triedSubmitting = false;
		_t.target_form = dojo.isString(_t.target_form) && dojo.byId(_t.target_form) || _t.target_form;
		_t.connect();
		_t.load_receiver();
	},
	connect : function(){
		var _t = this;
		if(dojo.byId("productSelector")){dojo.connect(dojo.byId("productSelector"), "onchange", dojo.hitch(_t, _t.swapProduct));}
		if(dojo.byId("occasionSelector")){dojo.connect(dojo.byId("occasionSelector"), "onchange", dojo.hitch(_t, _t.swapOccasionName));}
		dojo.connect(dojo.byId("occasionTyper"), "onkeyup", dojo.hitch(_t, _t.changeOccasionName));
	},
	changeOccasionName : function(evt){
		var _t = this;
		if(evt.target.value){
			dojo.byId(dojo.attr(evt.target, "_target")).value = evt.target.value;
		} else {
			var fake_evt = {target:dojo.byId("occasionSelector")};
			this.swapOccasionName(fake_evt);
		}
		_t.check_occasion_name();
	},
	swapOccasionName : function(evt){
		var _t = this;
		var selected_occasion = evt.target.options[evt.target.selectedIndex];
		dojo.byId(dojo.attr(evt.target, "_name_target")).value = selected_occasion.value;
		dojo.byId(dojo.attr(evt.target, "_key_target")).value = dojo.attr(selected_occasion, "key");
		_t.check_occasion_name();
	},
	swapProduct : function(evt){
		var selected_product = evt.target.options[evt.target.selectedIndex];
		dojo.query(".selectedProduct", "productArea").removeClass("selectedProduct").addClass("hidden");
		dojo.query("#product_"+dojo.attr(selected_product, "_guid")).addClass("selectedProduct").removeClass("hidden");
	},
	load_receiver : function(){
		var _t = this;
		_t.selector = new friendfund.CompoundFriendSelector({
								auth_provider : _t.auth_provider
								,container : _t.container
								,ref_node: "inviter"
								,invited_node_suffix : "_invitees"
								,inviter_node : "friend_list"
								,base_url : _t.base_url
								,mutuals : false
								,global_invited_node : _t.invited_node
								,avail_selectors : {'facebook':true, 'twitter':true, 'email':true}
								,onSelect : function(elem, evt){
									_t.selector.removeAll();
									this.inviteAppendNode(elem);
									dojo.addClass(_t.invited_node, "filled");
									_t.check_receiver();
									return true;
								}
								,unSelect : function(target){
									dojo.query('#'+target.id, this.invited_node).orphan().forEach(dojo.hitch(this, "uninviteAppendNode"));
									dojo.removeClass(_t.invited_node, "filled");
								}
							});
		_t.selector.draw(_t.method);
	},
	submit : function(url, level, evt){
		var _t = this;
		var complete = _t.checkCompleteness();
		if(!complete||_t.submitting){
			return false;
		} else {
			ff.t.onSubmitCleaner(_t.target_form);
			_t.submitting = true;
			return _t.auth_provider.checkLogin({level:level, success:dojo.hitch(_t, "_submit", url), fail:function(){_t.submitting = false}});
		};
 	},_submit:function(url){
		var _t = this;
		dojo.query("input[type=submit]").attr("disabled","disabled");
		_t.target_form.action = url;
		_t.target_form.onsubmit = function(){};
		_t.target_form.submit();
	},
	
	
	
	
	checkCompleteness : function(){
		var _t = this;
		return _t.check_receiver()&&_t.check_occasion_name();
	},
	check_receiver : function(clean_only){
		if(dojo.query(".invitee_row", "network_invitees").length != 1){
			dojo.query(".errorHook", "receiverSelectorContainer").addClass("error");
			dojo.query(".errorMsgIframe", "selectedReceiverContainer").removeClass("hidden");
			return false;
		} else {
			dojo.query(".errorHook", "receiverSelectorContainer").removeClass("error");
			dojo.query(".errorMsgIframe", "selectedReceiverContainer").addClass("hidden");
			return true;
		}
	},
	check_occasion_name : function(clean_only){
		var oname = dojo.byId("occasion_name");
		var parental = ff.t.findParent(oname, "generalBoxIframe");
		if(!oname.value){
			dojo.query(".errorMsgIframe", parental).removeClass("hidden");
			dojo.query("#yourOccasionSelector,#occasionSelectorContainer").addClass("error");
			return false;
		} else {
			dojo.query(".errorMsgIframe", parental).addClass("hidden");
			dojo.query("#yourOccasionSelector,#occasionSelectorContainer").removeClass("error");
			return true;
		}
	}
});

}

