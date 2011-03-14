reloadPicture = function(rootnode, intermediate_imgid, persisterid){
	var rn=dojo.byId(rootnode);
	return function(data){
		var f = function(evt){
			dojo.byId(persisterid).value=data.rendered_picture_url;
			dojo.query("img.displayed", rn).addClass("hiddenSpec").removeClass("displayed");
			if(dojo.byId("pictureCounter")){picCounter+=1;dojo.byId("pictureCounter").innerHTML=picCounter;}
			rn.insertBefore(dojo.create("IMG", {"class":"allowed displayed", src:data.rendered_picture_url}), rn.firstChild);
			closePopup();
		};
		dojo.byId(intermediate_imgid).src = data.rendered_picture_url;
		dojo.query("input.hidden", intermediate_imgid.parentNode).removeClass("hidden").onclick(f);
	};
};

parseSelectables = function(rootnode, className){
	var classes = className||"borderBottom";
	var a = function(evt){evt&&addClassToParent(evt.target, classes, "selected");},
		r = function(evt){evt&&remClassFromParent(evt.target, classes, "selected");};
	dojo.byId(rootnode).onfocusin = a;
	dojo.byId(rootnode).onfocusout = r;
	if(dojo.isIE===undefined){
		dojo.byId(rootnode).addEventListener('focus',a,true);
		dojo.byId(rootnode).addEventListener('blur',r,true);
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
							dojo.forEach(_backups, function(elem){root.appendChild(elem);});
							if(length&&newval.length>length){root.innerHTML=root.innerHTML+"...";}
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
loadPopup = function(evt){closePopup(evt);xhrPost(dojo.attr(this, "_href"), {});};
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

findParent = function(rootnode, className){
	if(!dojo.hasClass(rootnode, className)&&rootnode.parentNode){return findParent(rootnode.parentNode, className);}
	else if(dojo.hasClass(rootnode, className)){return rootnode;}
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

place_element = function(node, callback){
	return function(data){
		dojo.place(data, node, "only");
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
		if (callback && data.data !== undefined){callback(data.data);}
		if (data.redirect !== undefined){window.location.href = data.redirect;}
		if (data.popup !== undefined){displayPopup(data.popup);}
		if (data.reload === true){page_reloader();}
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


doFBFFLogin = function(callback){
	FB.api('/me', function(response) {
		response.scope=FBSCOPE;
		loadElement('/fb/login', "accountcontainer", response, callback);
	});
};

fbSessionChange = function() {
	if (FB.getSession()) {
		doFBFFLogin(page_reloader);
	} else {
		window.location.href = "/logout?furl=/";
	}
};


fbLogin = function() {
	if(!FB.getSession()){
		if(facebook_tried_loggin_in_already === false){
			facebook_tried_loggin_in_already = true;
			setTimeout(function(){facebook_tried_loggin_in_already=false;},timeoutValue);
			FB.login(function(){}, {perms:FBSCOPE});
		}
	}else{fbSessionChange();}
};

fbLogout = function(evt){
	if(FB.getSession()){
		FB.logout(function(response){});
	}else{
		fbSessionChange();
	}
};


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
fbInit = function(app_id, has_prev_tried_logging_in) {
	window.fbAsyncInit = function() {
		var channelUrl = document.location.protocol + '//' + document.location.host+"/channel.htm";
		FB.init({appId  : app_id,status : true,cookie : true,xfbml  : false, channelUrl:channelUrl});
		FB.Event.subscribe('auth.sessionChange', fbSessionChange);
		if(!has_prev_tried_logging_in && FB.getSession()){
			FB.api("/me", function(response) {
					response.scope=FBSCOPE;
					loadElement("/fb/login", "accountcontainer", response, page_reloader);
			});
		}
	};
	var e = document.createElement('script');
	e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
	e.async = true;
	document.getElementById('fb-root').appendChild(e);
};

/*===========================================*/
var urlmatch = /^(www\.|https?:\/\/)([-a-zA-Z0-9_]{2,256}\.)+[a-z]{2,4}(\/[-a-zA-Z0-9%_\+.,~#&=!]*)*(\?[-a-zA-Z0-9%_\+,.~#&=!\/]+)*$/i;
var picCounter = 0, accepted = false, _parser_backups = [], _localhndlrs = [];

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
		if((this.width||this.offsetWidth)<100||(this.height||this.offsetHeight)<75){
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
	dojo.removeClass("homeurlexpander", "home_expander");
	connectURLParser(baseRoot, editnode);
}

var loadSuccess = function(baseRoot, editnode, data){
	dojo.query(".loading", "homeurlexpander").orphan();
	if(data.success === false){
		resetParser(baseRoot, "homeurlexpander");
	} else {
		var home = dojo.byId("homeurlexpander");
		dojo.addClass(home, "home_expander");
		dojo.query(".hideable", baseRoot).addClass("hidden");
		dojo.place(data.html, home, "only");
		connectURLP(baseRoot, editnode);
	}
};
var connectURLParser = function(baseRoot, editnode, parseNow, extra_params){
	var dn = dojo.byId(editnode), _linkers= [],
		parseInput = function(elem){
		if(!dojo.hasClass(elem, "default")){
				dojo.some(elem.value.split(" "), function(elt){
				if(urlmatch.test(elt)){
					var query = elt, url = dojo.attr(elem, "_url");
						dojo.forEach(_linkers, dojo.disconnect);
						var div = dojo.create("DIV", {"class":"loading"});
						div.appendChild(dojo.create("IMG", {src:"/static/imgs/ajax-loader.gif"}));
						_parser_backups = dojo.query("> *", "homeurlexpander").orphan();
						dojo.place(div, "homeurlexpander", "last");
						dojo.removeClass("homeurlexpander", "hidden");
						extra_params = extra_params||{};
						extra_params.query = query;
						dojo.xhrPost({url:url, content:extra_params,
										handleAs: 'json',
										load:dojo.hitch(null, loadSuccess, baseRoot, editnode),
										error: function(){resetParser(baseRoot, editnode)}});
						return true;
					}
				});
			};
		},
		parseInputFromEvt = function(evt){
			if(evt.which === 2||(evt.which === undefined && evt.keyCode === undefined)||(evt.ctrlKey&&evt.keyCode==86||evt.keyCode==32)){parseInput(evt.target);}
		};
	_linkers.push(dojo.connect(dn, "onkeyup", parseInputFromEvt));
	_linkers.push(dojo.connect(dn, "onclick", parseInputFromEvt));
	_linkers.push(dojo.connect(dn, "onblur", parseInputFromEvt));
	if(parseNow){parseInput(dn);}
};