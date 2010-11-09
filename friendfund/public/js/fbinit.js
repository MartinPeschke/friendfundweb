facebook_tried_getting_permissions = false;
facebook_tried_loggin_in_already = false;
twitter_tried_loggin_in_already = false;
timeoutValue=500;
twInit = function(furl) {
	if(twitter_tried_loggin_in_already == false){
		twitter_tried_loggin_in_already = true;
		setTimeout("twitter_tried_loggin_in_already=false;",timeoutValue);
		var localhost = window.location.protocol + '//' + window.location.host;
		if(furl){
			page_reloader=function(){window.location.href=furl;}
			window.open(localhost+"/twitter/login?furl="+furl, '_blank', 'left=100,top=100,height=400,width=850,location=no,resizable=no,scrollbars=no');
		} else {
			window.open(localhost+"/twitter/login", '_blank', 'left=100,top=100,height=400,width=850,location=no,resizable=no,scrollbars=no');
		}
	}
}

fbInit = function(app_id, has_prev_tried_logging_in) {
	window.fbAsyncInit = function() {
		FB.init({appId  : app_id,status : true,cookie : true,xfbml  : false});
		FB.Event.subscribe('auth.sessionChange', fbSessionChange);
		if(!has_prev_tried_logging_in && FB.getSession()!=null){
			FB.api("/me", function(response) {loadElement("/fb/login", "accountcontainer", response);});
		}
	};
	var e = document.createElement('script');
	e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
	e.async = true;
	document.getElementById('fb-root').appendChild(e);
}

fbLogin = function() {
	if(FB.getSession() == null){
		if(facebook_tried_loggin_in_already == false){
			facebook_tried_loggin_in_already = true;
			setTimeout("facebook_tried_loggin_in_already=false;",timeoutValue);
			FB.login(function(){}, {perms:"user_birthday,friends_birthday,email"});
		}
	}else{
		fbSessionChange()
	}
}
fbLogout = function(){
	if(FB.getSession()){
		FB.logout(function(response){});
	}else{
		fbSessionChange();
	}
}

forward = function(furl){
	return function(){window.location.href = furl;}
}

checkForward = function(){
	var loc = dojo.byId("furl").value;
	if(loc != '')window.location.href = loc;
}

doFBFFLogin = function(callback){
	FB.api('/me', function(response) {
		loadElement('/fb/login', "accountcontainer", response, callback);
	});
}

fbSessionChange = function() {
	if (FB.getSession()) {
		doFBFFLogin(page_reloader);
	} else {
		loadElement("/logout", "accountcontainer");
	}
}

getfbEmail = function(api_key){
	var localhost = window.location.protocol + '//' + window.location.host;
	console.log('https://graph.facebook.com/oauth/authorize?client_id='+api_key
		+'&redirect_uri='+localhost+'/fb/get_email&display=popup'
		+'&scope=email');
	window.open('https://graph.facebook.com/oauth/authorize?client_id='+api_key
		+'&redirect_uri='+localhost+'/fb/get_email&display=popup'
		+'&scope=email', '_blank', 'left=100,top=100,height=300,width=500,location=no,resizable=no,scrollbars=no');
}
getfbStreamPublish = function(api_key){
	var localhost = window.location.protocol + '//' + window.location.host;
	console.log('https://graph.facebook.com/oauth/authorize?client_id='+api_key
		+'&redirect_uri='+localhost+'/fb/get_streampublish&display=popup'
		+'&scope=publish_stream');
	window.open('https://graph.facebook.com/oauth/authorize?client_id='+api_key
		+'&redirect_uri='+localhost+'/fb/get_streampublish&display=popup'
		+'&scope=publish_stream', '_blank', 'left=100,top=100,height=300,width=500,location=no,resizable=no,scrollbars=no');
}

getfbStreamPublishnEmail = function(api_key){
	if (facebook_tried_getting_permissions==false){
		facebook_tried_getting_permissions = true;
		setTimeout("facebook_tried_getting_permissions=false;",timeoutValue);
		var localhost = window.location.protocol + '//' + window.location.host;
		window.open('https://graph.facebook.com/oauth/authorize?client_id='+api_key
			+'&redirect_uri='+localhost+'/fb/get_streampublishnemail&display=popup'
			+'&scope=publish_stream,email', '_blank', 'left=100,top=100,height=300,width=500,location=no,resizable=no,scrollbars=no');
	}
}

getfbPermanent = function(api_key){
	var localhost = window.location.protocol + '//' + window.location.host;
	window.open('https://graph.facebook.com/oauth/authorize?client_id='+api_key
		+'&redirect_uri='+localhost+'/fb/get_offline&display=popup'
		+'&scope=offline_access', '_blank', 'left=100,top=100,height=300,width=500,location=no,resizable=no,scrollbars=no');
}