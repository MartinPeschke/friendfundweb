if (!FriendFund) {var FriendFund = {};}
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

FriendFund.Button = {
	button_id: "friendfund_fund_button",
	button_text: "Friendfund this",
	css_template: "#${button_id} {margin: 10px;width: auto} #${button_id} .friendfundButton{pointer:cursor;background:blue;margin:10px auto;color:white;padding:5px;width:100%;display:block}",
	show: function (options) {
		this.button_id = options.button_id || this.button_id;
		var button = document.createElement('A');
		button.className="friendfundButton";
		button.onclick=function(){console.log(window.location.href)};
		button.innerText = this.button_text;
		document.getElementById(this.button_id).appendChild(button);
		FriendFund.Util.includeCss(FriendFund.Util.render(options.css_template || this.css_template, options));
	 }
}
if (typeof(friendfundOptions) !== 'undefined' && friendfundOptions.showButton == true) {
    FriendFund.Button.show(friendfundOptions);
}


