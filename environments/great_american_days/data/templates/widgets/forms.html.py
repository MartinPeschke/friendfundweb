# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291204359.013062
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/widgets/forms.html'
_template_uri=u'/widgets/forms.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['expression_quote', 'black_input', 'input_checked', 'input_text', 'black_search_text', 'black_input_select', 'button_submitlink', 'input_checkbox', 'input_textarea', 'input_select', 'black_input_text', 'black_input_datepicker', 'black_submitlink', 'error_msg', 'input_selected', 'black_submitlink_back']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        x = context.get('x', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'\n\n')
        # SOURCE LINE 7
        __M_writer(u'\n\n')
        # SOURCE LINE 14
        __M_writer(u'\n\n')
        # SOURCE LINE 20
        __M_writer(u'\n\n\n')
        # SOURCE LINE 28
        __M_writer(u'\n\n\n')
        # SOURCE LINE 50
        __M_writer(u'\n\n\n')
        # SOURCE LINE 64
        __M_writer(u'\n\n\n')
        # SOURCE LINE 77
        __M_writer(u'\n\n\n')
        # SOURCE LINE 95
        __M_writer(u'\n\n\n')
        # SOURCE LINE 105
        __M_writer(u'\n\n\n\n')
        # SOURCE LINE 126
        __M_writer(u'\n\n\n')
        # SOURCE LINE 139
        __M_writer(u'\n\n\n\n')
        # SOURCE LINE 143
        __M_writer(u'\n')
        # SOURCE LINE 144
        __M_writer(u'\n\n')
        # SOURCE LINE 146
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_expression_quote(context,expr,tagname,value=None):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 146
        __M_writer((expr and '%s="%s"'%(tagname, value or tagname) or ''))
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_black_input(context,id,name,label=None,type='text',value='',required=False,width='100',leftbrackettag=None,leftbracketclass=None,defaulting=True,default=None,baseclass=None):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 31
        __M_writer(u'\n\t<div class="inputcontainer">\n')
        # SOURCE LINE 33
        if label is not None:
            # SOURCE LINE 34
            __M_writer(u'\t\t\t<label class="black_labeled_container" for="')
            __M_writer(escape(id))
            __M_writer(u'">')
            __M_writer(escape(label))
            __M_writer(escape(required and "(*)" or ""))
            __M_writer(u'</label>\n')
            pass
        # SOURCE LINE 36
        __M_writer(u'\t\t<div class="black_labeled_container')
        __M_writer(escape(baseclass and '_%s'%baseclass or ''))
        __M_writer(u'" style="width:')
        __M_writer(escape(width))
        __M_writer(u'px;" id="')
        __M_writer(escape(id))
        __M_writer(u'_container">\n\t\t\t<div class="right_bracket">&nbsp;</div>\n\t\t\t<')
        # SOURCE LINE 38
        __M_writer(escape(leftbrackettag))
        __M_writer(u' class="')
        __M_writer(escape(leftbracketclass))
        __M_writer(u'">&nbsp;</')
        __M_writer(escape(leftbrackettag))
        __M_writer(u'>\n\t\t\t<input class="black_labeled_input')
        # SOURCE LINE 39
        __M_writer(escape((not value and defaulting) and ' default' or ''))
        __M_writer(u'"\n')
        # SOURCE LINE 40
        if defaulting and default:
            # SOURCE LINE 41
            __M_writer(u'\t\t\t\t\t\t_default_text="')
            __M_writer(escape(default))
            __M_writer(u'"\n')
            pass
        # SOURCE LINE 43
        __M_writer(u'\t\t\t\t\tstyle="width:')
        __M_writer(escape(width))
        __M_writer(u'px;" \n\t\t\t\t\ttype="')
        # SOURCE LINE 44
        __M_writer(escape(type))
        __M_writer(u'" \n\t\t\t\t\tid="')
        # SOURCE LINE 45
        __M_writer(escape(id))
        __M_writer(u'" \n\t\t\t\t\tname="')
        # SOURCE LINE 46
        __M_writer(escape(name))
        __M_writer(u'" \n\t\t\t\t\tvalue="')
        # SOURCE LINE 47
        __M_writer(escape(value or default))
        __M_writer(u'"/>\n\t\t</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_input_checked(context,group,name,value,default=False):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        def expression_quote(expr,tagname,value=None):
            return render_expression_quote(context,expr,tagname,value)
        dict = context.get('dict', UNDEFINED)
        getattr = context.get('getattr', UNDEFINED)
        hasattr = context.get('hasattr', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 144
        __M_writer(expression_quote((name not in getattr(c, "%s_values"%group,dict()) and default) or hasattr(c, "%s_values"%group) and getattr(c, "%s_values"%group).get(name, "") == value, "checked"))
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_input_text(context,group,name,label,type='text',with_value=True,with_errors=True,required=False,_classes=[],_labelclasses=[],_inputclasses=[],attribs=[]):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        h = context.get('h', UNDEFINED)
        k = context.get('k', UNDEFINED)
        float = context.get('float', UNDEFINED)
        getattr = context.get('getattr', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        unicode = context.get('unicode', UNDEFINED)
        v = context.get('v', UNDEFINED)
        isinstance = context.get('isinstance', UNDEFINED)
        hasattr = context.get('hasattr', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 80
        __M_writer(u'\n')
        # SOURCE LINE 81

        value = getattr(c, "%s_values"%group, dict()).get(name, "")
        if isinstance(value, float):
                value = h.format_number(value)
        
        
        # SOURCE LINE 85
        __M_writer(u'\n\t<label for="')
        # SOURCE LINE 86
        __M_writer(escape(group))
        __M_writer(u'_')
        __M_writer(escape(name))
        __M_writer(u'" class="')
        __M_writer(escape(' '.join(_classes+_labelclasses)))
        __M_writer(u'">')
        __M_writer(escape(label))
        __M_writer(escape(required and "(*)" or ""))
        __M_writer(u'</label>\n\t<input type="')
        # SOURCE LINE 87
        __M_writer(escape(type))
        __M_writer(u'" id="')
        __M_writer(escape(group))
        __M_writer(u'_')
        __M_writer(escape(name))
        __M_writer(u'" name="')
        __M_writer(escape(group))
        __M_writer(u'.')
        __M_writer(escape(name))
        __M_writer(u'"\n\t\t\t')
        # SOURCE LINE 88
        __M_writer(attribs and ' '.join('%s="%s"'%(k,v) for k,v in attribs) or '')
        __M_writer(u'\n\t\t\tvalue="')
        # SOURCE LINE 89
        __M_writer(escape(value))
        __M_writer(u'"\n\t\t\tclass="')
        # SOURCE LINE 90
        __M_writer(escape((name in getattr(c, "%s_errors"%group, dict())) and 'error' or ''))
        __M_writer(u' ')
        __M_writer(escape(' '.join(_classes+_inputclasses)))
        __M_writer(u'"\n\t\t/>\n')
        # SOURCE LINE 92
        if with_errors and hasattr(c, "%s_errors"%group) and getattr(c, "%s_errors"%group).get(name, None):
            # SOURCE LINE 93
            __M_writer(u'\t\t\t<div class="error_message error_input ')
            __M_writer(escape(' '.join(_classes)))
            __M_writer(u'">')
            __M_writer(unicode(getattr(c, "%s_errors"%group).get(name, "")))
            __M_writer(u'</div>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_black_search_text(context,id,name,label=None,type='text',value='',required=False,width='100',defaulting=True,default=None):
    context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 5
        __M_writer(u'\n\t')
        # SOURCE LINE 6
        __M_writer(self.black_input(id, name, label, type, value, required, width, leftbrackettag='div', leftbracketclass='left_button_search', defaulting=defaulting, default=default,baseclass='big'))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_black_input_select(context,id,name,choices,choicegetter=lambda x: (x[0], x[1]),width='280'):
    context.caller_stack._push_frame()
    try:
        map = context.get('map', UNDEFINED)
        x = context.get('x', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 67
        __M_writer(u'\n<div class="black_labeled_container" style="overflow: hidden; width: 280px; padding: 0px 10px;">\n\t<div style="left:0px" class="left_bracket">&nbsp;</div>\n\t<select id="')
        # SOURCE LINE 70
        __M_writer(escape(id))
        __M_writer(u'" name="')
        __M_writer(escape(name))
        __M_writer(u'" class="black_labeled_input"> \n')
        # SOURCE LINE 71
        for key, val in map(choicegetter, choices): 
            # SOURCE LINE 72
            __M_writer(u'\t\t\t\t<option value="')
            __M_writer(escape(key))
            __M_writer(u'">')
            __M_writer(escape(val))
            __M_writer(u'</option>\n')
            pass
        # SOURCE LINE 74
        __M_writer(u'\t</select>\n\t<a style="right:6px;" class="button_open_down" onclick="console.log(this)" href="#">&nbsp;</a>\n</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_button_submitlink(context,label,args,classes='',href=None):
    context.caller_stack._push_frame()
    try:
        k = context.get('k', UNDEFINED)
        v = context.get('v', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 16
        __M_writer(u'\n<a class="button_labeled_container ')
        # SOURCE LINE 17
        __M_writer(escape(classes))
        __M_writer(u'" ')
        __M_writer(' '.join(['%s="%s"'%(k,v) for k,v in args]))
        __M_writer(u'  ')
        __M_writer((href and 'href="%s"'%href or ''))
        __M_writer(u'>\n<div class="right_bracket"></div>')
        # SOURCE LINE 18
        __M_writer(escape(label))
        __M_writer(u'\n</a>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_input_checkbox(context,group,name,label,value,with_value=True,required=False):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        self = context.get('self', UNDEFINED)
        hasattr = context.get('hasattr', UNDEFINED)
        getattr = context.get('getattr', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 129
        __M_writer(u'\n\t<label for="')
        # SOURCE LINE 130
        __M_writer(escape(group))
        __M_writer(u'_')
        __M_writer(escape(name))
        __M_writer(u'">')
        __M_writer(escape(label))
        __M_writer(escape(required and "(*)" or ""))
        __M_writer(u'</label>\n\t<input type="checkbox" id="')
        # SOURCE LINE 131
        __M_writer(escape(group))
        __M_writer(u'_')
        __M_writer(escape(name))
        __M_writer(u'" name="')
        __M_writer(escape(group))
        __M_writer(u'.')
        __M_writer(escape(name))
        __M_writer(u'" value="')
        __M_writer(escape(value))
        __M_writer(u'"\n')
        # SOURCE LINE 132
        if with_value and hasattr(c, "%s_values"%group):
            # SOURCE LINE 133
            __M_writer(u'\t\t\t')
            __M_writer(escape(self.input_checked(group, name, value)))
            __M_writer(u'\n')
            pass
        # SOURCE LINE 135
        __M_writer(u'\t\t/>\n')
        # SOURCE LINE 136
        if hasattr(c, "%s_errors"%group) and getattr(c, "%s_errors"%group).get(name, None):
            # SOURCE LINE 137
            __M_writer(u'\t\t\t<div class="error_message error_checkbox">')
            __M_writer(escape(getattr(c, "%s_errors"%group).get(name, "")))
            __M_writer(u'</div>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_input_textarea(context,group,name,label,with_value=True,with_errors=True):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        getattr = context.get('getattr', UNDEFINED)
        hasattr = context.get('hasattr', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 98
        __M_writer(u'\n\t<label for="')
        # SOURCE LINE 99
        __M_writer(escape(group))
        __M_writer(u'_')
        __M_writer(escape(name))
        __M_writer(u'">')
        __M_writer(escape(label))
        __M_writer(u'</label>\n\t<textarea id="')
        # SOURCE LINE 100
        __M_writer(escape(group))
        __M_writer(u'_')
        __M_writer(escape(name))
        __M_writer(u'" name="')
        __M_writer(escape(group))
        __M_writer(u'.')
        __M_writer(escape(name))
        __M_writer(u'" \n\t\t>')
        # SOURCE LINE 101
        __M_writer(escape(with_value and getattr(c, "%s_values"%group, "").get(name, "")))
        __M_writer(u'</textarea>\n')
        # SOURCE LINE 102
        if with_errors and hasattr(c, "%s_errors"%group) and getattr(c, "%s_errors"%group).get(name, None):
            # SOURCE LINE 103
            __M_writer(u'\t\t\t<div class="error_message error_textarea">')
            __M_writer(escape(getattr(c, "%s_errors"%group).get(name, "")))
            __M_writer(u'</div>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_input_select(context,group,name,label,choices,choicegetter=lambda x: (x[0], x[1]),with_value=True,with_errors=True,required=False):
    context.caller_stack._push_frame()
    try:
        map = context.get('map', UNDEFINED)
        c = context.get('c', UNDEFINED)
        getattr = context.get('getattr', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        unicode = context.get('unicode', UNDEFINED)
        x = context.get('x', UNDEFINED)
        hasattr = context.get('hasattr', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 109
        __M_writer(u'\n')
        # SOURCE LINE 110
        if label:
            # SOURCE LINE 111
            __M_writer(u'\t\t<label for="')
            __M_writer(escape(group))
            __M_writer(u'_')
            __M_writer(escape(name))
            __M_writer(u'">')
            __M_writer(escape(label))
            __M_writer(escape(required and "(*)" or ""))
            __M_writer(u'</label>\n')
            pass
        # SOURCE LINE 113
        __M_writer(u'\t<select id="')
        __M_writer(escape(group))
        __M_writer(u'_')
        __M_writer(escape(name))
        __M_writer(u'" name="')
        __M_writer(escape(group))
        __M_writer(u'.')
        __M_writer(escape(name))
        __M_writer(u'" class="')
        __M_writer(escape((name in getattr(c, "%s_errors"%group, dict())) and 'error' or ''))
        __M_writer(u'"> \n')
        # SOURCE LINE 114
        for key, val in map(choicegetter, choices): 
            # SOURCE LINE 115
            if with_value and hasattr(c, "%s_values"%group):
                # SOURCE LINE 116
                __M_writer(u'\t\t\t\t<option value="')
                __M_writer(escape(key))
                __M_writer(u'" \n\t\t\t\t\t')
                # SOURCE LINE 117
                __M_writer(escape(getattr(c, "%s_values"%group).get(name, "") == unicode(key) and 'selected="selected"' or ' '))
                __M_writer(u'>')
                __M_writer(escape(val))
                __M_writer(u'</option>\n')
                # SOURCE LINE 118
            else:
                # SOURCE LINE 119
                __M_writer(u'\t\t\t\t<option value="')
                __M_writer(escape(key))
                __M_writer(u'">')
                __M_writer(escape(val))
                __M_writer(u'</option>\n')
                pass
            pass
        # SOURCE LINE 122
        __M_writer(u'\t\t</select>\n')
        # SOURCE LINE 123
        if hasattr(c, "%s_errors"%group) and getattr(c, "%s_errors"%group).get(name, None):
            # SOURCE LINE 124
            __M_writer(u'\t\t\t<div class="error_message error_select">')
            __M_writer(escape(getattr(c, "%s_errors"%group).get(name, "")))
            __M_writer(u'</div>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_black_input_text(context,id,name,label=None,type='text',value='',required=False,width='100',defaulting=True,default=None):
    context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\t')
        # SOURCE LINE 2
        __M_writer(self.black_input(id, name, label, type, value, required, width, leftbrackettag='div', leftbracketclass='left_bracket', defaulting=defaulting, default=default))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_black_input_datepicker(context,id,name,value,label=None,width='100',args=[]):
    context.caller_stack._push_frame()
    try:
        k = context.get('k', UNDEFINED)
        v = context.get('v', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 53
        __M_writer(u'\n\t<div class="black_labeled_container right" style="width:')
        # SOURCE LINE 54
        __M_writer(escape(width))
        __M_writer(u'px;">\n\t\t<div class="left_bracket">&nbsp;</div>\n\t\t<div class="black_labeled_input" style="width:')
        # SOURCE LINE 56
        __M_writer(escape(width))
        __M_writer(u'px;">\n\t\t<div id="')
        # SOURCE LINE 57
        __M_writer(escape(id))
        __M_writer(u'" jsid="')
        __M_writer(escape(id))
        __M_writer(u'" type="text" name="')
        __M_writer(escape(name))
        __M_writer(u'" value="')
        __M_writer(escape(value))
        __M_writer(u'" dojoType="dijit.form.DateTextBox" ')
        __M_writer(' '.join(['%s="%s"'%(k,v) for k,v in args]))
        __M_writer(u'></div>\n\t\t</div>\n\t\t<a class="button_open_down" id="datepicker_opener">&nbsp;</a>\n\t</div>\n')
        # SOURCE LINE 61
        if label:
            # SOURCE LINE 62
            __M_writer(u'\t\t<label class="black_labeled_container right" for="')
            __M_writer(escape(id))
            __M_writer(u'">')
            __M_writer(escape(label))
            __M_writer(u'</label>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_black_submitlink(context,label,args,classes='',href=None):
    context.caller_stack._push_frame()
    try:
        k = context.get('k', UNDEFINED)
        v = context.get('v', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 9
        __M_writer(u'\n<a class="black_labeled_container ')
        # SOURCE LINE 10
        __M_writer(escape(classes))
        __M_writer(u'" ')
        __M_writer(' '.join(['%s="%s"'%(k,v) for k,v in args]))
        __M_writer(u' ')
        __M_writer((href and 'href="%s"'%href or ''))
        __M_writer(u'>\n<div class="right_bracket">&nbsp;</div>\n<div class="left_bracket">&nbsp;</div>\n')
        # SOURCE LINE 13
        __M_writer(escape(label))
        __M_writer(u'</a>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_error_msg(context,group,name,msg=None,type=''):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        getattr = context.get('getattr', UNDEFINED)
        hasattr = context.get('hasattr', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 148
        __M_writer(u'\n')
        # SOURCE LINE 149
        if not msg and hasattr(c, "%s_errors"%group):
            # SOURCE LINE 150
            __M_writer(u'\t\t\t<div class="error_message ')
            __M_writer(escape(type))
            __M_writer(u'">\n\t\t\t\t')
            # SOURCE LINE 151
            __M_writer(escape(getattr(c, "%s_errors"%group).get(name, "")))
            __M_writer(u'\n\t\t\t</div>\n')
            # SOURCE LINE 153
        else:
            # SOURCE LINE 154
            __M_writer(u'\t\t\t<div class="error_message ')
            __M_writer(escape(type))
            __M_writer(u'">\n\t\t\t\t')
            # SOURCE LINE 155
            __M_writer(escape(msg))
            __M_writer(u'\n\t\t\t</div>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_input_selected(context,group,name,value):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        def expression_quote(expr,tagname,value=None):
            return render_expression_quote(context,expr,tagname,value)
        getattr = context.get('getattr', UNDEFINED)
        hasattr = context.get('hasattr', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 143
        __M_writer(expression_quote(hasattr(c, "%s_values"%group) and getattr(c, "%s_values"%group).get(name, "") == value, "selected"))
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_black_submitlink_back(context,label,args,classes='',href=None):
    context.caller_stack._push_frame()
    try:
        k = context.get('k', UNDEFINED)
        v = context.get('v', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 23
        __M_writer(u'\n<a class="black_labeled_container ')
        # SOURCE LINE 24
        __M_writer(escape(classes))
        __M_writer(u'" ')
        __M_writer(' '.join(['%s="%s"'%(k,v) for k,v in args]))
        __M_writer(u'  ')
        __M_writer((href and 'href="%s"'%href or ''))
        __M_writer(u'>\n<div class="right_bracket_back">&nbsp;</div>\n<div class="left_bracket_back">&nbsp;</div>\n')
        # SOURCE LINE 27
        __M_writer(escape(label))
        __M_writer(u'</a>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


