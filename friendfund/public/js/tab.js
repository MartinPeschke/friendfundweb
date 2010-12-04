if (!FriendFund) {var FriendFund = {};}

if (!FriendFund.JSON) {FriendFund.JSON = {};}
(function () {
	function f(n) {
		return n < 10 ? '0' + n : n;
	}
	if (typeof Date.prototype.toJSON !== 'function') {
		Date.prototype.toJSON = function (key) {
			return isFinite(this.valueOf()) ? this.getUTCFullYear() + '-' + f(this.getUTCMonth() + 1) + '-' + f(this.getUTCDate()) + 'T' + f(this.getUTCHours()) + ':' + f(this.getUTCMinutes()) + ':' + f(this.getUTCSeconds()) + 'Z' : null;
		};
		String.prototype.toJSON = Number.prototype.toJSON = Boolean.prototype.toJSON = function (key) {
			return this.valueOf();
		};
	}
	var cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
		escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
		gap, indent, meta = {
			'\b': '\\b',
			'\t': '\\t',
			'\n': '\\n',
			'\f': '\\f',
			'\r': '\\r',
			'"': '\\"',
			'\\': '\\\\'
		},
		rep;

	function quote(string) {
		escapable.lastIndex = 0;
		return escapable.test(string) ? '"' + string.replace(escapable, function (a) {
			var c = meta[a];
			return typeof c === 'string' ? c : '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
		}) + '"' : '"' + string + '"';
	}

	function str(key, holder) {
		var i, k, v, length, mind = gap,
			partial, value = holder[key];
		if (value && typeof value === 'object' && typeof value.toJSON === 'function') {
			value = value.toJSON(key);
		}
		if (typeof rep === 'function') {
			value = rep.call(holder, key, value);
		}
		switch (typeof value) {
		case 'string':
			return quote(value);
		case 'number':
			return isFinite(value) ? String(value) : 'null';
		case 'boolean':
		case 'null':
			return String(value);
		case 'object':
			if (!value) {
				return 'null';
			}
			gap += indent;
			partial = [];
			if (Object.prototype.toString.apply(value) === '[object Array]') {
				length = value.length;
				for (i = 0; i < length; i += 1) {
					partial[i] = str(i, value) || 'null';
				}
				v = partial.length === 0 ? '[]' : gap ? '[\n' + gap + partial.join(',\n' + gap) + '\n' + mind + ']' : '[' + partial.join(',') + ']';
				gap = mind;
				return v;
			}
			if (rep && typeof rep === 'object') {
				length = rep.length;
				for (i = 0; i < length; i += 1) {
					k = rep[i];
					if (typeof k === 'string') {
						v = str(k, value);
						if (v) {
							partial.push(quote(k) + (gap ? ': ' : ':') + v);
						}
					}
				}
			} else {
				for (k in value) {
					if (Object.hasOwnProperty.call(value, k)) {
						v = str(k, value);
						if (v) {
							partial.push(quote(k) + (gap ? ': ' : ':') + v);
						}
					}
				}
			}
			v = partial.length === 0 ? '{}' : gap ? '{\n' + gap + partial.join(',\n' + gap) + '\n' + mind + '}' : '{' + partial.join(',') + '}';
			gap = mind;
			return v;
		}
	}
	if (typeof FriendFund.JSON.stringify !== 'function') {
		FriendFund.JSON.stringify = function (value, replacer, space) {
			var i;
			gap = '';
			indent = '';
			if (typeof space === 'number') {
				for (i = 0; i < space; i += 1) {
					indent += ' ';
				}
			} else if (typeof space === 'string') {
				indent = space;
			}
			rep = replacer;
			if (replacer && typeof replacer !== 'function' && (typeof replacer !== 'object' || typeof replacer.length !== 'number')) {
				throw new Error('JSON.stringify');
			}
			return str('', {
				'': value
			});
		};
	}
	if (typeof FriendFund.JSON.parse !== 'function') {
		FriendFund.JSON.parse = function (text, reviver) {
			var j;

			function walk(holder, key) {
				var k, v, value = holder[key];
				if (value && typeof value === 'object') {
					for (k in value) {
						if (Object.hasOwnProperty.call(value, k)) {
							v = walk(value, k);
							if (v !== undefined) {
								value[k] = v;
							} else {
								delete value[k];
							}
						}
					}
				}
				return reviver.call(holder, key, value);
			}
			text = String(text);
			cx.lastIndex = 0;
			if (cx.test(text)) {
				text = text.replace(cx, function (a) {
					return '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
				});
			}
			if (/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g, '@').replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, ']').replace(/(?:^|:|,)(?:\s*\[)+/g, ''))) {
				j = eval('(' + text + ')');
				return typeof reviver === 'function' ? walk({
					'': j
				}, '') : j;
			}
			throw new SyntaxError('JSON.parse');
		};
	}
}());

FriendFund.Util = {
    sslFrameHost: "https://dev.friendfund.de",
    frameHost: "http://dev.friendfund.de",
    getFrameHost: function () {
        return ("https:" == document.location.protocol) ? this.sslFrameHost : this.frameHost;
    },
    render: function (template, params) {
        return template.replace(/\${([^{}]*)}/g, function (a, b) {
            var r = params[b];
            return typeof r === 'string' || typeof r === 'number' ? r : a;
        })
    },
    toQueryString: function (params) {
        var pairs = [];
        for (key in params) {
            if (params[key] != null && params[key] != '') {
                pairs.push([key, params[key]].join('='));
            }
        }
        return pairs.join('&');
    },
    isIE: function (test) {
        if (/MSIE (\d+\.\d+);/.test(navigator.userAgent)) {
            if (typeof test === "function") {
                return test(new Number(RegExp.$1));
            } else {
                return true;
            }
        } else {
            return false;
        }
    },
    isQuirksMode: function () {
        return document.compatMode && document.compatMode == "BackCompat";
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
        return {
            width: width,
            height: height
        };
    }
}


FriendFund.Popup = {
	preload: function (id_or_html) {
		if (!this.preloaded) {
			var element = document.getElementById(id_or_html);
			var html = (element == null) ? id_or_html : element.innerHTML;
			this.setContent(html);
			this.preloaded = true;
		}
	},
	show: function (id_or_html) {
		if (!this.preloaded) {
			this.preload(id_or_html);
		}
		this.Overlay.show();
		this.setPosition();
		FriendFund.Element.addClassName(this.htmlElement(), 'dialog-open');
		this.element().style.display = 'block';
		this.element().focus();
	},
	close: function () {
		var change = FriendFund.needsConfirm;
		if (change) {
			var answer = confirm(change);
			if (!answer) {
				return
			}
		}
		this.element().style.display = 'none';
		FriendFund.Element.removeClassName(this.htmlElement(), 'dialog-open');
		this.Overlay.hide();
		FriendFund.onClose();
	},
	id: 'FriendFund_Popup',
	css_template: "\
	#FriendFund_Popup {\
	  z-index:10000008;\
	  display: block;\
	  text-align: left;\
	  margin: -2em auto 0 auto;\
	  position: fixed; \
	}\
	\
	#FriendFund_overlay {\
	  position: fixed;\
	  z-index:10000007;\
	  width: 100%;\
	  height: 100%;\
	  left: 0;\
	  top: 0;\
	  background-color: #000;\
	  opacity: 0.7;\
	}\
	\
	#FriendFund_overlay p {\
	  padding: 5px;\
	  color: #ddd;\
	  font: bold 14px arial, sans-serif;\
	  margin: 0;\
	  letter-spacing: -1px;\
	}\
	\
	#FriendFund_Popup #FriendFund_Popup_close {\
	  position: absolute;\
	  height: 48px;\
	  width: 48px;\
	  top: -11px;\
	  right: -12px;\
	  color: #06c;\
	  cursor: pointer;\
	  background-position: 0 0;\
	  background-repeat: no-repeat;\
	  background-color: transparent;\
	}\
	\
	html.dialog-open object,\
	html.dialog-open embed {\
	  visibility: hidden;\
	}\
	a#FriendFund_Popup_close { background-image: url(#{background_image_url}); }" + (FriendFund.Util.isIE() ? "\
    #FriendFund_overlay {\
      filter: alpha(opacity=70);\
    }" : "") + ((FriendFund.Util.isIE() && (FriendFund.Util.isIE(function (v) {
        return v < 7
    }) || (FriendFund.Util.isIE(function (v) {
        return v >= 7
    }) && FriendFund.Util.isQuirksMode()))) ? "\
    #FriendFund_overlay,\
    #FriendFund_Popup {\
      position: absolute;\
    }\
    \
    .dialog-open,\
    .dialog-open body {\
      overflow: hidden;\
    }\
    \
    .dialog-open body {\
      height: 100%;\
    }\
    #FriendFund_overlay {\
      width: 100%;\
    }\
    \
    #FriendFund_Popup #FriendFund_Popup_close {\
      background: none;\
      filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='https://uservoice.com/images/icons/close.png');\
    }\
    .dialog-open select {\
      visibility: hidden;\
    }\
    .dialog-open #FriendFund_Popup select {\
      visibility: visible;\
    }" : ""),
	element: function () {
		if (!document.getElementById(this.id)) {
			var popup = document.createElement('div');
			popup.innerHTML = '<div id="' + this.id + '" style="display:none;">\
						<a href="#close" onclick="FriendFund.Dialog.close(); return false;" id="' + this.id + '_close" title="Close Dialog">\
						<span style="display: none;">Close Dialog</span></a>' + '<div id="' + this.id + '-content"></div></div>';
			document.body.insertBefore(popup.firstChild, document.body.firstChild);
		}
		return document.getElementById(this.id);
	},
	setContent: function (html) {
		this.element()
		if (typeof(Prototype) != 'undefined') {
			document.getElementById(this.id + "-content").innerHTML = html.stripScripts();
			setTimeout(function () {
				html.evalScripts()
			}, 100);
		} else {
			document.getElementById(this.id + "-content").innerHTML = html;
		}
	},
	setPosition: function () {
		var dialogDimensions = FriendFund.Element.getDimensions(this.element());
		var pageDimensions = FriendFund.Page.getDimensions();
		var els = this.element().style;
		els.width = 'auto';
		els.height = 'auto';
		els.left = ((pageDimensions.width - dialogDimensions.width) / 2) + "px";
		var computedHeight = ((pageDimensions.height - dialogDimensions.height) / 2);
		els.top = Math.max(computedHeight, 55) + "px";
	},
	htmlElement: function () {
		return document.getElementsByTagName('html')[0];
	}
};

FriendFund.Util.includeCss(FriendFund.Util.render(FriendFund.Popup.css_template, {
    background_image_url: FriendFund.Util.getFrameHost() + '/images/icons/close.png'
}));
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
    content_template: '<iframe id="friendfund_dialog_iframe" src="" frameborder="0" scrolling="no" allowtransparency="true" width="${width}" height="${height}" style="height: ${height}; width: ${width};"></iframe>',
    opened_url_template: '${url}?${query}#opened',
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
            FriendFund.Logger.warning("'key' must be set for the widget to work with SSL.");
        }
        if (!options.params) {
            options.params = {};
        }
        this.options = options;
    },
    show: function (options) {
        this.setupOptions(options);
        FriendFund.Popup.show(FriendFund.Util.render(this.content_template, this.getContext(options)));
        try {
            var iframeElement = document.getElementById("friendfund_dialog_iframe").contentWindow;
            iframeElement.location = FriendFund.Util.render(this.opened_url_template, this.getContext(options));
        } catch (e) {
            FriendFund.Logger.warning("Error sending the 'open' notification");
            FriendFund.Logger.warning(e);
        }
    },
    getContext: function (options) {
        var context = {dialog: 'popin',width: '930px',height: '693px',lang: 'en'};
        for (attr in this.options) {context[attr] = this.options[attr];};
        context.url = this.url(options);
        context.params.lang = this.options.lang;
        context.params.referer = this.getReferer();
        context.query = FriendFund.Util.toQueryString(context.params);
        return context;
    },
    getReferer: function () {
        var referer = window.location.href;
        if (referer.indexOf('?') != -1) {
            referer = referer.substring(0, referer.indexOf('?'));
        }
        return referer;
    },
    url: function (options) {return options.protocol+options.host+'/product/bounce';}
};

FriendFund.Button = {
	button_id: "friendfund_fund_button",
	button_text: "Friendfund this",
	css_template: "#${button_id} {margin: 10px;width: auto} #${button_id}\
					.friendfundButton{pointer:cursor;margin:10px auto;color:white;width:122px;height:196px;\
					background:url(${protocol}${host}/static/imgs/button_logo.png) no-repeat 0 0 transparent;display:block}",
	fixed_css_template: "#${button_id} {position:fixed;${alignment}:-150px;top:${top};width:196px;height:122px;} \
					#${button_id}:hover {${alignment}:0px;} \
					#${button_id} .friendfundButton{pointer:cursor;color:white;width:196px;height:122px;\
					background:url(${protocol}${host}/static/imgs/badges/friendfund_it_button_complete.png) no-repeat 0 0 transparent;display:block}",
	
	show: function (options) {
		FriendFund.Popin.setup(options);
		this.button_id = options.button_id || this.button_id;
		if(!document.getElementById(this.button_id)){
			var bc = document.createElement('div');bc.id=this.button_id;
			document.body.insertBefore(bc, document.body.firstChild);
			
			var pageDimensions = FriendFund.Page.getDimensions();
			var computedTop = ((pageDimensions.height - 143) / 2);
			options.css_template = FriendFund.Util.render(this.fixed_css_template, {top:Math.max(computedTop, 55) + "px"});
		}else{
			options.css_template = this.css_template;
		}
		var button = document.createElement('A');
		button.id = "friendfund_button";
		button.className="friendfundButton";
		button.onclick=function(){FriendFund.Popin.show(options); return false;};
		button.innerHTML = "&nbsp;";
		document.getElementById(this.button_id).appendChild(button);
		FriendFund.Util.includeCss(FriendFund.Util.render(options.css_template || this.css_template, options));
	 }
}
if (typeof(friendfundOptions) !== 'undefined' && friendfundOptions.showButton == true) {
	FriendFund.Button.show(friendfundOptions);
}


