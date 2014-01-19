"""\
Perl generator functions for wxTextCtrl objects

@copyright: 2002-2004 D. H. aka crazyinsomniac on sourceforge
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class PerlCodeGenerator(wcodegen.PerlWidgetCodeWriter):
    tmpl = '%(name)s = %(klass)s->new(%(parent)s, %(id)s, %(value)s' \
           '%(style)s);\n'

# end of class PerlCodeGenerator


def initialize():
    common.class_names['EditTextCtrl'] = 'wxTextCtrl'

    plgen = common.code_writers.get('perl')
    if plgen:
        plgen.add_widget_handler('wxTextCtrl', PerlCodeGenerator())
