dojo.provide("friendfund.ProductSearch");
dojo.require("dojo.NodeList-manipulate");
dojo.require("dojo.NodeList-traverse");
dojo.require("dojox.fx.scroll");
dojo.require("dojo.fx.easing");
dojo.require("dojox.widget.AutoRotator");


dojo.require("dojox.widget.rotator.Pan");
dojo.require("friendfund.Tooltip");


dojo.declare("friendfund.ProductSearch", null, {
	_listener_locals : [],
	_widget_locals : [],
	onLoaded : null,
	onSelected : null,
	searchMixin : null,
	canSelectRegion:true,
	productBrowser : "product_browser_container",
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
	},
	draw : function(_t, evt, extra_params){
		var params = _t.searchMixin && _t.searchMixin() || {};
		if(extra_params==null || extra_params == {}){
			loadElement("/product/recommended_tab", _t.ref_node, params, dojo.hitch(null, _t.productLoaded, _t));
		} else {
			dojo.mixin(params, extra_params);
			loadElement("/product/search", _t.ref_node, params, dojo.hitch(null, _t.productLoaded, _t));
		}
		return false;
	},
	loadProductBrowser : function(_t, target, extra_params){
		var base_url = dojo.attr(target, "_base_url");
		var params = {sort:dojo.attr(target, "sort")||"RANK",page:dojo.attr(target, "page")||1}
		dojo.forEach(dojo.attr(target, "_search_keys").split(","), 
					function(key){params[key.substring(1)]=dojo.attr(target, key)}
				);
		dojo.mixin(params, extra_params);
		loadElement("/product/"+base_url, _t.productBrowser, params, function(){
			var node = dojo.byId(_t.productBrowser);
			var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:500, easing:dojo.fx.easing.expoOut});
			anim0.play();
		});
		var node = dojo.byId(_t.productBrowser);
		var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:500, easing:dojo.fx.easing.expoOut});
		anim0.play();
	},
	loadResults : function(_t, evt){
		var target=null;
		if(dojo.hasClass(evt.target, "anchorelem"))target=evt.target;
		else target = dojo.query(evt.target).parents(".anchorelem")[0];
		if(!target || target.id == "psort" || target.id == "region_picker")return;
		
		if(dojo.hasClass(target, "productselector")){
			return dojo.hitch(target, _t.productSelected, _t)();
		} else if(dojo.hasClass(target, "methodselector")){
			loadElement("/product/"+dojo.attr(target, "_base_url"), _t.ref_node, {}, dojo.hitch(null, _t.reinit, _t));
		} else if(dojo.hasClass(target, "popuplink")){
			dojo.hitch(target, loadPopup)(evt);
		} else if(dojo.hasClass(target, "searcher")){
			if (!dojo.hasClass(dojo.byId("pq"), "default"))
				_t.loadProductBrowser(_t, target, {searchterm:dojo.byId("pq").value});
		} else if(dojo.hasClass(target, "arrow")){
			if(dojo.hasClass(target, "arrowforward")){
				dojo.publish('productslider/rotator/control', ['next']);
			} else if(dojo.hasClass(target, "arrowback")){
				dojo.publish('productslider/rotator/control', ['prev']);
			}
		} else {
			_t.loadProductBrowser(_t, target);
		}
	},
	monitorChange : function(_t, evt){
		if (evt.target.id == "psort")_t.switchSort(_t, evt);
		else if (evt.target.id == "region_picker")_t.region_picker(_t, evt);
	},
	switchSort : function(_t, evt){
		if(dojo.hasClass(evt.target, "anchorelem"))_t.loadProductBrowser(_t, evt.target, {sort:evt.target.value});
	},
	region_picker:function(_t, evt){
		var params = _t.searchMixin && _t.searchMixin() || {};
		params[evt.target.name] = evt.target.value;
		params["action"] = dojo.attr(evt.target, "_base_url");
		loadElement("/product/set_region", _t.ref_node, params, dojo.hitch(null, _t.reinit, _t));
	},
	
	init_slider : function(_t){
		parseDefaultsInputs(_t.ref_node);
		if(dojo.query("div.productsuggestion", "scrollingproductsuggestions").length > 0)
		{
			dojo.parser.parse(dojo.byId("scrollingproductsuggestions"));
			dijit.byId("productslider") && _t._widget_list.push(dijit.byId("productslider"));
			dojo.query("div.productsuggestion", "scrollingproductsuggestions").forEach(function(elem){
					_t._widget_locals.push(
						new friendfund.Tooltip({
							connectId: [dojo.attr(elem, '_target_id')],
							label: dojo.query("textarea", elem)[0].value,
							position: ["below"]
						})
					);
			});
			dojo.query(".dijitTooltipContainer").forEach(function(elem){
				_t._listener_locals.push(dojo.connect(elem, "onclick", dojo.hitch(null, _t.loadResults, _t)));
			});
		}
	},productLoaded: function(_t){
		_t.onLoaded && _t.onLoaded(_t);
		if (!_t.canSelectRegion){dojo.query("#region_picker", _t.ref_node).attr("disabled","disabled")}
		_t._listener_locals.push(dojo.connect(dojo.byId(_t.ref_node), "onclick", dojo.hitch(null, _t.loadResults, _t)));
		_t._listener_locals.push(dojo.connect(dojo.byId(_t.ref_node), "onchange", dojo.hitch(null, _t.monitorChange, _t)));
		_t._listener_locals.push(dojo.connect(dojo.byId(_t.ref_node), "onkeyup", dojo.hitch(null, _t.accessability, _t)));
		_t.init_slider(_t);
	},destroy : function(_t){
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		dojo.forEach(_t._widget_locals, function(item){item.destroy(item);});
		_t._widget_locals = [];
	},
	reinit : function(_t, evt){
		_t.destroy(_t);
		_t.productLoaded(_t);
		
	},accessability : function(_t, evt){
		if(evt.target.id == 'pq'){
			switch (evt.keyCode){
				case (dojo.keys.ENTER):
					if (!dojo.hasClass(dojo.byId("pq"), "default"))
						_t.loadProductBrowser(_t, dojo.byId("searchsubmitter"), {searchterm:dojo.byId("pq").value});
					break;
				case (dojo.keys.ESCAPE):
					dojo.byId("pq").value = "";
					break;
			}
		}
	},
	productSelected : function(_t, evt){
		var return_args = {guid : dojo.attr(this, "_guid"),
			net : dojo.attr(this, "_net"),
			progid : dojo.attr(this, "_progid"),
			imgurl : dojo.attr(this, "_imgurl"),
			is_virtual : dojo.attr(this, "_is_virtual"),
			label : dojo.attr(this, "_label"),
			element : this};
		_t.onSelected && _t.onSelected(return_args);
	}
});