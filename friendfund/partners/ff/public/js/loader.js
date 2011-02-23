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