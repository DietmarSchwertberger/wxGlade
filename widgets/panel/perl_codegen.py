# perl_codegen.py : perl generator functions for wxPanel objects
# $Id: perl_codegen.py,v 1.5 2003/07/09 09:23:59 crazyinsomniac Exp $
#
# Copyright (c) 2002-2003 D.H. aka crazyinsomniac on sourceforge.net
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

import common

class PerlCodeGenerator:
#wxPanel(  parent, id, pos , size , style ,   name )
#wxScrolledWindow(parent, id, pos, size, style, name )
    new_signature = [
        '$parent', '$id', '$pos', '$size', '$style', '$name'
    ]

    def get_code(self, panel):
        plgen = common.code_writers['perl']
        prop = panel.properties
        try:
            scrollable = int(prop['scrollable'])
        except:
            scrollable = False

        id_name, id = plgen.generate_code_id(panel)
        if not panel.parent.is_toplevel:
            parent = '$self->{%s}' % panel.parent.name
        else:
            parent = '$self'

        if panel.is_toplevel:
            l = []
            if id_name: l.append(id_name)
            l.append('$self->{%s} = %s->new(%s, %s);\n' %
                 (panel.name, panel.klass.replace('wx','Wx::',1), parent, id))
            return l, [], []

        init = []
        if id_name: init.append(id_name)
        style = prop.get("style", 'wxTAB_TRAVERSAL')
        if not( scrollable or style != 'wxTAB_TRAVERSAL' ):
            style = ''
        if scrollable:
            klass = 'Wx::ScrolledWindow'
        else:
            klass = 'Wx::Panel'

        init.append('$self->{%s} = %s->new(%s, %s, \
wxDefaultPosition, wxDefaultSize, %s);\n'
            % (panel.name, klass, parent, id, style))

        props_buf = plgen.generate_common_properties(panel)
        if scrollable:
            sr = prop.get('scroll_rate', '0, 0')
            props_buf.append('$self->{%s}->SetScrollRate(%s);\n'
                % (panel.name, sr))
        return init, props_buf, []

    def get_properties_code(self, obj):
        plgen = common.code_writers['perl']
        prop = obj.properties
        try:
            scrollable = int(prop['scrollable'])
        except:
            scrollable = False

        props_buf = plgen.generate_common_properties(obj)
        if scrollable:
            sr = prop.get('scroll_rate', '0, 0')
            props_buf.append('$self->SetScrollRate(%s);\n' % sr)
        return props_buf

# end of class PerlCodeGenerator


def initialize():
    common.class_names['EditPanel'] = 'wxPanel'
    common.class_names['EditTopLevelPanel'] = 'wxPanel'
    common.toplevels['EditPanel'] = 1
    common.toplevels['EditTopLevelPanel'] = 1

    plgen = common.code_writers.get('perl')
    if plgen:
        plgen.add_widget_handler('wxPanel', PerlCodeGenerator())
        plgen.add_widget_handler('wxScrolledWindow', PerlCodeGenerator())