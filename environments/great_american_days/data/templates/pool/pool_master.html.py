# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291292196.954324
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/pool/pool_master.html'
_template_uri=u'/pool/pool_master.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['title']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 2
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'../widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'../layout_layer.html', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        len = context.get('len', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n\n')
        # SOURCE LINE 4
        __M_writer(u'\n\n')
        # SOURCE LINE 6

        locals = {"amount_contributed":h.format_currency(c.pool.get_total_contrib_float(), c.pool.currency),
                        "amount_left":c.pool.is_pending() and '???' or h.format_currency(c.pool.get_amount_left(), c.pool.currency),
                        "end_date":h.format_date(c.pool.occasion.date, format="long"),
                        "number_contributors": c.pool.get_number_of_contributors(),
                        "number_invitees":len(c.pool.invitees)+1,
                        "receiver_first_name":c.pool.receiver.name.split()[0],
                        "receiver_name":c.pool.receiver.name
                        }
        if c.pool.is_pending():
                locals['progress'] = 0
                locals["selector_name"] = c.pool.selector and c.pool.selector.name or _("POOL_PAGE_SELECTOR_Someone")
        else:
                locals['progress'] = (850 * (c.pool.get_total_contrib_float() / c.pool.product.get_price_float())) 
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['locals'] if __M_key in __M_locals_builtin_stored]))
        # SOURCE LINE 20
        __M_writer(u'\n\n')
        # SOURCE LINE 22
        __M_writer(escape(self.admin_slogan(locals)))
        __M_writer(u'\n')
        # SOURCE LINE 23
        __M_writer(escape(self.pool_pool_panel(locals)))
        __M_writer(u'\n')
        # SOURCE LINE 24
        __M_writer(escape(self.social_tools(locals)))
        __M_writer(u'\n')
        # SOURCE LINE 25
        __M_writer(escape(self.contributors(locals)))
        __M_writer(u'\n')
        # SOURCE LINE 26
        __M_writer(escape(self.fundchat(locals)))
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 4
        __M_writer(escape(_("POOL_PAGE__TITLE_Pool")))
        return ''
    finally:
        context.caller_stack._pop_frame()


