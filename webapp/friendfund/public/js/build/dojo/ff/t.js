if(!dojo._hasResource["ff.t"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["ff.t"] = true;
dojo.provide("ff.t");

dojo.mixin(ff,{t:{
	getPageDimensions: function () {
		var de = document.documentElement, db = document.body
			, width = window.innerWidth || self.innerWidth || (de && de.clientWidth) || db.clientWidth
			, height = window.innerHeight || self.innerHeight || (de && de.clientHeight) || db.clientHeight
			, xOffset = Math.max(window.pageXOffset ? window.pageXOffset : 0, de ? de.scrollLeft : 0, db ? db.scrollLeft : 0)
			, yOffset = Math.max(window.pageYOffset ? window.pageYOffset : 0, de ? de.scrollTop : 0, db ? db.scrollTop : 0)
		return {w: width,h: height, xOffset:xOffset, yOffset:yOffset};
	},
	centerElementInViewPort : function (element) {
		var dialogDimensions = dojo.coords(element)
			, pageDimensions = this.getPageDimensions()
			, els = element.style;
		els.left = (pageDimensions.xOffset+(pageDimensions.w - dialogDimensions.w) / 2) + "px";
		var computedHeight = (pageDimensions.yOffset+75);
		els.top = Math.max(computedHeight, 0) + "px";
	}
	,goto_url : function(link){return function(){window.location.href=dojo.attr(link, "_href");};}
	,goto_url_or_reload : function(link){return function(){
		var url = dojo.attr(link, "_href");
		if(url)window.location.href=url;
		else window.location.reload(true);
	}}
	,reload : function(link){window.location.reload(true);}
	,findParent : function(rootnode, className){
		if(dojo.hasClass(rootnode, className)){return rootnode;}
		else if(!dojo.hasClass(rootnode, className)&&rootnode.parentNode){return ff.t.findParent(rootnode.parentNode, className);}
		else {return null;}
	}
	,addClassToParent : function(rootnode, className, addClass){
		var node = ff.t.findParent(rootnode, className);
		if(node){dojo.addClass(node, addClass);}
	}
	,remClassFromParent : function(rootnode, className, remClass){
		var node = ff.t.findParent(rootnode, className);
		if(node){dojo.removeClass(node, remClass);}
	}
	,onSubmitCleaner : function(rootnode){
		dojo.query("input[_default_text],textarea[_default_text]", rootnode).forEach(
			function(element){
				if(dojo.attr(element, "_default_text") === element.value){element.value="";}
			});
		return true;
	}
	,showLoadingInfo : function(rootnode){
		dojo.query(".loading_animation", rootnode).removeClass("hidden");
		dojo.query("input[type=submit]", rootnode).forEach(function(elem){elem.disabled = "disabled";});
	}
	,accessability : function(callbackRet, callbackEsc, evt){
		if(evt.keyCode === 13){dojo.hitch(this, callbackRet(this, evt));}
		else if(evt.keyCode === 27){dojo.hitch(this, callbackEsc(this, evt));}
	}
	,getKeys : function(map){
		var result = [];
		for(var key in map){
			if(map.hasOwnProperty(key))result.push(key);
		}
		return result;
	}
	,getValues : function(map){
		var result = [];
		for(var key in map){
			if(map.hasOwnProperty(key))result.push(map[key]);
		}
		return result;
	}
	,toMap : function(list){
		var result = {}, i, len;
		for(i=0,len=list.length; i<len;i++){
			result[list[i]] = 1;
		}
		return result;
	}
	,render: function (template, params) {
		return template.replace(/\${([^{}]*)}/g, function (a, b) {
			var r = params[b];
			return typeof r === 'string' || typeof r === 'number' ? r : a;
		})
	}
	,debounce : function (func, threshold, execAsap) {
		var timeout;
		return function debounced () {
			var obj = this, args = arguments;
			function delayed () {
				if (!execAsap)
					func.apply(obj, args);
				timeout = null; 
			};
	 
			if (timeout)
				clearTimeout(timeout);
			else if (execAsap)
				func.apply(obj, args);
			timeout = setTimeout(delayed, threshold || 100); 
		};
	}
	,deferreds: function (doneFunc, context) {
		var deferreds = [], _t = this;
		this.doneFunc = doneFunc;
		this.add = function (f) {
			deferreds.push(f);
			_t.run(arguments);
		};
		this.run = function () {
			if (_t.doneFunc.apply(context)) {
				var i = 0; len = deferreds.length;
				for (; i < len; i++) {
					var f = deferreds.pop();
					f.apply(_t, arguments);
				}
			}
		};
	}
}});

}
