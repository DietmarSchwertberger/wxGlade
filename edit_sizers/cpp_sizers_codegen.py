"""
C++ generator functions for the various wxSizerS

@copyright: 2014-2015 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
from edit_sizers import BaseSizerBuilder


class BaseCPPSizerBuilder(BaseSizerBuilder):
    """\
    C++ base class for all sizer code generators
    """

    language = 'C++'

    tmpl_SetSizer = '%(parent_ref)sSetSizer(%(sizer_name)s);\n'
    tmpl_Fit = '%(sizer_name)s->Fit(%(parent_widget)s);\n'
    tmpl_SetSizeHints = '%(sizer_name)s->SetSizeHints(%(parent_widget)s);\n'
    tmpl_StaticBox = '%s_staticbox'

    def _get_wparent(self, obj):
        if not obj.parent.is_toplevel:
            parent = '%s' % obj.parent.name
        else:
            parent = 'this'
        return parent

    def _get_parent_ref(self, obj):
        if not obj.parent.is_toplevel:
            parent_ref = '%s->' % obj.parent.name
        else:
            parent_ref = ''
        return parent_ref

    def _get_code(self, obj):
        self.props_get_code['parent_ref'] = self._get_parent_ref(obj)
        result = BaseSizerBuilder._get_code(self, obj)

        # get_code() for C++ has different return values
        result = list(result)
        result.insert(2, [])
        return result

# end of class BaseCPPSizerBuilder


class CppBoxSizerBuilder(BaseCPPSizerBuilder):
    klass = 'wxBoxSizer'
    init_stmt = [
        '%(klass)s* %(sizer_name)s = new %(klass)s(%(orient)s);\n',
        ]

# end of class CppBoxSizerBuilder


class CppStaticBoxSizerBuilder(BaseCPPSizerBuilder):
    klass = 'wxStaticBoxSizer'
    init_stmt = [
        '%(staticbox_name)s = new wxStaticBox(%(parent_widget)s, '
            'wxID_ANY, %(label)s);\n',
        '%(klass)s* %(sizer_name)s = new %(klass)s(%(staticbox_name)s, '
            '%(orient)s);\n',
        '%(staticbox_name)s->Lower();\n'
        ]

# end of class CppStaticBoxSizerBuilder


class CppGridSizerBuilder(BaseCPPSizerBuilder):
    klass = 'wxGridSizer'
    init_stmt = [
        '%(klass)s* %(sizer_name)s = new %(klass)s(%(rows)s, %(cols)s, '
            '%(vgap)s, %(hgap)s);\n',
        ]

# end of class CppGridSizerBuilder


class CppFlexGridSizerBuilder(CppGridSizerBuilder):
    klass = 'wxFlexGridSizer'

    tmpl_AddGrowableRow = '%(sizer_name)s->AddGrowableRow(%(row)s);\n'
    tmpl_AddGrowableCol = '%(sizer_name)s->AddGrowableCol(%(col)s);\n'

# end of class CppFlexGridSizerBuilder


def initialize():
    cn = common.class_names
    cn['EditBoxSizer'] = 'wxBoxSizer'
    cn['EditStaticBoxSizer'] = 'wxStaticBoxSizer'
    cn['EditGridSizer'] = 'wxGridSizer'
    cn['EditFlexGridSizer'] = 'wxFlexGridSizer'

    cppgen = common.code_writers.get("C++")
    if cppgen:
        awh = cppgen.add_widget_handler
        awh('wxBoxSizer', CppBoxSizerBuilder())
        awh('wxStaticBoxSizer', CppStaticBoxSizerBuilder())
        awh('wxGridSizer', CppGridSizerBuilder())
        awh('wxFlexGridSizer', CppFlexGridSizerBuilder())
