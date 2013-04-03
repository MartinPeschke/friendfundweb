dojo.provide("ff.w");
dojo.require("dojo.fx.easing");

dojo.mixin(ff, {w: {
	displayMessage : function(message){return alert(message)}
	,parseSelectables : function(rootnode, parentClass, selectedName){
		var _t = this;
		parentClass = parentClass||"borderBottom";
		selectedName = selectedName||"selected";
		var a = function(evt){
				if(evt){ff.t.addClassToParent(evt.target, parentClass, selectedName);}
			},
			r = function(evt){
				if(evt){ff.t.remClassFromParent(evt.target, parentClass, selectedName);}
			};
		if(dojo.isIE===undefined){
			dojo.byId(rootnode).addEventListener('focus',a,true);
			dojo.byId(rootnode).addEventListener('blur',r,true);
		} else {
			dojo.connect(dojo.byId(rootnode), "onfocusin", a);
			dojo.connect(dojo.byId(rootnode), "onfocusout", r);
		}
	}
	,parseSimpleEditables : function(rootnode){
		var _t = this;
		dojo.query(".simpleeditable.active", rootnode).forEach(
			function(root){
				dojo.removeClass(root,'active');
				var d = dojo.connect(root, "onclick", 
					function(evt){
						dojo.disconnect(d);
						var field = dojo.query("input[type=hidden]", root)[0],
							length = dojo.attr(field, "_length"),
							editor = dojo.create(dojo.attr(field, "_type"), {type:"text", "class":field.className, _length:length, value:field.value, name:field.name, id:field.id}),
							evts = [],  _backups = [],
							f = function(editevt){
								var newval=editevt.target.value;
								if(newval.length===0){return;}
								dojo.forEach(evts, dojo.disconnect);
								dojo.addClass(root,'active');
								field.value = newval;
								dojo.empty(root);
								root.innerHTML = length?newval.substr(0,length):newval;
								if(length&&newval.length>length){root.innerHTML=root.innerHTML+"...";}
								dojo.forEach(_backups, function(elem){root.appendChild(elem);});
								delete _backups;
								_t.parseSimpleEditables(rootnode);
								return editevt;
							};
						evts.push(dojo.connect(editor, "onblur", f));
						_backups  = dojo.query('> *', root).orphan();
						dojo.empty(root);
						root.appendChild(editor);
						editor.focus();
					});
			});
	}
	,parseEditables : function(rootnode){
		var _t = this;
		dojo.query(".editable.active", rootnode).forEach(
			function(root){
				dojo.removeClass(root,'active');
				var d = dojo.connect(root, "onclick", 
					function(evt){
						ff.io.xhrPost(dojo.attr(root, '_href'), {value:dojo.attr(root, '_value')}, 
							function(data){
								dojo.place(data,root,"only");
								dojo.disconnect(d);
								dojo.query('input[type=text],select,textarea', root).forEach(
									function(editor){
										editor.focus();
										var evts = [],
											f = function(editevt){
												dojo.forEach(evts, dojo.disconnect);
												dojo.addClass(root,'active');
												if(editor.tagName=='SELECT'){
													dojo.attr(root, '_value', editevt.target.options[editevt.target.selectedIndex].value);
												} else {
													dojo.attr(root, '_value', editevt.target.value);
												}
												ff.io.xhrPost(dojo.attr(root, '_href'), {value:dojo.attr(root, '_value')}, 
													function(data){
														root.innerHTML = data;
														_t.parseEditables(rootnode);
													}, "Post");
												return editevt;
												};
										evts.push(dojo.connect(editor, "onchange", f, null, f, true));
										evts.push(dojo.connect(editor, "onblur", f, null, f, true));
									});
							}, "Get");
					});
			});
	}
	,parseDefaultsInputs : function(rootnode){
		dojo.query("input[_default_text], textarea[_default_text]", rootnode).onfocus(
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
			}).forEach(function(elt){
				if(elt.value!=dojo.attr(elt, "_default_text")){dojo.removeClass(elt, "default");}
			});
	}
	,onLoadPagelets : function(root_node){
		var _t = this
			,place_element = function(node, callback){
				return function(data){
					if(data){dojo.place(data, node, "only");}
					dojo.style(node, 'display', 'Block');
					if(callback){callback.call();}
				};
			}
			,loadElement = function(url, node, args, callback, method){
				if(dojo.byId(node)){
					ff.io.xhrPost(url, args, place_element(node, callback), method);
				} else {
					ff.io.xhrPost(url, args, callback, method);
				}
			};
		dojo.query('.pagelet', root_node).forEach(function(elem){loadElement(dojo.attr(elem, 'pagelet_href'), elem, {}, null, 'Get');});
	}
	,sliderF:function(root, noElems, duration, autostart){
		var rootNode = dojo.byId(root), slider = dojo.query("ul.slider", rootNode)[0], leftAmount = parseInt(dojo.attr(slider, "_elem_width"), 10)
			,position=0, child, transitioning = false, hover=false
			,countElems = dojo.query("ul.slider li", rootNode).length
			,setHoverOn = function(evt){hover=true;}
			,setHoverOff = function(evt){hover=false;}
			,slide = function(step, force){ return function(evt){
				var reset = function(){transitioning=false;};
				if(!transitioning&&(!hover||force)){
					transitioning = true;
					if(position===0&&step>0){
						child = slider.getElementsByTagName("li");
						child = slider.removeChild(child[child.length-1]);
						dojo.style(slider, "marginLeft", (leftAmount*(position-step))+"px");
						slider.insertBefore(child, slider.firstChild);
						dojo.animateProperty({node:slider,duration: duration,easing:dojo.fx.easing.sineInOut, properties: {marginLeft:  { start: (leftAmount*(position-step)), end:(leftAmount*(position)), units:"px" }}, onEnd:reset}).play();
					} else if (position===noElems-countElems&&step<0){
						child = slider.removeChild(slider.getElementsByTagName("li")[0]);
						dojo.style(slider, "marginLeft", (leftAmount*(position-step))+"px");
						slider.appendChild(child);
						dojo.animateProperty({node:slider,duration: duration,easing:dojo.fx.easing.sineInOut, properties: {marginLeft:  { start: (leftAmount*(position-step)), end:(leftAmount*(position)), units:"px" }}, onEnd:reset}).play();
					} else {
						dojo.animateProperty({node:slider,duration: duration,easing:dojo.fx.easing.sineInOut, properties: {marginLeft:  { start: (leftAmount*(position)), end:(leftAmount*(position+step)), units:"px" }}, onEnd:reset}).play();
						position = position + step;
					}
				}
			};};
		dojo.query(".controllerLeft", rootNode).onclick(slide(1, true));
		dojo.query(".controllerRight", rootNode).onclick(slide(-1, true));
		dojo.connect(rootNode, "onmouseover", setHoverOn);
		dojo.connect(rootNode, "onmouseout", setHoverOff);
		if(autostart===true){window.setInterval(slide(-1, false), 3500);}
	}
	,anythingSlider : function(root){
		var rootNode = dojo.byId(root)
			, slider = dojo.query(".contentSlider", rootNode)[0]
			, left_controller = dojo.query(".controllerLeft", rootNode)[0]
			, right_controller = dojo.query(".controllerRight", rootNode)[0]
			, panes = dojo.query(".contentSlider > .sliderPane", rootNode)
			, no_elems = panes.length
			, position = 0
			, transitioning = false
			, width = dojo.coords(panes[0]).w
			, slide = function(step){ return function(evt){
				var reset = function(){
					transitioning=false;
				}, sC = function(){
					dojo.query(".sliderNumberControl.selected", rootNode).removeClass("selected");
					dojo.addClass(dojo.query(".sliderNumberControl",rootNode)[position], "selected");
					if(position===0){dojo.addClass(left_controller, "hidden");}
					else if(dojo.hasClass(left_controller,"hidden")){dojo.removeClass(left_controller, "hidden");}
					if(position===no_elems-1){dojo.addClass(right_controller, "hidden");}
					else if(dojo.hasClass(right_controller,"hidden")){dojo.removeClass(right_controller, "hidden");}
				};
				if(!transitioning){
					transitioning = true;
					if(position===0&&step<0){/*skip*/
					} else if (position===no_elems-1&&step>0){/*skip*/
					} else {
						position = position + step;
						dojo.animateProperty({node:slider,duration:300,easing:dojo.fx.easing.sineInOut, properties: {left:  { start: (-width*(position-step)), end:(-width*(position)), units:"px" }}, onBegin:sC, onEnd:reset}).play();
					}
				}
			};
		};
		dojo.query(left_controller).onclick(slide(-1));
		dojo.query(right_controller).onclick(slide(1));
		dojo.query(".sliderNumberControl", rootNode).onclick(function(evt){
			var pane = parseInt(dojo.attr(evt.target, "_pane"),10);
			slide(pane-position)(evt);
		});
	}
	,showTime : function(root, unit){
		var delay = unit*1000,
		d=dojo.query(".timerDays", root)[0], days=parseInt(d.innerHTML, 10),
		h=dojo.query(".timerHours", root)[0], hrs=parseInt(h.innerHTML, 10),
		m=dojo.query(".timerMinutes", root)[0], mins=parseInt(m.innerHTML, 10),
		s=dojo.query(".timerSeconds", root)[0], secs=parseInt(s.innerHTML, 10),
		tick = function(step){return function(){
			if(secs>0){s.innerHTML=secs=secs+step;}
			else if(mins>0){s.innerHTML=secs=59;m.innerHTML=mins=mins-1;}
			else if(hrs>0){s.innerHTML=secs=59;m.innerHTML=mins=59;h.innerHTML=hrs=hrs-1;}
			else if(days>0){s.innerHTML=secs=59;m.innerHTML=mins=59;h.innerHTML=hrs=23;d.innerHTML=days=days-1;}
			else{return;}
			window.setTimeout(tick(-unit), delay);
		};};
		window.setTimeout(tick(-unit), delay);
	}
}});
