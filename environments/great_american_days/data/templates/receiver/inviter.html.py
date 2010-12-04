# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291205917.164607
_template_filename='/home/www-data/ff_dev/friendfund/templates/receiver/inviter.html'
_template_uri='/receiver/inviter.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['networkinviter']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 1
    ns = runtime.Namespace(u'forms', context._clean_inheritance_tokens(), templateuri=u'../widgets/forms.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'forms')] = ns

    # SOURCE LINE 2
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'../widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

    # SOURCE LINE 3
    ns = runtime.Namespace(u'blockrenderer', context._clean_inheritance_tokens(), templateuri=u'../invite/inviter.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'blockrenderer')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        def networkinviter(network_name,friends,mutuals):
            return render_networkinviter(context.locals_(__M_locals),network_name,friends,mutuals)
        blockrenderer = _mako_get_namespace(context, 'blockrenderer')
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n')
        # SOURCE LINE 3
        __M_writer(u'\n\n\n')
        # SOURCE LINE 6
        if c.method == 'facebook':
            # SOURCE LINE 7
            __M_writer(u'\t')
            __M_writer(escape(networkinviter("facebook", c.friends, False)))
            __M_writer(u'\n')
            # SOURCE LINE 8
        elif c.method == 'twitter':
            # SOURCE LINE 9
            __M_writer(u'\t')
            __M_writer(escape(networkinviter("twitter", c.friends, False)))
            __M_writer(u'\n')
            # SOURCE LINE 10
        elif c.method == 'email':
            # SOURCE LINE 11
            __M_writer(u'\t')
            __M_writer(escape(blockrenderer.mailinviter()))
            __M_writer(u'\n')
            pass
        # SOURCE LINE 13
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_networkinviter(context,network_name,friends,mutuals):
    context.caller_stack._push_frame()
    try:
        forms = _mako_get_namespace(context, 'forms')
        html = _mako_get_namespace(context, 'html')
        blockrenderer = _mako_get_namespace(context, 'blockrenderer')
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 14
        __M_writer(u'\n\t<div id="networkinviter_')
        # SOURCE LINE 15
        __M_writer(escape(network_name))
        __M_writer(u'">\n\t<div id="inviteheader" class="receiverselector">\n\t\t')
        # SOURCE LINE 17
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n\t\t<div style="margin: 15px 15px 0 15px; padding: 15px; background: white;">\n\t\t')
        # SOURCE LINE 19
        __M_writer(escape(forms.black_input_text("fb_filter", "fb_filter", label=_("RECEIVER_PANEL_Search your %s friends:") % network_name.title(), default="Name", width=200)))
        __M_writer(u'\n\t\t')
        # SOURCE LINE 20
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n\t\t</div>\n\t</div>\n\t<div id="friend_list" class="fb">\n\t\t')
        # SOURCE LINE 24
        __M_writer(blockrenderer.render_network_friends(friends, mutuals = mutuals, show_birthdays = True, add_label=_("RECEIVER_PANEL_Select")))
        __M_writer(u'\n\t</div>\n\t')
        # SOURCE LINE 26
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


