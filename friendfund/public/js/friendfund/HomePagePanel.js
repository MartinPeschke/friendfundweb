dojo.provide("friendfund.HomePagePanel");
dojo.require("dijit.form.DateTextBox");
dojo.require("dojo.date.locale");
dojo.require("dojo.NodeList-manipulate");
dojo.require("dojo.NodeList-traverse");
dojo.require("dojox.fx.scroll");
dojo.require("dojo.fx.easing");



dojo.declare("friendfund.HomePagePanel", null, {
	_widget_list : [],
	_listener_locals : [],
	_listener_globals : [],
	receiver_selectors : {},
	selected_elems : {receiver:false, occasion:false, product:false},
	onLoaded : null,
	onSelected : null,
	onDestroy : null,
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		for (var action in _t.selected_elems){
			_t.connect(_t, action);
		}
		_t._listener_globals.push(dojo.connect(dojo.byId("funders_button"), "onclick", dojo.hitch(null, _t.submit, _t)));
		_t.check_complete(_t);
	},
	connect:function(_t, action){
		dojo.connect(dojo.byId("button_"+action), "onclick", dojo.hitch(null, _t.preload, _t, action, false));
	},
	submit:function(_t, evt){
		if (!dojo.hasClass(this, 'inactive')){
			dojo.forEach(_t._listener_globals, dojo.disconnect);
			_t._listener_globals = [];
			dojo.byId("pool_configurator_form").submit();
		} else {
			dojo.removeClass("funders_panel_tooltip", "hidden");
			dojo.style("funders_panel_tooltip", "opacity", "1");
			dojo.fadeOut({node: dojo.byId("funders_panel_tooltip"),duration: 5000}).play();
		}
	},check_complete : function(_t){
		var complete = true;
		for (var elem in _t.selected_elems){
			complete = _t.selected_elems[elem] && complete;
		}
		if(complete==true){dojo.removeClass("funders_button", "inactive");}
		return complete;
	},
	set_complete : function(_t, action){
		_t.selected_elems[action] = true;
		_t.connect(_t, action);
		_t.check_complete(_t);
	},
	preload: function(_t, action, open_at_all_costs, evt, params){
		/*check if any panel is open*/
		var panel = dojo.byId("button_panel");

		/*check if panel is of this/action or another kind, close it anyways */
		var thisisopen = panel && dojo.hasClass(panel, action);
		if (panel && ((thisisopen && !open_at_all_costs) || (!thisisopen)))_t.unload(_t, thisisopen);
		
		/*if closed panel was of another kind, we now wanna open this */
		if (!thisisopen || open_at_all_costs){
			_t["load_"+action](_t, evt, params);
			var node = dojo.byId("button_panel_container_anchor");
			var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:500, easing:dojo.fx.easing.expoOut});
			anim0.play();
		}
	},load: function(_t, elem){
		_t.onLoad && this.onLoad(_t);
		dojo.query("#get_started").orphan();
		dojo.query("#"+elem+"_panel.frontpagebutton div.extender").removeClass("hidden");
		dojo.query("#button_"+elem+".hpbutton a.panel_opener").addClass("opened");
		dojo.query("a.button_panel_closer", "button_panel").onclick(dojo.hitch(null, _t.unload, _t, true));
		dojo.query("#"+elem+"_panel").addClass('front_panel_active');
		parseDefaultsInputs(_t.ref_node);
	},verify: function() {
		return false;
	},unload: function(_t, success){
		_t.onDestroy && _t.onDestroy();
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		dojo.forEach(_t._widget_list, function(item){item.destroy();});
		_t._widget_list = [];
		for (var item in _t.receiver_selectors){item = _t.receiver_selectors[item]; item.unload(item);};
		_t.receiver_selectors = {};
		var picker = dijit.byId("datestamp");
		picker && picker.destroy();
		dojo.query("*", _t.ref_node).orphan();
		dojo.query(_t.ref_node).style("display", "None");
		dojo.query("div.extender", _t.config_node).addClass("hidden");
		dojo.query(".front_panel_active", _t.config_node).removeClass("front_panel_active");
		dojo.query("a.opened", _t.config_node).removeClass("opened");
		if(success == true){
			var node = dojo.byId("top");
			var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:500, easing:dojo.fx.easing.expoOut});
			anim0.play();
		}
	},
	
	/*                OCCASION PANELS               */
	load_occasion: function(_t, evt, params){
		var params = {};
		params.date = dojo.byId("occasion_date").value;
		params.key = dojo.byId("occasion_key").value;
		params.name = dojo.byId("occasion_name").value;
		loadElement("/occasion/panel", _t.ref_node, params, dojo.hitch(null, _t.occLoaded, _t));
		return false;
	},occLoaded: function(_t){
		_t.load(_t, "occasion");
		
		dojo.query(".occasion_panel_button div.selector", _t.ref_node).onclick(dojo.hitch(null, _t.occasion_preselect, _t));
		dojo.query(".occasion_submitter", _t.ref_node).onclick(dojo.hitch(null, _t.occasion_selected, _t));
		
		dojo.query(".occasion_panel_button div.selector[custom=1] input", _t.ref_node).connect("onfocus", dojo.hitch(null, _t.occasion_focused, _t));
		
		dojo.parser.parse(dojo.byId(_t.ref_node));
		dijit.byId("datestamp") && _t._widget_list.push(dijit.byId("datestamp"));
		dojo.query("div.black_labeled_container a.button_open_down", _t.ref_node).connect("onclick", dojo.hitch(null, _t.openDatePicker, _t));
	}, openDatePicker:function(_t, evt){
		dijit.byId("datestamp").focus();
		evt.stopPropagation();
		evt.preventDefault();
		return false;
	}, occasion_focused: function(_t, evt){
		var elem = dojo.query(this).closest("div.selector")[0];
		dojo.hitch(elem, _t.occasion_preselect, _t)();
	}, occasion_preselect: function(_t, evt){
		dojo.query(".occasion_panel_button div.selector.selected", _t.ref_node).removeClass("selected");
		dojo.addClass(this, "selected");
		var datewijit =dijit.byId("datestamp");
		var newdate = dojo.attr(this, "date").split("-");
		newdate = (newdate.length>=3)?(new Date(newdate[0], newdate[1]-1, newdate[2])) : null;
		if(datewijit.value===null) {
			if(newdate!=null){
				datewijit.set("value", newdate);
			} else if (parseInt(dojo.attr(this, "custom")) == 0){
				datewijit.focus();
			}
		}
		evt.stopPropagation();
		evt.preventDefault();
		return false;
	},
	occasion_selected : function(_t, evt){
		var selected = dojo.query(".occasion_panel_button div.selector.selected", _t.ref_node).length == 1;
		var datepicker = dijit.byId("datestamp");
		if(datepicker.value && selected && datepicker.value >= datepicker.constraints.min){
			var selected = dojo.query(".occasion_panel_button div.selector.selected", _t.ref_node)[0];
			
			var params = {};
			params['occasion.custom'] = dojo.attr(selected, "custom") == "1";
			params['occasion.key'] = dojo.attr(selected, "key");
			params['occasion.name'] = params['occasion.custom']?dojo.query("input", selected)[0].value:"";
			params['occasion.date'] = formatDate(datepicker.value);
			params['occasion.picture_url'] = dojo.attr(selected, "imgurl");
			loadElement("/occasion/set", "occasion_panel", params, dojo.hitch(null, _t.set_complete, _t, 'occasion'));
			_t.verify_dates(_t, {occasion_date:params['occasion.date']});
			_t.unload(_t, true);
		} else {
			var id = (!selected)?"occasion_button_bar":"occasion_date_input_bar";
			dojo.animateProperty(
				{node: dojo.byId(id),duration: 1000,
					properties: {
						backgroundColor: {start: "red", end: "#c7dee4"}
					}}).play();
			evt.stopPropagation();
			evt.preventDefault();
			return false;
		}
	},
	
	verify_dates : function(_t, args){
		args = args || {};
		var params = {net: args.net || dojo.byId("product_net").value,
						occasion_date : args.occasion_date || dojo.byId("occasion_date").value,
						progid: args.progid || dojo.byId("product_progid").value
					}
		if(params.net && params.occasion_date && params.progid){
			xhrPost("/product/verify_dates", params);
		}
	},
	
	/*--------------- PRODUCT PANELS --------------*/
	load_product : function(_t, evt, params){
		_t.productsearch = new friendfund.ProductSearch({
			ref_node : _t.ref_node,
			onLoaded : dojo.hitch(null, _t.load, _t, "product"),
			onSelected : dojo.hitch(null, _t.productSelected, _t),
			searchMixin : function(){
						var args = {
							occasion_key : dojo.byId("occasion_key").value||null,
							occasion_date : dojo.byId("occasion_date").value||null,
							sex : dojo.byId("receiver_sex").value||null
						};
						return args;
					}
			});
		_t.productsearch.draw(_t.productsearch, null, params);
	},
	productSelected : function(_t, selection_args){
		var params = {};
		params["product.guid"] = selection_args.guid;
		params["product.is_virtual"] = selection_args.is_virtual;
		params["product.aff_net"] = selection_args.net;
		params["product.aff_program_id"] =  selection_args.progid;
		loadElement("/product/set", "product_panel", params, dojo.hitch(null, _t.set_complete, _t, 'product'));
		_t.verify_dates();
		_t.unload(_t, true);
	},
	/*--------------- RECEIVER PANELS --------------*/
	
	load_receiver : function(_t, evt, params){
		var params = {};
		xhrPost("/receiver/panel", params, dojo.hitch(null, _t.receiverLoaded, _t));
		return false;
	},
	receiverLoaded : function(_t, data){
		place_element(_t.ref_node)(data.html);
		_t.load(_t, "receiver");
		_t.receiver_selectors.facebook = new friendfund.NetworkFriendSelector(
							{
								container : "button_panel"
								, ref_node: "receiver_selector_container"
								, inviter_node : "friend_list"
								, base_url : "/receiver"
								, network : "facebook"
								, onSelect : function(networkid, name, pos, elem, evt){
									var params = {};
									params["receiver.network"] = "facebook";
									params["receiver.network_id"] = networkid;
									params["receiver.name"] = name;
									params["receiver.profile_picture_url"] = dojo.attr(elem, "large_profile_picture_url");
									
									loadElement("/receiver/set", "receiver_panel", params, dojo.hitch(null, _t.set_complete, _t, 'receiver'));
									_t.unload(_t, true);
									FB.api("/"+networkid, function(response){
										dojo.byId("receiver_email").value = response.email || "";
										dojo.byId("receiver_sex").value = response.gender || "";
									});
									return true;
								}
							});
		_t.receiver_selectors.twitter = new friendfund.NetworkFriendSelector(
							{
								container : "button_panel"
								, ref_node: "receiver_selector_container"
								, inviter_node : "friend_list"
								, base_url : "/receiver"
								, network : "twitter"
								, onSelect : function(networkid, name, pos, elem, evt){
									var params = {};
									params["receiver.network"] = "twitter";
									params["receiver.network_id"] = networkid;
									params["receiver.name"] = name;
									params["receiver.profile_picture_url"] = dojo.attr(elem, "large_profile_picture_url");
									
									loadElement("/receiver/set", "receiver_panel", params, dojo.hitch(null, _t.set_complete, _t, 'receiver'));
									_t.unload(_t, true);
									return true;
								}
							});
		_t.receiver_selectors.email = new friendfund.EmailFriendSelector(
						{
							ref_node: "receiver_selector_container"
							, base_url : "/receiver"
							, onSelect : function(ctx, data){
									if(data.success===true){
										var params = {};
										params["receiver.network"] = data.network || "";
										params["receiver.network_id"] = data.network_id || "";
										params["receiver.name"] =  data.name || "";
										params["receiver.email"] =  data.email || "";
										params["receiver.sex"] =  data.gender || "";
										params["receiver.profile_picture_url"] = data.imgurl;
										loadElement("/receiver/set", "receiver_panel", params, dojo.hitch(null, _t.set_complete, _t, 'receiver'));
										_t.unload(_t, true);
									} else {
										dojo.place(data.message, dojo.byId("email_inviter_error"), "only");
									}
								}
						});
			_t.receiver_selectors.yourself = new friendfund.YourselfSelector(
						{
							base_url : "/receiver"
							,ref_node: "receiver_selector_container"
							,onSelect : function(ctx, data){
									if(data.success===true){
										var params = {};
										params["receiver.network"] = data.network || "";
										params["receiver.network_id"] = data.network_id || "";
										params["receiver.name"] =  data.name || "";
										params["receiver.email"] =  data.email || "";
										params["receiver.sex"] =  data.gender || "";
										params["receiver.profile_picture_url"] = data.imgurl;
										loadElement("/receiver/set", "receiver_panel", params, dojo.hitch(null, _t.set_complete, _t, 'receiver'));
										_t.unload(_t, true);
									} else {
										dojo.place(data.html, ctx.ref_node, "only");
									}
							}
						});
		_t.receiver_selectors[data.method].draw();
		dojo.query("a.ajaxlink", _t.ref_node).onclick(
			function(evt){
				dojo.query("a.ajaxlink.selected", _t.ref_node).removeClass("selected");
				dojo.addClass(this, "selected");
				if(dojo.attr(this, "_type") in _t.receiver_selectors)_t.receiver_selectors[dojo.attr(this, "_type")].draw();
				evt.stopPropagation();
				evt.preventDefault();
				return false;
		});
	}
});