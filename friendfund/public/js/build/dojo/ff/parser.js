/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["ff.parser"]){dojo._hasResource["ff.parser"]=true;dojo.provide("ff.parser");dojo.require("ff.t");dojo.require("ff.w");dojo.mixin(ff,{parser:{urlmatch:/^(www\.|https?:\/\/)([\-a-zA-Z0-9_]{2,256}\.)+[a-z]{2,4}(\/[\-a-zA-Z0-9%_\+.,~#&=!;:]*)*(\?[\-a-zA-Z0-9%_;:\+,.~#&=!\/]+)*$/i,_accepted:false,_picCounter:0,_parser_backups:[],_localhndlrs:[],__rootnode__:"homeurlexpander",findParent:ff.t.findParent,reloadPicture:function(_1,_2,_3){var rn=dojo.byId(_1),_4=this;return function(_5){var f=function(_6){dojo.byId(_3).value=_5.rendered_picture_url;dojo.query("img.displayed",rn).addClass("hiddenSpec").removeClass("displayed");if(dojo.byId("pictureCounter")){_4._picCounter+=1;dojo.byId("pictureCounter").innerHTML=_4._picCounter;}if(dojo.byId("pictureCounterPos")){dojo.byId("pictureCounterPos").innerHTML=1;}rn.insertBefore(dojo.create("IMG",{"class":"allowed displayed",src:_5.rendered_picture_url}),rn.firstChild);rn.appendChild(dojo.create("INPUT",{"type":"hidden",value:_5.rendered_picture_url,"class":"PURLImgListElem",name:"img_list"}));dojo.publish("/ff/popup/all/destroy");};if(_5.success){dojo.byId(_2).src=_5.rendered_picture_url;dojo.query("input.transp",_2.parentNode).removeClass("transp");dojo.byId("purlSaveButton").onclick=f;}else{alert("Unsupported file type");}};},createAppendPicture:function(_7,_8,_9){var _a=_8.shift(),_b;if(_a!==undefined){_b=dojo.create("IMG",{"class":"hiddenSpec forbidden"});_7.appendChild(_b);dojo.connect(_b,"onload",dojo.hitch(this,"pic_judger",_7,_8,_9));dojo.connect(_b,"onerror",dojo.hitch(this,"createAppendPicture",_7,_8,_9));_b.src=_a;}else{_8=dojo.query(".imgCntSld img.allowed",this.__rootnode__);if(_8.length<=1){dojo.query(".imgCntSld img.forbidden",this.__rootnode__).forEach(dojo.hitch(this,"judger",40,30,_9));}}},judger:function(_c,_d,_e,_f){var _10,w=_f.width||_f.offsetWidth||_f.naturalWidth,h=_f.height||_f.offsetHeight||_f.naturalHeight;if(w>=_c&&h>=_d){this._picCounter+=1;dojo.byId("pictureCounter").innerHTML=this._picCounter;dojo.removeClass(_f,"forbidden");dojo.addClass(_f,"allowed");if(!_e&&!this._accepted||_f.src===_e){this._accepted=true;dojo.addClass(_f,"displayed");dojo.removeClass(_f,"hiddenSpec");dojo.byId("pictureCounterPos").innerHTML=dojo.query(".imgCntSld img.allowed",this.__rootnode__).indexOf(_f)+1;_10=dojo.byId("URLPproductPicture");if(!_10){_10=dojo.create("INPUT",{type:"hidden",value:_f.src,id:"URLPproductPicture",name:"product_picture"});dojo.byId(this.__rootnode__).appendChild(_10);}else{if(dojo.attr(_10,"_set_default")){_10.value=_f.src;}}}}},pic_judger:function(_11,_12,_13,evt){if(dojo.byId("pictureCounter")){this.judger(177,140,_13,evt.target);this.createAppendPicture(_11,_12,_13);}},slide:function(_14,evt){var _15=dojo.query(".imgCntSld img.allowed",this.__rootnode__),i,pos;for(i=0,len=_15.length;i<len;i++){pos=(len+(_14+i))%len;if(!dojo.hasClass(_15[i],"hiddenSpec")&&pos!=i){dojo.addClass(_15[i],"hiddenSpec");dojo.removeClass(_15[i],"displayed");dojo.addClass(_15[pos],"displayed");dojo.removeClass(_15[pos],"hiddenSpec");dojo.byId("pictureCounterPos").innerHTML=pos+1;dojo.byId("URLPproductPicture").value=_15[pos].src;break;}}},urlPEEvents:function(_16,_17,evt){if(this.findParent(evt.target,"smallLeft")){this.slide(-1);}else{if(this.findParent(evt.target,"smallRight")){this.slide(1);}else{if(_17&&dojo.hasClass(evt.target,"parsercloser")){this.resetParser(_16,_17);}}}},connectURLP:function(_18,_19){var _1a=dojo.byId(this.__rootnode__);ff.w.parseSimpleEditables(_1a);ff.w.parseDefaultsInputs(_1a);this._localhndlrs.push(dojo.connect(_1a,"onclick",dojo.hitch(this,"urlPEEvents",_18,_19)));this.createAppendPicture(dojo.byId("URLPimgCntSld"),dojo.query(".PURLImgListElem",_1a).attr("value"),dojo.byId("URLPproductPicture").value);},resetParser:function(_1b,_1c){var _1d=this;dojo.empty(this.__rootnode__);dojo.forEach(this._parser_backups,function(_1e){dojo.byId(_1d.__rootnode__).appendChild(_1e);});dojo.forEach(this._localhndlrs,dojo.disconnect);this._picCounter=0;this._accepted=false;this._parser_backups=[];this._localhndlrs=[];dojo.query(".hideable",_1b).removeClass("hidden");dojo.query("#homeurlexpander").removeClass("home_expander");this.connectURLParser(_1b,_1c);},loadSuccess:function(_1f,_20,_21){dojo.empty(this.__rootnode__);if(_21.success===false){this.resetParser(_1f,_20);}else{var _22=dojo.byId(this.__rootnode__);dojo.place(_21.html,_22,"only");this.connectURLP(_1f,_20);}},connectURLParser:function(_23,_24,_25,_26){var _27=this,dn=dojo.byId(_24),_28=[],_29=function(){_27._picCounter=0;_27._accepted=false;_27._parser_backups=[];_27._localhndlrs=[];_28.push(dojo.connect(dn,"onkeyup",_2a));_28.push(dojo.connect(dn,"onpaste",_2a));_28.push(dojo.connect(dn,"onblur",_2a));},_2b=function(){var _2c=false,_2d,i,elt,_2e,div,url;if(!dojo.hasClass(dn,"default")){_2d=dn.value.split(" ");for(i=0,len=_2d.length;i<len;i++){elt=_2d[i];if(_27.urlmatch.test(elt)){_2e=elt;url=dojo.attr(dn,"_url");dojo.query(".hideable",_23).addClass("hidden");div=dojo.create("DIV",{"class":"loading"});div.appendChild(dojo.create("IMG",{src:"/static/imgs/ajax-loader.gif"}));_27._parser_backups=dojo.query("> *",_27.__rootnode__).orphan();dojo.place(div,_27.__rootnode__,"last");dojo.query("#homeurlexpander").addClass("home_expander").removeClass("hidden");_26=_26||{};_26.query=_2e;dojo.xhrPost({url:url,content:_26,handleAs:"json",load:dojo.hitch(_27,"loadSuccess",_23,_24),error:dojo.hitch(_27,"resetParser",_23,_24)});_2c=true;break;}}}if(!_2c&&_28.length===0){_29();}},_2a=function(evt,_2f){if(evt.type==="paste"){dojo.forEach(_28,dojo.disconnect);_28=[];window.setTimeout(_2b,200);}else{if(!evt.keyCode||(evt.keyCode==32)){dojo.forEach(_28,dojo.disconnect);_28=[];_2b();}}return evt;};_29();if(_25){_2b(dn);}}}});}