"""\
Perl generator functions for wxSlider objects

@copyright: 2002-2004 D. H. aka crazyinsomniac on sourceforge
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class PerlSliderGenerator(wcodegen.PerlWidgetCodeWriter):
    tmpl = '%(name)s = %(klass)s->new(%(parent)s, %(id)s, %(value)s, ' \
           '%(minValue)s, %(maxvalue)s%(style)s);\n'
    default_style = 'wxSL_HORIZONTAL'

    def _prepare_tmpl_content(self, obj):
        wcodegen.PerlWidgetCodeWriter._prepare_tmpl_content(self, obj)
        prop = obj.properties
        self.tmpl_dict['value'] = prop.get('value', '0')
        try:
            minValue, maxValue = [s.strip() for s in prop['range'].split(',')]
        except:
            minValue, maxValue = '0', '10'
        self.tmpl_dict['minValue'] = minValue
        self.tmpl_dict['maxValue'] = maxValue
        return

# end of class PerlSliderGenerator


def initialize():
    common.class_names['EditSlider'] = 'wxSlider'

    plgen = common.code_writers.get('perl')
    if plgen:
        plgen.add_widget_handler('wxSlider', PerlSliderGenerator())
