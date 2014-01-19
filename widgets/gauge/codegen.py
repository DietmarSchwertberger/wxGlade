"""\
Code generator functions for wxGauge objects

@copyright: 2002-2007 Alberto Griggio
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class PythonGaugeGenerator(wcodegen.PythonWidgetCodeWriter):
    tmpl = '%(name)s = %(klass)s(%(parent)s, %(id)s, %(range)s%(style)s)\n'
    default_style = 'wxGA_HORIZONTAL'

    def _prepare_tmpl_content(self, obj):
        wcodegen.PythonWidgetCodeWriter._prepare_tmpl_content(self, obj)
        self.tmpl_dict['range'] = obj.properties.get('range', '10')
        return

# end of class PythonGaugeGenerator


class CppGaugeGenerator(wcodegen.CppWidgetCodeWriter):
    tmpl = '%(name)s = new %(klass)s(%(parent)s, %(id)s, ' \
           '%(range)s%(style)s);\n'
    default_style = 'wxGA_HORIZONTAL'

    def _prepare_tmpl_content(self, obj):
        wcodegen.CppWidgetCodeWriter._prepare_tmpl_content(self, obj)
        self.tmpl_dict['range'] = obj.properties.get('range', '10')
        return

# end of class CppGaugeGenerator


def initialize():
    common.class_names['EditGauge'] = 'wxGauge'

    pygen = common.code_writers.get("python")
    if pygen:
        pygen.add_widget_handler('wxGauge', PythonGaugeGenerator())
    cppgen = common.code_writers.get('C++')
    if cppgen:
        cppgen.add_widget_handler('wxGauge', CppGaugeGenerator())
