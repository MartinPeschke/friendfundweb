dojo.provide("ff.auth");
dojo.require("ff.Popup");

String.prototype.strip = function(ch){var re = new RegExp("^"+ch+"+|"+ch+"+$", "g");return String(this).replace(re, '');};

dojo.declare("ff.auth", null, {
	timeoutValue:500
	,_FBSCOPE : {  '3':"email",'6':"email,publish_stream",'9':"email,publish_stream,create_event,user_birthday,friends_birthday"}
	,_get_scope:function(args){return this._FBSCOPE[""+(args.level||3)];}
	,_facebook_login_in_process : false
	,_twitter_login_in_process : false
	,_fbperms : null
	,_loginPanelContainer : "accountcontainer"
	,_loginPanelForm : "loginPanelContent"
	,_loginPanelHandler : []
	,_workflow : {success : null, fail : null}
	,_fwd : function(){window.location.href = '/mypools/stream'}
	,fwd : false
	,_rld : ff.t.reload
	,rld : false
	,hasLoginPanel : true
	,isLoggedIn : function(){return !dojo.byId("loginlink");}
	,constructor: function(args, optionals){
		dojo.mixin(this, args);
		if(optionals&&typeof(optionals)==="object"){dojo.mixin(this, optionals);}
		if(this.hasLoginPanel){this.connectLoginPanel();}
		this.fbInit(args.fbappId, args.fbRootNode);
		this._fb_login_in_progress = false;
	}
	
	,loginPanelFormConnect : function(){
		var _t = this;
		dojo.forEach(_t._loginPanelHandler, dojo.disconnect);_t._loginPanelHandler=[];
		dojo.query("form", _t._loginPanelContainer).forEach(function(form){_t._loginPanelHandler.push(dojo.connect(form, "onsubmit", _t, "emailLogin"));});
	}
	,connectLoginPanel : function(){
		var _t = this
			,evts = []
			,subscriptions = []
			,global_panel = []
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
					_t.loginPanelFormConnect();
					var i = dojo.query("input", _t._loginPanelForm);i[0].focus();
				} else if(evt.target.id == 'loginlink'){closeLoginPanel();}
			}, reconnect = function(){
				dojo.forEach(global_panel, dojo.disconnect);global_panel=[];
				dojo.query(".loginToggleLink", _t._loginPanelContainer).forEach(function(elem){global_panel.push( dojo.connect(elem, "onclick", openLoginPanel));})
				dojo.query(".logoutLink", _t._loginPanelContainer).forEach(function(elem){global_panel.push( dojo.connect(elem, "onclick", _t, "logout", true));})
				dojo.subscribe("/ff/login/panel/reconnect", reconnect);
			};
		reconnect();
	}
	,logout : function(logoutFB){
		if(this.isLoggedIn()){
			FB.getLoginStatus(function(response){
				if(response.session){FB.logout(function(){window.location.href = "/logout?furl=/";})}
				else{window.location.href = "/logout?furl=/";}
			});
		}
	}
	
	,fbInit : function(app_id, fbRootNode) {
		var _t = this;
		window.fbAsyncInit = function() {
			var channelUrl = document.location.protocol + '//' + document.location.host+"/channel.htm";
			FB.init({appId:app_id, status:true, cookie:true, xfbml:false, channelUrl:channelUrl});
			FB.Event.subscribe("auth.sessionChange", dojo.hitch(_t, "handleSessionChange"));
			if(_t.requireFBPerms){_t.getFBPerms();}
		}
		
		var e = document.createElement('script');
		e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
		e.async = true;
		document.getElementById(fbRootNode).appendChild(e);
	}
	,handleSessionChange : function(response){
		var _t = this;
		if(response.status==="connected"){
			var sess = response.session;
			if(_t.fbId&&sess.uid!=_t.fbId){
				if(_t.isLoggedIn()){window.location.href = "/logout?furl=/";}
			}else{
			if(!_t._fb_login_in_progress){
				_t.forceRefreshPerms(dojo.hitch(_t, "fbHandleLogin", _t._get_scope(_t._workflow), response));
			} else { _t._fb_login_in_progress = false; }
			}
		} else {
			if(_t.isLoggedIn()){window.location.href = "/logout?furl=/";}
		}
	}
	,forceRefreshPerms : function(cb){
		var _t = this;
		FB.api("/me/permissions", function(perms){
			_t._fbperms = perms.data[0];cb&&cb(_t._fbperms)
		});
	}
	,forceFBLogin : function(required_scope){
		var _t = this;
		_t._fb_login_in_progress = true;
		FB.login(function(response){
			if(response.status=="connected"){
				_t.forceRefreshPerms(dojo.hitch(_t, "fbHandleLogin", required_scope, response));
			}
		}, {perms:required_scope});
	}
	,getFBPerms : function(cb, notloggedin){
		var _t = this;
		if(!_t._fbperms){
			session = FB.getSession();
			if(session&&session.uid){
				_t.forceRefreshPerms(cb);
			}else{
				notloggedin&&notloggedin();
			}
		}else{cb&&cb(_t._fbperms);}
	}
	,getMissingFBPerms : function(/*comma seperated*/ required_scope, /* map */perms){
		var mp = required_scope.split(","),missing_perms = [], perms=perms||{};
		for(var i=0;i<mp.length;i++){
			if(!perms[mp[i]]){
				missing_perms.push(mp[i]);
			}
		}
		return missing_perms;
	}
	,checkFBIsInOrder : function(required_scope, level){
		var response = {}, _t = this, sess = FB.getSession();
		if(this.fbId && sess){
			var mp = this.getMissingFBPerms(required_scope, this._fbperms);
			if(mp.length&&level>3){
				this.forceFBLogin(required_scope);
				return false;
			} else {
				return true;
			}
		} else return true;
	}
	,checkLogin : function(args){
		var _t = this;
		this._workflow.level=args.level||3;
		var url = args.url||this.loginurl, required_scope = _t._get_scope(_t._workflow);
		if(args.success||args.fail){this._workflow.success = args.success; this._workflow.fail = args.fail;}
		if(this.isLoggedIn()){
			if(args.ignoreFB||_t.checkFBIsInOrder(required_scope, _t._workflow.level)){
				_t._workflow.success();
			}
		} else {
			ff.io.xhrPost(url, {level:this._workflow.level}, dojo.hitch(this, "logincb"));
		}
		return false;
	}
	,fbHandleLogin : function(required_scope, response){
		var _t = this, scope, i, missing_perms, a, response = {};
		var mp = _t.getMissingFBPerms(required_scope, _t._fbperms);
		if(mp.length){
			response.scope = ff.t.getKeys(_t._fbperms).join(",");
			response.missing_scope = mp.join(",");
			ff.io.xhrPost('/fb/failed_login', response);
		} else {
			FB.api('/me', function(response) {
				response.scope = ff.t.getKeys(_t._fbperms).join(",");
				response.fbsession = dojo.toJson(FB.getSession());
				ff.io.xhrPost('/fb/login', response, dojo.hitch(_t, "logincb"));
			});
		}
	}
	
	,doFBLogin : function(args){
		var _t = this;
		dojo.mixin(_t._workflow, args);
		if(_t._facebook_login_in_process === false){
			_t._facebook_login_in_process = true;
			setTimeout(function(){_t._facebook_login_in_process=false;},_t.timeoutValue);
			
			var required_scope = _t._get_scope(_t._workflow);
			if(args.success||args.fail){_t._workflow.success = args.success; _t._workflow.fail = args.fail;}
			
			_t.getFBPerms(
				/*if loggedin*/function(perms){
					var mp = _t.getMissingFBPerms(required_scope, perms);
					if(mp.length){
						_t.forceFBLogin(required_scope);
					} else {
						FB.api('/me', function(response) {
							response.scope = ff.t.getKeys(perms).join(",");
							response.fbsession = dojo.toJson(FB.getSession());
							ff.io.xhrPost('/fb/login', response, dojo.hitch(_t, "logincb"));
						});
					}
				},
				/*else*/function(){
					_t.forceFBLogin(required_scope);
				}
			);
		}
	}
	
	,doTWLogin : function(args) {
		this._workflow.level=args.level||3;
		
		if(args.success||args.fail){this._workflow.success = args.success; this._workflow.fail = args.fail;}
		
		var _t = this;
		if(_t._twitter_login_in_process === false){
			_t._twitter_login_in_process = true;
			setTimeout(function(){_t._twitter_login_in_process=false;},_t.timeoutValue);
			var host = window.location.protocol + '//' + window.location.host;
			_t._twitterAction_ = _t._workflow.success ;
			window.open(host+"/twitter/login", '_blank', 'left=100,top=100,height=400,width=850,location=no,resizable=yes,scrollbars=yes');
		}
	}
	,emailLogin : function(evt){
		ff.io.xhrFormPost(evt.target.action, evt.target, dojo.hitch(this, "logincb"));
		evt.stopPropagation();
		evt.preventDefault()
		return false;
	}
	,forgotPassword : function(url){
		dojo.publish("/ff/login/panel/close");
		ff.io.xhrPost(url, {}, dojo.hitch(this, "logincb"));
	}
	,logincb : function(login_result){
		var _t = this, i
			,login_popup
			,required_scope=_t._get_scope(_t._workflow)
			,popupHandler=[]
			,loginFormArbiter = function(){
				ff.io.xhrFormPost(this.action, this, dojo.hitch(_t,"logincb"));
				return false;
			}, loginLinkArbiter = function(evt){
				var href = dojo.attr(evt.target, "_href");
				ff.io.xhrPost(href, {}, dojo.hitch(_t, "logincb"));
				return false;
			};
		login_popup = _t._workflow._login_popup;
		if(login_popup){
			delete login_popup.afterClose;
			login_popup.destroy();
		}
		if(login_result.panel!==undefined&&dojo.byId(_t._loginPanelContainer)){
			dojo.place(login_result.panel, _t._loginPanelContainer, "only");
			dojo.publish("/ff/login/panel/reconnect");
		}else if(login_result.form&&dojo.byId(_t._loginPanelForm)){
			dojo.place(login_result.form, dojo.byId(_t._loginPanelForm), "only");
			if(this.hasLoginPanel){_t.loginPanelFormConnect();}
			i = dojo.query("input", _t._loginPanelForm);
			if(i.length>0){i[0].focus();}
		}
		if(login_result.popup !== undefined){
			login_popup = new ff.Popup();
			login_popup.afterDisplay = function(popupNode){
				var __t = this;
				dojo.query("form.loginAction", popupNode).forEach(function(form){form.onsubmit = loginFormArbiter;});
				dojo.query("a.loginAction", popupNode).forEach(function(form){__t._handler.push(dojo.connect(form, "onclick", loginLinkArbiter));});
				dojo.query("a.loginFBAction", popupNode).forEach(function(form){__t._handler.push(dojo.connect(form, "onclick", dojo.hitch(_t, "doFBLogin", _t._workflow)));});
				dojo.query("a.loginTWAction", popupNode).forEach(function(form){__t._handler.push(dojo.connect(form, "onclick", dojo.hitch(_t, "doTWLogin", _t._workflow)));});
			};
			login_popup.afterClose = function(popupNode){
				_t._workflow.fail&&_t._workflow.fail();
				_t._workflow = {};
			};
			login_popup.display(login_result.popup);
			_t._workflow._login_popup = login_popup;
		}
		else if(login_result.success === true&&_t._workflow.success!=null){_t._workflow.success(login_result);_t._workflow = {};}
		else if(login_result.success === false&&_t._workflow.fail!=null){_t._workflow.fail(login_result);_t._workflow = {};}
		else if(login_result.has_activity === true&&_t.fwd===true){_t._fwd(login_result);_t._workflow = {};}
		else if(login_result.success === true&&_t.rld===true){_t._rld(login_result);_t._workflow = {};}
		else if(login_result.reload === true){window.location.href = window.location.href;_t._workflow = {};}
	}
});