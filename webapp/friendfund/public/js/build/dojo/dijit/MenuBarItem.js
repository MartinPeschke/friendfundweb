if(!dojo._hasResource["dijit.MenuBarItem"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dijit.MenuBarItem"] = true;
dojo.provide("dijit.MenuBarItem");
dojo.require("dijit.MenuItem");


dojo.declare("dijit._MenuBarItemMixin", null, {
	templateString: dojo.cache("dijit", "templates/MenuBarItem.html", "<div class=\"dijitReset dijitInline dijitMenuItem dijitMenuItemLabel\" dojoAttachPoint=\"focusNode\" role=\"menuitem\" tabIndex=\"-1\"\n\t\tdojoAttachEvent=\"onmouseenter:_onHover,onmouseleave:_onUnhover,ondijitclick:_onClick\">\n\t<span dojoAttachPoint=\"containerNode\"></span>\n</div>\n"),

	// overriding attributeMap because we don't have icon
	attributeMap: dojo.delegate(dijit._Widget.prototype.attributeMap, {
		label: { node: "containerNode", type: "innerHTML" }
	})
});

dojo.declare("dijit.MenuBarItem", [dijit.MenuItem, dijit._MenuBarItemMixin], {
	// summary:
	//		Item in a MenuBar that's clickable, and doesn't spawn a submenu when pressed (or hovered)

});

}
