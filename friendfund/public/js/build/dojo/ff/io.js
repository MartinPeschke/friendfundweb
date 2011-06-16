/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["ff.io"]){dojo._hasResource["ff.io"]=true;dojo.provide("ff.io");dojo.require("dojo.io.iframe");dojo.mixin(ff,{io:{xhrHandler:function(_1){return function(_2,_3,_4){if(_2.message!==undefined){ff.w.displayMessage(_2.message);}if(_2.login!==undefined&&_1){_1(_2.login);}if(_2.popup!==undefined){ff.w.displayPopup(_2.popup);}if(_1&&_2.html!==undefined){_1(_2.html);}if(_1&&_2.data!==undefined){_1(_2.data);}if(_2.redirect!==undefined){window.location.href=_2.redirect;}if(_2.reload===true){window.location.reload(true);}return _2;};},xhrErrorHandler:function(_5,_6,_7){if(window.console){}},xhrFormPost:function(_8,_9,_a){dojo.xhrPost({url:_8,form:_9,handleAs:"json",load:ff.io.xhrHandler(_a),error:ff.io.xhrErrorHandler});},xhrPost:function(_b,_c,_d,_e){var _f=_e||"Post";dojo["xhr"+_f]({url:_b,content:_c,handleAs:"json",load:ff.io.xhrHandler(_d),error:ff.io.xhrErrorHandler});},ioIframeGetJson:function(url,_10,_11){dojo.io.iframe.send({url:url,form:_10,method:"Post",content:{},timeoutSeconds:15,preventCache:true,handleAs:"json",load:ff.io.xhrHandler(_11),error:ff.io.xhrErrorHandler});}}});}