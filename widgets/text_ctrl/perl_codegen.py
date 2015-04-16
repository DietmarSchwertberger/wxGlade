"""\
Perl generator functions for wxTextCtrl objects

@copyright: 2002-2004 D. H. aka crazyinsomniac on sourceforge
@copyright: 2014-2015 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class PerlTextCtrlGenerator(wcodegen.PerlWidgetCodeWriter):
    tmpl = '%(name)s = %(klass)s->new(%(parent)s, %(id)s, %(value)s' \
           '%(style)s);\n'

# end of class PerlTextCtrlGenerator


def initialize():
    klass = 'wxTextCtrl'
    common.class_names['EditTextCtrl'] = klass
    common.register('perl', klass, PerlTextCtrlGenerator(klass))
