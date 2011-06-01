/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["ff.w"]){dojo._hasResource["ff.w"]=true;dojo.provide("ff.w");dojo.require("dojo.fx.easing");dojo.mixin(ff,{w:{displayMessage:function(_1){return alert(_1);},parseSelectables:function(_2,_3,_4){var _5=this;_3=_3||"borderBottom";_4=_4||"selected";var a=function(_6){if(_6){ff.t.addClassToParent(_6.target,_3,_4);}},r=function(_7){if(_7){ff.t.remClassFromParent(_7.target,_3,_4);}};if(dojo.isIE===undefined){dojo.byId(_2).addEventListener("focus",a,true);dojo.byId(_2).addEventListener("blur",r,true);}else{dojo.connect(dojo.byId(_2),"onfocusin",a);dojo.connect(dojo.byId(_2),"onfocusout",r);}},parseSimpleEditables:function(_8){var _9=this;dojo.query(".simpleeditable.active",_8).forEach(function(_a){dojo.removeClass(_a,"active");var d=dojo.connect(_a,"onclick",function(_b){dojo.disconnect(d);var _c=dojo.query("input[type=hidden]",_a)[0],_d=dojo.attr(_c,"_length"),_e=dojo.create(dojo.attr(_c,"_type"),{type:"text","class":_c.className,_length:_d,value:_c.value,name:_c.name,id:_c.id}),_f=[],_10=[],f=function(_11){var _12=_11.target.value;if(_12.length===0){return;}dojo.forEach(_f,dojo.disconnect);dojo.addClass(_a,"active");_c.value=_12;dojo.empty(_a);_a.innerHTML=_d?_12.substr(0,_d):_12;if(_d&&_12.length>_d){_a.innerHTML=_a.innerHTML+"...";}dojo.forEach(_10,function(_13){_a.appendChild(_13);});delete _10;_9.parseSimpleEditables(_8);return _11;};_f.push(dojo.connect(_e,"onblur",f));_10=dojo.query("> *",_a).orphan();dojo.empty(_a);_a.appendChild(_e);_e.focus();});});},parseEditables:function(_14){var _15=this;dojo.query(".editable.active",_14).forEach(function(_16){dojo.removeClass(_16,"active");var d=dojo.connect(_16,"onclick",function(evt){ff.io.xhrPost(dojo.attr(_16,"_href"),{value:dojo.attr(_16,"_value")},function(_17){dojo.place(_17,_16,"only");dojo.disconnect(d);dojo.query("input[type=text],select,textarea",_16).forEach(function(_18){_18.focus();var _19=[],f=function(_1a){dojo.forEach(_19,dojo.disconnect);dojo.addClass(_16,"active");if(_18.tagName=="SELECT"){dojo.attr(_16,"_value",_1a.target.options[_1a.target.selectedIndex].value);}else{dojo.attr(_16,"_value",_1a.target.value);}ff.io.xhrPost(dojo.attr(_16,"_href"),{value:dojo.attr(_16,"_value")},function(_1b){_16.innerHTML=_1b;_15.parseEditables(_14);},"Post");return _1a;};_19.push(dojo.connect(_18,"onchange",f,null,f,true));_19.push(dojo.connect(_18,"onblur",f,null,f,true));});},"Get");});});},parseDefaultsInputs:function(_1c){dojo.query("input[_default_text], textarea[_default_text]",_1c).onfocus(function(evt){if(dojo.hasClass(this,"default")){dojo.removeClass(this,"default");this.value="";}}).onblur(function(evt){if(!dojo.hasClass(this,"default")&&this.value.replace(/ /g,"")===""){dojo.addClass(this,"default");this.value=dojo.attr(this,"_default_text");}}).forEach(function(elt){if(elt.value!=dojo.attr(elt,"_default_text")){dojo.removeClass(elt,"default");}});},onLoadPagelets:function(_1d){var _1e=this,_1f=function(_20,_21){return function(_22){if(_22){dojo.place(_22,_20,"only");}dojo.style(_20,"display","Block");if(_21){_21.call();}};},_23=function(url,_24,_25,_26,_27){if(dojo.byId(_24)){ff.io.xhrPost(url,_25,_1f(_24,_26),_27);}else{ff.io.xhrPost(url,_25,_26,_27);}};dojo.query(".pagelet",_1d).forEach(function(_28){_23(dojo.attr(_28,"pagelet_href"),_28,{},null,"Get");});},sliderF:function(_29,_2a,_2b){var _2c=dojo.byId(_29),_2d=dojo.query("ul.slider",_2c)[0],_2e=parseInt(dojo.attr(_2d,"_elem_width"),10),_2f=0,_30,_31=false,_32=false,_33=dojo.query("ul.slider li",_2c).length,_34=function(evt){_32=true;},_35=function(evt){_32=false;},_36=function(_37,_38){return function(evt){var _39=function(){_31=false;};if(!_31&&(!_32||_38)){_31=true;if(_2f===0&&_37>0){_30=_2d.getElementsByTagName("li");_30=_2d.removeChild(_30[_30.length-1]);dojo.style(_2d,"marginLeft",(_2e*(_2f-_37))+"px");_2d.insertBefore(_30,_2d.firstChild);dojo.animateProperty({node:_2d,duration:900,easing:dojo.fx.easing.sineInOut,properties:{marginLeft:{start:(_2e*(_2f-_37)),end:(_2e*(_2f)),units:"px"}},onEnd:_39}).play();}else{if(_2f===_2a-_33&&_37<0){_30=_2d.removeChild(_2d.getElementsByTagName("li")[0]);dojo.style(_2d,"marginLeft",(_2e*(_2f-_37))+"px");_2d.appendChild(_30);dojo.animateProperty({node:_2d,duration:900,easing:dojo.fx.easing.sineInOut,properties:{marginLeft:{start:(_2e*(_2f-_37)),end:(_2e*(_2f)),units:"px"}},onEnd:_39}).play();}else{dojo.animateProperty({node:_2d,duration:900,easing:dojo.fx.easing.sineInOut,properties:{marginLeft:{start:(_2e*(_2f)),end:(_2e*(_2f+_37)),units:"px"}},onEnd:_39}).play();_2f=_2f+_37;}}}};};dojo.query(".controllerLeft",_2c).onclick(_36(1,true));dojo.query(".controllerRight",_2c).onclick(_36(-1,true));dojo.connect(_2c,"onmouseover",_34);dojo.connect(_2c,"onmouseout",_35);if(_2b===true){window.setInterval(_36(-1,false),3500);}},showTime:function(_3a,_3b){var _3c=_3b*1000,d=dojo.query(".timerDays",_3a)[0],_3d=parseInt(d.innerHTML,10),h=dojo.query(".timerHours",_3a)[0],hrs=parseInt(h.innerHTML,10),m=dojo.query(".timerMinutes",_3a)[0],_3e=parseInt(m.innerHTML,10),s=dojo.query(".timerSeconds",_3a)[0],_3f=parseInt(s.innerHTML,10),_40=function(_41){return function(){if(_3f>0){s.innerHTML=_3f=_3f+_41;}else{if(_3e>0){s.innerHTML=_3f=59;m.innerHTML=_3e=_3e-1;}else{if(hrs>0){s.innerHTML=_3f=59;m.innerHTML=_3e=59;h.innerHTML=hrs=hrs-1;}else{if(_3d>0){s.innerHTML=_3f=59;m.innerHTML=_3e=59;h.innerHTML=hrs=23;d.innerHTML=_3d=_3d-1;}else{return;}}}}window.setTimeout(_40(-_3b),_3c);};};window.setTimeout(_40(-_3b),_3c);}}});}