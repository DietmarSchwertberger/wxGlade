# codegen.py: code generator functions for wxToggleButton objects
#
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: GPL (see license.txt)

import common

def python_code_generator(obj):
    """\
    fuction that generates python code for wxToggleButton objects.
    """
    pygen = common.code_writers['python']
    prop = obj.properties
    id_name, id = pygen.generate_code_id(obj)
    label = '"' + prop.get('label', '').replace('"', '\"') + '"'
    if obj.is_toplevel:
        l = ['self.%s = %s(self, %s, %s)\n' % (obj.name, obj.klass, id, label)]
        if id_name: l.append(id_name) # init lines are written in reverse order
        return l , [], []    
    size = pygen.generate_code_size(obj)
    if not obj.parent.is_toplevel: parent = 'self.%s' % obj.parent.name
    else: parent = 'self'
    init = [ 'self.%s = wxToggleButton(%s, %s, %s, size=%s)\n' % 
             (obj.name, parent, id, label, size) ]
    if id_name: init.append(id_name) # init lines are written in reverse order
    props_buf = []
    if prop.has_key('foreground'):
        props_buf.append(pygen.generate_code_foreground(obj))
    if prop.has_key('background'):
        props_buf.append(pygen.generate_code_background(obj))
    if prop.has_key('font'): props_buf.append(pygen.generate_code_font(obj))
    value = prop.get('value')
    if value: props_buf.append('self.%s.SetValue(%s)\n' % (obj.name, value))
    return init, props_buf, []


def initialize():
    common.class_names['EditToggleButton'] = 'wxToggleButton'

    pygen = common.code_writers.get('python')
    if pygen:
        pygen.add_widget_handler('wxToggleButton', python_code_generator)
