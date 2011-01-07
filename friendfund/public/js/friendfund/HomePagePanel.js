dojo.provide("friendfund.HomePagePanel");
dojo.provide("friendfund.MinifiedHomePagePanel");
dojo.require("dijit.form.DateTextBox");
dojo.require("dojo.NodeList-manipulate");
dojo.require("dojo.NodeList-traverse");
dojo.require("dojox.fx.scroll");
dojo.require("dojo.fx.easing");



dojo.declare("friendfund.HomePagePanel", null, {
	_widget_locals : [],
	_listener_locals : [],
	_listener_globals : [],
	receiver_selectors : {},
	selected_elems : {receiver:false, occasion:false, product:false},
	onLoaded : null,
	onSelected : null,
	onDestroy : null,
	scrolling : true,
	constructor: function(args){
		var _t = this;
		_t.window = window;
		dojo.mixin(_t, args);
		for (var action in _t.selected_elems){_t.connect(_t, action);}
		_t._listener_globals.push(dojo.connect(dojo.byId("funders_button"), "onclick", dojo.hitch(null, _t.submit, _t)));
		if(!_t.check_complete(_t) && _t.auto_extend){_t.preload(_t, _t.auto_extend, false);}
	},
	connect:function(_t, action){
		if(dojo.hasClass(action+"_panel", 'enabled')){
			_t._listener_globals.push(dojo.connect(dojo.byId("button_"+action), "onclick", dojo.hitch(null, _t.preload, _t, action, false)));
		}
	},
	submit:function(_t, evt){
		if (!dojo.hasClass(this, 'inactive')){
			dojo.forEach(_t._listener_globals, dojo.disconnect);
			_t._listener_globals = [];
			_t.window.location.href = dojo.byId("pool_configurator_form").action;
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
		if(complete===true){
			dojo.removeClass("funders_button", "inactive");
			dojo.addClass("funders_panel", "front_panel_active");
		}
		return complete;
	},
	set_complete : function(_t, action){
		_t.selected_elems[action] = true;
		_t.connect(_t, action);
		if(!_t.check_complete(_t) && _t.auto_suggest){
			var next = dojo.query(".frontpagebutton.enabled", _t.config_node);
			for(var i=0; i<next.length;i++){
				if(!_t.selected_elems[dojo.attr(next[i], "_type")]){
					_t.preload(_t, dojo.attr(next[i], "_type"), false); 
				}
			}
		}
	},
	preload: function(_t, action, open_at_all_costs, evt, params){
		/*check if any panel is open*/
		var panel = dojo.byId("button_panel");

		/*check if panel is of this/action or another kind, close it anyways */
		var thisisopen = panel && dojo.hasClass(panel, action);
		if (panel && ((thisisopen && !open_at_all_costs) || (!thisisopen))){_t.unload(_t, thisisopen);}
		
		/*if closed panel was of another kind, we now wanna open this */
		if (!thisisopen || open_at_all_costs){
			_t["load_"+action](_t, evt, params);
			if(_t.scrolling){
				var node = dojo.byId("button_panel_container_anchor");
				var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:500, easing:dojo.fx.easing.expoOut});
				anim0.play();
			}
		}
	}
	,load: function(_t, elem){
		if(_t.onLoad){this.onLoad(_t);}
		dojo.query("#get_started").orphan();
		dojo.query("#button_"+elem+".hpbutton a.panel_opener").addClass("opened");
		/* TODO: this gets disconnected on Product Panel Changing */
		dojo.query("a.button_panel_closer", "button_panel").onclick(dojo.hitch(null, _t.unload, _t, true));
		dojo.query("#"+elem+"_panel").addClass('front_panel_active');
		parseDefaultsInputs(_t.ref_node);
	},verify: function() {
		return false;
	},unload: function(_t, success){
		if(_t.onDestroy){_t.onDestroy();}
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		
		dojo.forEach(_t._widget_locals, function(item){item.destroy(item);});
		_t._widget_locals = [];
		_t.receiver_selectors = {};
		
		var picker = dijit.byId("datestamp");
		if(picker){picker.destroy();}
		dojo.query("*", _t.ref_node).orphan();
		dojo.query("#"+_t.ref_node).style("display", "None");
		dojo.query(".enabled.front_panel_active", _t.config_node).removeClass("front_panel_active");
		dojo.query("a.opened", _t.config_node).removeClass("opened");
		if(_t.scrolling && success === true){
			var node = dojo.byId("top");
			var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:500, easing:dojo.fx.easing.expoOut});
			anim0.play();
		}
	},
	/*                OCCASION PANELS               */
	load_occasion: function(_t, evt, args){
		var params = {};
		params.date = dojo.byId("occasion_date").value;
		params.key = dojo.byId("occasion_key").value;
		params.name = dojo.byId("occasion_name").value;
		params.dob = dojo.byId("receiver_dob")&&dojo.byId("receiver_dob").value||"";
		loadElement("/occasion/panel", _t.ref_node, params, dojo.hitch(null, _t.occLoaded, _t));
		return false;
	},occLoaded: function(_t){
		_t.load(_t, "occasion");
		dojo.query(".occasion_panel_button div.selector", _t.ref_node).forEach(
			function(item){_t._listener_locals.push(dojo.connect(item, "onclick", dojo.hitch(null, _t.occasion_preselect, _t)));});
		dojo.query(".occasion_submitter", _t.ref_node).forEach(
			function(item){_t._listener_locals.push(dojo.connect(item, "onclick", dojo.hitch(null, _t.occasion_selected, _t)));});
		dojo.query(".occasion_panel_button div.selector[custom=1] input", _t.ref_node).forEach(
			function(item){_t._listener_locals.push(dojo.connect(item, "onfocus", dojo.hitch(null, _t.occasion_focused, _t)));});
		
		dojo.parser.parse(dojo.byId(_t.ref_node));
		if(dijit.byId("datestamp")){_t._widget_locals.push(dijit.byId("datestamp"));}
		
		dojo.query(".black_labeled_input.dijitTextBox", _t.ref_node).forEach(
			function(item){_t._listener_locals.push(dojo.connect(item, "onclick", dijit.byId("datestamp"), "_open"));});
	}, occasion_focused: function(_t, evt){
		var elem = dojo.query(this).closest("div.selector")[0];
		dojo.hitch(elem, _t.occasion_preselect, _t)();
	}, occasion_preselect: function(_t, evt){
		dojo.query(".occasion_panel_button div.selector.selected", _t.ref_node).removeClass("selected");
		dojo.addClass(this, "selected");
		var datewijit = dijit.byId("datestamp");
		var newdate = dojo.attr(this, "date").split("-");
		newdate = (newdate.length>=3)?(new Date(newdate[0], newdate[1]-1, newdate[2])) : null;
		if(!datewijit.value) {
			if(newdate){
				datewijit.set("value", newdate);
			} else if (parseInt(dojo.attr(this, "custom"),10) === 0){
				datewijit.focus();
			}
		}
	}, occasion_selected : function(_t, evt){
		var selected = dojo.query(".occasion_panel_button div.selector.selected", _t.ref_node);
		var datepicker = dijit.byId("datestamp");
		if(datepicker.value && selected.length === 1 && datepicker.value >= datepicker.constraints.min){
			selected = dojo.query(".occasion_panel_button div.selector.selected", _t.ref_node)[0];
			
			var params = {};
			params['occasion.custom'] = dojo.attr(selected, "custom") === "1";
			params['occasion.key'] = dojo.attr(selected, "key");
			params['occasion.name'] = params['occasion.custom']?dojo.query("input", selected)[0].value:"";
			params['occasion.date'] = formatDate(datepicker.value);
			params['occasion.picture_url'] = dojo.attr(selected, "imgurl");
			loadElement("/occasion/set", "occasion_panel", params, dojo.hitch(null, _t.set_complete, _t, 'occasion'));
			_t.verify_dates(_t, {occasion_date:params['occasion.date']});
			_t.unload(_t, true);
		} else {
			var id = (!selected.length)?"occasion_button_bar":"occasion_date_input_bar";
			dojo.animateProperty(
				{node: dojo.byId(id),duration: 1000,
					properties: {
						backgroundColor: {start: "red", end: "#c7dee4"}
					}
				}
			).play();
		}
	},
	verify_dates : function(_t, args){
		args = args || {};
		var params = {net: args.affnet || dojo.byId("product_net").value,
						occasion_date : args.occasion_date || dojo.byId("occasion_date").value,
						progid: args.progid || dojo.byId("product_progid").value
					};
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
		_t._widget_locals.push(_t.productsearch);
		_t.productsearch.draw(_t.productsearch, null, params);
	},
	productSelected : function(_t, selection_args){
		var params = {};
		params["product.guid"] = selection_args.guid;
		params["product.is_virtual"] = selection_args.is_virtual;
		params["product.is_curated"] = selection_args.is_curated;
		params["product.is_amazon"] = selection_args.is_amazon;
		params["product.is_pending"] = selection_args.is_pending;
		loadElement("/product/set", "product_panel", params, 
			function(){
				_t.set_complete(_t, 'product');
				_t.verify_dates(_t, selection_args);
				_t.unload(_t, true);
		});
	},
	/*--------------- RECEIVER PANELS --------------*/
	
	load_receiver : function(_t, evt, params){
		xhrPost("/receiver/panel", params, dojo.hitch(null, _t.receiverLoaded, _t));
		return false;
	},
	receiverLoaded : function(_t, data){
		place_element(_t.ref_node)(data.html);
		_t.load(_t, "receiver");
		_t.receiver_selectors = new friendfund.CompoundFriendSelector(
							{
								container : "button_panel",
								ref_node: "receiver_selector_container",
								inviter_node : "friend_list",
								base_url : "/myfriends",
								avail_selectors : {'facebook':true, 'twitter':true, 'email':true, 'yourself':true},
								onSelect : function(ctx, params, elem, evt){
									loadElement("/receiver/set", "receiver_panel", params, dojo.hitch(null, _t.set_complete, _t, 'receiver'));
									_t.unload(_t, true);
									return true;
								}
							});
		_t.receiver_selectors.selectors.facebook.onSelect = function(ctx, params, elem, evt){
									loadElement("/receiver/set", "receiver_panel", params, dojo.hitch(null, _t.set_complete, _t, 'receiver'));
									_t.unload(_t, true);
									FB.api("/"+params.network_id, function(response){
										dojo.byId("receiver_email").value = response.email || "";
										dojo.byId("receiver_sex").value = response.gender || "";
									});
									return true;
								};
		_t._widget_locals.push(_t.receiver_selectors);
		_t.receiver_selectors.draw(data.method);
	}
});

dojo.declare("friendfund.MinifiedHomePagePanel", friendfund.HomePagePanel, {
	_displacement_backup : null,
	_change_observer : null,
	selected_elems : {receiver:false, occasion:false},
	constructor: function(args){
		var _t = this;
		_t._change_observer = dojo.connect(dojo.byId("product_selector"), "onchange", dojo.hitch(null, _t.productSelected, _t));
	},
	productSelected : function(_t, evt){
		dojo.disconnect(_t._change_observer);
		var selected_product = this.options[this.selectedIndex];
		loadElement("/product/set_minified", "product_panel", {product_guid:selected_product.value}, 
			function(){
				_t.set_complete(_t, 'product')
				_t._change_observer = dojo.connect(dojo.byId("product_selector"), "onchange", dojo.hitch(null, _t.productSelected, _t));
			}
		);
	},
	preload: function(_t, action, open_at_all_costs, evt, params){
		_t._displacement_backup = dojo.query(".displacement", _t.config_node).orphan();
		_t.inherited(arguments);
	},
	unload: function(_t, success){
		_t.inherited(arguments);
		if(_t._displacement_backup){_t._displacement_backup.forEach(function(elem){dojo.place(elem, _t.config_node, "last")});}
	},
	occLoaded: function(_t){
		_t.load(_t, "occasion");
		
		dojo.query("select", _t.ref_node).onchange(dojo.hitch(null, _t.occasion_preselect, _t));
		dojo.query(".occasion_submitter", _t.ref_node).onclick(dojo.hitch(null, _t.occasion_selected, _t));
		dojo.query(".dateopener", _t.ref_node).onclick(function(){dijit.byId("datestamp").focus()});
		dojo.parser.parse(dojo.byId(_t.ref_node));
		if(dijit.byId("datestamp")){_t._widget_locals.push(dijit.byId("datestamp"));}
		dojo.query("div.black_labeled_container a.button_open_down", _t.ref_node).connect("onclick", dojo.hitch(null, _t.openDatePicker, _t));
	}, openDatePicker:function(_t, evt){
		dijit.byId("datestamp").focus();
		evt.stopPropagation();
		evt.preventDefault();
		return false;
	}, occasion_preselect: function(_t, evt){
		var datewijit =dijit.byId("datestamp");
		var selected_date = this.options[this.selectedIndex];
		var newdate = dojo.attr(selected_date, "date").split("-");
		
		newdate = (newdate.length>=3)?(new Date(newdate[0], newdate[1]-1, newdate[2])) : null;
		if(!datewijit.value) {
			if(newdate){
				datewijit.set("value", newdate);
			}
			if (parseInt(dojo.attr(selected_date, "custom"),10) === 1){
				dojo.byId("occasion_custom_name").focus();
			}
		}
	},
	occasion_selected : function(_t, evt){
		var selected = dojo.query("select", _t.ref_node);
		var datepicker = dijit.byId("datestamp");
		if(datepicker.value && selected.length === 1 && datepicker.value >= datepicker.constraints.min){
			selected = selected[0].options[selected[0].selectedIndex];
			var params = {};
			params['occasion.custom'] = dojo.byId("occasion_custom_name").value !== "";
			params['occasion.key'] = dojo.attr(selected, "key");
			params['occasion.name'] = params['occasion.custom']?dojo.byId("occasion_custom_name").value:"";
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
						backgroundColor: {start: "red", end: "#89A79E"}
					}
				}
			).play();
		}
	}
});












