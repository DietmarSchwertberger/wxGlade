# perl_codegen.py : perl generator functions for wxSlider objects
# $Id: perl_codegen.py,v 1.1 2003/06/23 21:35:10 crazyinsomniac Exp $
#
# Copyright (c) 2002-2003 D.H. aka crazyinsomniac on sourceforge.net
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

import common


class PerlCodeGenerator:
    def get_code(self, obj):
        plgen = common.code_writers['perl']
        prop = obj.properties
        id_name, id = plgen.generate_code_id(obj)
        value = prop.get('value', '0')

        try:
            min_v, max_v = [ s.strip() for s in prop['range'].split(',') ]
        except:
            min_v, max_v = '0', '10'

        if not obj.parent.is_toplevel:
            parent = '$self->{%s}' % obj.parent.name
        else:
            parent = '$self'

        style = prop.get("style")
        if not( style and style != 'wxSL_HORIZONTAL'): style = ''

        init = []

        if id_name: init.append(id_name)

        init.append('$self->{%s} = %s->new(%s, %s, %s, %s, %s, wxDefaultPosition, wxDefaultSize, %s);\n' %
                    (obj.name, obj.klass.replace('wx','Wx::',1), parent, id, value, min_v,
                     max_v, style))
        props_buf = plgen.generate_common_properties(obj)

        return init, props_buf, []

# end of class PerlCodeGenerator


def initialize():
    common.class_names['EditSlider'] = 'wxSlider'

    plgen = common.code_writers.get('perl')
    if plgen:
        plgen.add_widget_handler('wxSlider', PerlCodeGenerator())

