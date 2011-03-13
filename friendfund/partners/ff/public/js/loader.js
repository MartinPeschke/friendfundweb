parseSelectables = function(rootnode, className){
	var classes = className||"borderBottom";
	var a = function(evt){addClassToParent(evt.target, classes, "selected");},
		r = function(evt){remClassFromParent(evt.target, classes, "selected");};
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
	var td = dojo.io.iframe.send({
		url: url,
		form: formid,
		method: "post",
		content: {},
		timeoutSeconds: 15,
		preventCache: true,
		handleAs: "json",
		handle: xhrHandler(callback),
		//error: function (res,ioArgs) {console.log(res);}
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
var picCounter = 0, accepted = false, _parser_backups = [];

var createAppendPicture = function(imgContainer, imgs, preselected){
	var imgsrc = imgs.shift();
	if(imgsrc!==undefined){
		var img = dojo.create("IMG", {"class":'hidden'});
		imgContainer.appendChild(img);
		img.onload = dojo.hitch(null, pic_judger, img, imgContainer, imgs, preselected);
		img.src = imgsrc;
	}
};

var pic_judger = function(img, imgContainer, imgs, preselected, evt){
	console.log(arguments);
	console.log(img.width);
	console.log(img.offsetWidth);
	console.log(img.height);
	console.log(img.offsetHeight);
	console.log(this.width);
	console.log(this.height);
	
	if((img.width||img.offsetWidth)<100||(img.height||img.offsetHeight)<75){
		dojo.addClass(img, "forbidden");
	}else{
		picCounter+=1;
		dojo.byId("pictureCounter").innerHTML=picCounter;
		dojo.addClass(img, "allowed");
		if(!preselected&&!accepted||img.src===preselected){
			accepted = true;
			dojo.removeClass(img, "hidden");
			dojo.byId("pictureCounterPos").innerHTML=dojo.query(".imgCntSld img.allowed", "homeurlexpander").indexOf(img)+1;
			var ctrInput = dojo.byId("productPicture");
			if(!ctrInput){
				ctrInput = dojo.create("INPUT", {type:"hidden", value:img.src, id:"productPicture", name:'product_picture'});
				dojo.byId("homeurlexpander").appendChild(ctrInput);
			} else {
				ctrInput.value = img.src;
			}
		}
	}
	createAppendPicture(imgContainer, imgs, preselected);
};

var slide = function(step, evt){
	var imgs=dojo.query(".imgCntSld img.allowed", "homeurlexpander");
	for(var i=0, len=imgs.length;i<len;i++){
		var pos = ((i+step)<len&&(i+step)>=0)?(i+step):i;
		if(!dojo.hasClass(imgs[i], "hidden")&&pos!=i){
			dojo.addClass(imgs[i], "hidden");dojo.removeClass(imgs[pos], "hidden");
			dojo.byId("pictureCounterPos").innerHTML=pos+1;
			dojo.byId("productPicture").value=imgs[pos].src;
			break;
		}
	}
};


var renderPictures = function(imgs, preselected){
	var imgContainer = dojo.create("DIV" , { "class":"imgCntSld"}), tmp;
	var i, totalcounter = imgs.length;
	for(i=0;i<totalcounter; i++){
		imgContainer.appendChild(dojo.create("INPUT", {type:"hidden", value:imgs[i], name:'img_list'}));
	}
	createAppendPicture(imgContainer, imgs, preselected);
	return imgContainer;
};
var renderController = function(editnode){
	var left = dojo.create("SPAN", {"class":"smallLeft", "innerHTML":"<span></span>"});
	var right = dojo.create("SPAN", {"class":"smallRight", "innerHTML":"<span></span>"});
	left.onclick = dojo.hitch(null, slide, -1);
	right.onclick = dojo.hitch(null, slide, 1);
	var controller = dojo.create("DIV", {"class":"controller", 
			innerHTML:'<span class="counterDescr">Choose a thumbnail (<span id="pictureCounterPos">1</span> of <span id="pictureCounter">0</span>)</span>'});
	controller.appendChild(left);
	controller.appendChild(right);
	if(editnode){
		var parsercloser = dojo.create("A", {"class":"parsercloser", "innerHTML":"X"});
		parsercloser.onclick = dojo.hitch(null, resetParser,editnode);
		controller.appendChild(parsercloser);
	}
	return controller;
};

var resetParser = function(editnode){
	dojo.empty("homeurlexpander");
	dojo.forEach(_parser_backups, function(elem){dojo.byId("homeurlexpander").appendChild(elem)});
	picCounter = 0; accepted = false; _parser_backups = [];
	connectURLParser(editnode);
}

var loadSuccess = function(editnode, data){
	dojo.query(".loading", "homeurlexpander").orphan();
	if(data.success === false){
		resetParser("homeurlexpander");
	} else {
		var div = dojo.create("DIV", {"class":"loading"});
		div.appendChild(renderPictures(data.imgs));
		div.appendChild(dojo.create("a", {innerHTML : data.display_url, 'class':'address', 'href':data.url}));
		
		var name = dojo.create("DIV", {innerHTML : data.display_name, "class":'title active simpleeditable'});
		name.appendChild(dojo.create("INPUT", {type:"hidden", _type:"INPUT", value:data.name, _length:50, name:'product_name', "class":"ptitleSimpleEdit", id:"product_name_edit"}));
		div.appendChild(name);
		
		var desc = dojo.create("DIV", {innerHTML : data.display_description, "class":'desc simpleeditable active'});
		desc.appendChild(dojo.create("INPUT", {type:"hidden", _type:"TEXTAREA", _length:180, value:data.description, name:'product_description', id:"product_desc_edit"}));
		div.appendChild(desc);
		
		div.appendChild(dojo.create("INPUT", {type:"hidden", value:data.url, name:'tracking_link'}));
		dojo.place(div, "homeurlexpander", "only");
		parseSimpleEditables(div);
		div.appendChild(renderController(editnode));
	}
};
var connectURLParser = function(editnode){
	var dn = dojo.byId(editnode), ht1, ht2,
		parseInput = function(elem){
		if(!dojo.hasClass(elem, "default")){
				dojo.some(elem.value.split(" "), function(elt){
				if(urlmatch.test(elt)){
					var query = elt, url = dojo.attr(elem, "_url");
						dojo.disconnect(ht1);dojo.disconnect(ht2);
						var div = dojo.create("DIV", {"class":"loading"});
						div.appendChild(dojo.create("IMG", {src:"/static/imgs/ajax-loader.gif"}));
						_parser_backups = dojo.query("> *", "homeurlexpander").orphan();
						dojo.place(div, "homeurlexpander", "last");
						dojo.removeClass("homeurlexpander", "hidden");
						dojo.xhrPost({url:url, content:{query:query},
										handleAs: 'json',
										load:dojo.hitch(null, loadSuccess, editnode)});
						return true;
					}
				});
			};
		},
		parseInputFromEvt = function(evt){
			parseInput(evt.target);
		};
	ht1 = dojo.connect(dn, "onkeyup", parseInputFromEvt);
	ht2 = dojo.connect(dn, "onblur", parseInputFromEvt);
	parseInput(dn);
};