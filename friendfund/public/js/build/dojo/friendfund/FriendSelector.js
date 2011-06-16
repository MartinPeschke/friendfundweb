/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["friendfund.CompoundFriendSelector"]){dojo._hasResource["friendfund.CompoundFriendSelector"]=true;dojo.provide("friendfund.CompoundFriendSelector");dojo.require("friendfund.NetworkFriendSelector");dojo.require("friendfund.EmailFriendSelector");dojo.require("ff.t");dojo.require("ff.io");dojo.declare("friendfund.CompoundFriendSelector",null,{_widget_locals:[],_listener_locals:[],selectors:{},constructor:function(_1){var _2=this;dojo.mixin(_2,_1);this.networkSelector=this.networkSelector||friendfund.NetworkFriendSelector;this.emailSelector=this.emailSelector||friendfund.EmailFriendSelector;if(_1.avail_selectors.facebook===true){_2.selectors.facebook=new this.networkSelector({container:_2.container,auth_provider:_2.auth_provider,ref_node:_2.ref_node,invited_node:"network"+_2.invited_node_suffix,global_invited_node:_2.global_invited_node,base_url:_2.base_url,network:"facebook"});}if(_1.avail_selectors.twitter===true){_2.selectors.twitter=new this.networkSelector({container:_2.container,auth_provider:_2.auth_provider,ref_node:_2.ref_node,invited_node:"network"+_2.invited_node_suffix,global_invited_node:_2.global_invited_node,base_url:_2.base_url,network:"twitter"});}if(_1.avail_selectors.email===true){_2.selectors.email=new this.emailSelector({ref_node:_2.ref_node,auth_provider:_2.auth_provider,invited_node:"network"+_2.invited_node_suffix,global_invited_node:_2.global_invited_node,base_url:_2.base_url,network:"email"});}for(var _3 in _2.selectors){var s=_2.selectors[_3];if(_2.selectors.hasOwnProperty(_3)&&_2.selectors[_3]){if(_2.onSelect){s.onSelect=dojo.hitch(s,_2.onSelect);}if(_2.unSelect){s.unSelect=dojo.hitch(s,_2.unSelect);}_2._widget_locals.push(s);}}if(_2.invited_node_suffix){_2._listener_locals.push(dojo.connect(dojo.byId(_2.global_invited_node),"onclick",_2,"unselect"));}var _4=dojo.byId("removeall");if(_4){_2._listener_locals.push(dojo.connect(_4,"onclick",_2,"removeAll"));}},removeAll:function(){var _5=this;dojo.query(".invitee_row.selectable",_5.global_invited_node).forEach(function(_6){_5.selectors[dojo.attr(_6,"_network")].unSelect(_6);});},unselect:function(_7){var _8=ff.t.findParent(_7.target,"invitee_row");if(!_8||!dojo.hasClass(_8,"selectable")){return;}this.selectors[dojo.attr(_8,"_network")].unSelect(_8);},destroy:function(){dojo.forEach(this._listener_locals,dojo.disconnect);this._listener_locals=[];dojo.forEach(this._widget_locals,function(_9){_9.destroy();});this._widget_locals=[];},switchMethod:function(_a){var _b=this;if(dojo.hasClass(_a.target,"selected")){return;}dojo.query(".ajaxlink.selected",_b.container).forEach(function(_c){dojo.removeClass(_c,"selected");var _d=_b.selectors[dojo.attr(_c,"_type")];if(_d){_d.undraw();}});dojo.addClass(_a.target,"selected");var _e=_b.selectors[dojo.attr(_a.target,"_type")];if(_e){_e.draw();}},draw:function(_f){var _10=this;_10.selectors[_f].draw();dojo.query(".ajaxlink",_10.container).forEach(function(_11){_10._listener_locals.push(dojo.connect(_11,"onclick",_10,"switchMethod"));});}});}