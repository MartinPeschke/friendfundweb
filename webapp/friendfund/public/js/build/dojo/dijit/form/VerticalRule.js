if(!dojo._hasResource["dijit.form.VerticalRule"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dijit.form.VerticalRule"] = true;
dojo.provide("dijit.form.VerticalRule");
dojo.require("dijit.form.HorizontalRule");


dojo.declare("dijit.form.VerticalRule", dijit.form.HorizontalRule,
{
	// summary:
	//		Hash marks for the `dijit.form.VerticalSlider`

	templateString: '<div class="dijitRuleContainer dijitRuleContainerV"></div>',
	_positionPrefix: '<div class="dijitRuleMark dijitRuleMarkV" style="top:',

/*=====
	// container: String
	//		This is either "leftDecoration" or "rightDecoration",
	//		to indicate whether this rule goes to the left or to the right of the slider.
	//		Note that on RTL system, "leftDecoration" would actually go to the right, and vice-versa.
	container: "",
=====*/

	// Overrides HorizontalRule._isHorizontal
	_isHorizontal: false

});

}
