"""\
Code generator functions for wxDatePickerCtrl objects

@copyright: 2002-2007 Alberto Griggio
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class PythonDatePickerCtrlGenerator(wcodegen.PythonWidgetCodeWriter):
    tmpl = '%(name)s = %(klass)s(%(parent)s, %(id)s%(style)s)\n'

    def _prepare_tmpl_content(self, obj):
        wcodegen.PythonWidgetCodeWriter._prepare_tmpl_content(self, obj)
        self.has_setdefault = obj.properties.get('default', False)
        return

# end of class PythonDatePickerCtrlGenerator


class CppDatePickerCtrlGenerator(wcodegen.CppWidgetCodeWriter):
    extra_headers = ['<wx/datectrl.h>']
    tmpl = '%(name)s = new %(klass)s(%(parent)s, %(id)s%(style)s);\n'

    def _prepare_tmpl_content(self, obj):
        wcodegen.CppWidgetCodeWriter._prepare_tmpl_content(self, obj)
        self.has_setdefault = obj.properties.get('default', False)
        return

# end of class CppDatePickerCtrlGenerator


def xrc_code_generator(obj):
    xrcgen = common.code_writers['XRC']
    class DatePickerCtrlXrcObject(xrcgen.DefaultXrcObject):
        def write_property(self, name, val, outfile, tabs):
            if name == 'label':
                # translate & into _ as accelerator marker
                val2 = val.replace('&', '_')
                if val.count('&&') > 0:
                    while True:
                        index = val.find('&&')
                        if index < 0: break
                        val = val2[:index] + '&&' + val2[index+2:]
                else: val = val2
            xrcgen.DefaultXrcObject.write_property(self, name, val,
                                                   outfile, tabs)
    # end of class DatePickerCtrlXrcObject

    return DatePickerCtrlXrcObject(obj)


def initialize():
    common.class_names['EditDatePickerCtrl'] = 'wxDatePickerCtrl'
    pygen = common.code_writers.get('python')
    if pygen:
        pygen.add_widget_handler('wxDatePickerCtrl', PythonDatePickerCtrlGenerator())
    xrcgen = common.code_writers.get("XRC")
    if xrcgen:
        xrcgen.add_widget_handler('wxDatePickerCtrl', xrc_code_generator)
    cppgen = common.code_writers.get('C++')
    if cppgen:
        cppgen.add_widget_handler('wxDatePickerCtrl', CppDatePickerCtrlGenerator())
