# codegen.py: code generator functions for wxPanel objects
#
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: Python 2.2 license (see license.txt)

import common

def python_code_generator(panel):
    """\
    generates the python code for wxPanel objects
    """
    pygen = common.code_writers['python']
    prop = panel.properties
    id_name, id = pygen.generate_code_id(panel)
    if not panel.parent.is_toplevel: parent = 'self.%s' % panel.parent.name
    else: parent = 'self'
    if panel.is_toplevel:
        l = []
        if id_name: l.append(id_name)
        l.append('self.%s = %s(%s, %s)\n' %
                 (panel.name, panel.klass, parent, id))
        return l, [], []
    init = []
    if id_name: init.append(id_name)
    style = prop.get("style", 'wxTAB_TRAVERSAL')
    if style != 'wxTAB_TRAVERSAL': style = ", style=%s" % style
    else: style = ''
    init.append('self.%s = wxPanel(%s, %s%s)\n' % \
                (panel.name, parent, id, style))
    props_buf = pygen.generate_common_properties(panel)
    return init, props_buf, []


def cpp_code_generator(panel):
    """\
    generates the python code for wxPanel objects
    """
    cppgen = common.code_writers['C++']
    prop = panel.properties
    id_name, id = cppgen.generate_code_id(panel)
    if id_name: ids = [ id_name ]
    else: ids = []
    if not panel.parent.is_toplevel: parent = '%s' % panel.parent.name
    else: parent = 'this'
    if panel.is_toplevel:
        l = ['%s = new %s(%s, %s);\n' % (panel.name, panel.klass, parent, id)]
        return l, ids, [], []
    extra = ''
    style = prop.get("style", 'wxTAB_TRAVERSAL')
    if style != wxTAB_TRAVERSAL:
        extra = ', wxDefaultPosition, wxDefaultSize, %s' % style
    init = ['%s = new wxPanel(%s, %s%s);\n' %
            (panel.name, parent, id, extra) ]
    props_buf = cppgen.generate_common_properties(panel)
    return init, ids, props_buf, []


def initialize():
    common.class_names['EditPanel'] = 'wxPanel'
    common.class_names['EditTopLevelPanel'] = 'wxPanel'

    # python code generation functions
    pygen = common.code_writers.get('python')
    if pygen:
        pygen.add_widget_handler('wxPanel', python_code_generator)
    cppgen = common.code_writers.get('C++')
    if cppgen:
        constructor = [('wxWindow*', 'parent'), ('int', 'id'),
                       ('const wxPoint&', 'pos', 'wxDefaultPosition'),
                       ('const wxSize&', 'size', 'wxDefaultSize'),
                       ('long', 'style', '0')]
        cppgen.add_widget_handler('wxPanel', cpp_code_generator, constructor)
