# perl_codegen.py : perl generator functions for CustomWidget objects
# $Id: perl_codegen.py,v 1.1 2003/06/23 21:26:44 crazyinsomniac Exp $
#
# Copyright (c) 2002-2003 D.H. aka crazyinsomniac on sourceforge.net
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY


import common
from codegen import ArgumentsCodeHandler, _fix_arguments


class PerlCodeGenerator:
    def get_code(self, widget):
        init = []
        plgen = common.code_writers['perl']
        prop = widget.properties
        id_name, id = plgen.generate_code_id(widget)

        if not widget.parent.is_toplevel:
            parent = '$self->{%s}' % widget.parent.name
        else:
            parent = '$self'

        if id_name: init.append(id_name)
        arguments = _fix_arguments(prop.get('arguments', []), parent, id)
        init.append('$self->{%s} = %s->new(%s);\n' %
            (widget.name, widget.klass.replace('wx','Wx::',1),
                                            ", ".join(arguments)))
        props_buf = plgen.generate_common_properties(widget)
        return init, props_buf, []

# end of class PerlCodeGenerator

def initialize():
    common.class_names['CustomWidget'] = 'CustomWidget'

    plgen = common.code_writers.get('perl')
    if plgen:
        plgen.add_widget_handler('CustomWidget', PerlCodeGenerator())
        plgen.add_property_handler('arguments', ArgumentsCodeHandler,
                                    'CustomWidget')
