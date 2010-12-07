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

















