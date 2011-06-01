/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["ff.auth"]){dojo._hasResource["ff.auth"]=true;dojo.provide("ff.auth");dojo.require("ff.Popup");String.prototype.strip=function(ch){var re=new RegExp("^"+ch+"+|"+ch+"+$","g");return String(this).replace(re,"");};dojo.declare("ff.auth",null,{timeoutValue:500,_FBSCOPE:{"3":"email","6":"email,publish_stream","9":"email,publish_stream,create_event"},_get_scope:function(_1){return this._FBSCOPE[""+(_1.level||3)];},_facebook_login_in_process:false,_twitter_login_in_process:false,_fbperms:null,_loginPanelContainer:"accountcontainer",_loginPanelForm:"loginPanelContent",_loginPanelHandler:[],_workflow:{success:null,fail:null},_fwd:function(){window.location.href="/mypools/stream";},fwd:false,_rld:ff.t.reload,rld:false,hasLoginPanel:true,isLoggedIn:function(){return !dojo.byId("loginlink");},constructor:function(_2,_3){dojo.mixin(this,_2);if(_3&&typeof (_3)==="object"){dojo.mixin(this,_3);}if(this.hasLoginPanel){this.connectLoginPanel();}this.fbInit(_2.fbappId,_2.fbRootNode);},loginPanelFormConnect:function(){var _4=this;dojo.forEach(_4._loginPanelHandler,dojo.disconnect);_4._loginPanelHandler=[];dojo.query("form",_4._loginPanelContainer).forEach(function(_5){_4._loginPanelHandler.push(dojo.connect(_5,"onsubmit",_4,"emailLogin"));});},connectLoginPanel:function(){var _6=this,_7=[],_8=[],_9=[],_a=function(){dojo.forEach(_7,dojo.disconnect);_7=[];dojo.forEach(_8,dojo.unsubscribe);_8=[];if(dojo.hasClass("loginlink","active")){dojo.removeClass("loginlink","active");if(dojo.byId(_6._loginPanelForm)){dojo.addClass(_6._loginPanelForm,"hidden");}}},_b=function(_c){if(!dojo.hasClass(this,"active")){dojo.addClass(this,"active");dojo.removeClass(_6._loginPanelForm,"hidden");_7.push(dojo.connect(document,"onkeydown",function(_d){if(_d.keyCode==27){_a(_d);}}));_7.push(dojo.connect(document,"onclick",function(_e){if(!(_e.target.id=="loginlink")&&!ff.t.findParent(_e.target,"loginPanel")){_a(_e);}}));_8.push(dojo.subscribe("/ff/login/panel/close",_a));_6.loginPanelFormConnect();var i=dojo.query("input",_6._loginPanelForm);i[0].focus();}else{if(_c.target.id=="loginlink"){_a();}}},_f=function(){dojo.forEach(_9,dojo.disconnect);_9=[];dojo.query(".loginToggleLink",_6._loginPanelContainer).forEach(function(_10){_9.push(dojo.connect(_10,"onclick",_b));});dojo.query(".logoutLink",_6._loginPanelContainer).forEach(function(_11){_9.push(dojo.connect(_11,"onclick",_6,"logout",true));});dojo.subscribe("/ff/login/panel/reconnect",_f);};_f();},logout:function(_12){if(this.isLoggedIn()){FB.getLoginStatus(function(_13){if(_13.session){FB.logout(function(){window.location.href="/logout?furl=/";});}else{window.location.href="/logout?furl=/";}});}},fbInit:function(_14,_15){var _16=this;window.fbAsyncInit=function(){var _17=document.location.protocol+"//"+document.location.host+"/channel.htm";FB.init({appId:_14,status:true,cookie:true,xfbml:false,channelUrl:_17});FB.Event.subscribe("auth.sessionChange",dojo.hitch(_16,"handleSessionChange"));if(_16.requireFBPerms){_16.getFBPerms();}};var e=document.createElement("script");e.src=document.location.protocol+"//connect.facebook.net/en_US/all.js";e.async=true;document.getElementById(_15).appendChild(e);},handleSessionChange:function(_18){var _19=this;if(_18.status==="connected"){var _1a=_18.session;if(_19.fbId&&_1a.uid!=_19.fbId){if(_19.isLoggedIn()){window.location.href="/logout?furl=/";}}else{_19.forceRefreshPerms(dojo.hitch(_19,"fbHandleLogin",_19._get_scope(_19._workflow),_18));}}else{if(_19.isLoggedIn()){window.location.href="/logout?furl=/";}}},forceRefreshPerms:function(cb){var _1b=this;FB.api("/me/permissions",function(_1c){_1b._fbperms=_1c.data[0];cb&&cb(_1b._fbperms);});},forceFBLogin:function(_1d){var _1e=this;FB.Event.unsubscribe("auth.sessionChange",_1e.handleSessionChange);FB.login(function(_1f){_1e.forceRefreshPerms(dojo.hitch(_1e,"fbHandleLogin",_1d,_1f));FB.Event.subscribe("auth.sessionChange",_1e.handleSessionChange);},{perms:_1d});},getFBPerms:function(cb,_20){var _21=this;if(!_21._fbperms){session=FB.getSession();if(session&&session.uid){_21.forceRefreshPerms(cb);}else{_20&&_20();}}else{cb&&cb(_21._fbperms);}},getMissingFBPerms:function(_22,_23){var mp=_22.split(","),_24=[],_23=_23||{};for(var i=0;i<mp.length;i++){if(!_23[mp[i]]){_24.push(mp[i]);}}return _24;},checkFBIsInOrder:function(_25){var _26={};var _27=FB.getSession();if(this.fbId&&_27){_26.scope=ff.t.getKeys(this._fbperms).join(",");var mp=this.getMissingFBPerms(_25,this._fbperms);if(mp.length){this.forceFBLogin(_25);return false;}else{return true;}}else{return true;}},checkLogin:function(_28){var _29=this;this._workflow.level=_28.level||3;var url=_28.url||this.loginurl,_2a=_29._get_scope(_29._workflow);if(_28.success||_28.fail){this._workflow.success=_28.success;this._workflow.fail=_28.fail;}if(this.isLoggedIn()){if(_28.ignoreFB||this.checkFBIsInOrder(_2a)){this._workflow.success();}}else{ff.io.xhrPost(url,{level:this._workflow.level},dojo.hitch(this,"logincb"));}return false;},fbHandleLogin:function(_2b,_2c){var _2d=this,_2e,i,_2f,a,_2c={};var mp=_2d.getMissingFBPerms(_2b,_2d._fbperms);if(mp.length){_2c.scope=ff.t.getKeys(_2d._fbperms).join(",");_2c.missing_scope=mp.join(",");ff.io.xhrPost("/fb/failed_login",_2c);}else{FB.api("/me",function(_30){_30.scope=ff.t.getKeys(_2d._fbperms).join(",");_30.fbsession=dojo.toJson(FB.getSession());ff.io.xhrPost("/fb/login",_30,dojo.hitch(_2d,"logincb"));});}},doFBLogin:function(_31){var _32=this;dojo.mixin(_32._workflow,_31);if(_32._facebook_login_in_process===false){_32._facebook_login_in_process=true;setTimeout(function(){_32._facebook_login_in_process=false;},_32.timeoutValue);var _33=_32._get_scope(_32._workflow);if(_31.success||_31.fail){_32._workflow.success=_31.success;_32._workflow.fail=_31.fail;}_32.getFBPerms(function(_34){var mp=_32.getMissingFBPerms(_33,_34);if(mp.length){_32.forceFBLogin(_33);}else{FB.api("/me",function(_35){_35.scope=ff.t.getKeys(_34).join(",");_35.fbsession=dojo.toJson(FB.getSession());ff.io.xhrPost("/fb/login",_35,dojo.hitch(_32,"logincb"));});}},function(){_32.forceFBLogin(_33);});}},doTWLogin:function(_36){this._workflow.level=_36.level||3;if(_36.success||_36.fail){this._workflow.success=_36.success;this._workflow.fail=_36.fail;}var _37=this;if(_37._twitter_login_in_process===false){_37._twitter_login_in_process=true;setTimeout(function(){_37._twitter_login_in_process=false;},_37.timeoutValue);var _38=window.location.protocol+"//"+window.location.host;_37._twitterAction_=_37._workflow.success;window.open(_38+"/twitter/login","_blank","left=100,top=100,height=400,width=850,location=no,resizable=yes,scrollbars=yes");}},emailLogin:function(evt){ff.io.xhrFormPost(evt.target.action,evt.target,dojo.hitch(this,"logincb"));evt.stopPropagation();evt.preventDefault();return false;},forgotPassword:function(url){dojo.publish("/ff/login/panel/close");ff.io.xhrPost(url,{},dojo.hitch(this,"logincb"));},logincb:function(_39){var _3a=this,i,_3b,_3c=_3a._get_scope(_3a._workflow),_3d=[],_3e=function(){ff.io.xhrFormPost(this.action,this,dojo.hitch(_3a,"logincb"));return false;},_3f=function(evt){var _40=dojo.attr(evt.target,"_href");ff.io.xhrPost(_40,{},dojo.hitch(_3a,"logincb"));return false;};_3b=_3a._workflow._login_popup;if(_3b){delete _3b.afterClose;_3b.destroy();}if(_39.panel!==undefined&&dojo.byId(_3a._loginPanelContainer)){dojo.place(_39.panel,_3a._loginPanelContainer,"only");dojo.publish("/ff/login/panel/reconnect");}else{if(_39.form&&dojo.byId(_3a._loginPanelForm)){dojo.place(_39.form,dojo.byId(_3a._loginPanelForm),"only");if(this.hasLoginPanel){_3a.loginPanelFormConnect();}i=dojo.query("input",_3a._loginPanelForm);if(i.length>0){i[0].focus();}}}if(_39.popup!==undefined){_3b=new ff.Popup();_3b.afterDisplay=function(_41){var _42=this;dojo.query("form.loginAction",_41).forEach(function(_43){_43.onsubmit=_3e;});dojo.query("a.loginAction",_41).forEach(function(_44){_42._handler.push(dojo.connect(_44,"onclick",_3f));});dojo.query("a.loginFBAction",_41).forEach(function(_45){_42._handler.push(dojo.connect(_45,"onclick",dojo.hitch(_3a,"doFBLogin",_3a._workflow)));});dojo.query("a.loginTWAction",_41).forEach(function(_46){_42._handler.push(dojo.connect(_46,"onclick",dojo.hitch(_3a,"doTWLogin",_3a._workflow)));});};_3b.afterClose=function(_47){_3a._workflow.fail&&_3a._workflow.fail();_3a._workflow={};};_3b.display(_39.popup);_3a._workflow._login_popup=_3b;}else{if(_39.success===true&&_3a._workflow.success!=null){_3a._workflow.success(_39);_3a._workflow={};}else{if(_39.success===false&&_3a._workflow.fail!=null){_3a._workflow.fail(_39);_3a._workflow={};}else{if(_39.has_activity===true&&_3a.fwd===true){_3a._fwd(_39);_3a._workflow={};}else{if(_39.success===true&&_3a.rld===true){_3a._rld(_39);_3a._workflow={};}else{if(_39.reload===true){window.location.href=window.location.href;_3a._workflow={};}}}}}}}});}