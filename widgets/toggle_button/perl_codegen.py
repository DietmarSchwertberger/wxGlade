# perl_codegen.py : perl generator functions for wxToggleButton objects
# $Id: perl_codegen.py,v 1.2 2003/06/25 23:51:27 crazyinsomniac Exp $
#
# Copyright (c) 2002-2003 D.H. aka crazyinsomniac on sourceforge.net
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

import common

class PerlCodeGenerator:
    def get_code(self, obj):
        init = []
        plgen = common.code_writers['perl']
        prop = obj.properties
        id_name, id = plgen.generate_code_id(obj)
        label = plgen.quote_str(prop.get('label', ''))
        if not obj.parent.is_toplevel:
            parent = '$self->{%s}' % obj.parent.name
        else:
            parent = '$self'

        if id_name: init.append(id_name)

        init.append('$self->{%s} = %s->new(%s, %s, %s);\n' %
            (obj.name, obj.klass.replace('wx','Wx::',1), parent, id, label))
        props_buf = plgen.generate_common_properties(obj)

        value = prop.get('value')
        if value:
            props_buf.append('$self->{%s}->SetValue(%s);\n'
                % (obj.name, value))
        return init, props_buf, []

# end of class PerlCodeGenerator


def initialize():
    common.class_names['EditToggleButton'] = 'wxToggleButton'
    plgen = common.code_writers.get('perl')

    if plgen:
        plgen.add_widget_handler('wxToggleButton', PerlCodeGenerator())

