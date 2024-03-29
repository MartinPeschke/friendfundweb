String.prototype.strip = function(ch){var re = new RegExp("^"+ch+"+|"+ch+"+$", "g");return String(this).replace(re, '');};
goto_url = function(link){return function(){window.location.href=dojo.attr(link, "_href");};};
reload = function(link){window.location.reload(true);};

if (!FriendFund) {var FriendFund = {};}
FriendFund.Util = {
	render: function (template, params) {
		return template.replace(/\${([^{}]*)}/g, function (a, b) {
			var r = params[b];
			return typeof r === 'string' || typeof r === 'number' ? r : a;
		})
	},
	displayMessage : alert
};
FriendFund.Element = {
	getDimensions: function (element) {
		var display = element.display;
		if (display != 'none' && display != null) {
			return {
				width: element.offsetWidth,
				height: element.offsetHeight
			};
		}
		var els = element.style;
		var originalVisibility = els.visibility;
		var originalPosition = els.position;
		var originalDisplay = els.display;
		els.visibility = 'hidden';
		els.position = 'absolute';
		els.display = 'block';
		var originalWidth = element.clientWidth;
		var originalHeight = element.clientHeight;
		els.display = originalDisplay;
		els.position = originalPosition;
		els.visibility = originalVisibility;
		return {
			width: originalWidth,
			height: originalHeight
		};
	},
	hasClassName: function (element, className) {
		var elementClassName = element.className;
		return (elementClassName.length > 0 && (elementClassName == className || new RegExp("(^|\\s)" + className + "(\\s|$)").test(elementClassName)));
	},
	addClassName: function (element, className) {
		if (!this.hasClassName(element, className)) {
			element.className += (element.className ? ' ' : '') + className;
		}
		return element;
	},
	removeClassName: function (element, className) {
		element.className = element.className.replace(new RegExp("(^|\\s+)" + className + "(\\s+|$)"), ' ');
		return element;
	}
};
FriendFund.Page = {
	getDimensions: function () {
		var de = document.documentElement;
		var width = window.innerWidth || self.innerWidth || (de && de.clientWidth) || document.body.clientWidth;
		var height = window.innerHeight || self.innerHeight || (de && de.clientHeight) || document.body.clientHeight;
		return {width: width,height: height};
	},
	getDocHeight: function() {
		var D = document, m = Math.max;
		return m(m(D.body.scrollHeight,D.documentElement.scrollHeight),m(D.body.offsetHeight,D.documentElement.offsetHeight),m(D.body.clientHeight,D.documentElement.clientHeight));
	}
};

FriendFund.Login {
	FBSCOPE : {  '3':"email",'6':"email,publish_stream",'9':"user_birthday,friends_birthday,email,publish_stream,create_event"},
	facebook_tried_getting_permissions : false,
	facebook_tried_loggin_in_already : false,
	twitter_tried_loggin_in_already : false,
	timeoutValue:500
};

FriendFund.Popup {
	popup_esc_handler : [],
	esc_handler_f : function(callback, evt){if(evt.keyCode === 27){dojo.hitch(this, callback(evt));}},
	facebook_tried_loggin_in_already : false,
	twitter_tried_loggin_in_already : false,
	timeoutValue:500
};



	
	
	accessability = function(callbackRet, callbackEsc, evt){
		if(evt.keyCode === 13){dojo.hitch(this, callbackRet(this, evt));}
		else if(evt.keyCode === 27){dojo.hitch(this, callbackEsc(this, evt));}
	};
	closePopup = function(){dojo.query("#generic_popup *").orphan();dojo.forEach(popup_esc_handler, dojo.disconnect);popup_esc_handler=[];};
	displayPopup = function(html){dojo.place(html, dojo.byId("generic_popup"), "only" );rigPopup("generic_popup");};
	rigPopup = function(id){
		dojo.query(".panelcloser,.popupBackground", id).forEach(function(elt){popup_esc_handler.push(dojo.connect(elt, "onclick", closePopup));});
		popup_esc_handler.push(dojo.connect(window, "onkeyup", dojo.hitch(null, esc_handler_f, closePopup)));
		var i = dojo.query("input", id);
		if(i.length>0){i[0].focus();}
	};
	loadPopup = function(evt, params){closePopup(evt);xhrPost(dojo.attr(evt.target, "_href"), params || {});};
	clear_messages = function(){destroyPopup("message_container");};
	destroyPopup = function(nodeid) {
		var node = dojo.byId(nodeid);
		if(node){
			dojo.empty(nodeid);
			dojo.style(nodeid, 'display', 'none');
		}
	};
	reloadPicture = function(rootnode, intermediate_imgid, persisterid){
		var rn=dojo.byId(rootnode);
		return function(data){
			var f = function(evt){
				dojo.byId(persisterid).value=data.rendered_picture_url;
				dojo.query("img.displayed", rn).addClass("hiddenSpec").removeClass("displayed");
				if(dojo.byId("pictureCounter")){__parserState__.picCounter+=1;dojo.byId("pictureCounter").innerHTML=__parserState__.picCounter;}
				if(dojo.byId("pictureCounterPos")){dojo.byId("pictureCounterPos").innerHTML=1;}
				rn.insertBefore(dojo.create("IMG", {"class":"allowed displayed", src:data.rendered_picture_url}), rn.firstChild);
				rn.appendChild(dojo.create("INPUT", {"type":"hidden", value:data.rendered_picture_url, "class":"PURLImgListElem", name:"img_list"}));
				closePopup();
			};
			if(data.success){
				dojo.byId(intermediate_imgid).src = data.rendered_picture_url;
				dojo.query("input.transp", intermediate_imgid.parentNode).removeClass("transp");
				dojo.byId("purlSaveButton").onclick = f;
			} else {
				alert("Unsupported file type");
			}
		};
	};
	findParent = function(rootnode, className){
		if(dojo.hasClass(rootnode, className)){return rootnode;}
		else if(!dojo.hasClass(rootnode, className)&&rootnode.parentNode){return findParent(rootnode.parentNode, className);}
		else {return null;}
	};
	addClassToParent = function(rootnode, className, addClass){
		var node = findParent(rootnode, className);
		if(node){dojo.addClass(node, addClass);}
	};
	remClassFromParent = function(rootnode, className, remClass){
		var node = findParent(rootnode, className);
		if(node){dojo.removeClass(node, remClass);}
	};
	parseSelectables = function(rootnode, parentClass, selectedName){
		parentClass = parentClass||"borderBottom";
		selectedName = selectedName||"selected";
		var a = function(evt){
				if(evt){addClassToParent(evt.target, parentClass, selectedName);}
			},
			r = function(evt){
				if(evt){remClassFromParent(evt.target, parentClass, selectedName);}
			};
		if(dojo.isIE===undefined){
			dojo.byId(rootnode).addEventListener('focus',a,true);
			dojo.byId(rootnode).addEventListener('blur',r,true);
		} else {
			dojo.connect(dojo.byId(rootnode), "onfocusin", a);
			dojo.connect(dojo.byId(rootnode), "onfocusout", r);
		}
	};

	showLoadingInfo = function(rootnode){
		dojo.query(".loading_animation", rootnode).removeClass("hidden");
		dojo.query("input[type=submit]", rootnode).forEach(function(elem){elem.disabled = "disabled";});
	};

	onSubmitCleaner = function(rootnode){
		dojo.query("input[_default_text],textarea[_default_text]", rootnode).forEach(
			function(element){
				if(dojo.attr(element, "_default_text") === element.value){element.value="";}
			});
		return true;
	};

	parseSimpleEditables = function(rootnode){
		dojo.query(".simpleeditable.active", rootnode).forEach(
			function(root){
				dojo.removeClass(root,'active');
				var d = dojo.connect(root, "onclick", 
					function(evt){
						dojo.disconnect(d);
						var field = dojo.query("input[type=hidden]", root)[0],
							length = dojo.attr(field, "_length"),
							editor = dojo.create(dojo.attr(field, "_type"), {type:"text", "class":field.className, _length:length, value:field.value, name:field.name, id:field.id}),
							evts = [],  _backups = [],
							f = function(editevt){
								var newval=editevt.target.value;
								if(newval.length===0){return;}
								dojo.forEach(evts, dojo.disconnect);
								dojo.addClass(root,'active');
								field.value = newval;
								dojo.empty(root);
								root.innerHTML = length?newval.substr(0,length):newval;
								if(length&&newval.length>length){root.innerHTML=root.innerHTML+"...";}
								dojo.forEach(_backups, function(elem){root.appendChild(elem);});
								parseSimpleEditables(rootnode);
								return editevt;
							};
						evts.push(dojo.connect(editor, "onblur", f));
						_backups  = dojo.query('> *', root).orphan();
						dojo.empty(root);
						root.appendChild(editor);
						editor.focus();
					});
			});
	};

	parseEditables = function(rootnode){
		dojo.query(".editable.active", rootnode).forEach(
			function(root){
				dojo.removeClass(root,'active');
				var d = dojo.connect(root, "onclick", 
					function(evt){
						xhrPost(dojo.attr(root, '_href'), {value:dojo.attr(root, '_value')}, 
							function(data){
								dojo.place(data,root,"only");
								dojo.disconnect(d);
								dojo.query('input[type=text],select,textarea', root).forEach(
									function(editor){
										editor.focus();
										var evts = [],
											f = function(editevt){
												dojo.forEach(evts, dojo.disconnect);
												dojo.addClass(root,'active');
												if(editor.tagName=='SELECT'){
													dojo.attr(root, '_value', editevt.target.options[editevt.target.selectedIndex].value);
												} else {
													dojo.attr(root, '_value', editevt.target.value);
												}
												xhrPost(dojo.attr(root, '_href'), {value:dojo.attr(root, '_value')}, 
													function(data){
														root.innerHTML = data;
														parseEditables(rootnode);
													}, "Post");
												return editevt;
												};
										evts.push(dojo.connect(editor, "onchange", f, null, f, true));
										evts.push(dojo.connect(editor, "onblur", f, null, f, true));
									});
							}, "Get");
					});
			});
	};

	parseDefaultsInputs = function(rootnode){
		dojo.query("input[_default_text], textarea[_default_text]", rootnode).onfocus(
			function(evt){
				if(dojo.hasClass(this, 'default')){
					dojo.removeClass(this, 'default');
					this.value = "";
				}
			}).onblur(function(evt){
				if(!dojo.hasClass(this, 'default')&&
					this.value.replace(/ /g, "")===""){
						dojo.addClass(this, 'default');
						this.value = dojo.attr(this, '_default_text');
					}
			}).forEach(function(elt){
				if(elt.value!=dojo.attr(elt, "_default_text")){dojo.removeClass(elt, "default");}
			});
	};

	onLoadPagelets = function(root_node){
		dojo.query('.pagelet', root_node).forEach(
			function(elem){
				loadElement(dojo.attr(elem, 'pagelet_href'), elem, {}, null, 'Get');
			});
	};

	place_element = function(node, callback){
		return function(data){
			if(data){dojo.place(data, node, "only");}
			dojo.style(node, 'display', 'Block');
			if(callback){callback.call();}
		};
	};

	xhrHandler = function(callback){
		return function(data,xhrobj,evt) {
			if (data.close_popup === true){closePopup();}
			if (data.clearmessage !== undefined){clear_messages();}
			if (data.message !== undefined){displayMessage(data.message);}
			if (callback && data.html !== undefined){callback(data.html);}
			if (data.login !== undefined&&callback){callback(data.login);}
			if (callback && data.data !== undefined){callback(data.data);}
			if (data.redirect !== undefined){window.location.href = data.redirect;}
			if (data.popup !== undefined){displayPopup(data.popup);}
			if (data.reload === true){window.location.reload(true);}
			return data;
		};
	};

	xhrErrorHandler = function(data,xhrobj,evt){
		if (window.console) {
			console.log(data);
			console.log(xhrobj);
			console.log(evt);
		}
	};

	loadFormElement = function(url, node, form, callback){
		place = function(node, data){
			if(data.success===true){
				callback(data.html);
			} else {
				dojo.place(data.message, dojo.byId(node), "only");
			}
		};
		xhrFormPost(url, form, dojo.hitch(null, place, node));
	};

	loadElement = function(url, node, args, callback, method){
		if(dojo.byId(node)){
			xhrPost(url, args, place_element(node, callback), method);
		} else {
			xhrPost(url, args, callback, method);
		}
	};

	xhrFormPost = function(url, form, callback) {
		dojo.xhrPost({
			url:url,
			form:form,
			handleAs: 'json',
			load:xhrHandler(callback),
			error:xhrErrorHandler
		});
	};

	xhrPost = function(url, args, callback, method) {
		var _method = method || 'Post';
		dojo['xhr'+_method]({
			url:url,
			content:args,
			handleAs: 'json',
			load:xhrHandler(callback),
			error:xhrErrorHandler
		});
	};
	
	ioIframeGetJson = function(url, formid, callback){
		dojo.io.iframe.send({
			url: url,
			form: formid,
			method: "Post",
			content: {},
			timeoutSeconds: 15,
			preventCache: true,
			handleAs: "json",
			load: xhrHandler(callback),
			error: xhrErrorHandler
		});
	};

	lpad = function(no, digits, chr){
		chr = chr || '0';
		digits = digits || 2;
		while((no+"").length < digits){no=chr+""+no;}
		return no;
	};

	displayformatDate = function(date){
		return lpad(date.getDate())+'.'+lpad(date.getMonth()+1)+'.'+date.getFullYear();
	};
	formatDate = function(date){
		return date.getFullYear()+'-'+lpad(date.getMonth()+1)+'-'+lpad(date.getDate());
	};
	/*=============== NETWORK CONNECTIVITY ==================*/
	twInit = function(cb) {
		if(twitter_tried_loggin_in_already === false){
			twitter_tried_loggin_in_already = true;
			setTimeout(function(){twitter_tried_loggin_in_already=false;},timeoutValue);
			var host = window.location.protocol + '//' + window.location.host;
			window.pageState.__twitterAction__ = cb;
			window.open(host+"/twitter/login", '_blank', 'left=100,top=100,height=400,width=850,location=no,resizable=yes,scrollbars=yes');
		}
	};

	fb_handleLogin = function(required_scope, callback){
		var fbhl = function(response){
			var scope, perms, session = response.session,i, missing_perms, a;
			if(response.perms){
				if(response.perms.match(/^[,a-zA-Z0-9_\-]+$/)){
					scope=response.perms.replace(/,/g,"|");
				}else{
					perms = dojo.fromJson(response.perms); a=[];
					for(i in perms){a.push(perms[i].join("|"));}
					scope = a.join("|");
				}
				missing_perms = required_scope.replace(new RegExp(scope, "g"), "").strip(",").replace(/,,+/g, ',');
				if(missing_perms){response.scope = scope;response.missing_scope = missing_perms;xhrPost('/fb/failed_login', response, callback);return false;}
				
				perms = scope.split('|');
				window.pageState.__fbperms__ = window.pageState.__fbperms__||{};
				for(i=0;i<perms.length;i++){if(perms[i]){window.pageState.__fbperms__[perms[i]] = 1;}}
				FB.api('/me', function(response) {
					response.scope = scope;
					response.fbsession = dojo.toJson(session);
					xhrPost('/fb/login', response, function(login){if(login.success){window.pageState.isA=false;}if(callback){return callback(login);}});
				});
				return true;
			}
			return false;
		};
		return fbhl;
	};

	fbLogin = function(scope, partial, callback){
		if(typeof(scope)!="string"){scope=FBSCOPE[""+scope];}
		var fbl = function(response) {
			FB.Event.unsubscribe('auth.login', baseFBLogin);
			if(facebook_tried_loggin_in_already === false){
				facebook_tried_loggin_in_already = true;
				setTimeout(function(){facebook_tried_loggin_in_already=false;},timeoutValue);
				if(response&&response.session&&response.status==="connected"){fb_handleLogin(scope, callback)(response);}
				else {FB.login(function(response){FB.getLoginStatus(fb_handleLogin(scope, callback), true);}, {perms:scope});}
			}};
		if(partial){return fbl;}else{return fbl();}
	};
	baseFBLogin = fbLogin(FBSCOPE['3'], true);
	fbLogout = function(logoutFB){window.location.href = "/logout?furl=/";};

	fbInit = function(app_id) {
		window.fbAsyncInit = function() {
			var channelUrl = document.location.protocol + '//' + document.location.host+"/channel.htm";
			FB.init({appId:app_id, status:true, cookie:true, xfbml:false, channelUrl:channelUrl});
			if(window.pageState.respectFB){
				FB.Event.subscribe('auth.sessionChange', function(response){
						if(response.status == 'connected'){fb_handleLogin(FBSCOPE['3'], false)(response);}else {fbLogout(true);}
					});
				if(window.pageState.getFBPerms){
					FB.getLoginStatus(function(response){
						if(response.status==="connected"){FB.api("/me/permissions", function(perms){window.pageState.__fbperms__ = perms.data[0];});}
					});
				}
			}
		};
		var e = document.createElement('script');
		e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
		e.async = true;
		document.getElementById('fb-root').appendChild(e);
	};

	doLogin = function(args){
		var cb = args.cb, 
			failcb = args.failcb, 
			level = args.level||3, 
			url = args.url||"/myprofile/login", 
			link = args.link, 
			form = args.form, 
			popupHandler,
			required_scope=FBSCOPE[""+level],
			logincb = function(result){
				var loginFormArbiter = function(){
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
				if(result.panel!==undefined&&dojo.byId("accountcontainer")){dojo.place(result.panel, "accountcontainer", "only");}
				closeLoginPopup();
				if(result.popup !== undefined){
					dojo.place(result.popup, dojo.byId("generic_popup"), "only" );
					dojo.query(".panelcloser,.popupBackground", "generic_popup").forEach(function(elt){popupHandler.push(dojo.connect(elt, "onclick", closeLoginPopup));});
					popupHandler.push(dojo.connect(window, "onkeyup", dojo.hitch(null, esc_handler_f, closeLoginPopup)));
					i = dojo.query("input", "generic_popup");
					if(i.length>0){i[0].focus();}
					dojo.query("form.loginAction", "generic_popup").forEach(function(form){form.onsubmit = loginFormArbiter;});
					dojo.query("a.loginAction", "generic_popup").forEach(function(form){popupHandler.push(dojo.connect(form, "onclick", loginLinkArbiter));});
					dojo.query("a.loginFBAction", "generic_popup").forEach(function(form){popupHandler.push(dojo.connect(form, "onclick", fbLogin(required_scope, true, logincb)));});
					dojo.query("a.loginTWAction", "generic_popup").forEach(function(form){popupHandler.push(dojo.connect(form, "onclick", dojo.hitch(null, twInit, logincb)));});
				}
				if(result.has_activity===true&&window.pageState.fwd){window.pageState.fwd(result);}
				else if(result.success===true&&cb){cb(result);}
				else if(result.success===false&&failcb){failcb(result);}
				else if(result.require_facebook_perms!==undefined){fbLogin(result.require_facebook_perms, false, logincb);}
				else if(result.reload === true){window.location.reload(true);}
				else if(result.form&&dojo.byId("loginPanelContent")){
					dojo.place(result.form, dojo.byId("loginPanelContent"), "only");
					i = dojo.query("input", "loginPanelContent");
					if(i.length>0){i[0].focus();}
				}
			};
		if(args.isFB){
			fbLogin(required_scope, false, logincb);
		} else if(args.isTW){
			twInit(logincb);
		} else {
			if(form){
				xhrFormPost(form.action, form, logincb); 
			} else if(link){
				xhrPost(dojo.attr(link, "_href"), {}, logincb);
			} else {
				FB.getLoginStatus(function(response){
					if(!args.ignoreFB&&window.pageState.respectFB&&response.status==='connected'){
						var perms = window.pageState.__fbperms__||{},i,
							missing_perms=[], req_perms = required_scope.split(',');
						for(i=0;i<req_perms.length;i++){
							if(!perms[req_perms[i]]){missing_perms.push(req_perms[i]);}
						}
						if(missing_perms.length>0||window.pageState.isA){
							fbLogin(required_scope, false, logincb);
						} else {
							if(cb){cb();}
						}
					} else {
						xhrPost(url, {level:level}, logincb);
					}
				});
			}
		}
		return false;
	};



/*======================================================================================*/
__parserState__ = {urlmatch:/^(www\.|https?:\/\/)([\-a-zA-Z0-9_]{2,256}\.)+[a-z]{2,4}(\/[\-a-zA-Z0-9%_\+.,~#&=!;:]*)*(\?[\-a-zA-Z0-9%_;:\+,.~#&=!\/]+)*$/i};

createAppendPicture = function(imgContainer, imgs, preselected){
	var imgsrc = imgs.shift(), img;
	if(imgsrc!==undefined){
		img = dojo.create("IMG", {"class":'hiddenSpec forbidden'});
		imgContainer.appendChild(img);
		img.onload = dojo.hitch(null, pic_judger, imgContainer, imgs, preselected);
		img.onerror = dojo.hitch(null, createAppendPicture, imgContainer, imgs, preselected);
		img.src = imgsrc;
	} else {
		imgs=dojo.query(".imgCntSld img.allowed", "homeurlexpander");
		if(imgs.length<=1){
			dojo.query(".imgCntSld img.forbidden", "homeurlexpander").forEach(dojo.hitch(null, judger, 25, 20, preselected));
		}
	}
};

judger = function(minw, minh, preselected, img){
	var ctrInput, w = img.width||img.offsetWidth||img.naturalWidth, h = img.height||img.offsetHeight||img.naturalHeight;
	if(w>=minw&&h>=minh){
		__parserState__.picCounter+=1;
		dojo.byId("pictureCounter").innerHTML=__parserState__.picCounter;
		dojo.removeClass(img, "forbidden");
		dojo.addClass(img, "allowed");
		if(!preselected&&!__parserState__.accepted||img.src===preselected){
			__parserState__.accepted = true;
			dojo.addClass(img, "displayed");
			dojo.removeClass(img, "hiddenSpec");
			dojo.byId("pictureCounterPos").innerHTML=dojo.query(".imgCntSld img.allowed", "homeurlexpander").indexOf(img)+1;
			ctrInput = dojo.byId("URLPproductPicture");
			if(!ctrInput){
				ctrInput = dojo.create("INPUT", {type:"hidden", value:img.src, id:"URLPproductPicture", name:'product_picture'});
				dojo.byId("homeurlexpander").appendChild(ctrInput);
			} else {
				if(dojo.attr(ctrInput, "_set_default")){ctrInput.value = img.src;}
			}
		}
	}
};

pic_judger = function(imgContainer, imgs, preselected, evt){
	if(dojo.byId("pictureCounter")){
		judger(100, 75, preselected, this);
		createAppendPicture(imgContainer, imgs, preselected);
	}
};

slide = function(step, evt){
	var imgs=dojo.query(".imgCntSld img.allowed", "homeurlexpander"), i, pos;
	for(i=0, len=imgs.length;i<len;i++){
		pos=(len+(step+i))%len;
		if(!dojo.hasClass(imgs[i], "hiddenSpec")&&pos!=i){
			dojo.addClass(imgs[i], "hiddenSpec");
			dojo.removeClass(imgs[i], "displayed");
			dojo.addClass(imgs[pos], "displayed");
			dojo.removeClass(imgs[pos], "hiddenSpec");
			dojo.byId("pictureCounterPos").innerHTML=pos+1;
			dojo.byId("URLPproductPicture").value=imgs[pos].src;
			break;
		}
	}
};

urlPEEvents = function(baseRoot, editnode, evt){
	if(findParent(evt.target, "smallLeft")){slide(-1);}
	else if(findParent(evt.target, "smallRight")){slide(1);}
	else if(editnode && dojo.hasClass(evt.target, "parsercloser")){resetParser(baseRoot, editnode);}
};
connectURLP = function(baseRoot, editnode){
	var _p = __parserState__, home = dojo.byId("homeurlexpander");
	_p.picCounter = _p.picCounter||0; 
	_p.accepted = _p.accepted||false; 
	_p._parser_backups = _p._parser_backups||[]; 
	_p._localhndlrs = _p._localhndlrs||[];
	parseSimpleEditables(home);
	parseDefaultsInputs(home);
	_p._localhndlrs.push(dojo.connect(home, "onclick", dojo.hitch(null, urlPEEvents, baseRoot, editnode)));
	createAppendPicture(dojo.byId("URLPimgCntSld"), 
						dojo.query(".PURLImgListElem", home).attr("value"), 
						dojo.byId("URLPproductPicture").value);
};

resetParser = function(baseRoot, editnode){
	dojo.empty("homeurlexpander");
	dojo.forEach(__parserState__._parser_backups, function(elem){dojo.byId("homeurlexpander").appendChild(elem);});
	dojo.forEach(__parserState__._localhndlrs, dojo.disconnect);
	__parserState__.picCounter = 0; 
	__parserState__.accepted = false; 
	__parserState__._parser_backups = []; 
	__parserState__._localhndlrs = [];
	dojo.query(".hideable", baseRoot).removeClass("hidden");
	dojo.query("#homeurlexpander").removeClass("home_expander");
	connectURLParser(baseRoot, editnode);
};

loadSuccess = function(baseRoot, editnode, data){
	dojo.empty("homeurlexpander");
	if(data.success === false){
		resetParser(baseRoot, editnode);
	} else {
		var home = dojo.byId("homeurlexpander");
		dojo.place(data.html, home, "only");
		connectURLP(baseRoot, editnode);
	}
};
connectURLParser = function(baseRoot, editnode, parseNow, extra_params){
	var dn = dojo.byId(editnode), _linkers= [],
		reconnect = function(){
			__parserState__.picCounter = 0; 
			__parserState__.accepted = false; 
			__parserState__._parser_backups = []; 
			__parserState__._localhndlrs = [];
			_linkers.push(dojo.connect(dn, "onkeyup", parseInputFromEvt));
			_linkers.push(dojo.connect(dn, "onpaste", parseInputFromEvt));
			_linkers.push(dojo.connect(dn, "onblur", parseInputFromEvt));
		},
		parseInput = function(){
			var found=false, token, i, elt, query, div, url;
			if(!dojo.hasClass(dn, "default")){
				token = dn.value.split(" ");
				for(i=0, len = token.length;i<len;i++){
					elt = token[i];
					if(__parserState__.urlmatch.test(elt)){
							query = elt;
							url = dojo.attr(dn, "_url");
							dojo.query(".hideable", baseRoot).addClass("hidden");
							
							div = dojo.create("DIV", {"class":"loading"});
							div.appendChild(dojo.create("IMG", {src:"/static/imgs/ajax-loader.gif"}));
							__parserState__._parser_backups = dojo.query("> *", "homeurlexpander").orphan();
							dojo.place(div, "homeurlexpander", "last");
							dojo.query("#homeurlexpander").addClass("home_expander").removeClass("hidden");
							extra_params = extra_params||{};
							extra_params.query = query;
							dojo.xhrPost({url:url, content:extra_params,
											handleAs: 'json',
											load:dojo.hitch(null, loadSuccess, baseRoot, editnode),
											error: function(){resetParser(baseRoot, editnode);}});
							found = true;
							break;
						}
				}
			}
			if(!found&&_linkers.length===0){reconnect();}
		},
		parseInputFromEvt = function(evt, ename){
			if(evt.type==="paste"){
				dojo.forEach(_linkers, dojo.disconnect);_linkers=[];
				window.setTimeout(parseInput, 200);
			} else if(!evt.keyCode||(evt.keyCode==32)){
				dojo.forEach(_linkers, dojo.disconnect);_linkers=[];
				parseInput();
			}
			return evt;
		};
	reconnect();
	if(parseNow){parseInput(dn);}
};
/**** SLIDER ****/
sliderF=function(root, noElems){
	dojo.require("dojo.fx.easing");
	var rootNode = dojo.byId(root), slider = dojo.query("ul.slider", rootNode)[0], leftAmount = parseInt(dojo.attr(slider, "_elem_width"), 10),
		position=0, child, transitioning = false, hover=false,
		countElems = dojo.query("ul.slider li", rootNode).length,
		setHoverOn = function(evt){hover=true;},
		setHoverOff = function(evt){hover=false;},
		slide = function(step, force){ return function(evt){
			var reset = function(){transitioning=false;};
			if(!transitioning&&(!hover||force)){
				transitioning = true;
				if(position===0&&step>0){
					child = slider.getElementsByTagName("li");
					child = slider.removeChild(child[child.length-1]);
					dojo.style(slider, "marginLeft", (leftAmount*(position-step))+"px");
					slider.insertBefore(child, slider.firstChild);
					dojo.animateProperty({node:slider,duration: 900,easing:dojo.fx.easing.sineInOut, properties: {marginLeft:  { start: (leftAmount*(position-step)), end:(leftAmount*(position)), units:"px" }}, onEnd:reset}).play();
				} else if (position===noElems-countElems&&step<0){
					child = slider.removeChild(slider.getElementsByTagName("li")[0]);
					dojo.style(slider, "marginLeft", (leftAmount*(position-step))+"px");
					slider.appendChild(child);
					dojo.animateProperty({node:slider,duration: 900,easing:dojo.fx.easing.sineInOut, properties: {marginLeft:  { start: (leftAmount*(position-step)), end:(leftAmount*(position)), units:"px" }}, onEnd:reset}).play();
				} else {
					
					dojo.animateProperty({node:slider,duration: 900,easing:dojo.fx.easing.sineInOut, properties: {marginLeft:  { start: (leftAmount*(position)), end:(leftAmount*(position+step)), units:"px" }}, onEnd:reset}).play();
					position = position + step;
				}
			}
		};};
	dojo.query(".controllerLeft", rootNode).onclick(slide(1, true));
	dojo.query(".controllerRight", rootNode).onclick(slide(-1, true));
	dojo.connect(rootNode, "onmouseover", setHoverOn);
	dojo.connect(rootNode, "onmouseout", setHoverOff);
	window.setInterval(slide(-1, false), 3500);
};
showTime = function(root, unit){
	var delay = unit*1000,
	d=dojo.query(".timerDays", root)[0], days=parseInt(d.innerHTML, 10),
	h=dojo.query(".timerHours", root)[0], hrs=parseInt(h.innerHTML, 10),
	m=dojo.query(".timerMinutes", root)[0], mins=parseInt(m.innerHTML, 10),
	s=dojo.query(".timerSeconds", root)[0], secs=parseInt(s.innerHTML, 10),
	tick = function(step){return function(){
		if(secs>0){s.innerHTML=secs=secs+step;}
		else if(mins>0){s.innerHTML=secs=59;m.innerHTML=mins=mins-1;}
		else if(hrs>0){s.innerHTML=secs=59;m.innerHTML=mins=59;h.innerHTML=hrs=hrs-1;}
		else if(days>0){s.innerHTML=secs=59;m.innerHTML=mins=59;h.innerHTML=hrs=23;d.innerHTML=days=days-1;}
		else{return;}
		window.setTimeout(tick(-unit), delay);
	};};
	window.setTimeout(tick(-unit), delay);
};











