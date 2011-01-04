esc_handler_f = function(callback, evt){
	if(evt.keyCode == 27){dojo.hitch(this, callback(evt));}
};
accessability = function(callbackRet, callbackEsc, evt){
	if(evt.keyCode == 13){dojo.hitch(this, callbackRet(this, evt));}
	else if(evt.keyCode == 27){dojo.hitch(this, callbackEsc(this, evt));}
};

closePopup = function(evt){
	dojo.query("#generic_popup *").orphan();
	dojo.disconnect(esc_handler);
};

displayPopup = function(html){
	dojo.place(html, dojo.byId("generic_popup"), "only" );
	dojo.query(".panelclosing_x,.window_container", "generic_popup").connect("onclick", closePopup);
	esc_handler = dojo.connect(window, "onkeyup", dojo.hitch(null, esc_handler_f, closePopup));
};

loadPopup = function(evt){
	xhrPost(dojo.attr(this, "_href"), {});
};

parseDefaultsInputs = function(rootnode){
	dojo.query("input[_default_text]", rootnode).onfocus(
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
		});
};

closeBadges = function(evt) {
	dojo.query("#badge_popup").orphan();
	dojo.disconnect(esc_handler);
};


closeBlocks = function(){
	dojo.query("#blocking_msgs *").orphan();
};

displayMessage = function(msg){
	dojo.place(msg, 'message_container', 'last');
	dojo.query("#message_container").style('display', 'block');
};

clear_messages = function(){destroyPopup("message_container");};

destroyPopup = function(nodeid) {
	var node = dojo.byId(nodeid);
	if(node){
		dojo.empty(nodeid);
		dojo.style(nodeid, 'display', 'none');
	}
};

loadnext_fundchat_batch = function(elem, offset){
	var onLoaded = function(data){
		dojo.place(data.html, dojo.byId("fundchatmore"), "last");
		if(data.has_more){
			dojo.attr(elem, "_offset", data.offset);
		}else{
			dojo.query('#chat_get_more_link').orphan();
		}};
	xhrPost(dojo.attr(elem, '_href'), {offset:dojo.attr(elem, "_offset")}, onLoaded, 'Get');
};

submit_fundchat = function(node){
	var onLoaded = function(data){
		dojo.query("div.placeholder", dojo.byId("fundchat")).orphan();
		dojo.place(data.html, dojo.byId("fundchat"), "first");
		dojo.byId("addcommenttext").value="";
		var elem = dojo.byId("chat_get_more_link");
		if(elem){
			dojo.attr(elem, "_offset", parseInt(dojo.attr(elem, "_offset"), 10)+1);
		}
	};
	var _node = dojo.byId(node);
	var params = {};
	if(!_node.value){return;}
	params[_node.name] = _node.value;
	xhrPost(dojo.attr(_node, '_href'), params, onLoaded);
	return false;
};

onLoadPagelets = function(root_node){
	dojo.query('div.pagelet', root_node).forEach(
		function(elem){
			loadElement(dojo.attr(elem, 'pagelet_href'), elem, {}, null, 'Get');
		});
};


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

ioIframeGetJson = function(url, formid, callback){
	var td = dojo.io.iframe.send({
		url: url,
		form: formid,
		method: "post",
		content: {},
		timeoutSeconds: 15,
		preventCache: true,
		handleAs: "json",
		handle: callback,
		error: function (res,ioArgs) {console.log(res);}
	});
};


/*********************************TOOLS******************************************/



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

checkForward = function(){
	var loc = dojo.byId("furl").value;
	if(loc !== ""){window.location.href = loc;}
};

fbInit = function(app_id, has_prev_tried_logging_in) {
	window.fbAsyncInit = function() {
		var channelUrl = document.location.protocol + '//' + document.location.host+"/channel.htm";
		FB.init({appId  : app_id,status : true,cookie : true,xfbml  : false, channelUrl:channelUrl});
		FB.Event.subscribe('auth.sessionChange', fbSessionChange);
		if(!has_prev_tried_logging_in && FB.getSession()){
			FB.api("/me", function(response) {loadElement("/fb/login", "accountcontainer", response, page_reloader);});
		}
	};
	var e = document.createElement('script');
	e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
	e.async = true;
	document.getElementById('fb-root').appendChild(e);
};

fbLogin = function() {
	if(!FB.getSession()){
		if(facebook_tried_loggin_in_already === false){
			facebook_tried_loggin_in_already = true;
			setTimeout(function(){facebook_tried_loggin_in_already=false;},timeoutValue);
			FB.login(function(){}, {perms:"user_birthday,friends_birthday,email"});
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

forward = function(furl){
	return function(){window.location.href = furl;};
};

doFBFFLogin = function(callback){
	FB.api('/me', function(response) {
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

getfbEmail = function(api_key){
	var localhost = window.location.protocol + '//' + window.location.host;
	window.open('https://graph.facebook.com/oauth/authorize?client_id='+api_key+'&redirect_uri='+localhost+'/fb/get_email&display=popup&scope=email', '_blank', 'left=100,top=100,height=300,width=500,location=no,resizable=no,scrollbars=no');
};

getfbStreamPublish = function(api_key){
	var localhost = window.location.protocol + '//' + window.location.host;
	window.open('https://graph.facebook.com/oauth/authorize?client_id='+api_key+'&redirect_uri='+localhost+'/fb/get_streampublish&display=popup&scope=publish_stream', '_blank', 'left=100,top=100,height=300,width=500,location=no,resizable=no,scrollbars=no');
};

getfbCreateEvent = function(api_key){
	var localhost = window.location.protocol + '//' + window.location.host;
	window.open('https://graph.facebook.com/oauth/authorize?client_id='+api_key+'&redirect_uri='+localhost+'/fb/get_create_event&display=popup&scope=create_event', '_blank', 'left=100,top=100,height=300,width=500,location=no,resizable=no,scrollbars=no');
};

getfbStreamPublishnEmail = function(api_key){
	if (facebook_tried_getting_permissions===false){
		facebook_tried_getting_permissions = true;
		setTimeout(function(){facebook_tried_getting_permissions=false;},timeoutValue);
		var localhost = window.location.protocol + '//' + window.location.host;
		window.open('https://graph.facebook.com/oauth/authorize?client_id='+api_key+'&redirect_uri='+localhost+'/fb/get_streampublishnemail&display=popup&scope=publish_stream,email', '_blank', 'left=100,top=100,height=300,width=500,location=no,resizable=no,scrollbars=no');
	}
};

getfbPermanent = function(api_key){
	var localhost = window.location.protocol + '//' + window.location.host;
	window.open('https://graph.facebook.com/oauth/authorize?client_id='+api_key+'&redirect_uri='+localhost+'/fb/get_offline&display=popup&scope=offline_access', '_blank', 'left=100,top=100,height=300,width=500,location=no,resizable=no,scrollbars=no');
};

fbShare = function(url, title){
	window.open('https://www.facebook.com/sharer.php?u='+encodeURIComponent(url)+'&t='+encodeURIComponent(title), '_blank', 'left=100,top=100,height=350,width=600,location=no,resizable=no,scrollbars=no');
};


fbStreamPub = function(app_id, message, name, link, picture, redirect) {
	window.open('http://www.facebook.com/dialog/feed?display=popup&app_id='+app_id+'&name='+name+'&message='+message+'&link='+link+'&redirect_uri='+redirect, '_blank', 'left=100,top=100,height=300,width=600,location=no,resizable=no,scrollbars=no');
};






















