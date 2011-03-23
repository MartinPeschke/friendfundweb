String.prototype.strip = function(char) 
    {
        var re = new RegExp("^"+char+"+|"+char+"+$", "g");
        return String(this).replace(re, '');
    };

protected = function(callback){return function(data){
	if(data.success){callback(data)} else {protect()};};
};
protect = function(callback){ return function(evt){
	xhrPost("/myprofile/login", {}, protected(callback));
	page_reloader = callback;
	if(evt){evt.stopPropagation();evt.preventDefault();}return false;
};};
reloadPicture = function(rootnode, intermediate_imgid, persisterid){
	var rn=dojo.byId(rootnode);
	return function(data){
		var f = function(evt){
			dojo.byId(persisterid).value=data.rendered_picture_url;
			dojo.query("img.displayed", rn).addClass("hiddenSpec").removeClass("displayed");
			if(dojo.byId("pictureCounter")){picCounter+=1;dojo.byId("pictureCounter").innerHTML=picCounter;}
			if(dojo.byId("pictureCounterPos")){dojo.byId("pictureCounterPos").innerHTML=1;}
			rn.insertBefore(dojo.create("IMG", {"class":"allowed displayed", src:data.rendered_picture_url}), rn.firstChild);
			rn.appendChild(dojo.create("INPUT", {"type":"hidden", value:data.rendered_picture_url, "class":"PURLImgListElem", name:"img_list"}));
			closePopup();
		};
		if(data.success){
		dojo.byId(intermediate_imgid).src = data.rendered_picture_url;
		dojo.query("input.transp", intermediate_imgid.parentNode).removeClass("transp").onclick(f);
		} else {
			alert("Unsupported file type")
		}
	};
};
findParent = function(rootnode, className){
	if(dojo.hasClass(rootnode, className)){return rootnode;}
	else if(!dojo.hasClass(rootnode, className)&&rootnode.parentNode){return findParent(rootnode.parentNode, className);}
	else {return null}
}
addClassToParent = function(rootnode, className, addClass){
	var node = findParent(rootnode, className);
	if(node){dojo.addClass(node, addClass);}
}
remClassFromParent = function(rootnode, className, remClass){
	var node = findParent(rootnode, className);
	if(node){dojo.removeClass(node, remClass);}
}

parseSelectables = function(rootnode, parentClass, selectedName){
	var parentClass = parentClass||"borderBottom";
	var selectedName = selectedName||"selected";
	var a = function(evt){
			evt&&addClassToParent(evt.target, parentClass, selectedName);
		},
		r = function(evt){
			evt&&remClassFromParent(evt.target, parentClass, selectedName);
		};
	if(dojo.isIE===undefined){
		dojo.byId(rootnode).addEventListener('focus',a,true);
		dojo.byId(rootnode).addEventListener('blur',r,true);
	} else {
		dojo.connect(dojo.byId(rootnode), "onfocusin", a);
		dojo.connect(dojo.byId(rootnode), "onfocusout", r);
	}
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
					var field = dojo.query("input[type=hidden]", root)[0];
					var length = dojo.attr(field, "_length");
					var editor = dojo.create(dojo.attr(field, "_type"), {type:"text", "class":field.className, _length:length, value:field.value, name:field.name, id:field.id});
					var evts = [],  _backups = [];
					var f = function(editevt){
							var newval=editevt.target.value;
							if(newval.length==0){return;}
							dojo.forEach(evts, dojo.disconnect);
							dojo.addClass(root,'active');
							field.value = newval;
							dojo.empty(root);
							root.innerHTML = length?newval.substr(0,length):newval;
							if(length&&newval.length>length){root.innerHTML=root.innerHTML+"...";}
							dojo.forEach(_backups, function(elem){root.appendChild(elem);});
							parseSimpleEditables(rootnode);
						};
					evts.push(dojo.connect(editor, "onchange", f));
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
					xhrPost('/d/e/'+dojo.attr(root, '_elem'), {value:dojo.attr(root, '_value')}, 
						function(data){
							dojo.place(data,root,"only");
							dojo.disconnect(d);
							dojo.query('input[type=text],select,textarea', root).forEach(
								function(editor){
									editor.focus();
									var evts = [];
									var f = function(editevt){
											dojo.forEach(evts, dojo.disconnect);
											dojo.addClass(root,'active');
											if(editor.tagName=='SELECT'){
												dojo.attr(root, '_value', editevt.target.options[editevt.target.selectedIndex].value);
											} else {
												dojo.attr(root, '_value', editevt.target.value);
											}
											xhrPost('/d/d/'+dojo.attr(root, '_elem'), {value:dojo.attr(root, '_value')}, 
												function(data){
													root.innerHTML = data;
													parseEditables(rootnode);
												});
											};
									evts.push(dojo.connect(editor, "onchange", f));
									evts.push(dojo.connect(editor, "onblur", f));
								});
						});
				});
		});
};

popup_esc_handler = [];
esc_handler_f = function(callback, evt){if(evt.keyCode === 27){dojo.hitch(this, callback(evt));}};
accessability = function(callbackRet, callbackEsc, evt){
	if(evt.keyCode === 13){dojo.hitch(this, callbackRet(this, evt));}
	else if(evt.keyCode === 27){dojo.hitch(this, callbackEsc(this, evt));}
};
closePopup = function(){dojo.query("#generic_popup *").orphan();dojo.forEach(popup_esc_handler, dojo.disconnect);popup_esc_handler=[];};
displayPopup = function(html){
	dojo.place(html, dojo.byId("generic_popup"), "only" );
	dojo.query(".panelcloser,.popupBackground", "generic_popup").forEach(function(elt){popup_esc_handler.push(dojo.connect(elt, "onclick", closePopup));});
	popup_esc_handler.push(dojo.connect(window, "onkeyup", dojo.hitch(null, esc_handler_f, closePopup)));
	var i = dojo.query("input", "generic_popup");
	if(i.length>0){i[0].focus()};
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

ioFrameHandler = function(callback){;
	return function(data,xhrobj,evt) {
		//dojo.query("#dojoIoIframe").orphan();
		xhrHandler(callback)(data,xhrobj,evt);
	}
}

xhrHandler = function(callback){
	return function(data,xhrobj,evt) {
		if (data.close_popup === true){closePopup();}
		if (data.clearmessage !== undefined){clear_messages();}
		//if (data.message !== undefined){displayMessage(data.message);}
		if (callback && data.html !== undefined){callback(data.html);}
		if (data.login_panel !== undefined){closePopup();dojo.place(data.login_panel, "accountcontainer", "only");if(data['data'].success){page_reloader()};}
		if (callback && data.data !== undefined){callback(data.data);}
		if (data.redirect !== undefined){window.location.href = data.redirect;}
		if (data.popup !== undefined){displayPopup(data.popup);}
		if (data.reload === true){window.location.reload();}
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

xhrPost = function(url, args, callback, method, error_callback) {
	var _method = method || 'Post';
	dojo['xhr'+_method]({
		url:url,
		content:args,
		handleAs: 'json',
		load:xhrHandler(callback),
		error:error_callback||xhrErrorHandler
	});
};
ioIframeGetJson = function(url, formid, callback){
	var td = dojo.io.iframe.send({
		url: url,
		form: formid,
		method: "post",
		content: {},
		timeoutSeconds: 15,
		preventCache: true,
		handleAs: "json",
		load: ioFrameHandler(callback),
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
facebook_tried_getting_permissions = false;
facebook_tried_loggin_in_already = false;
twitter_tried_loggin_in_already = false;
timeoutValue=500;

twInit = function(furl) {
	if(twitter_tried_loggin_in_already === false){
		twitter_tried_loggin_in_already = true;
		setTimeout(function(){twitter_tried_loggin_in_already=false;},timeoutValue);
		var localhost = window.location.protocol + '//' + window.location.host;
		if(furl){
			page_reloader=function(){window.location.href=furl;};
			window.open(localhost+"/twitter/login?furl="+furl, '_blank', 'left=100,top=100,height=400,width=850,location=no,resizable=no,scrollbars=no');
		} else {
			window.open(localhost+"/twitter/login", '_blank', 'left=100,top=100,height=400,width=850,location=no,resizable=no,scrollbars=no');
		}
	}
};


var FBSCOPE="user_birthday,friends_birthday,email,publish_stream,create_event";
fb_handleLogin = function(response){
	var scope;
	if(response.perms.match(/^[,a-zA-Z0-9_-]+$/)){
		scope=response.perms.replace(/,/g,"|");
	}else{
		var perms = dojo.fromJson(response.perms);
		var a=[];for(var i in perms){a.push(perms[i].join("|"));}
		scope = a.join("|");
	};
	var missing_perms = FBSCOPE.replace(new RegExp(scope, "g"), "").strip(",");
	if(missing_perms){response.scope = scope;response.missing_scope = missing_perms;xhrPost('/fb/failed_login', response);return false;};
	FB.api('/me', function(response) {response.scope = scope;xhrPost('/fb/login', response);});
	return true;
};
fbLogin = function(response) {
	FB.Event.unsubscribe('auth.login', fbLogin);
	if(facebook_tried_loggin_in_already === false){
		if(response&&response['session']){
			FB.getLoginStatus(fb_handleLogin);
		} else {
			facebook_tried_loggin_in_already = true;
			setTimeout(function(){facebook_tried_loggin_in_already=false;},timeoutValue);
			FB.login(fb_handleLogin, {perms:FBSCOPE});
		};
	}
};
fbLogout = function(){if(FB.getSession()){FB.logout(function(response){});}else{window.location.href = "/logout?furl=/";}};
fbInit = function(app_id) {
	window.fbAsyncInit = function() {
		var channelUrl = document.location.protocol + '//' + document.location.host+"/channel.htm";
		FB.init({appId:app_id, status:true, cookie:true, xfbml:false, channelUrl:channelUrl});
		FB.Event.subscribe('auth.login', fbLogin);
		FB.Event.subscribe('auth.logout', fbLogout);
	};
	var e = document.createElement('script');
	e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
	e.async = true;
	document.getElementById('fb-root').appendChild(e);
};
/*===========================================*/
var urlmatch = /^(www\.|https?:\/\/)([-a-zA-Z0-9_]{2,256}\.)+[a-z]{2,4}(\/[-a-zA-Z0-9%_\+.,~#&=!]*)*(\?[-a-zA-Z0-9%_\+,.~#&=!\/]+)*$/i;
var picCounter, accepted, _parser_backups, _localhndlrs;

var createAppendPicture = function(imgContainer, imgs, preselected){
	var imgsrc = imgs.shift();
	if(imgsrc!==undefined){
		var img = dojo.create("IMG", {"class":'hiddenSpec'});
		imgContainer.appendChild(img);
		img.onload = dojo.hitch(null, pic_judger, imgContainer, imgs, preselected);
		img.src = imgsrc;
	}
};

var pic_judger = function(imgContainer, imgs, preselected, evt){
	if(dojo.byId("pictureCounter")){
		if((this.width||this.offsetWidth||this.naturalWidth)<100||(this.height||this.offsetHeight||this.naturalHeight)<75){
			dojo.query(this).orphan();
		}else{
			dojo.addClass(this, "allowed");
			picCounter+=1;
			dojo.byId("pictureCounter").innerHTML=picCounter;
			if(!preselected&&!accepted||this.src===preselected){
				accepted = true;
				dojo.addClass(this, "displayed");
				dojo.removeClass(this, "hiddenSpec");
				dojo.byId("pictureCounterPos").innerHTML=dojo.query(".imgCntSld img.allowed", "homeurlexpander").indexOf(this)+1;
				var ctrInput = dojo.byId("URLPproductPicture");
				if(!ctrInput){
					ctrInput = dojo.create("INPUT", {type:"hidden", value:this.src, id:"URLPproductPicture", name:'product_picture'});
					dojo.byId("homeurlexpander").appendChild(ctrInput);
				} else {
					ctrInput.value = this.src;
				}
			}
		}
		createAppendPicture(imgContainer, imgs, preselected);
	}
};

var slide = function(step, evt){
	var imgs=dojo.query(".imgCntSld img.allowed", "homeurlexpander");
	for(var i=0, len=imgs.length;i<len;i++){
		var pos=(len+(step+i))%len;
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

var urlPEEvents = function(baseRoot, editnode, evt){
	if(findParent(evt.target, "smallLeft")){slide(-1)}
	else if(findParent(evt.target, "smallRight")){slide(1);}
	else if(editnode && dojo.hasClass(evt.target, "parsercloser")){resetParser(baseRoot, editnode);}
};
var connectURLP = function(baseRoot, editnode){
	picCounter = picCounter||0; accepted = accepted||false; _parser_backups = _parser_backups||[]; _localhndlrs = _localhndlrs||[];
	var home = dojo.byId("homeurlexpander");
	parseSimpleEditables(home);
	parseDefaultsInputs(home);
	_localhndlrs.push(dojo.connect(home, "onclick", dojo.hitch(null, urlPEEvents, baseRoot, editnode)));
	createAppendPicture(dojo.byId("URLPimgCntSld"), 
						dojo.query(".PURLImgListElem", home).attr("value"), 
						dojo.byId("URLPproductPicture").value);
};

var resetParser = function(baseRoot, editnode){
	dojo.empty("homeurlexpander");
	dojo.forEach(_parser_backups, function(elem){dojo.byId("homeurlexpander").appendChild(elem)});
	dojo.forEach(_localhndlrs, dojo.disconnect);
	picCounter = 0; accepted = false; _parser_backups = [], _localhndlrs = [];
	dojo.query(".hideable", baseRoot).removeClass("hidden");
	dojo.query("#homeurlexpander").removeClass("home_expander");
	connectURLParser(baseRoot, editnode);
}

var loadSuccess = function(baseRoot, editnode, data){
	dojo.empty("homeurlexpander");
	if(data.success === false){
		resetParser(baseRoot, editnode);
	} else {
		var home = dojo.byId("homeurlexpander");
		dojo.place(data.html, home, "only");
		connectURLP(baseRoot, editnode);
	}
};
var connectURLParser = function(baseRoot, editnode, parseNow, extra_params){
	var dn = dojo.byId(editnode), _linkers= [],
		reconnect = function(){
			picCounter = 0; accepted = false; _parser_backups = []; _localhndlrs = [];
			_linkers.push(dojo.connect(dn, "onkeyup", parseInputFromEvt));
			_linkers.push(dojo.connect(dn, "onpaste", parseInputFromEvt));
			_linkers.push(dojo.connect(dn, "onblur", parseInputFromEvt));
		},
		parseInput = function(){
			var found=false
			if(!dojo.hasClass(dn, "default")){
				var token = dn.value.split(" ");
				for(var i=0, len = token.length;i<len;i++){
					var elt = token[i];
					if(urlmatch.test(elt)){
						var query = elt, url = dojo.attr(dn, "_url");
							dojo.query(".hideable", baseRoot).addClass("hidden");
							dojo.query("#homeurlexpander").addClass("home_expander").removeClass("hidden");
							
							var div = dojo.create("DIV", {"class":"loading"});
							div.appendChild(dojo.create("IMG", {src:"/static/imgs/ajax-loader.gif"}));
							_parser_backups = dojo.query("> *", "homeurlexpander").orphan();
							dojo.place(div, "homeurlexpander", "last");
							extra_params = extra_params||{};
							extra_params.query = query;
							dojo.xhrPost({url:url, content:extra_params,
											handleAs: 'json',
											load:dojo.hitch(null, loadSuccess, baseRoot, editnode),
											error: function(){resetParser(baseRoot, editnode)}});
							found = true;
							break;
						};
				}
			};
			if(!found&&_linkers.length==0){reconnect();}
		},
		parseInputFromEvt = function(evt, ename){
			if(evt.type==="paste"){
				dojo.forEach(_linkers, dojo.disconnect);_linkers=[];
				window.setTimeout(parseInput, 200);
			} else if(!evt.keyCode||(evt.keyCode==32)){
				dojo.forEach(_linkers, dojo.disconnect);_linkers=[];
				parseInput();
			};
			return evt;
		};
	reconnect();
	if(parseNow){parseInput(dn);}
};