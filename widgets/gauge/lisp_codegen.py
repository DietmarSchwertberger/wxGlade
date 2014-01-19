"""\
Lisp generator functions for wxGauge objects

@copyright: 2002-2004 D. H. aka crazyinsomniac on sourceforge
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""


import common
import wcodegen


class LispGaugeGenerator(wcodegen.LispWidgetCodeWriter):

    tmpl = '(setf %(name)s (%(klass)s_Create %(parent)s %(id)s ' \
           '%(range)s -1 -1 -1 -1 %(style)s))\n'
    default_style = 'wxGA_HORIZONTAL'

    def _prepare_tmpl_content(self, obj):
        wcodegen.LispWidgetCodeWriter._prepare_tmpl_content(self, obj)
        self.tmpl_dict['range'] = obj.properties.get('range', '10')
        return

# end of class LispGaugeGenerator

def initialize():
    common.class_names['EditGauge'] = 'wxGauge'

    codegen = common.code_writers.get('lisp')
    if codegen:
        codegen.add_widget_handler('wxGauge', LispGaugeGenerator())
