"""
Lisp code generator functions for wxHyperlinkCtrl objects

@copyright: 2012-2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class LispHyperlinkCtrlGenerator(wcodegen.LispWidgetCodeWriter):

    supported_by = ((2, 8), (3, 0),)

    tmpl = '(setf %(name)s (%(klass)s_Create %(parent)s %(id)s ' \
           '%(label)s %(url)s -1 -1 -1 -1 %(style)s))\n'

    def _prepare_tmpl_content(self, obj):
        wcodegen.LispWidgetCodeWriter._prepare_tmpl_content(self, obj)
        self.tmpl_dict['url'] = self.codegen.quote_str(obj.properties.get('url', ''))
        self.has_setvalue1 = obj.properties.get('checked', False)
        return

# end of class LispHyperlinkCtrlGenerator


def initialize():

    common.class_names['EditHyperlinkCtrl'] = 'wxHyperlinkCtrl'
    codegen = common.code_writers.get('lisp')

    if codegen:
        codegen.add_widget_handler(
            'wxHyperlinkCtrl',
            LispHyperlinkCtrlGenerator()
        )
