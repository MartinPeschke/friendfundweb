dojo.provide("friendfund.EmailFriendSelector");
dojo.require("ff.t");
dojo.require("ff.io");


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
