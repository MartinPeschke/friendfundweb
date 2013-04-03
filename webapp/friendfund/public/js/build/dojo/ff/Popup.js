if(!dojo._hasResource["ff.Popup"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["ff.Popup"] = true;
dojo.provide("ff.Popup");
dojo.require("ff.t");
dojo.require("ff.w");
dojo.require("ff.io");

dojo.mixin(ff.w, {
	connectPopupLinks : function(rootnode){
		dojo.query(".popuplink", rootnode).onclick(function(evt){new ff.Popup().openFromEvent(evt)});
	}
	,displayPopup : function(popup_html){
		new ff.Popup().display(popup_html);
	}
});


dojo.declare("ff.Popup", null, {
	_popup_node : null
	,_contentNode : null
	,_popup_anchor : "generic_popup"
	,_subscriptions : []
	,_handler : []
	,afterDisplay : null
	,afterClose : null
	,constructor: function(args){
		dojo.mixin(this, args);
		this._popup_anchor = dojo.byId(this._popup_anchor);
		dojo.publish("/ff/popup/all/destroy");
		this._subscriptions.push( dojo.subscribe("/ff/popup/all/destroy", dojo.hitch(this,"destroy")) );
		return this;
	}
	,openFromURL : function(url, params){
		ff.io.xhrPost(url, params || {}, dojo.hitch(this, "display"));
	}
	,openFromNode : function(node, params){
		this.openFromURL(dojo.attr(node, "_href"), params);
	}
	,openFromEvent : function(evt, params){
		this.openFromNode(evt.target, params);
	}
	,destroy : function(){
		dojo.forEach(this._handler, dojo.disconnect);
		delete this._handler;
		dojo.forEach(this._subscriptions, dojo.unsubscribe);
		delete this._subscriptions;
		var tmp = dojo.query(this._popup_node).orphan();
		this.afterClose&&this.afterClose(this._contentNode);
		delete this._contentNode;
		delete this._popup_node;
		delete tmp;
	}
	,esc_handler_f : function(evt){
		if(evt.keyCode === 27){this.destroy();}
	}
	,display : function(html){
		var _t = this
			, rigPopup = function(node){
				dojo.query(".panelcloser,.popupBackground", node).forEach(function(elt){_t._handler.push(dojo.connect(elt, "onclick", dojo.hitch(_t, "destroy")));});
				_t._handler.push(dojo.connect(window, "onkeyup", dojo.hitch(_t, "esc_handler_f")));
				var i = dojo.query("input", node);
				if(i.length>0){i[0].focus();}
			};
		_t._popup_node = dojo.create("DIV", {innerHTML:html});
		_t._contentNode = dojo.query(".popupContentWindow", _t._popup_node).pop();
		this._popup_anchor.appendChild(_t._popup_node);
		ff.t.centerElementInViewPort(_t._contentNode);
		rigPopup(_t._popup_node);
		this.afterDisplay&&this.afterDisplay(_t._contentNode);
		return this;
	}
});

}
