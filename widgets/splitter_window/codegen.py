# codegen.py: code generator functions for wxSplitterWindow objects
#
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: GPL (see license.txt)

import common

def python_code_generator(window):
    """\
    generates the python code for wxSplitterWindow
    """
    pygen = common.code_writers['python']
    prop = window.properties
    id_name, id = pygen.generate_code_id(window)
    if window.is_toplevel:
        l = ['self.%s = %s(self, %s)\n' % (window.name, window.klass, id)]
        if id_name: l.append(id_name)
        return l, [], []
    size = pygen.generate_code_size(window)
    if not window.parent.is_toplevel: parent = 'self.%s' % window.parent.name
    else: parent = 'self'
    style = prop.get('style', 'wxSP_3D')
    init = ['self.%s = wxSplitterWindow(%s, %s, size=%s, style=%s)\n' %
            (window.name, parent, id, size, style) ]
    if id_name: init.append(id_name)

    props_buf = []
    win_1 = prop.get('window_1')
    win_2 = prop.get('window_2')
    orientation = prop.get('orientation', 'wxSPLIT_VERTICAL')
    if win_1 and win_2:
        if orientation == 'wxSPLIT_VERTICAL': f_name = 'SplitVertically'
        else: f_name = 'SplitHorizontally'
        props_buf.append('self.%s.%s(self.%s, self.%s)\n' % \
                         (window.name, f_name, win_1, win_2))
    else:
        def add_sub(win):
            props_buf.append('self.%s.SetSplitMode(%s)\n' % (window.name,
                                                             orientation))
            props_buf.append('self.%s.Initialize(self.%s)\n' % \
                             (window.name, win))
        if win_1: add_sub(win_1)
        elif win_2: add_sub(win_2)

    if prop.has_key('foreground'):
        props_buf.append(pygen.generate_code_foreground(window))
    if prop.has_key('background'):
        props_buf.append(pygen.generate_code_background(window))
    if prop.has_key('font'): props_buf.append(pygen.generate_code_font(window))
    sash_pos = prop.get('sash_pos')
    if sash_pos:
        props_buf.append('self.%s.SetSashPosition(%s)\n' % (window.name,
                                                            sash_pos))
    return init, props_buf, []


def python_generate_properties(obj):
    prop = obj.properties
    pygen = common.code_writers['python']
    win_1 = prop.get('window_1')
    win_2 = prop.get('window_2')
    orientation = prop.get('orientation', 'wxSPLIT_VERTICAL')
    props_buf = []
    if win_1 and win_2:
        if orientation == 'wxSPLIT_VERTICAL': f_name = 'SplitVertically'
        else: f_name = 'SplitHorizontally'
        props_buf.append('self.%s(self.%s, self.%s)\n' %
                         (f_name, win_1, win_2))
    else:
        def add_sub(win):
            props_buf.append('self.SetSplitMode(%s)\n' % orientation)
            props_buf.append('self.Initialize(self.%s)\n' % win)
        if win_1: add_sub(win_1)
        elif win_2: add_sub(win_2)
    sash_pos = prop.get('sash_pos')
    if sash_pos:
        props_buf.append('self.SetSashPosition(%s)\n' % sash_pos)
    props_buf.extend(pygen.generate_common_properties(obj))
    return props_buf    


def initialize():
    common.class_names['EditSplitterWindow'] = 'wxSplitterWindow'
    common.class_names['SplitterPane'] = 'wxPanel'

    # python code generation functions
    pygen = common.code_writers.get('python')
    if pygen:
        pygen.add_widget_handler('wxSplitterWindow', python_code_generator,
                                 python_generate_properties)
        
    
