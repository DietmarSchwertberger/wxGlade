"""\
Perl generator functions for wxSpinButton objects

@copyright: 2004 D. H. aka crazyinsomniac on sourceforge
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class PerlSpinButtonGenerator(wcodegen.PerlWidgetCodeWriter):
    tmpl = '%(name)s = %(klass)s->new(%(parent)s, %(id)s,%(style)s);\n'
    default_style = 'wxSP_HORIZONTAL'

# end of class PerlSpinButtonGenerator


def initialize():
    common.class_names['EditSpinButton'] = 'wxSpinButton'

    plgen = common.code_writers.get('perl')
    if plgen:
        plgen.add_widget_handler('wxSpinButton', PerlSpinButtonGenerator())
