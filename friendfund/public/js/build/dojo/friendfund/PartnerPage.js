/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["friendfund.PartnerPage"]){dojo._hasResource["friendfund.PartnerPage"]=true;dojo.provide("friendfund.PartnerPage");dojo.declare("friendfund.PartnerPage",null,{connect:function(){dojo.connect(dojo.byId("occasionSelector"),"onchange",this,"swapOccasionName");dojo.connect(dojo.byId("occasionTyper"),"onkeyup",this,"changeOccasionName");},changeOccasionName:function(_1){if(_1.target.value){dojo.byId(dojo.attr(_1.target,"_target")).value=_1.target.value;}else{var _2={target:dojo.byId("occasionSelector")};this.swapOccasionName(_2);}this.check_occasion_name();},swapOccasionName:function(_3){var _4=_3.target.options[_3.target.selectedIndex];dojo.byId(dojo.attr(_3.target,"_name_target")).value=_4.value;dojo.byId(dojo.attr(_3.target,"_key_target")).value=dojo.attr(_4,"key");this.check_occasion_name();},constructor:function(_5){dojo.mixin(this,_5);this.triedSubmitting=false;this.target_form=dojo.isString(this.target_form)&&dojo.byId(this.target_form)||this.target_form;this.load_receiver();this.connect();dojo.byId("selectedReceiver").value="";},load_receiver:function(){this.selector=new friendfund.CompoundFriendSelector({auth_provider:this.auth_provider,container:this.container,ref_node:"inviter",inviter_node:"friend_list",base_url:this.base_url,avail_selectors:{"facebook":true,"twitter":true,"email":true},networkSelector:friendfund.FriendTypeAhead,emailSelector:friendfund.EmailInPlaceSelector});this.selector.draw(this.method);},submit:function(_6,_7,_8){var _9=this;var _a=_9.checkCompleteness();if(!_a||_9.submitting){return false;}else{ff.t.onSubmitCleaner(_9.target_form);_9.submitting=true;return _9.auth_provider.checkLogin({level:_7,success:dojo.hitch(_9,"_submit",_6),fail:function(){_9.submitting=false;}});}},_submit:function(_b){var _c=this;dojo.query("input[type=submit]").attr("disabled","disabled");_c.target_form.action=_b;_c.target_form.onsubmit=function(){};_c.target_form.submit();},checkCompleteness:function(){var _d=this;return _d.check_receiver()&&_d.check_occasion_name();},check_receiver:function(_e){if(dojo.query(".invitee_row","network_invitees").length!=1){dojo.query(".errorHook","receiverSelectorContainer").addClass("error");dojo.query(".errorMsgIframe","selectedReceiverContainer").removeClass("hidden");return false;}else{dojo.query(".errorHook","receiverSelectorContainer").removeClass("error");dojo.query(".errorMsgIframe","selectedReceiverContainer").addClass("hidden");return true;}},check_occasion_name:function(_f){var _10=dojo.byId("occasion_name");var _11=ff.t.findParent(_10,"generalBoxIframe");if(!_10.value){dojo.query(".errorMsgIframe",_11).removeClass("hidden");dojo.query("#yourOccasionSelector,#occasionSelectorContainer").addClass("error");return false;}else{dojo.query(".errorMsgIframe",_11).addClass("hidden");dojo.query("#yourOccasionSelector,#occasionSelectorContainer").removeClass("error");return true;}}});}