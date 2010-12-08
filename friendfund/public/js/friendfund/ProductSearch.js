dojo.provide("friendfund.ProductSearch");
dojo.require("dojox.fx.scroll");
dojo.require("dojo.fx.easing");
dojo.require("friendfund.Tooltip");
dojo.require("dojo.NodeList-manipulate");
dojo.require("dojo.NodeList-traverse");

dojo.declare("friendfund.ProductSearch", null, {
	_listener_locals : [],
	_browser_locals : [],
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
		if(!extra_params || extra_params === {}){
			loadElement("/product/search_tab", _t.ref_node, params, dojo.hitch(null, _t.productLoaded, _t));
		} else {
			dojo.mixin(params, extra_params);
			loadElement("/product/remote_search", _t.ref_node, params, dojo.hitch(null, _t.productLoaded, _t));
		}
		return false;
	},
	loadProductBrowser : function(_t, target, extra_params){
		_t.destroyBrowserLocals(_t);
		var base_url = dojo.attr(target, "_base_url");
		var params = _t.searchMixin && _t.searchMixin() || {};
		params.sort = dojo.attr(target, "sort")||"RANK";
		params.page=dojo.attr(target, "page")||1;
		
		dojo.forEach(dojo.attr(target, "_search_keys").split(","), 
					function(key){params[key.substring(1)]=dojo.attr(target, key);}
				);
		dojo.mixin(params, extra_params);
		loadElement("/product/"+base_url, _t.productBrowser, params, function(){
			_t._browser_locals.push(dojo.connect(dojo.byId("psort"), "onchange", dojo.hitch(null, _t.monitorChange, _t)));
			var node = dojo.byId("scroller_anchor");
			var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:500, easing:dojo.fx.easing.expoOut});
			anim0.play();
		});
		var node = dojo.byId("scroller_anchor");
		var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:500, easing:dojo.fx.easing.expoOut});
		anim0.play();
	},
	loadResults : function(_t, evt){
		var target;
		if(dojo.hasClass(evt.target, "anchorelem")){target=evt.target;}
		else {target = dojo.query(evt.target).parents(".anchorelem")[0];}
		if(!target || target.id == "psort" || target.id == "region_picker"){return;}
		
		if(dojo.hasClass(target, "productselector")){
			return dojo.hitch(target, _t.productSelected, _t)();
		} else if(dojo.hasClass(target, "methodselector")){
			loadElement("/product/"+dojo.attr(target, "_base_url"), _t.ref_node, _t.searchMixin && _t.searchMixin() || {}, dojo.hitch(null, _t.reinit, _t));
		} else if(dojo.hasClass(target, "popuplink")){
			dojo.hitch(target, loadPopup)(evt);
		} else if(dojo.hasClass(target, "searcher")){
			if (!dojo.hasClass(dojo.byId("pq"), "default")){
				_t.loadProductBrowser(_t, target, {searchterm:dojo.byId("pq").value});
			}
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
		if (evt.target.id === "psort"){_t.switchSort(_t, evt);}
		else if (evt.target.id === "region_picker"){_t.region_picker(_t, evt);}
	},
	switchSort : function(_t, evt){
		if(dojo.hasClass(evt.target, "anchorelem")){_t.loadProductBrowser(_t, evt.target, {sort:evt.target.value});}
	},
	region_picker:function(_t, evt){
		var params = _t.searchMixin && _t.searchMixin() || {};
		params[evt.target.name] = evt.target.value;
		params.action = dojo.attr(evt.target, "_base_url");
		loadElement("/product/set_region", _t.ref_node, params, dojo.hitch(null, _t.reinit, _t));
	},
	
	init_slider : function(_t){
		parseDefaultsInputs(_t.ref_node);
		if(dojo.query("div.productsuggestion", "scrollingproductsuggestions").length > 0)
		{
			dojo.parser.parse(dojo.byId("scrollingproductsuggestions"));
			if(dijit.byId("productslider")){_t._widget_list.push(dijit.byId("productslider"));}
			dojo.query("div.productsuggestion", "scrollingproductsuggestions").forEach(function(elem){
					_t._widget_locals.push(
						new friendfund.Tooltip({
							connectId: [dojo.attr(elem, '_target_id')],
							label: dojo.query("textarea", elem)[0].value,
							position: ["below"],
							showDelay:700
						})
					);
			});
			dojo.query(".dijitTooltipContainer").forEach(function(elem){
				_t._listener_locals.push(dojo.connect(elem, "onclick", dojo.hitch(null, _t.loadResults, _t)));
			});
		}
	},productLoaded: function(_t){
		if(_t.onLoaded){_t.onLoaded(_t);}
		if (!_t.canSelectRegion){dojo.query("#region_picker", _t.ref_node).attr("disabled","disabled");}
		_t._listener_locals.push(dojo.connect(dojo.byId(_t.ref_node), "onclick", dojo.hitch(null, _t.loadResults, _t)));
		_t._listener_locals.push(dojo.connect(dojo.byId(_t.ref_node), "onkeyup", dojo.hitch(null, _t.accessability, _t)));
		_t._listener_locals.push(dojo.connect(dojo.byId("region_picker"), "onchange", dojo.hitch(null, _t.monitorChange, _t)));
		if(dojo.byId("psort")){_t._browser_locals.push(dojo.connect(dojo.byId("psort"), "onchange", dojo.hitch(null, _t.monitorChange, _t)));}
		_t.init_slider(_t);
	},destroyBrowserLocals : function(_t){
		dojo.forEach(_t._browser_locals, dojo.disconnect);
		_t._browser_locals = [];
	},destroy : function(_t){
		_t.destroyBrowserLocals(_t);
		dojo.forEach(_t._listener_locals, dojo.disconnect);
		_t._listener_locals = [];
		dojo.forEach(_t._widget_locals, function(item){item.destroy(item);});
		_t._widget_locals = [];
	},reinit : function(_t, evt){
		_t.destroy(_t);
		_t.productLoaded(_t);
		
	},accessability : function(_t, evt){
		if(evt.target.id == 'pq'){
			switch (evt.keyCode){
				case (dojo.keys.ENTER):
					if (!dojo.hasClass(dojo.byId("pq"), "default")){
						_t.loadProductBrowser(_t, dojo.byId("searchsubmitter"), {searchterm:dojo.byId("pq").value});
					}
					break;
				case (dojo.keys.ESCAPE):
					dojo.byId("pq").value = "";
					break;
			}
		}
	},productSelected : function(_t, evt){
		var target = this;
		var return_args = {element : this};
		dojo.forEach(dojo.attr(target, "_search_keys").split(","), 
					function(key){return_args[key.substring(1)]=dojo.attr(target, key);}
				);
		if(_t.onSelected){_t.onSelected(return_args);}
	}
});













