dojo.provide("friendfund.YourselfSelector");

dojo.declare("friendfund.YourselfSelector", null, {
	constructor: function(args){
		var _t = this;
		dojo.mixin(_t, args);
		_t.ref_node = dojo.isString(_t.ref_node) && dojo.byId(_t.ref_node) || _t.ref_node;
	},
	draw : function(){
		var _t = this;
		xhrPost(_t.base_url+"/add", {"invitee.network":"yourself"}, dojo.hitch(null, _t.onSelect, _t));
	}, 
	unload:function(){}
});
