dojo.provide("ff.auth");
dojo.require("ff.Popup");

String.prototype.strip = function(ch){var re = new RegExp("^"+ch+"+|"+ch+"+$", "g");return String(this).replace(re, '');};

dojo.declare("ff.auth", null, {
	timeoutValue:500
	,_FBSCOPE : {  '3':"email",'6':"email,publish_stream",'9':"user_birthday,friends_birthday,email,publish_stream,create_event"}
	,_facebook_login_in_process : false
	,_twitter_login_in_process : false
	,_fbperms : {}
	,_loginPanelContainer : "accountcontainer"
	,_loginPanelForm : "loginPanelContent"
	,_workflow : {success : null, fail : null}
	,constructor: function(args){
		dojo.mixin(this, args);
		this.connectLoginPanel();
		this.fbInit(args.fbappId, args.fbRootNode);
	}
	,connectLoginPanel : function(){
		var _t = this
			,evts = [], subscriptions = []
			,closeLoginPanel = function(){
				dojo.forEach(evts, dojo.disconnect);evts=[];
				dojo.forEach(subscriptions, dojo.unsubscribe);subscriptions=[];
				if(dojo.hasClass("loginlink", "active")){
					dojo.removeClass("loginlink", "active");
					if(dojo.byId(_t._loginPanelForm)){dojo.addClass(_t._loginPanelForm, "hidden");}
				}
			}
			,openLoginPanel = function(evt){
				if(!dojo.hasClass(this, "active")){
					dojo.addClass(this, "active");
					dojo.removeClass(_t._loginPanelForm, "hidden");
					evts.push(dojo.connect(document, "onkeydown", function(evt){if(evt.keyCode == 27){closeLoginPanel(evt);}}));
					evts.push(dojo.connect(document, "onclick", function(evt){if(!(evt.target.id=="loginlink")&&!ff.t.findParent(evt.target, "loginPanel")){closeLoginPanel(evt);}}));
					subscriptions.push( dojo.subscribe("/ff/login/panel/close", closeLoginPanel) );
					
					var i = dojo.query("input", _t._loginPanelForm);i[0].focus();
				} else if(evt.target.id == 'loginlink'){closeLoginPanel();}
			};
		dojo.query(".loginToggleLink", this._loginPanelContainer).onclick(openLoginPanel);
		dojo.query(".logoutLink", this._loginPanelContainer).onclick(_t, "logout", true);
		dojo.query("form", _t._loginPanelContainer).forEach(function(form){form.onsubmit = dojo.hitch(_t, "emailLogin");});
	}
	,forgotPassword : function(url){
		dojo.publish("/ff/login/panel/close");
		ff.w.popupFromLink(url);
	}
	,logout : function(logoutFB){window.location.href = "/logout?furl=/";}
	,fbInit : function(app_id, fbRootNode) {
		var _t = this;
		window.fbAsyncInit = function() {
			var channelUrl = document.location.protocol + '//' + document.location.host+"/channel.htm";
			FB.init({appId:app_id, status:true, cookie:true, xfbml:false, channelUrl:channelUrl});
			if(_t.respectFB){
				FB.Event.subscribe('auth.sessionChange', function(response){
						if(response.status == 'connected'){_t.fbHandleLogin(_t._FBSCOPE['3'], false, response);}else {_t.logout(true);}
				});
				if(_t.getFBPerms){
					FB.getLoginStatus(function(response){
						if(response.status==="connected"){FB.api("/me/permissions", function(perms){_t._fbperms = perms.data[0];});}
					});
				}
			}
		};
		var e = document.createElement('script');
		e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
		e.async = true;
		document.getElementById(fbRootNode).appendChild(e);
	}
	
	,twInit : function(cb) {
		var _t = this;
		if(_t._twitter_login_in_process === false){
			_t._twitter_login_in_process = true;
			setTimeout(function(){_t._twitter_login_in_process=false;},_t.timeoutValue);
			var host = window.location.protocol + '//' + window.location.host;
			_t._twitterAction_ = cb;
			window.open(host+"/twitter/login", '_blank', 'left=100,top=100,height=400,width=850,location=no,resizable=yes,scrollbars=yes');
		}
	}

	,fbHandleLogin : function(required_scope, response){
		var _t = this
			,scope, perms, i, missing_perms, a;
		if(response && response.session && response.status==="connected"){
			console.log(perms);

			missing_perms = required_scope.replace(new RegExp(scope, "g"), "").strip(",").replace(/,,+/g, ',');
			if(missing_perms){
				response.scope = scope;
				response.missing_scope = missing_perms;
				ff.io.xhrPost('/fb/failed_login', response);
				return false;
			}
			
			perms = scope.split('|');
			for(i=0;i<perms.length;i++){
				if(perms[i]){
					_t._fbperms[perms[i]] = 1;
				}
			}
			
			FB.api('/me', function(response) {
				response.scope = scope;
				response.fbsession = dojo.toJson(session);
				ff.io.xhrPost('/fb/login', response);
			});
			return true;
		} else return false;
	}

	,fbLogin : function(scope){
		var _t = this;
		if(typeof(scope)!="string"){scope=_t._FBSCOPE[""+scope];}
		if(_t._facebook_login_in_process === false){
			
			_t._facebook_login_in_process = true;
			setTimeout(function(){_t._facebook_login_in_process=false;},_t.timeoutValue);
			
			FB.login(dojo.hitch(_t, "fbHandleLogin", scope), {perms:scope});
		};
	}
	
	,emailLogin : function(evt){
		ff.io.xhrFormPost(evt.target.action, evt.target, dojo.hitch(this, "logincb"));
		return false;
	}
	
	,logincb : function(login_result){
		var _t = this, login_popup
			,popupHandler=[]
			,loginFormArbiter = function(){
				xhrFormPost(this.action, this, logincb);
				return false;
			}, loginLinkArbiter = function(evt){
				var href = dojo.attr(evt.target, "_href");
				xhrPost(href, {}, logincb);
				return false;
			}, closeLoginPopup = function(){
				dojo.forEach(popupHandler, dojo.disconnect);popupHandler=[];
				dojo.query("#generic_popup").empty();
			}, i;
		
		if(login_result.popup !== undefined){
			dojo.publish("/ff/popup/all/destroy");
			login_popup = new ff.Popup();
			login_popup.afterDisplay = function(popupNode){
				var __t = this;
				dojo.query("form.loginAction", popupNode).forEach(function(form){form.onsubmit = loginFormArbiter;});
				dojo.query("a.loginAction", popupNode).forEach(function(form){__t._handler.push(dojo.connect(form, "onclick", loginLinkArbiter));});
				dojo.query("a.loginFBAction", popupNode).forEach(function(form){__t._handler.push(dojo.connect(form, "onclick", dojo.hitch(_t, "fbLogin", required_scope, true)));});
				dojo.query("a.loginTWAction", popupNode).forEach(function(form){__t._handler.push(dojo.connect(form, "onclick", dojo.hitch(_t, "twInit")));});
			};
			login_popup.afterClose = function(popupNode){
				_t._workflow = {};
			};
			login_popup.display(login_result.popup);
		}
		if(login_result.panel!==undefined&&dojo.byId(_t._loginPanelContainer)){
			dojo.place(login_result.panel, _t._loginPanelContainer, "only");
		}else if(login_result.form&&dojo.byId(_t._loginPanelForm)){
			dojo.place(login_result.form, dojo.byId(_t._loginPanelForm), "only");
			dojo.query("form", _t._loginPanelContainer).forEach(function(form){form.onsubmit = dojo.hitch(_t, "emailLogin");});
			i = dojo.query("input", _t._loginPanelForm);
			if(i.length>0){i[0].focus();}
		}
		else if(login_result.success === true&&_t._workflow.success!=null){_t._workflow.success(login_result);}
		else if(login_result.success === false&&_t._workflow.fail!=null){_t._workflow.fail(login_result);}
		else if(login_result.has_activity === true&&_t._workflow.fwd){_t._workflow.fwd(login_result);}
		else if(login_result.reload === true){window.location.reload(true);}
		

		// }
		// else if(login_result.require_facebook_perms!==undefined){fbLogin(login_result.require_facebook_perms, false, logincb);}
	}

	,doLogin : function(args){
		var _t = this,
			cb = args.cb, 
			failcb = args.failcb, 
			level = args.level||3, 
			url = args.url||"/myprofile/login", 
			link = args.link, 
			form = args.form, 
			popupHandler,
			required_scope=_FBSCOPE[""+level];
		if(args.isFB){
			fbLogin(required_scope, false, logincb);
		} else if(args.isTW){
			twInit(logincb);
		} else {
			if(form){
				xhrFormPost(form.action, form, logincb);
			} else if(link){
				ff.io.xhrPost(dojo.attr(link, "_href"), {}, logincb);
			} else {
				FB.getLoginStatus(function(response){
					if(!args.ignoreFB&&_t.respectFB&&response.status==='connected'){
						var perms = _t._fbperms||{},i,
							missing_perms=[], req_perms = required_scope.split(',');
						for(i=0;i<req_perms.length;i++){
							if(!perms[req_perms[i]]){missing_perms.push(req_perms[i]);}
						}
						if(missing_perms.length>0||_t.isA){
							fbLogin(required_scope, false, logincb);
						} else {
							if(cb){cb();}
						}
					} else {
						ff.io.xhrPost(url, {level:level}, logincb);
					}
				});
			}
		}
		return false;
	}
});