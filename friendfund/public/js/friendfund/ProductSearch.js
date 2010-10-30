dojo.provide("friendfund.ProductSearch");
dojo.require("dojo.NodeList-manipulate");
dojo.require("dojo.NodeList-traverse");
dojo.require("dojox.fx.scroll");
dojo.require("dojo.fx.easing");

dojo.declare("friendfund.ProductSearch", null, {
	_widget_list : [],
	_listener_list : [],
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
		var base_url = dojo.attr(target, '_base_url');
		var params = {sort:dojo.attr(target, 'sort')||"RANK",page:dojo.attr(target, 'page')||1}
		dojo.forEach(dojo.attr(target, "_search_keys").split(','), 
					function(key){params[key.substring(1)]=dojo.attr(target, key)}
				);
		dojo.mixin(params, extra_params);
		loadElement("/product/"+base_url, _t.productBrowser, params);
	},
	loadResults : function(_t, evt){
		var target=null;
		if(dojo.hasClass(evt.target, "anchorelem"))target=evt.target;
		else target = dojo.query(evt.target).parents(".anchorelem")[0];
		if(!target || target.id == 'psort')return;
		
		if(dojo.hasClass(target, "productselector")){
			return dojo.hitch(target, _t.productSelected, _t)();
		} else if(dojo.hasClass(target, "methodselector")){
			loadElement("/product/"+dojo.attr(target, '_base_url'), _t.ref_node);
		} else {
			_t.loadProductBrowser(_t, target);
		}
	},
	switchSort : function(_t, evt){
		if(dojo.hasClass(evt.target, "anchorelem"))_t.loadProductBrowser(_t, evt.target, {sort:evt.target.value});
	},
	region_picker:function(_t, evt){
		var params = _t.searchMixin && _t.searchMixin() || {};
		params[this.name] = this.value;
		params["action"] = dojo.attr(this, '_base_url');
		loadElement("/product/set_region", _t.ref_node, params, dojo.hitch(null, _t.productLoaded, _t));
	},
	productLoaded: function(_t){
		if (!_t.canSelectRegion){dojo.query("#region_picker", _t.ref_node).attr("disabled","disabled")}
		_t.onLoaded && _t.onLoaded(_t);
		
		dojo.connect(dojo.byId(_t.ref_node), "onclick", dojo.hitch(null, _t.loadResults, _t));
		dojo.connect(dojo.byId(_t.ref_node), "onchange", dojo.hitch(null, _t.switchSort, _t));
		
		dojo.query(".popuplink", _t.ref_node).onclick(dojo.hitch(null, loadPopup));
		var slider2 = ['Recipe', 'Quote', 'Image', 'Quote #2', 'Image #2'];
		function formatText(index, panel){
			return slider2[index - 1];
		}
		jQuery(function () {
			jQuery('#slider1').anythingSlider({
				startStopped    : false,  // If autoPlay is on, this can force it to start stopped
				width           : 830,    // Override the default CSS width
				height          : 180,    // Override the default CSS height
				autoPlay        : true,   // This turns off the entire slideshow FUNCTIONALY, not just if it starts running or not
				delay           : 5000,   // How long between slideshow transitions in AutoPlay mode (in milliseconds)
			});
		});
	},
	
	
	
	
	
	
	accessability : function(_t, callback, evt){
		switch (evt.keyCode){
			case (dojo.keys.ENTER):
				callback(_t, evt);
				break;
			case (dojo.keys.ESCAPE):
				dojo.byId('pq').value = '';
				break;
		}
	},
	
	suggestionSelected : function(_t, evt){
		var params = {back_q: dojo.attr(this, "searchterm")||null
					, q:null
					, aff_net: dojo.attr(this, "aff_net")||null
					, aff_net_ref: dojo.attr(this, "aff_net_ref")||null
					, sort : dojo.attr(this, "sort")||"RANK"
					, is_virtual : dojo.attr(this, "is_virtual")||null
				};
		_t.search(_t, evt, params);
		
		var node = dojo.byId("product_search");
		var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:300, easing:dojo.fx.easing.expoOut});
		anim0.play();
		evt.stopPropagation();
		evt.preventDefault();
		return false;
	},performSearch : function(_t, evt){
		_t.search(_t, evt, {q:_t.getSearchString(), sort : dojo.attr(this, "sort")||null});
		var node = dojo.byId("product_search");
		var anim0 = dojox.fx.smoothScroll({node:node, win: window, duration:300, easing:dojo.fx.easing.expoOut});
		anim0.play();
	},resort: function(_t, evt){
		var params = _t.getSearchParams(_t);
		dojo.mixin(params, {aff_net: dojo.attr(this, "aff_net")||null
							, aff_net_ref: dojo.attr(this, "aff_net_ref")||null
							, sort : this.value||null
							, is_virtual : dojo.attr(this, "is_virtual")||null
							});
		_t.search(_t, evt, params);
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
		_t.destroy(_t);
	}, 
	destroy : function(_t){
		dojo.query("*", _t.ref_node).orphan();
	}
});