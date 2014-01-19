"""\
Perl generator functions for wxSpinCtrl objects

@copyright: 2002-2004 D. H. aka crazyinsomniac on sourceforge
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class PerlSpinCtrlGenerator(wcodegen.PerlWidgetCodeWriter):
    tmpl = '%(name)s = %(klass)s->new(%(parent)s, %(id)s, "%(value)s", ' \
           'wxDefaultPosition, wxDefaultSize, %(style)s, %(minValue)s, ' \
           '%(maxValue)s, %(value)s);\n'
    default_style = 'wxSP_ARROW_KEYS'
    prefix_style = False
    set_default_style = True

    def _prepare_tmpl_content(self, obj):
        wcodegen.PerlWidgetCodeWriter._prepare_tmpl_content(self, obj)
        prop = obj.properties
        self.tmpl_dict['value'] = prop.get('value', '')
        try:
            minValue, maxValue = [s.strip() for s in
                                  prop.get('range', '0, 100').split(',')]
        except:
            minValue, maxValue = '0', '100'
        self.tmpl_dict['minValue'] = minValue
        self.tmpl_dict['maxValue'] = maxValue
        return

# end of class PerlSpinCtrlGenerator


def initialize():
    common.class_names['EditSpinCtrl'] = 'wxSpinCtrl'

    plgen = common.code_writers.get('perl')
    if plgen:
        plgen.add_widget_handler('wxSpinCtrl', PerlSpinCtrlGenerator())
