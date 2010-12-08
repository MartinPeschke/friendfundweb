dojo.provide("friendfund.Tooltip");
dojo.require("dijit.Tooltip");

dojo.require("dijit._Widget");
dojo.require("dijit._Templated");

dojo.declare(
	"friendfund.Tooltip",
	dijit._Widget,
	{
		// summary:
		//		Pops up a tooltip (a help message) when you hover over a node.

		// label: String
		//		Text to display in the tooltip.
		//		Specified as innerHTML when creating the widget from markup.
		label: "",

		// showDelay: Integer
		//		Number of milliseconds to wait after hovering over/focusing on the object, before
		//		the tooltip is displayed.
		showDelay: 400,

		// connectId: [const] String[]
		//		Id's of domNodes to attach the tooltip to.
		//		When user hovers over any of the specified dom nodes, the tooltip will appear.
		//
		//		Note: Currently connectId can only be specified on initialization, it cannot
		//		be changed via attr('connectId', ...)
		//
		//		Note: in 2.0 this will be renamed to connectIds for less confusion.
		connectId: [],

		// position: String[]
		//		See description of `friendfund.Tooltip.defaultPosition` for details on position parameter.
		position: [],

		constructor: function(){
			// Map id's of nodes I'm connected to to a list of the this.connect() handles
			this._nodeConnectionsById = {};
		},

		_setConnectIdAttr: function(newIds){
			for(var oldId in this._nodeConnectionsById){
				this.removeTarget(oldId);
			}
			dojo.forEach(dojo.isArrayLike(newIds) ? newIds : [newIds], this.addTarget, this);
		},

		_getConnectIdAttr: function(){
			var ary = [];
			for(var id in this._nodeConnectionsById){
				ary.push(id);
			}
			return ary;
		},

		addTarget: function(/*DOMNODE || String*/ id){
			// summary:
			//		Attach tooltip to specified node, if it's not already connected
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
			// summary:
			//		Detach tooltip from specified node

			// map from DOMNode back to plain id string
			var id = node.id || node;

			if(id in this._nodeConnectionsById){
				dojo.forEach(this._nodeConnectionsById[id], this.disconnect, this);
				delete this._nodeConnectionsById[id];
			}
		},

		postCreate: function(){
			dojo.addClass(this.domNode,"dijitTooltipData");
		},

		startup: function(){
			this.inherited(arguments);

			// If this tooltip was created in a template, or for some other reason the specified connectId[s]
			// didn't exist during the widget's initialization, then connect now.
			var ids = this.connectId;
			dojo.forEach(dojo.isArrayLike(ids) ? ids : [ids], this.addTarget, this);
		},

		_onTargetMouseEnter: function(/*Event*/ e){
			// summary:
			//		Handler for mouseenter event on the target node
			// tags:
			//		private
			this._onHover(e);
		},

		_onTargetMouseLeave: function(/*Event*/ e){
			// summary:
			//		Handler for mouseleave event on the target node
			// tags:
			//		private
			this._onUnHover(e);
		},

		_onTargetFocus: function(/*Event*/ e){
			// summary:
			//		Handler for focus event on the target node
			// tags:
			//		private

			this._focus = true;
			this._onHover(e);
		},

		_onTargetBlur: function(/*Event*/ e){
			// summary:
			//		Handler for blur event on the target node
			// tags:
			//		private

			this._focus = false;
			this._onUnHover(e);
		},
		_onClick: function(/*Event*/ e){
			// summary:
			//		Despite the name of this method, it actually handles both hover and focus
			//		events on the target node, setting a timer to show the tooltip.
			// tags:
			//		private
			if(this._focus){ return; }
			this.open(e.target);
		}, 
		_onHover: function(/*Event*/ e){
			// summary:
			//		Despite the name of this method, it actually handles both hover and focus
			//		events on the target node, setting a timer to show the tooltip.
			// tags:
			//		private
			if(!this._showTimer){
				var target = e.target;
				this._showTimer = setTimeout(dojo.hitch(this, function(){this.open(target)}), this.showDelay);
			}
		},

		_onUnHover: function(/*Event*/ e){
			// summary:
			//		Despite the name of this method, it actually handles both mouseleave and blur
			//		events on the target node, hiding the tooltip.
			// tags:
			//		private

			// keep a tooltip open if the associated element still has focus (even though the
			// mouse moved away)
			if(this._focus){ return; }

			if(this._showTimer){
				clearTimeout(this._showTimer);
				delete this._showTimer;
			}
			this.close();
		},

		open: function(/*DomNode*/ target){
 			// summary:
			//		Display the tooltip; usually not called directly.
			// tags:
			//		private

			if(this._showTimer){
				clearTimeout(this._showTimer);
				delete this._showTimer;
			}
			dijit.showTooltip(this.label || this.domNode.innerHTML, target, this.position, !this.isLeftToRight());

			this._connectNode = target;
			this.onShow(target, this.position);
		},

		close: function(){
			// summary:
			//		Hide the tooltip or cancel timer for show of tooltip
			// tags:
			//		private

			if(this._connectNode){
				// if tooltip is currently shown
				dijit.hideTooltip(this._connectNode);
				delete this._connectNode;
				this.onHide();
			}
			if(this._showTimer){
				// if tooltip is scheduled to be shown (after a brief delay)
				clearTimeout(this._showTimer);
				delete this._showTimer;
			}
		},

		onShow: function(target, position){
			// summary:
			//		Called when the tooltip is shown
			// tags:
			//		callback
		},

		onHide: function(){
			// summary:
			//		Called when the tooltip is hidden
			// tags:
			//		callback
		},

		uninitialize: function(){
			this.close();
			this.inherited(arguments);
		}
	}
);

dojo.declare("friendfund.Tooltip", [friendfund.Tooltip], {
    postCreate: function()
        {
            if(!dijit._masterTT){
                dijit._masterTT = new dijit._MasterTooltip();
            }
            // should get the connection list & see if another heroic.widget.PersistTooltip
            // has already made these connections.
            dijit._masterTT.connect(dijit._masterTT.domNode,'onmouseover',this.ttPersist);
            dijit._masterTT.connect(dijit._masterTT.domNode,'onmouseout',this.ttFade);
            this.inherited("postCreate", arguments);
        },

		 ttPersist: function (evt)
		 {
			 // console.log("persist");
			 this.fadeOut.stop();
			 this.fadeIn.play();
		 },

		 ttFade: function (evt)
		 {
			 // console.log("fade");
			 this.fadeOut.play();
		 }

    }
    );












