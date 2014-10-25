"""
Python generator functions for the various wxSizerS

@copyright: 2002-2007 Alberto Griggio
@copyright: 2013-2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""


import common
from edit_sizers import BaseSizerBuilder


class BasePythonSizerBuilder(BaseSizerBuilder):
    """\
    Python base class for all sizer code generators
    """

    language = 'python'

    tmpl_SetSizer = '%(parent_widget)s.SetSizer(%(sizer_name)s)\n'
    tmpl_Fit = '%(sizer_name)s.Fit(%(parent_widget)s)\n'
    tmpl_SetSizeHints = '%(sizer_name)s.SetSizeHints(%(parent_widget)s)\n'
    tmpl_StaticBox = 'self.%s_staticbox'

    def _get_wparent(self, obj):
        if not obj.parent.is_toplevel:
            parent = 'self.%s' % obj.parent.name
        else:
            parent = 'self'
        return parent

# end of class BasePythonSizerBuilder


class PythonBoxSizerBuilder(BasePythonSizerBuilder):
    klass = 'wxBoxSizer'
    init_stmt = [
        '%(sizer_name)s = %(klass)s(%(orient)s)\n',
        ]

# end of class PythonBoxSizerBuilder


class PythonStaticBoxSizerBuilder(BasePythonSizerBuilder):
    klass = 'wxStaticBoxSizer'
    init_stmt = [
        '%(staticbox_name)s = %(wxStaticBox)s(%(parent_widget)s, '
            '%(wxIDANY)s, %(label)s)\n',
        '%(sizer_name)s = %(klass)s(%(staticbox_name)s, %(orient)s)\n',
        '%(staticbox_name)s.Lower()\n',
        ]

# end of class PythonStaticBoxSizerBuilder


class PythonGridSizerBuilder(BasePythonSizerBuilder):
    klass = 'wxGridSizer'
    init_stmt = [
        '%(sizer_name)s = %(klass)s(%(rows)s, %(cols)s, '
            '%(vgap)s, %(hgap)s)\n',
        ]

# end of class PythonGridSizerBuilder


class PythonFlexGridSizerBuilder(PythonGridSizerBuilder):
    klass = 'wxFlexGridSizer'

    tmpl_AddGrowableRow = '%(sizer_name)s.AddGrowableRow(%(row)s)\n'
    tmpl_AddGrowableCol = '%(sizer_name)s.AddGrowableCol(%(col)s)\n'

# end of class PythonFlexGridSizerBuilder


def initialize():
    cn = common.class_names
    cn['EditBoxSizer'] = 'wxBoxSizer'
    cn['EditStaticBoxSizer'] = 'wxStaticBoxSizer'
    cn['EditGridSizer'] = 'wxGridSizer'
    cn['EditFlexGridSizer'] = 'wxFlexGridSizer'

    pygen = common.code_writers.get("python")
    if pygen:
        awh = pygen.add_widget_handler
        awh('wxBoxSizer', PythonBoxSizerBuilder())
        awh('wxStaticBoxSizer', PythonStaticBoxSizerBuilder())
        awh('wxGridSizer', PythonGridSizerBuilder())
        awh('wxFlexGridSizer', PythonFlexGridSizerBuilder())
