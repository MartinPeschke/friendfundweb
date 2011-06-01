dojo.provide("ff.parser");
dojo.require("ff.t");
dojo.require("ff.w");


dojo.mixin(ff, {parser: {
	urlmatch:/^(www\.|https?:\/\/)([\-a-zA-Z0-9_]{2,256}\.)+[a-z]{2,4}(\/[\-a-zA-Z0-9%_\+.,~#&=!;:]*)*(\?[\-a-zA-Z0-9%_;:\+,.~#&=!\/]+)*$/i
	,_accepted : false
	,_picCounter : 0
	,_parser_backups : []
	,_localhndlrs : []
	,__rootnode__ : "homeurlexpander"
	,findParent : ff.t.findParent
	
	,reloadPicture : function(rootnode, intermediate_imgid, persisterid){
		var rn=dojo.byId(rootnode), _t = this;
		return function(data){
			var f = function(evt){
				dojo.byId(persisterid).value=data.rendered_picture_url;
				dojo.query("img.displayed", rn).addClass("hiddenSpec").removeClass("displayed");
				if(dojo.byId("pictureCounter")){_t._picCounter+=1;dojo.byId("pictureCounter").innerHTML=_t._picCounter;}
				if(dojo.byId("pictureCounterPos")){dojo.byId("pictureCounterPos").innerHTML=1;}
				rn.insertBefore(dojo.create("IMG", {"class":"allowed displayed", src:data.rendered_picture_url}), rn.firstChild);
				rn.appendChild(dojo.create("INPUT", {"type":"hidden", value:data.rendered_picture_url, "class":"PURLImgListElem", name:"img_list"}));
				dojo.publish("/ff/popup/all/destroy");
			};
			if(data.success){
				dojo.byId(intermediate_imgid).src = data.rendered_picture_url;
				dojo.query("input.transp", intermediate_imgid.parentNode).removeClass("transp");
				dojo.byId("purlSaveButton").onclick = f;
			} else {
				alert("Unsupported file type");
			}
		};
	}
	,createAppendPicture : function(imgContainer, imgs, preselected){
		var imgsrc = imgs.shift(), img;
		if(imgsrc!==undefined){
			img = dojo.create("IMG", {"class":'hiddenSpec forbidden'});
			imgContainer.appendChild(img);
			dojo.connect(img, "onload", dojo.hitch(this, "pic_judger", imgContainer, imgs, preselected));
			dojo.connect(img, "onerror", dojo.hitch(this, "createAppendPicture", imgContainer, imgs, preselected));
			img.src = imgsrc;
		} else {
			imgs=dojo.query(".imgCntSld img.allowed", this.__rootnode__);
			if(imgs.length<=1){
				dojo.query(".imgCntSld img.forbidden", this.__rootnode__).forEach(dojo.hitch(this, "judger", 40, 30, preselected));
			}
		}
	}
	,judger : function(minw, minh, preselected, img){
		var ctrInput, w = img.width||img.offsetWidth||img.naturalWidth, h = img.height||img.offsetHeight||img.naturalHeight;
		if(w>=minw&&h>=minh){
			this._picCounter+=1;
			dojo.byId("pictureCounter").innerHTML=this._picCounter;
			dojo.removeClass(img, "forbidden");
			dojo.addClass(img, "allowed");
			if(!preselected&&!this._accepted||img.src===preselected){
				this._accepted = true;
				dojo.addClass(img, "displayed");
				dojo.removeClass(img, "hiddenSpec");
				dojo.byId("pictureCounterPos").innerHTML=dojo.query(".imgCntSld img.allowed", this.__rootnode__).indexOf(img)+1;
				ctrInput = dojo.byId("URLPproductPicture");
				if(!ctrInput){
					ctrInput = dojo.create("INPUT", {type:"hidden", value:img.src, id:"URLPproductPicture", name:'product_picture'});
					dojo.byId(this.__rootnode__).appendChild(ctrInput);
				} else {
					if(dojo.attr(ctrInput, "_set_default")){ctrInput.value = img.src;}
				}
			}
		}
	}
	,pic_judger : function(imgContainer, imgs, preselected, evt){
		if(dojo.byId("pictureCounter")){
			this.judger(177, 140, preselected, evt.target);
			this.createAppendPicture(imgContainer, imgs, preselected);
		}
	}
	,slide : function(step, evt){
		var imgs=dojo.query(".imgCntSld img.allowed", this.__rootnode__), i, pos;
		for(i=0, len=imgs.length;i<len;i++){
			pos=(len+(step+i))%len;
			if(!dojo.hasClass(imgs[i], "hiddenSpec")&&pos!=i){
				dojo.addClass(imgs[i], "hiddenSpec");
				dojo.removeClass(imgs[i], "displayed");
				dojo.addClass(imgs[pos], "displayed");
				dojo.removeClass(imgs[pos], "hiddenSpec");
				dojo.byId("pictureCounterPos").innerHTML=pos+1;
				dojo.byId("URLPproductPicture").value=imgs[pos].src;
				break;
			}
		}
	}
	,urlPEEvents : function(baseRoot, editnode, evt){
		if(this.findParent(evt.target, "smallLeft")){this.slide(-1);}
		else if(this.findParent(evt.target, "smallRight")){this.slide(1);}
		else if(editnode && dojo.hasClass(evt.target, "parsercloser")){this.resetParser(baseRoot, editnode);}
	}
	,connectURLP : function(baseRoot, editnode){
		var home = dojo.byId(this.__rootnode__);
		ff.w.parseSimpleEditables(home);
		ff.w.parseDefaultsInputs(home);
		this._localhndlrs.push(dojo.connect(home, "onclick", dojo.hitch(this, "urlPEEvents", baseRoot, editnode)));
		this.createAppendPicture(dojo.byId("URLPimgCntSld"), 
							dojo.query(".PURLImgListElem", home).attr("value"), 
							dojo.byId("URLPproductPicture").value);
	}
	,resetParser : function(baseRoot, editnode){
		var _t = this;
		dojo.empty(this.__rootnode__);
		dojo.forEach(this._parser_backups, function(elem){dojo.byId(_t.__rootnode__).appendChild(elem);});
		dojo.forEach(this._localhndlrs, dojo.disconnect);
		this._picCounter = 0; 
		this._accepted = false; 
		this._parser_backups = []; 
		this._localhndlrs = [];
		dojo.query(".hideable", baseRoot).removeClass("hidden");
		dojo.query("#homeurlexpander").removeClass("home_expander");
		this.connectURLParser(baseRoot, editnode);
	}
	,loadSuccess : function(baseRoot, editnode, data){
		dojo.empty(this.__rootnode__);
		if(data.success === false){
			this.resetParser(baseRoot, editnode);
		} else {
			var home = dojo.byId(this.__rootnode__);
			dojo.place(data.html, home, "only");
			this.connectURLP(baseRoot, editnode);
		}
	}
	,connectURLParser : function(baseRoot, editnode, parseNow, extra_params){
		var _t = this
			,dn = dojo.byId(editnode)
			,_linkers= []
			,reconnect = function(){
				_t._picCounter = 0; 
				_t._accepted = false; 
				_t._parser_backups = []; 
				_t._localhndlrs = [];
				_linkers.push(dojo.connect(dn, "onkeyup", parseInputFromEvt));
				_linkers.push(dojo.connect(dn, "onpaste", parseInputFromEvt));
				_linkers.push(dojo.connect(dn, "onblur", parseInputFromEvt));
			},parseInput = function(){
				var found=false, token, i, elt, query, div, url;
				if(!dojo.hasClass(dn, "default")){
					token = dn.value.split(" ");
					for(i=0, len = token.length;i<len;i++){
						elt = token[i];
						if(_t.urlmatch.test(elt)){
								query = elt;
								url = dojo.attr(dn, "_url");
								dojo.query(".hideable", baseRoot).addClass("hidden");
								
								div = dojo.create("DIV", {"class":"loading"});
								div.appendChild(dojo.create("IMG", {src:"/static/imgs/ajax-loader.gif"}));
								_t._parser_backups = dojo.query("> *", _t.__rootnode__).orphan();
								dojo.place(div, _t.__rootnode__, "last");
								dojo.query("#homeurlexpander").addClass("home_expander").removeClass("hidden");
								extra_params = extra_params||{};
								extra_params.query = query;
								dojo.xhrPost({url:url, content:extra_params,
												handleAs: 'json',
												load:dojo.hitch(_t, "loadSuccess", baseRoot, editnode),
												error:dojo.hitch(_t, "resetParser", baseRoot, editnode)
											});
								found = true;
								break;
							}
					}
				}
				if(!found&&_linkers.length===0){reconnect();}
			},parseInputFromEvt = function(evt, ename){
				if(evt.type==="paste"){
					dojo.forEach(_linkers, dojo.disconnect);_linkers=[];
					window.setTimeout(parseInput, 200);
				} else if(!evt.keyCode||(evt.keyCode==32)){
					dojo.forEach(_linkers, dojo.disconnect);_linkers=[];
					parseInput();
				}
				return evt;
			};
		reconnect();
		if(parseNow){parseInput(dn);}
	}
}});