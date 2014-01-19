"""\
Lisp generator functions for wxListBox objects

@copyright: 2002-2004 D. H. aka crazyinsomniac on sourceforge
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""


import common
import wcodegen
from ChoicesCodeHandler import *


class LispListBoxGenerator(wcodegen.LispWidgetCodeWriter):
    tmpl = '(setf %(name)s (%(klass)s_Create %(parent)s %(id)s -1 -1 -1 ' \
           '-1 %(choices_len)s (vector %(choices)s) %(style)s))\n'
    has_choice = True

# end of class LispListBoxGenerator


def initialize():
    common.class_names['EditListBox'] = 'wxListBox'

    codegen = common.code_writers.get('lisp')
    if codegen:
        codegen.add_widget_handler('wxListBox', LispListBoxGenerator())
        codegen.add_property_handler('choices', ChoicesCodeHandler)
