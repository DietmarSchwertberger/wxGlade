"""\
Lisp generator functions for wxSplitterWindow objects

@copyright: 2002-2004 D. H. aka crazyinsomniac on sourceforge
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common


class LispSplitterWindowGenerator:
    new_signature = [
        '$parent', '$id', '$pos', '$size', '$style', '$name'
    ]

    def get_code(self, window):
        codegen = common.code_writers['lisp']
        prop = window.properties
        id_name, id = codegen.generate_code_id(window)

        if not window.parent.is_toplevel:
            parent = '(slot-%s obj)' % window.parent.name
        else:
            parent = '(slot-top-window obj)'

        if window.is_toplevel:
            l = []
            if id_name: l.append(id_name)

            l.append('(setf (slot-%s obj) (wxSplitterWindow_Create %s %s))\n' %
                     (window.name, parent,id))
            return l, [], []

        style = prop.get("style")
        if not( style and style != 'wxSP_3D' ): # default style
            style = ''
        else:
            style = codegen.cn_f(style)

        init = []
        if id_name: init.append(id_name)

        init.append('(setf (slot-%s obj) (wxSplitterWindow_Create %s %s -1 -1 -1 -1 %s))\n'
                    % (window.name, parent, id, style))

        props_buf = codegen.generate_common_properties(window)

        layout_buf = []
        win_1 = prop.get('window_1')
        win_2 = prop.get('window_2')
        orientation = prop.get('orientation', 'wxSPLIT_VERTICAL')

        if win_1 and win_2:
            sash_pos = prop.get('sash_pos', '')

            if orientation == 'wxSPLIT_VERTICAL':
                f_name = 'SplitVertically'
            else:
                f_name = 'SplitHorizontally'

            layout_buf.append('(%s %s %s %s %s)\n'
                % (f_name, window.name, win_1, win_2, sash_pos))
        else:
            def add_sub(win):
                layout_buf.append('(wxSplitterWindow_SetSplitMode (slot-%s obj) %s)\n'
                                  % (window.name, orientation))
                layout_buf.append('(wxSplitterWindow_Initialize (slot-%s obj) %s)\n'
                                  % (window.name, win))
            if win_1:
                add_sub(win_1)
            elif win_2:
                add_sub(win_2)

        return init, props_buf, layout_buf


    def get_layout_code(self, obj):
        codegen = common.code_writers['lisp']
        props_buf = []
        prop = obj.properties
        orientation = prop.get('orientation', 'wxSPLIT_VERTICAL')

        win_1 = prop.get('window_1')
        win_2 = prop.get('window_2')

        if win_1 and win_2:
            sash_pos = prop.get('sash_pos', '')

            if orientation == 'wxSPLIT_VERTICAL':
                f_name = 'SplitVertically'
            else:
                f_name = 'SplitHorizontally'

            props_buf.append('$self->%s($self->{%s}, $self->{%s}, %s);\n' %
                             (f_name, win_1, win_2, sash_pos))
        else:
            def add_sub(win):
                props_buf.append('(wxSplitterWindow_SetSplitMode (slot-%s obj) %s)\n' %
                                 (obj.name,orientation))
                props_buf.append('(wxSplitterWindow_Initialize (slot-%s obj) %s)\n' %
                                 (obj.name,win))
            if win_1:
                add_sub(win_1)
            elif win_2:
                add_sub(win_2)

        return props_buf    

# end of class LispSplitterWindowGenerator


def initialize():
    klass = 'wxSplitterWindow'
    common.class_names['EditSplitterWindow'] = klass
    common.class_names['SplitterPane'] = 'wxPanel'
    common.toplevels['EditSplitterWindow'] = 1
    common.toplevels['SplitterPane'] = 1
    common.register('lisp', klass, LispSplitterWindowGenerator())
