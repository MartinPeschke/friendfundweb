onSubmitCleaner = function(rootnode){
	dojo.query("input[_default_text],textarea[_default_text]", rootnode).forEach(
		function(element){
			if(dojo.attr(element, "_default_text") == element.value){element.value=""}
		});
	return true;
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
esc_handler_f = function(callback, evt){if(evt.keyCode == 27){dojo.hitch(this, callback(evt));}};
closePopup = function(evt){dojo.query("#generic_popup *").orphan();dojo.forEach(popup_esc_handler, dojo.disconnect);popup_esc_handler=[]};
displayPopup = function(html){
	dojo.place(html, dojo.byId("generic_popup"), "only" );
	dojo.query(".panelclosing_x,.popupBackground", "generic_popup").forEach(function(elt){popup_esc_handler.push(dojo.connect(elt, "onclick", closePopup));});
	popup_esc_handler.push(dojo.connect(window, "onkeyup", dojo.hitch(null, esc_handler_f, closePopup)));
};
loadPopup = function(evt){closePopup(evt);xhrPost(dojo.attr(this, "_href"), {});};
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
			if(elt.value!=dojo.attr(elt, "_default_text"))dojo.removeClass(elt, "default");
		});
};

onLoadPagelets = function(root_node){
	dojo.query('.pagelet', root_node).forEach(
		function(elem){
			loadElement(dojo.attr(elem, 'pagelet_href'), elem, {}, null, 'Get');
		});
};


findParent = function(rootnode, className){
	if(!dojo.hasClass(rootnode, className)&&rootnode.parentNode){findParent(rootnode.parentNode, className)}
	else return null;
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
				if ('clearblocks' in data){closeBlocks(data.clearblocks);}
				if ('clearmessage' in data){clear_messages();}
				if ('message' in data){displayMessage(data.message);}
				if (callback && 'html' in data){callback(data.html);}
				if (callback && 'data' in data){callback(data.data);}
				if ('redirect' in data){window.location.href = data.redirect;}
				if ('popup' in data){displayPopup(data.popup);}
				if ('reload' in data){page_reloader();}
	};
};

xhrErrorHandler = function(data,xhrobj,evt){
	console.log(data);
	console.log(xhrobj);
	console.log(evt);
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
		loadElement("/logout?furl="+window.location.pathname, "accountcontainer");
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

var FBSCOPE="user_birthday,friends_birthday,email,publish_stream";
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
var urlmatch = /^(www\.|https?:\/\/)([-a-zA-Z0-9_]{2,256}\.)+[a-z]{2,4}(\/[-a-zA-Z0-9%_\+.,~#&=!]*)*(\?[-a-zA-Z0-9%_\+,.~#&=!\/]+)*$/i, ht1, ht2;
var totalcounter = 0, picCounter = 0;

var pic_judger = function(preselected, evt){
	if((evt.target.width||evt.target.offsetWidth)<50||(evt.target.height||evt.target.offsetHeight)<50){
		dojo.addClass(evt.target, "forbidden");
	}else{
		dojo.byId("pictureCounter").innerHTML=++picCounter;
		dojo.addClass(evt.target, "allowed");
	}
	if(!--totalcounter){
		var imgs=dojo.query(".imgCntSld img.allowed", "homeurlexpander");
		var pos = 0;
		if(imgs&&preselected){
			for(var i=0;i<imgs.length;i++){
				if(imgs[i].src==preselected){pos = i;break;}
			}
		}
		if(imgs){
			dojo.removeClass(imgs[pos], "hidden");dojo.addClass(imgs[pos], "visible");
			dojo.byId("pictureCounterPos").innerHTML=pos+1;
		}
	};
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
	var imgContainer = dojo.create ("DIV" , { class:"imgCntSld"})
	totalcounter = imgs.length; 
	for(var i=0;i<totalcounter; i++){
		var img = dojo.create("IMG", {src:imgs[i], class:'hidden'});
		dojo.connect(img, "onload", dojo.hitch(null, pic_judger, preselected));
		imgContainer.appendChild(img);
	};
	return imgContainer;
};
var renderController = function(){
	var left = dojo.create("SPAN", {"class":"smallLeft", "innerHTML":"<span></span>"});
	var right = dojo.create("SPAN", {"class":"smallRight", "innerHTML":"<span></span>"});
	left.onclick = dojo.hitch(null, slide, -1);
	right.onclick = dojo.hitch(null, slide, 1);
	var controller = dojo.create("DIV", {"class":"controller", 
			innerHTML:'<span class="counterDescr">Choose a thumbnail (<span id="pictureCounterPos">1</span> of <span id="pictureCounter">0</span>)</span>'});
	controller.appendChild(left);
	controller.appendChild(right);
	return controller;
};

var loadSuccess = function(data){
	dojo.query(".loading", "homeurlexpander").orphan();
	if(data.success == false){
		dojo.addClass("homeurlexpander", "hidden");
		dojo.byId("productLink").value="";
		dojo.byId("productPicture").value="";
		connect_home();
	} else {
		var div = dojo.create("DIV", {class:"home_expander loading"});
		div.appendChild(renderPictures(data.imgs));
		div.appendChild(dojo.create("a", {innerHTML : data.display_url, 'class':'address', 'href':data.url}));
		div.appendChild(dojo.create("DIV", {innerHTML : data.name, class:'title'}));
		div.appendChild(dojo.create("DIV", {innerHTML : data.description, class:'desc'}));
		dojo.place(div, "homeurlexpander", "last");
		div.appendChild(renderController());
	}
};
var parseURL = function(query, url){
	dojo.disconnect(ht1);dojo.disconnect(ht2);
	var div = dojo.create("DIV", {class:"home_expander loading"});
	div.appendChild(dojo.create("IMG", {src:"/static/imgs/ajax-loader.gif"}));
	dojo.place(div, "homeurlexpander", "last");dojo.removeClass("homeurlexpander", "hidden");
	dojo.xhrPost({url:url, content:{query:query},
					handleAs: 'json',
					load:loadSuccess});
	return true;
};
var parseInput = function(type, evt){
	if(dojo.hasClass("homeurlexpander", "hidden")&&(type=="onblur"||evt.ctrlKey&&evt.keyCode==86||evt.keyCode==32)){
		evt.target.value.split(" ").some(function(elt){
			if(urlmatch.test(elt)){
				dojo.byId("productLink").value=elt;
				parseURL(elt, dojo.attr(evt.target, "_url"));
			}
		})
}};
var connect_home = function(){
	var dn = dojo.byId("home_title");
	ht1 = dojo.connect(dn, "onkeyup", dojo.hitch(null, parseInput, "onkeyup"));
	ht2 = dojo.connect(dn, "onblur", dojo.hitch(null, parseInput,"onblur"));
};