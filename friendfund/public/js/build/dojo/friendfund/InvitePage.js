/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["friendfund.InvitePage"]){dojo._hasResource["friendfund.InvitePage"]=true;dojo.provide("friendfund.InvitePage");dojo.declare("friendfund.InvitePage",null,{selector:null,_listener_locals:[],_widget_locals:[],submitting:false,constructor:function(_1){var _2=this;dojo.mixin(_2,_1);_2.selector=new friendfund.CompoundFriendSelector({auth_provider:_2.auth_provider,container:_2.container,ref_node:"inviter",invited_node_suffix:"_invitees",inviter_node:"friend_list",base_url:_2.base_url,global_invited_node:_2.invited_node,avail_selectors:{"facebook":true,"twitter":true,"email":true}});_2._widget_locals.push(_2.selector);dojo.connect(document,"onclick",dojo.hitch(null,_2.loadPreviewPopup,_2,_2.method));},loadPreviewPopup:function(_3,_4,_5){if(dojo.hasClass(_5.target,"message_preview")){dojo.query("input.addRefContent",_3.target_form).forEach(function(_6){_6.value=dojo.byId(dojo.attr(_6,"_source")).value;});params=dojo.formToObject(_3.target_form);params.method=dojo.attr(_5.target,"_method");ff.io.xhrPost(dojo.attr(_5.target,"_href"),params);}},prepareSubmit:function(_7,_8,_9){ff.t.onSubmitCleaner(_7.target_form);if(_7.submitting){return false;}_7.submitting=true;return _7.auth_provider.checkLogin({level:_8,success:dojo.hitch(_7,"_submit"),fail:function(){_7.submitting=false;}});},_submit:function(){var _a=this;dojo.forEach(_a._widget_locals,function(_b){_b.destroy(_b);});_a._widget_locals=[];_a.receiver_selectors={};dojo.query("input.addRefContent",_a.target_form).forEach(function(_c){_c.value=dojo.byId(dojo.attr(_c,"_source")).value;});dojo.byId(_a.target_form).submit();}});}