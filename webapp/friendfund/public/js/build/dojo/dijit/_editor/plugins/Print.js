if(!dojo._hasResource["dijit._editor.plugins.Print"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dijit._editor.plugins.Print"] = true;
dojo.provide("dijit._editor.plugins.Print");
dojo.require("dijit._editor._Plugin");
dojo.require("dijit.form.Button");
dojo.require("dojo.i18n");
dojo.requireLocalization("dijit._editor", "commands");


dojo.declare("dijit._editor.plugins.Print",dijit._editor._Plugin,{
	// summary:
	//		This plugin provides Print cabability to the editor.  When
	//		clicked, the document in the editor frame will be printed.

	_initButton: function(){
		// summary:
		//		Over-ride for creation of the Print button.
		var strings = dojo.i18n.getLocalization("dijit._editor", "commands"),
			editor = this.editor;
		this.button = new dijit.form.Button({
			label: strings["print"],
			dir: editor.dir,
			lang: editor.lang,
			showLabel: false,
			iconClass: this.iconClassPrefix + " " + this.iconClassPrefix + "Print",
			tabIndex: "-1",
			onClick: dojo.hitch(this, "_print")
		});
	},

	setEditor: function(/*dijit.Editor*/ editor){
		// summary:
		//		Tell the plugin which Editor it is associated with.
		// editor: Object
		//		The editor object to attach the print capability to.
		this.editor = editor;
		this._initButton();

		// Set up a check that we have a print function
		// and disable button if we do not.
		this.editor.onLoadDeferred.addCallback(
			dojo.hitch(this, function(){
				if(!this.editor.iframe.contentWindow["print"]){
					this.button.set("disabled", true);
				}
			})
		);
	},

	updateState: function(){
		// summary:
		//		Over-ride for button state control for disabled to work.
		var disabled = this.get("disabled");
		if(!this.editor.iframe.contentWindow["print"]){
			disabled = true;
		}
		this.button.set("disabled", disabled);
	},

	_print: function(){
		// summary:
		//		Function to trigger printing of the editor document
		// tags:
		//		private
		var edFrame = this.editor.iframe;
		if(edFrame.contentWindow["print"]){
			// IE requires the frame to be focused for
			// print to work, but since this is okay for all
			// no special casing.
			if(!dojo.isOpera && !dojo.isChrome){
				dijit.focus(edFrame);
				edFrame.contentWindow.print();
			}else{
				// Neither Opera nor Chrome 3 et you print single frames.
				// So, open a new 'window', print it, and close it.
				// Also, can't use size 0x0, have to use 1x1
				var edDoc = this.editor.document;
				var content = this.editor.get("value");
				content = "<html><head><meta http-equiv='Content-Type' " +
					"content='text/html; charset='UTF-8'></head><body>" +
					content + "</body></html>";
				var win = window.open("javascript: ''",
					"",
					"status=0,menubar=0,location=0,toolbar=0," +
					"width=1,height=1,resizable=0,scrollbars=0");
				win.document.open();
				win.document.write(content);
				win.document.close();
				var styles = [];
				var styleNodes = edDoc.getElementsByTagName("style");
				if(styleNodes){
					// Clone over any editor view styles, since we can't print the iframe
					// directly.
					var i;
					for(i = 0; i < styleNodes.length; i++){
						var style = styleNodes[i].innerHTML;
						var sNode = win.document.createElement("style");
						sNode.appendChild(win.document.createTextNode(style));
						win.document.getElementsByTagName("head")[0].appendChild(sNode);
					}
				}
				win.print();
				win.close();
			}
		}
	}
});

// Register this plugin.
dojo.subscribe(dijit._scopeName + ".Editor.getPlugin",null,function(o){
	if(o.plugin){ return; }
	var name = o.args.name.toLowerCase();
	if(name === "print"){
		o.plugin = new dijit._editor.plugins.Print({command: "print"});
	}
});

}
