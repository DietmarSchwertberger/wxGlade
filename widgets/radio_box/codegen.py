"""
Code generator functions for wxRadioBox objects

@copyright: 2002-2007 Alberto Griggio
@copyright: 2014-2015 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen
from ChoicesCodeHandler import *


class PythonRadioBoxGenerator(wcodegen.PythonWidgetCodeWriter):
    tmpl = '%(name)s = %(klass)s(%(parent)s, %(id)s, %(label)s, ' \
           'choices=[%(choices)s], majorDimension=%(majorDimension)s' \
           '%(style)s)\n'

    default_style = 'wxRA_SPECIFY_COLS'
    set_default_style = True

    def _prepare_tmpl_content(self, obj):
        wcodegen.PythonWidgetCodeWriter._prepare_tmpl_content(self, obj)
        self.tmpl_dict['majorDimension'] = obj.properties.get('dimension', '1')
        return

# end of class PythonRadioBoxGenerator


class CppRadioBoxGenerator(wcodegen.CppWidgetCodeWriter):
    tmpl = '%(name)s = new %(klass)s(%(parent)s, %(id)s, %(label)s, ' \
           'wxDefaultPosition, wxDefaultSize, %(choices_len)s, ' \
           '%(name)s_choices, %(majorDimension)s, %(style)s);\n'

    default_style = 'wxRA_SPECIFY_COLS'
    prefix_style = False
    set_default_style = True

    def _prepare_tmpl_content(self, obj):
        wcodegen.CppWidgetCodeWriter._prepare_tmpl_content(self, obj)

        # wx raises an assertion if choices are empty and majorDim is 0
        majorDimension = obj.properties.get('dimension', '1')
        choices = obj.properties.get('choices', [])
        if not choices and majorDimension == '0':
            majorDimension = '1'

        self.tmpl_dict['majorDimension'] = majorDimension


        return

# end of class CppRadioBoxGenerator


def xrc_code_generator(obj):
    xrcgen = common.code_writers['XRC']

    class RadioBoxXrcObject(xrcgen.DefaultXrcObject):
        def write_property(self, name, val, outfile, tabs):
            if name == 'choices':
                xrc_write_choices_property(self, outfile, tabs)
            else:
                xrcgen.DefaultXrcObject.write_property(self, name, val,
                                                       outfile, tabs)

    # end of class RadioBoxXrcObject

    return RadioBoxXrcObject(obj)


def initialize():
    klass = 'wxRadioBox'
    common.class_names['EditRadioBox'] = klass
    common.register('python', klass, PythonRadioBoxGenerator(klass),
                    'choices', ChoicesCodeHandler)
    common.register('C++', klass, CppRadioBoxGenerator(klass),
                    'choices', ChoicesCodeHandler)
    common.register('XRC', klass, xrc_code_generator,
                    'choices', ChoicesCodeHandler)
