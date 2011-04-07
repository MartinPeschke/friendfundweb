dojo.provide("friendfund.Tooltip");
dojo.require("dijit._Widget");

dojo.declare("friendfund.Tooltip",dijit._Widget,
	{
		label: "",
		showDelay: 400,
		connectId: [],
		position: [],
		constructor: function(){this._nodeConnectionsById = {};},
		_setConnectIdAttr: function(newIds){
			for(var oldId in this._nodeConnectionsById){this.removeTarget(oldId);}
			dojo.forEach(dojo.isArrayLike(newIds) ? newIds : [newIds], this.addTarget, this);
		},
		_getConnectIdAttr: function(){
			var ary = [];
			for(var id in this._nodeConnectionsById){ary.push(id);}
			return ary;
		},
		addTarget: function(/*DOMNODE || String*/ id){
			var node = dojo.byId(id);
			if(!node){ return; }
			if(node.id in this._nodeConnectionsById){ return; }//Already connected
			this._nodeConnectionsById[node.id] = [
				this.connect(node, "onmouseenter", "_onTargetMouseEnter"),
				this.connect(node, "onclick", "_onClick"),
				this.connect(node, "onmouseleave", "_onTargetMouseLeave"),
				this.connect(node, "onfocus", "_onTargetFocus"),
				this.connect(node, "onblur", "_onTargetBlur")
			];
		},
		removeTarget: function(/*DOMNODE || String*/ node){
			var id = node.id || node;
			if(id in this._nodeConnectionsById){
				dojo.forEach(this._nodeConnectionsById[id], this.disconnect, this);
				delete this._nodeConnectionsById[id];
			}
		},
		postCreate: function(){
			dojo.addClass(this.domNode,"dijitTooltipData");
			if(!dijit._masterTT){
				dijit._masterTT = new dijit._MasterTooltip();
			}
			dijit._masterTT.connect(dijit._masterTT.domNode,'onmouseover',this.ttPersist);
			dijit._masterTT.connect(dijit._masterTT.domNode,'onmouseout',this.ttFade);
			this.inherited("postCreate", arguments);
		},
		startup: function(){
			this.inherited(arguments);
			var ids = this.connectId;
			dojo.forEach(dojo.isArrayLike(ids) ? ids : [ids], this.addTarget, this);
		},
		_onTargetMouseEnter: function(/*Event*/ e){this._onHover(e);},
		_onTargetMouseLeave: function(/*Event*/ e){this._onUnHover(e);},
		_onTargetFocus: function(/*Event*/ e){this._focus = true;this._onHover(e);},
		_onTargetBlur: function(/*Event*/ e){this._focus = false;this._onUnHover(e);},
		_onClick: function(/*Event*/ e){if(this._focus){ return; }this.open(e.target);}, 
		_onHover: function(/*Event*/ e){
			if(!this._showTimer){
				var target = e.target;
				this._showTimer = setTimeout(dojo.hitch(this, function(){this.open(target);}), this.showDelay);
			}
		},
		_onUnHover: function(/*Event*/ e){
			if(this._focus){ return; }
			if(this._showTimer){clearTimeout(this._showTimer);delete this._showTimer;}
			this.close();
		},
		open: function(/*DomNode*/ target){
			if(this._showTimer){
				clearTimeout(this._showTimer);
				delete this._showTimer;
			}
			dijit.showTooltip(this.label || this.domNode.innerHTML, target, this.position, !this.isLeftToRight());
			this._connectNode = target;
			this.onShow(target, this.position);
		},
		close: function(){
			if(this._connectNode){
				dijit.hideTooltip(this._connectNode);
				delete this._connectNode;
				this.onHide();
			}
			if(this._showTimer){
				clearTimeout(this._showTimer);
				delete this._showTimer;
			}
		},
		onShow: function(target, position){},
		onHide: function(){},
		uninitialize: function(){
			this.close();
			this.inherited(arguments);
		},
		ttPersist: function (evt){this.fadeOut.stop();this.fadeIn.play();},
		ttFade: function (evt){this.fadeOut.play();}
	}
);











