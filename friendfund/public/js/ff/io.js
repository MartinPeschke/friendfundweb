dojo.provide("ff.io");
dojo.require('dojo.io.iframe');
dojo.mixin(ff, {io:{
	xhrHandler : function(callback){
		return function(data,xhrobj,evt) {
			if (data.login !== undefined&&callback){callback(data.login);}
			if (data.popup !== undefined){ff.w.displayPopup(data.popup);}
			if (data.message !== undefined){ff.w.displayMessage(data.message);}
			if (callback && data.html !== undefined){callback(data.html);}
			if (callback && data.data !== undefined){callback(data.data);}
			if (data.redirect !== undefined){window.location.href = data.redirect;}
			if (data.reload === true){window.location.reload(true);}
			return data;
		};
	}
	,xhrErrorHandler : function(data,xhrobj,evt){
		if (window.console) {console.log(data);console.log(xhrobj);	console.log(evt);}
	}
	,xhrFormPost : function(url, form, callback) {
		dojo.xhrPost({
			url:url,
			form:form,
			handleAs: 'json',
			load:ff.io.xhrHandler(callback),
			error:ff.io.xhrErrorHandler
		});
	}
	,xhrPost : function(url, args, callback, method) {
		var _method = method || 'Post';
		dojo['xhr'+_method]({
			url:url,
			content:args,
			handleAs: 'json',
			load:ff.io.xhrHandler(callback),
			error:ff.io.xhrErrorHandler
		});
	}
	,ioIframeGetJson : function(url, formid, callback){
		dojo.io.iframe.send({
			url: url,
			form: formid,
			method: "Post",
			content: {},
			timeoutSeconds: 15,
			preventCache: true,
			handleAs: "json",
			load: ff.io.xhrHandler(callback),
			error: ff.io.xhrErrorHandler
		});
	}
}});