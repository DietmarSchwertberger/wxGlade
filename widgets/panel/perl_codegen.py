# perl_codegen.py : perl generator functions for wxPanel objects
# $Id: perl_codegen.py,v 1.1 2003/06/23 21:29:31 crazyinsomniac Exp $
#
# Copyright (c) 2002-2003 D.H. aka crazyinsomniac on sourceforge.net
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

import common

class PerlCodeGenerator:
    def get_code(self, panel):
        pygen = common.code_writers['perl']
        prop = panel.properties
        id_name, id = pygen.generate_code_id(panel)
        if not panel.parent.is_toplevel: parent = '$self->{%s}' % panel.parent.name
        else: parent = '$self'
        if panel.is_toplevel:
            l = []
            if id_name: l.append(id_name)
            l.append('$self->{%s} = %s->new(%s, %s);\n' %
                     (panel.name, panel.klass.replace('wx','Wx::',1), parent, id))
            return l, [], []
        init = []
        if id_name: init.append(id_name)
        style = prop.get("style", 'wxTAB_TRAVERSAL')
        if style != 'wxTAB_TRAVERSAL': style = "%s" % style
        else: style = ''
        init.append('$self->{%s} = Wx::Panel->new(%s, %s, wxDefaultPosition, wxDefaultSize, %s);\n' %
                    (panel.name, parent, id, style))
        props_buf = pygen.generate_common_properties(panel)
        return init, props_buf, []

# end of class PerlCodeGenerator


def initialize():
    common.class_names['EditPanel'] = 'wxPanel'
    common.class_names['EditTopLevelPanel'] = 'wxPanel'
    common.toplevels['EditPanel'] = 1
    common.toplevels['EditTopLevelPanel'] = 1

    plgen = common.code_writers.get('perl')
    if plgen:
        plgen.add_widget_handler('wxPanel', PerlCodeGenerator())
