"""\
Code generator functions for wxBitmapButton objects

@copyright: 2002-2007 Alberto Griggio
@copyright: 2014-2015 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class PythonBitmapButtonGenerator(wcodegen.PythonWidgetCodeWriter):
    tmpl = '%(name)s = %(klass)s(%(parent)s, %(id_number)s, ' \
           '%(bitmap)s%(style)s)\n'

# end of class PythonBitmapButtonGenerator


class CppBitmapButtonGenerator(wcodegen.CppWidgetCodeWriter):
    tmpl = '%(name)s = new %(klass)s(%(parent)s, %(id_number)s, ' \
           '%(bitmap)s%(style)s);\n'

# end of class CppBitmapButtonGenerator


def xrc_code_generator(obj):
    xrcgen = common.code_writers['XRC']

    class BitmapButtonXrcObject(xrcgen.DefaultXrcObject):
        def write_property(self, name, val, outfile, tabs):
            if name == 'disabled_bitmap':
                name = 'disabled'
            xrcgen.DefaultXrcObject.write_property(
                self, name, val, outfile, tabs)

    # end of class BitmapButtonXrcObject

    return BitmapButtonXrcObject(obj)


def initialize():
    klass = 'wxBitmapButton'
    common.class_names['EditBitmapButton'] = klass
    common.register('python', klass, PythonBitmapButtonGenerator(klass))
    common.register('C++', klass, CppBitmapButtonGenerator(klass))
    common.register('XRC', klass, xrc_code_generator)
