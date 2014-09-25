"""\
Lisp generator functions for wxNotebook objects

@copyright: 2002-2004 D.H. aka crazyinsomniac on sourceforge.net
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen
from codegen import TabsCodeHandler


class LispNotebookGenerator(wcodegen.LispWidgetCodeWriter):
    new_signature = [
        '$parent', '$id', '$pos', '$size', '$style', '$name'
    ]

    def get_code(self, window):
        codegen = common.code_writers['lisp']
        prop = window.properties
        id_name, id = codegen.generate_code_id(window)

        layout_props = []
        tabs = prop.get('tabs', [])
        for label, tab_win in tabs:
            tab_win = tab_win.replace('_', '-')
            layout_props.append(
                '(wxNotebook_AddPage (slot-%s obj) (slot-%s obj) %s '
                '1 -1)\n' % (
                    window.name,
                    tab_win,
                    codegen.quote_str(label)
                    )
                )

        if not window.parent.is_toplevel:
            parent = '(slot-%s obj)' % window.parent.name
        else:
            parent = '(slot-top-window obj)'

        if window.is_toplevel:
            l = []
            if id_name:
                l.append(id_name)
            l.append(
                '(setf (slot-%s obj) (wxNotebook_Create %s %s -1 -1 -1 -1 '
                'wxNB_TOP))\n' % (
                    window.name,
                    parent,
                    id
                    )
                )
            return l, [], []

        style = prop.get("style")
        if style:
            style = self.cn_f(style)
        else:
            style = 'wxNB_TOP'

        init = []
        if id_name:
            init.append(id_name)
        init.append(
            '(setf (slot-%s obj) (wxNotebook_Create %s %s '
            '-1 -1 -1 -1 %s))\n' % (
                window.name,
                parent,
                id,
                style
                )
            )

        props_buf = codegen.generate_common_properties(window)
        return init, props_buf, layout_props

    def get_properties_code(self, obj):
        prop = obj.properties
        codegen = common.code_writers['lisp']
        props_buf = []
        tabs = prop.get('tabs', [])
        for label, window in tabs:
            props_buf.append(
                '(wxNotebook_AddPage (slot-%s obj) page %s 1 -1);\n' % (
                    window,
                    codegen.quote_str(label),
                    )
                )
        props_buf.extend(codegen.generate_common_properties(obj))
        return props_buf

# end of class LispNotebookGenerator


def initialize():
    klass = 'wxNotebook'
    common.class_names['EditNotebook'] = klass
    common.class_names['NotebookPane'] = 'wxPanel'
    common.toplevels['EditNotebook'] = 1
    common.toplevels['NotebookPane'] = 1

    common.register('lisp', klass, LispNotebookGenerator(klass),
                    'tabs', TabsCodeHandler, klass)
