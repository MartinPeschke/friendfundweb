if(!FriendFund){var FriendFund={}}FriendFund.Util={render:function(a,b){return a.replace(/\${([^{}]*)}/g,function(d,c){var e=b[c];return typeof e==="string"||typeof e==="number"?e:d})},includeCss:function(b){var a=document.createElement("style");a.setAttribute("type","text/css");a.setAttribute("media","screen");if(a.styleSheet){a.styleSheet.cssText=b}else{a.appendChild(document.createTextNode(b))}document.getElementsByTagName("head")[0].appendChild(a)},get_tags:function(){var d={},a,e;var c=document.getElementsByTagName("META");for(var b=0;b<c.length;b++){e=c[b].getAttribute("property");a=c[b].name;if(a&&!e){d["ff.names."+a]=c[b].content}else{if(!a&&e){d["ff.props."+e]=c[b].content}}}d.referer=window.location.href;return d}};FriendFund.Logger={_log:function(a){if(typeof console!=="undefined"&&typeof console.log!=="undefined"){try{console.log(a)}catch(b){}}},warning:function(a){this._log("FriendFund WARNING: "+a)},error:function(a){this._log("FriendFund ERROR: "+a);alert("FriendFund ERROR: "+a)}};FriendFund.Element={getDimensions:function(c){var g=c.display;if(g!="none"&&g!=null){return{width:c.offsetWidth,height:c.offsetHeight}}var b=c.style;var f=b.visibility;var d=b.position;var a=b.display;b.visibility="hidden";b.position="absolute";b.display="block";var h=c.clientWidth;var e=c.clientHeight;b.display=a;b.position=d;b.visibility=f;return{width:h,height:e}},hasClassName:function(a,b){var c=a.className;return(c.length>0&&(c==b||new RegExp("(^|\\s)"+b+"(\\s|$)").test(c)))},addClassName:function(a,b){if(!this.hasClassName(a,b)){a.className+=(a.className?" ":"")+b}return a},removeClassName:function(a,b){a.className=a.className.replace(new RegExp("(^|\\s+)"+b+"(\\s+|$)")," ");return a}};FriendFund.Page={getDimensions:function(){var f=document.documentElement,b=document.body,d=window.innerWidth||self.innerWidth||(f&&f.clientWidth)||b.clientWidth,a=window.innerHeight||self.innerHeight||(f&&f.clientHeight)||b.clientHeight,c=Math.max(window.pageXOffset?window.pageXOffset:0,f?f.scrollLeft:0,b?b.scrollLeft:0),e=Math.max(window.pageYOffset?window.pageYOffset:0,f?f.scrollTop:0,b?b.scrollTop:0);return{width:d,height:a,xOffset:c,yOffset:e}},getDocHeight:function(){var b=document,a=Math.max;return a(a(b.body.scrollHeight,b.documentElement.scrollHeight),a(b.body.offsetHeight,b.documentElement.offsetHeight),a(b.body.clientHeight,b.documentElement.clientHeight))}};FriendFund.Popup={id:"FriendFund_Popup",close_text:{de:"Schliessen",en:"Close This",es:"Cerrar"},css_template:"#FriendFund_Popup {z-index:10000008;display: block;text-align: left;margin: 0 auto 0 auto;position:absolute;padding:10px;background-color:#000;}#FriendFund_Popup-content{background-color:white}#FriendFund_overlay {position: fixed;z-index:10000007;width: 100%;height: 100%;left: 0;top: 0;background-color: #000;opacity: 0.6;filter: alpha(opacity=60);}#FriendFund_overlay p {padding: 5px;color: #ddd;font: bold 14px arial, sans-serif;margin: 0;letter-spacing: -1px;}a#FriendFund_Popup_close {color:black;cursor:pointer;font-size:16px;font-weight:bold;line-height:15px;text-decoration:None;position:absolute;right:3px;top:3px;background:url(${protocol}${host}/static/partner/close_popup_cross.png) no-repeat 0 0 transparent;display:block;width:20px;height:20px;",preload:function(c){if(!this.preloaded){var b=document.getElementById(c);var a=(b==null)?c:b.innerHTML;this.setContent(a)}},show:function(b,a){this.options=a;this.preload(b);this.Overlay.show();this.setPosition();FriendFund.Element.addClassName(this.htmlElement(),"dialog-open");this.element().style.display="block";this.element().focus()},close:function(){this.element().style.display="none";FriendFund.Element.removeClassName(this.htmlElement(),"dialog-open");this.Overlay.hide();FriendFund.onClose()},element:function(){if(!document.getElementById(this.id)){var a=document.createElement("div");a.innerHTML='<div id="'+this.id+'" style="display:none;"><a href="#close" onclick="FriendFund.Popup.close(); return false;" id="'+this.id+'_close" title="'+this.close_text[this.options.lang]+'"><span style="display: none;">Close Popup</span></a><div id="'+this.id+'-content"></div></div>';document.body.insertBefore(a.firstChild,document.body.firstChild)}return document.getElementById(this.id)},setContent:function(a){this.element();document.getElementById(this.id+"-content").innerHTML=a},setPosition:function(){var d=FriendFund.Element.getDimensions(this.element());var b=FriendFund.Page.getDimensions();var a=this.element().style;a.width="auto";a.height="auto";a.left=(b.xOffset+(b.width-d.width)/2)+"px";var c=(b.yOffset+(b.height-d.height)/2);a.top=Math.max(c,0)+"px"},htmlElement:function(){return document.getElementsByTagName("html")[0]}};FriendFund.onClose=function(){};FriendFund.Popup.Overlay={show:function(){this.get_element().style.display="Block";this._keyUpSuper=document.onkeydown;document.onkeydown=function(a){var a=a||window.event;if(a.keyCode===27){FriendFund.Popup.close()}}},hide:function(){this.get_element().style.display="None";document.onkeydown=this._keyUpSuper;this._keyUpSuper&&delete this._keyUpSuper},olay_id:"FriendFund_overlay",get_element:function(){if(!document.getElementById(this.olay_id)){olay=document.createElement("div");olay.innerHTML='<div id="'+this.olay_id+'" class="FriendFund_popup_elem" return false;" style="display:none;"></div>';document.body.insertBefore(olay.firstChild,document.body.firstChild)}return document.getElementById(this.olay_id)}};FriendFund.Popin={context:{width:"720px",height:"530px"},content_template:'<iframe id="friendfund_dialog_iframe" name="friendfund_dialog_iframe" src="" frameborder="0" scrolling="no" allowtransparency="true" width="${width}" height="${height}" style="height: ${height}; width: ${width};"></iframe>',setup:function(a){this.setupOptions(a)},setupOptions:function(a){if(typeof(a)==="undefined"){return}if(a.key==null&&a.host==null){FriendFund.Logger.error("'host' must be set.");FriendFund.Logger.error("'key' must be set.")}else{if(a.key==null){FriendFund.Logger.warning("'key' must be set for the widget to work.")}}this.options=a},show:function(b){this.setupOptions(b);FriendFund.Popup.show(FriendFund.Util.render(this.content_template,this.context),b);try{var c=document.getElementById("friendfund_dialog_iform");if(c){document.body.removeChild(c)}var a=function(e,j){var i=document.createElement("form");i.setAttribute("id","friendfund_dialog_iform");i.setAttribute("method","POST");i.setAttribute("action",e);i.setAttribute("target","friendfund_dialog_iframe");for(var g in j){var h=document.createElement("input");h.setAttribute("type","hidden");h.setAttribute("name",g);h.setAttribute("value",j[g]);i.appendChild(h)}document.body.appendChild(i);i.submit()};var f=FriendFund.Util.get_tags();f.key=b.key;f.host=b.host;f.real_host=window.location.host;a(this.url(b),f)}catch(d){FriendFund.Logger.warning("Error sending the 'open' notification");FriendFund.Logger.warning(d)}},url:function(a){return a.protocol+a.host+"/partner/preset"}};FriendFund.Button={button_id:"friendfund_fund_button",css_template:"#${button_id} {margin: 10px 0;width: auto;background:${button_background};padding: 7px 0 5px;}#${button_id} a {background:None !important;width:auto;height:auto;text-indent: 0;}#${button_id}:hover {cursor:pointer}#${button_id} *, #${button_id} *:hover {text-decoration:none !important; font-weight:normal !important}#${button_id} .friendfundButton{pointer:cursor;display:block;text-align:${alignment};padding:0;}#${button_id} .friendfundButton img{margin:0px auto;}#${button_id} .friendfundButton span{text-transform: none;padding:0;font-size:10px;margin:0px auto;color:#a6a6a6;text-shadow: 0px 1px 0px white;display:block}",fixed_css_template:"#${button_id} {position:absolute;left:-150px;top:${top};width:196px;height:122px;} #${button_id}:hover {left:0px;cursor:pointer} #${button_id} .friendfundButton{pointer:cursor;color:white;width:196px;height:172px;background:url(${protocol}${host}/static/partner/buttons/friendfund_it_button_complete.png) no-repeat 0 0 transparent;display:block}",show:function(c){FriendFund.Popin.setup(c);this.button_id=c.button_id||this.button_id;if(c.render){var d=document.createElement("A");d.id="friendfund_button";d.className="friendfundButton";if(!document.getElementById(this.button_id)){var f=document.createElement("div");f.id=this.button_id;document.body.insertBefore(f,document.body.firstChild);var g=FriendFund.Page.getDimensions();var e=((g.height-143)/2);c.css_template=FriendFund.Util.render(this.fixed_css_template,{top:Math.max(e,55)+"px"});d.innerHTML="&nbsp;"}else{c.css_template=this.css_template;var a=document.createElement("IMG");a.src=FriendFund.Util.render("${protocol}${host}/static/partner/buttons/friendfund_it_button_${button_size}_${button_color}.png",c);d.appendChild(a);if(c.with_strap_line){var b=document.createElement("SPAN");b.innerHTML=c.button_text[c.lang];d.appendChild(b)}}FriendFund.Util.includeCss(FriendFund.Util.render(c.css_template||this.css_template,c));document.getElementById(this.button_id).appendChild(d)}else{var d=document.getElementById(this.button_id)}FriendFund.Util.includeCss(FriendFund.Util.render(FriendFund.Popup.css_template,c));d.onclick=function(){FriendFund.Popin.show(c);return false};c.docHeight=FriendFund.Page.getDocHeight()}};if(typeof(friendfundOptions)!=="undefined"&&friendfundOptions.showButton==true){defaultOptions={alignment:"center",lang:"en",render:true,button_text:{es:"Comparte los gastos con amigos!",en:"Share the costs with friends!",de:"Teile die Kosten mit Freunden!"},button_background:"#f4f4f4",button_size:"large",button_color:"blue",with_strap_line:true};for(var option in defaultOptions){friendfundOptions[option]=(friendfundOptions[option]===undefined)?defaultOptions[option]:friendfundOptions[option]}FriendFund.Button.show(friendfundOptions)};