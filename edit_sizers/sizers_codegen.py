# sizers_codegen.py: code generation functions for the various wxSizerS
# $Id: sizers_codegen.py,v 1.9 2003/09/24 07:18:46 dinogen Exp $
#
# Copyright (c) 2002-2003 Alberto Griggio <albgrig@tiscalinet.it>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

import common


class PythonBoxSizerBuilder:
    def get_code(self, obj):
        orient = obj.properties.get('orient', 'wxHORIZONTAL')
        init = ['%s = wxBoxSizer(%s)\n' % (obj.name, orient)]
        layout = []
        if obj.is_toplevel:
            if not obj.parent.is_toplevel: parent = 'self.%s' % obj.parent.name
            else: parent = 'self'
            layout.append('%s.SetAutoLayout(1)\n' % parent)
            layout.append('%s.SetSizer(%s)\n' % (parent, obj.name))
            if not obj.parent.properties.has_key('size'):
                layout.append('%s.Fit(%s)\n' % (obj.name, parent))
                layout.append('%s.SetSizeHints(%s)\n' % (obj.name, parent))
        return init, [], layout

# end of class PythonBoxSizerBuilder


class PythonStaticBoxSizerBuilder:
    def get_code(self, obj):
        pygen = common.code_writers['python']
        orient = obj.properties.get('orient', 'wxHORIZONTAL')
        label = obj.properties.get('label', '')
        if not obj.parent.is_toplevel: parent = 'self.%s' % obj.parent.name
        else: parent = 'self'
        init = ['%s = wxStaticBoxSizer(wxStaticBox(%s, -1, %s), %s)\n' %
                (obj.name, parent, pygen.quote_str(label), orient)]
        layout = []
        if obj.is_toplevel:
            layout.append('%s.SetAutoLayout(1)\n' % parent)
            layout.append('%s.SetSizer(%s)\n' % (parent, obj.name))
            if not obj.parent.properties.has_key('size'):
                layout.append('%s.Fit(%s)\n' % (obj.name, parent))
                layout.append('%s.SetSizeHints(%s)\n' % (obj.name, parent))
        return init, [], layout

# end of class PythonStaticBoxSizerBuilder


class PythonGridSizerBuilder:
    klass = 'wxGridSizer'

    def get_code(self, obj):
        props = obj.properties
        if not obj.parent.is_toplevel: parent = 'self.%s' % obj.parent.name
        else: parent = 'self'
        rows = props.get('rows', '0')
        cols = props.get('cols', '0')
        vgap = props.get('vgap', '0')
        hgap = props.get('hgap', '0')
        init = [ '%s = %s(%s, %s, %s, %s)\n' %
                 (obj.name, self.klass, rows, cols, vgap, hgap) ]
        layout = []
        if obj.is_toplevel:
            layout.append('%s.SetAutoLayout(1)\n' % parent)
            layout.append('%s.SetSizer(%s)\n' % (parent, obj.name))
            if not obj.parent.properties.has_key('size'):
                layout.append('%s.Fit(%s)\n' % (obj.name, parent))
                layout.append('%s.SetSizeHints(%s)\n' % (obj.name, parent))
        return init, [], layout   

# end of class PythonGridSizerBuilder


class PythonFlexGridSizerBuilder(PythonGridSizerBuilder):
    klass = 'wxFlexGridSizer'

    def get_code(self, obj):
        init, p, layout = PythonGridSizerBuilder.get_code(self, obj)
        props = obj.properties
        if props.has_key('growable_rows'):
            for r in props['growable_rows'].split(','):
                layout.append('%s.AddGrowableRow(%s)\n' %
                              (obj.name, r.strip()))
        if props.has_key('growable_cols'):
            for r in props['growable_cols'].split(','):
                layout.append('%s.AddGrowableCol(%s)\n' %
                              (obj.name, r.strip()))
        return init, p, layout

# end of class PythonFlexGridSizerBuilder


class CppBoxSizerBuilder:
    def get_code(self, obj):
        """\
        generates the C++ code for wxBoxSizer objects.
        """
        orient = obj.properties.get('orient', 'wxHORIZONTAL')
        init = ['wxBoxSizer* %s = new wxBoxSizer(%s);\n' % (obj.name, orient)]
        layout = []
        if obj.is_toplevel:
            if not obj.parent.is_toplevel: parent = '%s->' % obj.parent.name
            else: parent = ''
            layout.append('%sSetAutoLayout(true);\n' % parent)
            layout.append('%sSetSizer(%s);\n' % (parent, obj.name))
            if not obj.parent.properties.has_key('size'):
                if not obj.parent.is_toplevel: parent = '%s' % obj.parent.name
                else: parent = 'this'
                layout.append('%s->Fit(%s);\n' % (obj.name, parent))
                layout.append('%s->SetSizeHints(%s);\n' % (obj.name, parent))
        return init, [], [], layout

# end of class CppBoxSizerBuilder


class CppStaticBoxSizerBuilder:
    def get_code(self, obj):
        """\
        generates the C++ code for wxStaticBoxSizer objects.
        """
        cppgen = common.code_writers['C++']
        orient = obj.properties.get('orient', 'wxHORIZONTAL')
        label = obj.properties.get('label', '')
        if not obj.parent.is_toplevel: parent = '%s' % obj.parent.name
        else: parent = 'this'
        init = ['wxStaticBoxSizer* %s = new wxStaticBoxSizer('
                'new wxStaticBox(%s, -1, %s), %s);\n' %
                (obj.name, parent, cppgen.quote_str(label), orient)]
        layout = []
        if obj.is_toplevel:
            if not obj.parent.is_toplevel: parent = '%s->' % obj.parent.name
            else: parent = ''
            layout.append('%sSetAutoLayout(true);\n' % parent)
            layout.append('%sSetSizer(%s);\n' % (parent, obj.name))
            if not obj.parent.properties.has_key('size'):
                if not obj.parent.is_toplevel: parent = '%s' % obj.parent.name
                else: parent = 'this'
                layout.append('%s->Fit(%s);\n' % (obj.name, parent))
                layout.append('%s->SetSizeHints(%s);\n' % (obj.name, parent))
        return init, [], [], layout

# end of class CppStaticBoxSizerBuilder


class CppGridSizerBuilder:
    klass = 'wxGridSizer'

    def get_code(self, obj):
        props = obj.properties
        rows = props.get('rows', '0')
        cols = props.get('cols', '0')
        vgap = props.get('vgap', '0')
        hgap = props.get('hgap', '0')
        init = [ '%s* %s = new %s(%s, %s, %s, %s);\n' % \
                 (self.klass, obj.name, self.klass, rows, cols, vgap, hgap) ]
        layout = []
        if obj.is_toplevel:
            if not obj.parent.is_toplevel: parent = '%s->' % obj.parent.name
            else: parent = ''
            layout.append('%sSetAutoLayout(true);\n' % parent)
            layout.append('%sSetSizer(%s);\n' % (parent, obj.name))
            if not obj.parent.properties.has_key('size'):
                if not obj.parent.is_toplevel: parent = '%s' % obj.parent.name
                else: parent = 'this'
                layout.append('%s->Fit(%s);\n' % (obj.name, parent))
                layout.append('%s->SetSizeHints(%s);\n' % (obj.name, parent))
        return init, [], [], layout   

# end of class CppGridSizerBuilder


class CppFlexGridSizerBuilder(CppGridSizerBuilder):
    klass = 'wxFlexGridSizer'

    def get_code(self, obj):
        """\
        function used to generate the C++ code for wxFlexGridSizer objects.
        """
        init, ids, p, layout = CppGridSizerBuilder.get_code(self, obj)
        props = obj.properties
        if props.has_key('growable_rows'):
            for r in props['growable_rows'].split(','):
                layout.append('%s->AddGrowableRow(%s);\n' %
                              (obj.name, r.strip()))
        if props.has_key('growable_cols'):
            for r in props['growable_cols'].split(','):
                layout.append('%s->AddGrowableCol(%s);\n' %
                              (obj.name, r.strip()))
        return init, ids, p, layout

# end of class CppFlexGridSizerBuilder


def xrc_wxFlexGridSizer_builder(obj):
    xrcgen = common.code_writers['XRC']
    class FlexGridSizerXrcObject(xrcgen.DefaultXrcObject):
        def write_property(self, name, val, outfile, tabs):
            if val and name in ('growable_rows', 'growable_cols'):
                if name == 'growable_rows': name2 = 'growablerows'
                else: name2 = 'growablecols'
                outfile.write('    '*tabs + '<%s>%s</%s>\n' %
                                  (name2, val, name2))
            else:
                xrcgen.DefaultXrcObject.write_property(self, name, val,
                                                       outfile, tabs)

    # end of class FlexGridSizerXrcObject

    return FlexGridSizerXrcObject(obj)
    


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
    cppgen = common.code_writers.get("C++")
    if cppgen:
        awh = cppgen.add_widget_handler
        awh('wxBoxSizer', CppBoxSizerBuilder())
        awh('wxStaticBoxSizer', CppStaticBoxSizerBuilder())
        awh('wxGridSizer', CppGridSizerBuilder())
        awh('wxFlexGridSizer', CppFlexGridSizerBuilder())
    xrcgen = common.code_writers.get("XRC")
    if xrcgen:
        xrcgen.add_widget_handler('wxFlexGridSizer',
                                  xrc_wxFlexGridSizer_builder)
