/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["ff.auth"]){dojo._hasResource["ff.auth"]=true;dojo.provide("ff.auth");dojo.require("ff.t");dojo.require("ff.Popup");dojo.declare("ff._auth",null,{timeoutValue:500,_FBSCOPE:{"3":"email","6":"email,publish_stream","9":"email,publish_stream,create_event,user_birthday,friends_birthday"},_get_scope:function(_1){return this._FBSCOPE[""+(_1.level||3)];},_facebook_login_in_process:false,_twitter_login_in_process:false,_fbperms:null,_loginPanelContainer:"accountcontainer",_loginPanelForm:"loginPanelContent",_loginPanelHandler:[],_workflow:{success:null,fail:null},_fwd:function(){window.location.href="/mypools/stream";},fwd:false,_rld:ff.t.reload,rld:false,hasLoginPanel:true,isLoggedIn:function(){return !dojo.byId("loginlink");},constructor:function(){},_fbInit:function(_2,_3){var _4=this,_5=new ff.t.deferreds(function(){return this.fbDoneLoading;},this),_6=new ff.t.deferreds(function(){return this.fbDoneLoading&&typeof (FB)!=="undefined"&&FB.getAuthResponse();},this);window.fbAsyncInit=function(){var _7=document.location.protocol+"//"+document.location.host+"/channel.htm";FB.init({appId:_2,logging:true,status:true,cookie:true,xfbml:true,authResponse:true,channelUrl:_7});_4.fbDoneLoading=true;_4.runFBDeferred();FB.Event.subscribe("auth.authResponseChange",function(_8){if(_8.authResponse){_4.runLoginDeferred();}});};this.addFBDeferred=_5.add;this.runFBDeferred=_5.run;this.addLoginDeferred=_6.add;this.runLoginDeferred=_6.run;if(this.requireFBPerms){this.addLoginDeferred(dojo.hitch(this,"_guardedFBScope"));}var js,id="facebook-jssdk";if(document.getElementById(id)){return;}js=document.createElement("script");js.id=id;js.async=true;js.src="//connect.facebook.net/en_US/all.js";document.getElementsByTagName("body")[0].appendChild(js);},_loginPanelFormConnect:function(){var _9=this;dojo.forEach(_9._loginPanelHandler,dojo.disconnect);_9._loginPanelHandler=[];dojo.query("form",_9._loginPanelContainer).forEach(function(_a){_9._loginPanelHandler.push(dojo.connect(_a,"onsubmit",_9,"emailLogin"));});},_connectLoginPanel:function(){var _b=this,_c=[],_d=[],_e=[],_f=function(){dojo.forEach(_c,dojo.disconnect);_c=[];dojo.forEach(_d,dojo.unsubscribe);_d=[];if(dojo.hasClass("loginlink","active")){dojo.removeClass("loginlink","active");if(dojo.byId(_b._loginPanelForm)){dojo.addClass(_b._loginPanelForm,"hidden");}}},_10=function(evt){if(!dojo.hasClass(this,"active")){dojo.addClass(this,"active");dojo.removeClass(_b._loginPanelForm,"hidden");_c.push(dojo.connect(document,"onkeydown",function(evt){if(evt.keyCode==27){_f(evt);}}));_c.push(dojo.connect(document,"onclick",function(evt){if(!(evt.target.id=="loginlink")&&!ff.t.findParent(evt.target,"loginPanel")){_f(evt);}}));_d.push(dojo.subscribe("/ff/login/panel/close",_f));_b._loginPanelFormConnect();var i=dojo.query("input",_b._loginPanelForm);i[0].focus();}else{if(evt.target.id=="loginlink"){_f();}}},_11=function(){dojo.forEach(_e,dojo.disconnect);_e=[];dojo.query(".loginToggleLink",_b._loginPanelContainer).forEach(function(_12){_e.push(dojo.connect(_12,"onclick",_10));});dojo.query(".logoutLink",_b._loginPanelContainer).forEach(function(_13){_e.push(dojo.connect(_13,"onclick",_b,"logout",true));});dojo.subscribe("/ff/login/panel/reconnect",_11);};_11();},_simpleLogout:function(){if(this.isLoggedIn()){window.location.href="/logout?furl=/";}},_guardedFBScope:function(_14){var _15=this,aR=FB.getAuthResponse();if(aR&&aR!==true){this._getFBScope(_14);}else{FB.getLoginStatus(function(_16){_15._getFBScope(_14);});}},_getFBScope:function(_17){var _18=this;FB.api("/me/permissions",function(_19){if(!_19.error){_18._fbperms=_19.data[0];}if(_17){_17.apply(_18);}});},_onSessionChange:function(_1a){var _1b=this;if(_1a.status==="connected"){var aR=_1a.authResponse;if(_1b.fbId&&aR.userID!=_1b.fbId){_1b._simpleLogout();}else{if(!_1b._fb_login_in_progress){_1b._fbHandleLogin(_1b._get_scope(_1b._workflow));}else{_1b._fb_login_in_progress=false;}}}else{_1b._simpleLogout();}},_forceFBLogin:function(_1c){var _1d=this;_1d._fb_login_in_progress=true;FB.login(function(_1e){if(_1e.authResponse){_1d._guardedFBScope(dojo.hitch(_1d,"_fbHandleLogin",_1c));}},{scope:_1c});},_getMissingFBPerms:function(_1f){if(!this._fbperms){return [];}var mp=_1f.split(","),_20=[],_21=_21||{},i=0,l=mp.length;for(;i<l;i++){if(!this._fbperms[mp[i]]){_20.push(mp[i]);}}return _20;},_checkFBIsInOrder:function(_22){var _23=this;if(this.fbId){FB.getLoginStatus(function(){var mp=_23._getMissingFBPerms(_22);if(mp.length){_23._forceFBLogin(_22);}else{_23._logincb({success:true});}});}else{_23._logincb({success:true});}},_fbHandleLogin:function(_24){var _25=this,mp=_25._getMissingFBPerms(_24),_26={};if(mp.length){_26.scope=ff.t.getKeys(_25._fbperms).join(",");_26.missing_scope=mp.join(",");_26.access_token=FB.getAuthResponse().accessToken;ff.io.xhrPost("/fb/failed_login",_26,dojo.hitch(_25,"_logincb"));}else{FB.api("/me",function(_27){_27.scope=ff.t.getKeys(_25._fbperms).join(",");_27.access_token=FB.getAuthResponse().accessToken;ff.io.xhrPost("/fb/login",_27,dojo.hitch(_25,"_logincb"));});}},_logincb:function(_28){var _29=this,i,_2a,_2b=_29._get_scope(_29._workflow),_2c=[],_2d=function(){ff.io.xhrFormPost(this.action,this,dojo.hitch(_29,"_logincb"));return false;},_2e=function(evt){var _2f=dojo.attr(evt.target,"_href");ff.io.xhrPost(_2f,{},dojo.hitch(_29,"_logincb"));return false;};_2a=_29._workflow._login_popup;if(_2a){delete _2a.afterClose;_2a.destroy();}if(_28.panel!==undefined&&dojo.byId(_29._loginPanelContainer)){dojo.place(_28.panel,_29._loginPanelContainer,"only");dojo.publish("/ff/login/panel/reconnect");}else{if(_28.form&&dojo.byId(_29._loginPanelForm)){dojo.place(_28.form,dojo.byId(_29._loginPanelForm),"only");if(this.hasLoginPanel){_29._loginPanelFormConnect();}i=dojo.query("input",_29._loginPanelForm);if(i.length>0){i[0].focus();}}}if(_28.popup!==undefined){_2a=new ff.Popup();_2a.afterDisplay=function(_30){var _31=this;dojo.query("form.loginAction",_30).forEach(function(_32){_32.onsubmit=_2d;});dojo.query("a.loginAction",_30).forEach(function(_33){_31._handler.push(dojo.connect(_33,"onclick",_2e));});if(dojo.byId("ToC-agreeal-popup")){_29.connectToCToggle("ToC-agreeal-popup","ToC-checkbox-popup");}else{dojo.query("a.loginFBAction",_30).forEach(function(_34){_31._handler.push(dojo.connect(_34,"onclick",dojo.hitch(_29,"doFBLogin",_29._workflow)));});dojo.query("a.loginTWAction",_30).forEach(function(_35){_31._handler.push(dojo.connect(_35,"onclick",dojo.hitch(_29,"doTWLogin",_29._workflow)));});}};_2a.afterClose=function(_36){_29._workflow.fail&&_29._workflow.fail();_29._workflow={};};_2a.display(_28.popup);_29._workflow._login_popup=_2a;}else{if(_28.success===true&&_29._workflow.success!=null){_29._workflow.success(_28);_29._workflow={};}else{if(_28.success===false&&_29._workflow.fail!=null){_29._workflow.fail(_28);_29._workflow={};}else{if(_28.has_activity===true&&_29.fwd===true){_29._fwd(_28);_29._workflow={};}else{if(_28.success===true&&_29.rld===true){_29._rld(_28);_29._workflow={};}else{if(_28.reload===true){window.location.href=window.location.href;_29._workflow={};}}}}}}}});dojo.declare("ff.auth",[ff._auth],{constructor:function(_37,_38){dojo.mixin(this,_37);if(_38&&typeof (_38)==="object"){dojo.mixin(this,_38);}if(this.hasLoginPanel){this._connectLoginPanel();}this._fbInit(_37.fbappId,_37.fbRootNode);this._fb_login_in_progress=false;},checkLogin:function(_39){this._workflow.level=_39.level||3;var url=_39.url||this.loginurl,_3a=this._get_scope(this._workflow);if(_39.success||_39.fail){this._workflow.success=_39.success;this._workflow.fail=_39.fail;}if(this.isLoggedIn()){if(_39.ignoreFB){this._logincb({success:true});}else{this._checkFBIsInOrder(_3a);}}else{ff.io.xhrPost(url,{level:this._workflow.level},dojo.hitch(this,"_logincb"));}return false;},emailLogin:function(evt){ff.io.xhrFormPost(evt.target.action,evt.target,dojo.hitch(this,"_logincb"));evt.stopPropagation();evt.preventDefault();return false;},forgotPassword:function(url){dojo.publish("/ff/login/panel/close");ff.io.xhrPost(url,{},dojo.hitch(this,"_logincb"));},signupPopup:function(url,_3b){dojo.publish("/ff/login/panel/close");ff.io.xhrPost(url,{level:_3b},dojo.hitch(this,"_logincb"));},logout:function(_3c){if(this.isLoggedIn()){FB.getLoginStatus(function(_3d){if(_3d.session){FB.logout(function(){window.location.href="/logout?furl=/";});}else{window.location.href="/logout?furl=/";}});}},doFBLogin:function(_3e){var _3f=this;dojo.mixin(_3f._workflow,_3e);if(_3f._facebook_login_in_process===false){_3f._facebook_login_in_process=true;setTimeout(function(){_3f._facebook_login_in_process=false;},_3f.timeoutValue);var _40=_3f._get_scope(_3f._workflow);if(_3e.success||_3e.fail){_3f._workflow.success=_3e.success;_3f._workflow.fail=_3e.fail;}var aR=FB.getAuthResponse();if(aR&&aR!==true){FB.api("/me",function(_41){FB.api("/me/permissions",function(_42){_41.scope=ff.t.getKeys(_42.data[0]).join(",");_41.access_token=aR.accessToken;_41.expires=aR.expiresIn;ff.io.xhrPost("/fb/login",_41,dojo.hitch(_3f,"_logincb"));});});}else{_3f._forceFBLogin(_40);}}},doTWLogin:function(_43){this._workflow.level=_43.level||3;if(_43.success||_43.fail){this._workflow.success=_43.success;this._workflow.fail=_43.fail;}var _44=this;if(_44._twitter_login_in_process===false){_44._twitter_login_in_process=true;setTimeout(function(){_44._twitter_login_in_process=false;},_44.timeoutValue);var _45=window.location.protocol+"//"+window.location.host;_44._twitterAction_=_44._workflow.success;window.open(_45+"/twitter/login","_blank","left=100,top=100,height=480,width=850,location=no,resizable=yes,scrollbars=yes");}},connectToCToggle:function(_46,_47){var _48=function(){dojo.query(".error",_46).removeClass("hidden");},_49=function(){dojo.query(".error",_46).addClass("hidden");},_4a=[];dojo.query("input",_46).connect("change",function(e){if(e.target.checked){_49();}});dojo.query(".facebookBtn",_46).forEach(function(_4b){_4a.push(dojo.connect(_4b,"click",function(e){if(!dojo.byId(_47).checked){_48();}else{_49();return window.__auth__.doFBLogin({success:ff.t.goto_url_or_reload(this)});}}));});dojo.query(".twitterBtn",_46).forEach(function(_4c){_4a.push(dojo.connect(_4c,"click",function(e){if(!dojo.byId(_47).checked){_48();}else{_49();dojo.forEach(_4a,dojo.disconnect);return window.__auth__.doTWLogin({success:ff.t.goto_url_or_reload(this)});}}));});}});}