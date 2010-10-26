dojo.provide("friendfund.ProductSearch");
dojo.require("dojo.NodeList-manipulate");
dojo.require("dojox.fx.scroll");
dojo.require("dojo.fx.easing");

dojo.declare("friendfund.ProductSearch", null, {
	_widget_list : [],
	_listener_list : [],
	onLoaded : null,
	onSelected : null,
	searchMixin : null,
	canSelectRegion:true,
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
	},
	draw : function(_t, evt, extra_params){
		var params = _t.searchMixin && _t.searchMixin() || {};
		if(extra_params==null || extra_params == {}){
			loadElement("/product/panel", _t.ref_node, params, dojo.hitch(null, _t.productLoaded, _t));
		} else {
			dojo.mixin(params, extra_params);
			loadElement("/product/search", _t.ref_node, params, dojo.hitch(null, _t.productLoaded, _t));
		}
		return false;
	},
	getSearchString : function(){
		return (dojo.hasClass("pq", "default")?"":dojo.byId("pq").value);
	},
	getSearchParams : function(_t){
		var params = {q:_t.getSearchString()
					, back_q : dojo.byId("back_q").value}
		return params;
	},
	search : function(_t, evt, args){
		_t.searchMixin && dojo.mixin(args, _t.searchMixin());
		loadElement("/product/search", _t.ref_node, args, dojo.hitch(null, _t.productLoaded, _t));
	},
	productLoaded: function(_t){
		if (!_t.canSelectRegion){dojo.query("#region_picker", _t.ref_node).attr("disabled","disabled")}
		_t.onLoaded && _t.onLoaded(_t);
		dojo.query("a.productsuggestion", _t.ref_node).onclick(dojo.hitch(null, _t.suggestionSelected, _t));
		dojo.query("a.searcher", _t.ref_node).onclick(dojo.hitch(null, _t.performSearch, _t));
		dojo.query("a.selector", _t.ref_node).onclick(dojo.hitch(null, _t.productSelected, _t));
		dojo.query("select#psort", _t.ref_node).onchange(dojo.hitch(null, _t.resort, _t));
		dojo.query("a.paginator", _t.ref_node).onclick(dojo.hitch(null, _t.gotoPage, _t));
		dojo.query("#pq", _t.ref_node).onkeyup(dojo.hitch(null, _t.accessability, _t, _t.performSearch));
		dojo.query("#region_picker", _t.ref_node).onchange(dojo.hitch(null, _t.region_picker, _t));
		
		dojo.query(".popuplink", _t.ref_node).onclick(dojo.hitch(null, loadPopup));
		
	},
	region_picker:function(_t, evt){
		var params = _t.searchMixin && _t.searchMixin() || {};
		params[this.name] = this.value;
		loadElement("/product/set_region", _t.ref_node, params, dojo.hitch(null, _t.productLoaded, _t));
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
	gotoPage : function(_t, evt){
		var params = _t.getSearchParams(_t);
		dojo.mixin(params, {page:dojo.attr(this, "page")||null
					, aff_net: dojo.attr(this, "aff_net")||null
					, aff_net_ref: dojo.attr(this, "aff_net_ref")||null
					, sort : dojo.attr(this, "sort")||null
					, is_virtual : dojo.attr(this, "is_virtual")||null});
		_t.search(_t, evt, params);
		evt.stopPropagation();
		evt.preventDefault();
		return false;
	},
	destroy : function(_t){
		dojo.query("*", _t.ref_node).orphan();
	}
});