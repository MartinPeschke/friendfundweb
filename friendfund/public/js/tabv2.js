if (!FriendFund) {var FriendFund = {};}

FriendFund.Util = {
	render: function (template, params) {
		return template.replace(/\${([^{}]*)}/g, function (a, b) {
			var r = params[b];
			return typeof r === 'string' || typeof r === 'number' ? r : a;
		})
	},
	includeCss: function (css) {
		var styleElement = document.createElement('style');
		styleElement.setAttribute('type', 'text/css');
		styleElement.setAttribute('media', 'screen');
		if (styleElement.styleSheet) {
			styleElement.styleSheet.cssText = css;
		} else {
			styleElement.appendChild(document.createTextNode(css));
		}
		document.getElementsByTagName('head')[0].appendChild(styleElement);
	},
	get_tags: function(){
		var params = {}, name, prop;
		var metas = document.getElementsByTagName("META");
		for (var i=0;i<metas.length; i++){
			prop = metas[i].getAttribute("property");
			name = metas[i].name;
			if(name&&!prop){params["ff.names."+name] = metas[i].content;}else if(!name&&prop){params["ff.props."+prop] = metas[i].content;}
		}
		params.referer = window.location.href;
		return params;
	}
};

FriendFund.Logger = {
	_log: function (message) {
		if (typeof console !== "undefined" && typeof console.log !== "undefined") {
			try {
				console.log(message);
			} catch (e) {}
		}
	},
	warning: function (message) {
		this._log("FriendFund WARNING: " + message);
	},
	error: function (message) {
		this._log("FriendFund ERROR: " + message);
		alert("FriendFund ERROR: " + message);
	}
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
}


FriendFund.Popup = {
	id: 'FriendFund_Popup',
	close_text:{'de':"Schliessen", 'en':"Close This", 'es':"Cerrar"},
	css_template: "\
	#FriendFund_Popup {\
	  z-index:10000008;\
	  display: block;\
	  text-align: left;\
	  margin: 0 auto 0 auto;\
	  position: absolute; \
	  padding:10px;\
	  background:url(${protocol}${host}/static/partner/opacity.png) repeat 0 0 transparent;\
	}#FriendFund_Popup-content{background-color:white}\
	#FriendFund_overlay {\
	  position: absolute;\
	  z-index:10000007;\
	  width: 100%;\
	  height: ${docHeight}px;\
	  left: 0;\
	  top: 0;\
	  background-color: #000;\
	  opacity: 0.7;\
	  filter: alpha(opacity=70);\
	}\
	#FriendFund_overlay p {\
	  padding: 5px;\
	  color: #ddd;\
	  font: bold 14px arial, sans-serif;\
	  margin: 0;\
	  letter-spacing: -1px;\
	}\
	a#FriendFund_Popup_close {color:black;cursor:pointer;font-size:16px;font-weight:bold;line-height:15px;text-decoration:None;position:absolute;right:-10px;top:-10px;\
	background:url(${protocol}${host}/static/partner/close_popup_cross.png) no-repeat 0 0 transparent;display:block;width:33px;height:33px;",
	preload: function (id_or_html) {
		if (!this.preloaded) {
			var element = document.getElementById(id_or_html);
			var html = (element == null) ? id_or_html : element.innerHTML;
			this.setContent(html);
			//this.preloaded = true;
		}
	},
	show: function (id_or_html, options) {
		this.options = options;
		this.preload(id_or_html);
		this.Overlay.show();
		this.setPosition();
		FriendFund.Element.addClassName(this.htmlElement(), 'dialog-open');
		this.element().style.display = 'block';
		this.element().focus();
	},
	close: function () {
		this.element().style.display = 'none';
		FriendFund.Element.removeClassName(this.htmlElement(), 'dialog-open');
		this.Overlay.hide();
		FriendFund.onClose();
	},
	element: function () {
		if (!document.getElementById(this.id)) {
			var popup = document.createElement('div');
			popup.innerHTML = '<div id="' + this.id + '" style="display:none;">\
					<a href="#close" onclick="FriendFund.Popup.close(); return false;" id="' + this.id + '_close" title="'+this.close_text[this.options.lang]+'"><span style="display: none;">Close Popup</span></a>\
					<div id="' + this.id + '-content"></div></div>';
			document.body.insertBefore(popup.firstChild, document.body.firstChild);
		}
		return document.getElementById(this.id);
	},
	setContent: function (html) {
		this.element();document.getElementById(this.id + "-content").innerHTML = html;
	},
	setPosition: function () {
		var dialogDimensions = FriendFund.Element.getDimensions(this.element());
		var pageDimensions = FriendFund.Page.getDimensions();
		var els = this.element().style;
		els.width = 'auto';
		els.height = 'auto';
		els.left = ((pageDimensions.width - dialogDimensions.width) / 2) + "px";
		var computedHeight = ((pageDimensions.height - dialogDimensions.height) / 2);
		els.top = Math.max(computedHeight, 0) + "px";
	},
	htmlElement: function () {
		return document.getElementsByTagName('html')[0];
	}
};

FriendFund.onClose = function () {};

FriendFund.Popup.Overlay = {
	show: function () {this.get_element().style.display = 'Block';},
	hide: function () {this.get_element().style.display = 'None';},
	olay_id: 'FriendFund_overlay',
	get_element: function () {
		if(!document.getElementById(this.olay_id)){olay = document.createElement('div');
			olay.innerHTML = '<div id="' + this.olay_id + '" class="FriendFund_popup_elem" onclick="FriendFund.Popup.close(); return false;" style="display:none;"></div>';
			document.body.insertBefore(olay.firstChild, document.body.firstChild);
		}
		return document.getElementById(this.olay_id);
	}
};

FriendFund.Popin = {
	context : {width:'930px',height:'580px'},
	content_template: '<iframe id="friendfund_dialog_iframe" name="friendfund_dialog_iframe" src="" frameborder="0" scrolling="no" allowtransparency="true" width="${width}" height="${height}" style="height: ${height}; width: ${width};"></iframe>',
	setup: function (options) {
		this.setupOptions(options);
	},
	setupOptions: function (options) {
		if (typeof(options) === 'undefined') {
			return;
		}
		if (options.key == null && options.host == null) {
			FriendFund.Logger.error("'host' must be set.");
			FriendFund.Logger.error("'key' must be set.");
		} else if (options.key == null) {
			FriendFund.Logger.warning("'key' must be set for the widget to work.");
		}
		this.options = options;
	},
	show: function (options) {
		this.setupOptions(options);
		FriendFund.Popup.show(FriendFund.Util.render(this.content_template, this.context), options);
		try {
			var iForm = document.getElementById("friendfund_dialog_iform");
			if(iForm){document.body.removeChild(iForm);}
			var post_to_url = function(url, params) {
				var form = document.createElement("form");
				form.setAttribute("id", "friendfund_dialog_iform");
				form.setAttribute("method", "POST");
				form.setAttribute("action", url);
				form.setAttribute("target", "friendfund_dialog_iframe");
				for(var key in params) {
					var hf = document.createElement("input");
					hf.setAttribute("type", "hidden");
					hf.setAttribute("name", key);
					hf.setAttribute("value", params[key]);
					form.appendChild(hf);
				}
				document.body.appendChild(form);
				form.submit();
			};
			var params = FriendFund.Util.get_tags();
			params.key = options.key;
			params.host = options.host;
			params.real_host = window.location.host;
			post_to_url(this.url(options), params);
		} catch (e) {
			FriendFund.Logger.warning("Error sending the 'open' notification");
			FriendFund.Logger.warning(e);
		}
	},
	url: function (options) {return options.protocol+options.host+'/partner/bounce';}
};

FriendFund.Button = {
	button_id: "friendfund_fund_button",
	css_template: "#${button_id} {margin: 10px 0;width: auto;background:${button_background};padding: 7px 0 5px;} \
					#${button_id} a {background:None !important;width:auto;height:auto;text-indent: 0;}\
					#${button_id}:hover {cursor:pointer}\
					#${button_id} *, #${button_id} *:hover {text-decoration:none !important; font-weight:normal !important}\
					#${button_id} .friendfundButton{pointer:cursor;display:block;text-align:center;padding:0;}\
					#${button_id} .friendfundButton img{margin:0px auto;}\
					#${button_id} .friendfundButton span{text-transform: none;padding:0;font-size:10px;margin:0px auto;color:#a6a6a6;text-shadow: 0px 1px 0px white;display:block}",
	fixed_css_template: "#${button_id} {position:absolute;${alignment}:-150px;top:${top};width:196px;height:122px;} \
					#${button_id}:hover {${alignment}:0px;cursor:pointer} \
					#${button_id} .friendfundButton{pointer:cursor;color:white;width:196px;height:172px;\
					background:url(${protocol}${host}/static/partner/buttons/friendfund_it_button_complete.png) no-repeat 0 0 transparent;display:block}",
	
	show: function (options) {
		FriendFund.Popin.setup(options);
		this.button_id = options.button_id || this.button_id;
		
		var button = document.createElement('A');
		button.id = "friendfund_button";
		button.className="friendfundButton";
		button.onclick=function(){FriendFund.Popin.show(options); return false;};
		if(!document.getElementById(this.button_id)){
			var bc = document.createElement('div');bc.id=this.button_id;
			document.body.insertBefore(bc, document.body.firstChild);
			var pageDimensions = FriendFund.Page.getDimensions();
			var computedTop = ((pageDimensions.height - 143) / 2);
			options.css_template = FriendFund.Util.render(this.fixed_css_template, {top:Math.max(computedTop, 55) + "px"});
			button.innerHTML = "&nbsp;";
		}else{
			options.css_template = this.css_template;
			var img = document.createElement("IMG");
			img.src=FriendFund.Util.render("${protocol}${host}/static/partner/buttons/friendfund_it_button_${button_size}_${button_color}.png", options);
			button.appendChild(img);
			if(options.with_strap_line){
				var buttonSubscript = document.createElement("SPAN");
				buttonSubscript.innerHTML = options.button_text[options.lang];
				button.appendChild(buttonSubscript);
			};
		}
		options.docHeight = FriendFund.Page.getDocHeight();
		document.getElementById(this.button_id).appendChild(button);
		FriendFund.Util.includeCss(FriendFund.Util.render(options.css_template || this.css_template, options));
		FriendFund.Util.includeCss(FriendFund.Util.render(FriendFund.Popup.css_template, options));
	 }
}
if (typeof(friendfundOptions) !== 'undefined' && friendfundOptions.showButton == true) {
	defaultOptions = {alignment:"left", lang:"en"
					, button_text:{es:"Comparte los gastos con amigos!", en:"Share the costs with friends!", de:"Teile die Kosten mit Freunden!"}
					, button_background:"#f4f4f4", button_size:"large", button_color:"blue",with_strap_line:true};
	for(var option in defaultOptions){friendfundOptions[option] = (friendfundOptions[option]===undefined)?defaultOptions[option]:friendfundOptions[option];}
	FriendFund.Button.show(friendfundOptions);
}












