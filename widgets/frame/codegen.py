# codegen.py: code generator functions for wxDialog objects
#
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: GPL (see license.txt)

import common
from MenuTree import *

# python code generators

def python_menubar_code_generator(obj):
    """\
    function that generates code for the menubar of a wxFrame.
    """
    menus = obj.properties['menubar']
    init = [ '\n', '# Menu Bar\n', 'self.%s = wxMenuBar()\n' % obj.name,
             'self.SetMenuBar(self.%s)\n' % obj.name ]
    append = init.append
    def append_items(menu, items):
        for item in items:
            if item.name == '---': # item is a separator
                append('%s.AppendSeparator()\n' % menu)
            elif item.children:
                if item.name: name = item.name
                else: name = '%s_sub' % menu
                append('%s = wxMenu()\n' % name)
                if item.id: # generating id
                    tokens = item.id.split('=')
                    if len(tokens) > 1:
                        append('%s = %s\n' % tuple(tokens))
                        id = tokens[0]
                    else:
                        id = item.id
                else: id = 'wxNewId()'
                append_items(name, item.children)
                append('%s.AppendMenu(%s, %s, %s, "%s")\n' %
                       (menu, id, '"%s"' % item.label.replace('"', r'\"'),
                        name, item.help_str.replace('"', r'\"')))
            else:
                if item.id:
                    tokens = item.id.split('=')
                    if len(tokens) > 1:
                        append('%s = %s\n' % tuple(tokens))
                        id = tokens[0]
                    else:
                        id = item.id
                else: id = 'wxNewId()'
                if item.checkable == '1':
                    append('%s.Append(%s, "%s", "%s", 1)\n' %
                           (menu, id, item.label.replace('"', r'\"'),
                            item.help_str.replace('"', r'\"')))
                else:
                    append('%s.Append(%s, "%s", "%s")\n' %
                           (menu, id, item.label.replace('"', r'\"'),
                            item.help_str.replace('"', r'\"')))
    #print 'menus = %s' % menus
    for m in menus:
        menu = m.root
        if menu.name: name = 'self.' + menu.name
        else: name = 'wxglade_tmp_menu'
        append('%s = wxMenu()\n' % name)
        if menu.children:
            append_items(name, menu.children)
        append('self.%s.Append(%s, "%s")\n' %
               (obj.name, name, menu.label.replace('"', r'\"')))
    append('# Menu Bar end\n')
    init.reverse()
    return init, [], []

    
def python_statusbar_code_generator(obj):
    """\
    function that generates code for the statusbar of a wxFrame.
    """
    labels, widths = obj.properties['statusbar']
    init = [ 'self.%s = self.CreateStatusBar(%s)\n' % \
             (obj.name, len(labels)) ]
    props = []
    append = props.append
    append('self.%s.SetStatusWidths(%s)\n' % (obj.name, repr(widths)))
    append('# statusbar fields\n')
    append('%s_fields = %s\n' % (obj.name, repr(labels)))
    append('for i in range(len(%s_fields)):\n' % obj.name)
    append('    self.%s.SetStatusText(%s_fields[i], i)\n' % \
           (obj.name, obj.name))
    return init, props, []
    

def python_generate_frame_properties(frame):
    """\
    generates the code for the various wxFrame specific properties.
    Returns a list of strings containing the generated code
    """
    prop = frame.properties
    pygen = common.code_writers['python']
    out = []
    title = prop.get('title')
    if title: out.append('self.SetTitle("%s")\n' % title)
    out.extend(pygen.generate_common_properties(frame))
    return out


# property handlers for code generation

class StatusFieldsHandler:
    """Handler for statusbar fields"""
    def __init__(self):
        self.labels = []
        self.widths = []
        self.curr_label = []
        
    def start_elem(self, name, attrs):
        if name == 'field':
            self.widths.append(int(attrs.get('width', -1)))
            
    def end_elem(self, name, code_obj):
        if name == 'fields':
            code_obj.properties['statusbar'] = (self.labels, self.widths)
            return True
        self.labels.append("".join(self.curr_label))
        self.curr_label = []
        
    def char_data(self, data):
        self.curr_label.append(data)

# end of class StatusFieldsHandler


class MenuHandler:
    """Handler for menus and menu items of a menubar"""
    item_attrs = ('label', 'id', 'name', 'help_str', 'checkable')
    def __init__(self):
        self.menu_depth = 0
        self.menus = []
        self.curr_menu = None
        self.curr_item = None
        self.attr_val = []

    def start_elem(self, name, attrs):
        if name == 'menu':
            self.menu_depth += 1
            label = attrs['label']
            if self.menu_depth == 1:
                t = MenuTree(attrs['name'], label)
                self.curr_menu = t.root
                self.menus.append(t)
                return
            node = MenuTree.Node(label=label, name=attrs['name'])
            node.parent = self.curr_menu
            self.curr_menu.children.append(node)
            self.curr_menu = node
        elif name == 'item':
            self.curr_item = MenuTree.Node()

    def end_elem(self, name, code_obj):
        if name == 'menus':
            code_obj.properties['menubar'] = self.menus
            return True
        if name == 'item' and self.curr_menu:
            self.curr_menu.children.append(self.curr_item)
            self.curr_item.parent = self.curr_menu
        elif name == 'menu':
            self.menu_depth -= 1
            self.curr_menu = self.curr_menu.parent
        elif name in self.item_attrs:
            setattr(self.curr_item, name, "".join(self.attr_val))
            self.attr_val = []

    def char_data(self, data):
        self.attr_val.append(data)

# end of class MenuHandler


def xrc_frame_code_generator(obj):
    xrcgen = common.code_writers['XRC']
    class FrameXrcObject(xrcgen.DefaultXrcObject):
        def write_child_prologue(self, child, out_file, tabs):
            if child.code_obj.in_sizers:
                # XRC doesn't like sizers for Frames, so we add a Panel
                out_file.write('    '*tabs + '<object class="wxPanel">\n')

        def write_child_epilogue(self, child, out_file, tabs):
            if child.code_obj.in_sizers:
                # end of the fake panel
                out_file.write('    '*tabs + '</object>\n')

        def write(self, outfile, tabs):
            if self.properties.has_key('menubar'):
                del self.properties['menubar']
            if self.properties.has_key('statusbar'):
                del self.properties['statusbar']
            xrcgen.DefaultXrcObject.write(self, outfile, tabs)

    # end of class FrameXrcObject
    
    return FrameXrcObject(obj)
                

def xrc_menubar_code_generator(obj):
    """\
    function that generates XRC code for the menubar of a wxFrame.
    """
    from xml.sax.saxutils import escape, quoteattr
    xrcgen = common.code_writers['XRC']
    
    class MenuBarXrcObject(xrcgen.DefaultXrcObject):
        def append_item(self, item, outfile, tabs):
            write = outfile.write
            if item.name == '---': # item is a separator
                write('    '*tabs + '<object class="separator"/>\n')
            elif item.children:
                if item.name:
                    write('    '*tabs + '<object class="wxMenu" ' \
                          'name=%s>\n' % quoteattr(item.name))
                else:
                    write('    '*tabs + '<object class="wxMenu">\n')
                tab_s = '    ' * (tabs+1)
                if item.label:
                    write(tab_s + '<label>%s</label>\n' % \
                          escape(item.label))
                for c in item.children:
                    self.append_item(c, outfile, tabs+1)
                write('    '*tabs + '</object>\n')
            else:
                if item.name:
                    write('    '*tabs + '<object class="wxMenuItem" ' \
                          'name=%s>\n' % quoteattr(item.name))
                else:
                    write('    '*tabs + '<object class="wxMenuItem">\n')  
                if item.label:
                    write('    '*(tabs+1) + '<label>%s</label>\n' % \
                          escape(item.label))
                if item.checkable == '1':
                    write('    '*(tabs+1) + '<checkable>1</checkable>\n')
                write('    '*tabs + '</object>\n')
        
        def write(self, outfile, tabs):
            menus = self.code_obj.properties['menubar']
            write = outfile.write
            write('    '*tabs + '<object class="wxMenuBar" name=%s>\n' % \
                  quoteattr(self.name))
            for m in menus:
                self.append_item(m.root, outfile, tabs+1)
            write('    '*tabs + '</object>\n')

    # end of class MenuBarXrcObject
    
    return MenuBarXrcObject(obj)


def initialize():
    cn = common.class_names
    cn['EditFrame'] = 'wxFrame'
    cn['EditStatusBar'] = 'wxStatusBar'
    cn['EditMenuBar'] = 'wxMenuBar'

    pygen = common.code_writers.get('python')
    if pygen:
        awh = pygen.add_widget_handler
        awh('wxFrame', lambda o: None, python_generate_frame_properties)
        awh('wxStatusBar', python_statusbar_code_generator)
        awh('wxMenuBar', python_menubar_code_generator)
        aph = pygen.add_property_handler
        aph('menubar', pygen.DummyPropertyHandler)
        aph('statusbar', pygen.DummyPropertyHandler)
        aph('fields', StatusFieldsHandler)
        aph('menus', MenuHandler)

    xrcgen = common.code_writers.get('XRC')
    if xrcgen:
        xrcgen.add_widget_handler('wxFrame', xrc_frame_code_generator)
        xrcgen.add_widget_handler('wxMenuBar', xrc_menubar_code_generator)
        xrcgen.add_property_handler('menus', MenuHandler)
        xrcgen.add_widget_handler('wxStatusBar',
                                  xrcgen.NotImplementedXrcObject)
