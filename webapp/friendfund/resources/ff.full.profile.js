dependencies = {
	stripConsole: "normal",
	layers: [
		{
			name: "dojo.js",
			dependencies: ["dojo._base","dojo.dojo", "dojo.html", "dojo.parser", "dojo.fx", "dojo.fx.Toggler", "dojo.fx.easing", "dojo.string","dojo.io.iframe","ff.t", "ff.w", "ff.io", "ff.auth", "ff.parser", "ff.Popup"]
		},
		{
			name: "editor.js",
			layerDependencies: ["dojo.js"],
			dependencies:[
				"dojo.window"
				,"dijit._editor"
				,"dijit.Editor"
				,"dojo.nls.editor_en"
				,"dojo.nls.editor_de"
				,"dojo.nls.editor_es"
				,"dojo.i18n"
				,"dojo.cldr"
				,"dijit._editor.plugins.FontChoice"
				,"dijit._editor.plugins.TextColor"
				,"dijit._editor.plugins.LinkDialog"
				,"dijit._editor.plugins.ViewSource"
			]
		},{
			name: "friendfund.js",
			copyrightFile: "copyright.txt",
			layerDependencies: ["dojo.js", "editor.js"],
			dependencies: [
				"friendfund.FriendSelector"
				,"friendfund.InvitePage"
				,"friendfund.PartnerPage"
			]
		}
	],

	prefixes: [
		[ "dijit", "../dijit", "copyright.txt" ],
		[ "friendfund", "../../../public/js/friendfund", "copyright.txt"],
		[ "ff", "../../../public/js/ff", "copyright.txt"]
	]
}
