# list_box.py: wxListBox objects
#
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: GPL (see license.txt)

from wxPython.wx import *
import common, misc
from edit_windows import ManagedBase
from tree import Tree
from widget_properties import *
from ChoicesProperty import *

class EditListBox(ManagedBase):
    def __init__(self, name, parent, id, choices, sizer, pos, property_window,
                 show=True):
        """\
        Class to handle wxListBox objects
        """
        ManagedBase.__init__(self, name, 'wxListBox', parent, id, sizer,
                             pos, property_window, show=show)
        # properties
        self.access_functions['choices'] = (self.get_choices, self.set_choices)
        self.properties['choices'] = ChoicesProperty(self, 'choices', None,
                                                     [('Label',
                                                       GridProperty.STRING)],
                                                     len(choices))
        self.access_functions['selection'] = (self.get_selection,
                                              self.set_selection)
        self.access_functions['style'] = (self.get_style, self.set_style)
        self.properties['selection'] = SpinProperty(self, 'selection', None,
                                                    r=(0, self.Number()-1))
        self.style_pos  = (wxLB_SINGLE, wxLB_MULTIPLE, wxLB_EXTENDED,
                           wxLB_HSCROLL, wxLB_ALWAYS_SB, wxLB_NEEDED_SB,
                           wxLB_SORT)
        style_labels  = ('#section#Style', 'wxLB_SINGLE', 'wxLB_MULTIPLE',
                         'wxLB_EXTENDED', 'wxLB_HSCROLL', 'wxLB_ALWAYS_SB',
                         'wxLB_NEEDED_SB', 'wxLB_SORT')
        self.properties['style'] = CheckListProperty(self, 'style', None,
                                                     style_labels)

    def create_properties(self):
        ManagedBase.create_properties(self)
        panel = wxScrolledWindow(self.notebook, -1)
        szr = misc.Sizer(wxVERTICAL)
        self.properties['choices'].display(panel)
        self.properties['style'].display(panel)
        self.properties['selection'].display(panel)
        self.properties['choices'].set_col_sizes([-1])
        szr.Add(self.properties['style'].panel, 0, wxEXPAND)
        szr.Add(self.properties['selection'].panel, 0, wxEXPAND)
        ch = self.properties['choices'].panel
        ch.SetSize((ch.GetSize()[0]-20, 200))
        szr.Add(self.properties['choices'].panel, 0, wxEXPAND)
        panel.SetAutoLayout(True)
        panel.SetSizer(szr)
        szr.Fit(panel)
        w, h = panel.GetSize()
        from math import ceil
        panel.SetScrollbars(5, 5, ceil(w/5.0), ceil(h/5.0))
        self.notebook.AddPage(panel, 'Widget')
        
    def get_property_handler(self, prop_name):
        if prop_name == 'choices':
            return ChoicesHandler(self)

    def get_choices(self):
        # A copy of self.choice is returned, otherwise the caller
        # could be able to change self.choice but not what is shown
        # by self.widget.
        return list(self.choices)

    def set_choices(self, values):
        self.choices = list(values)
        self.properties['selection'].set_range(0, len(self.choices)-1)
        if self.widget:
            self.widget.Clear()
            for value in values:
                # !!! I can't understand what you are doing,
                # why value[0]?
                self.widget.Append(value[0])
            self.sizer.set_item(self.pos, size=self.widget.GetBestSize())
            self.widget.SetSelection(int(self.properties['selection'].get_value()))

    def get_style(self):
        retval = [0] * len(self.style_pos)
        try:
            for i in range(len(self.style_pos)):
                if self.style & self.style_pos[i]:
                    retval[i] = 1
        except AttributeError: pass
        return retval

    def set_style(self, value):
        value = self.properties['style'].prepare_value(value)
        self.style = 0
        for v in range(len(value)):
            if value[v]:
                self.style |= self.style_pos[v]
        if self.widget:
            self.SetWindowStyleFlag(self.style)

    def get_selection(self):
        return self.selection

    def set_selection(self, value):
        value = int(value)
        if value != self.selection:
            self.selection = value
            if self.widget:
                self.widget.SetSelection(value)

    def create_widget(self):
        self.widget = wxListBox(self.parent.widget, self.id, choices=self.choices) 
        EVT_LEFT_DOWN(self.widget, self.on_set_focus)

# end of class EditListBox


def builder(parent, sizer, pos, number=[1]):
    """\
    factory function for EditListBox objects.
    """
    name = 'list_box_%d' % number[0]
    while common.app_tree.has_name(name):
        number[0] += 1
        name = 'list_box_%d' % number[0]
    list_box = EditListBox(name, parent, wxNewId(),
                           [misc._encode('choice 1')], sizer, pos,
                           common.property_panel)
    node = Tree.Node(list_box)
    sizer.set_item(pos, size=list_box.GetBestSize())
    list_box.node = node
    common.app_tree.insert(node, sizer.node, pos-1)

def xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    """\
    factory to build EditListBox objects from an xml file
    """
    from xml_parse import XmlParsingError
    try: name = attrs['name']
    except KeyError: raise XmlParsingError, "'name' attribute missing"
    if sizer is None or sizeritem is None:
        raise XmlParsingError, "sizer or sizeritem object cannot be None"
    list_box = EditListBox(name, parent, wxNewId(), [], sizer, pos,
                           common.property_panel)
    sizer.set_item(list_box.pos, option=sizeritem.option,
                   flag=sizeritem.flag, border=sizeritem.border,
                   size=list_box.GetBestSize())
    node = Tree.Node(list_box)
    list_box.node = node
    if pos is None: common.app_tree.add(node, sizer.node)
    else: common.app_tree.insert(node, sizer.node, pos-1)
    return list_box

def code_generator(obj):
    """\
    generates the python code for wxListBox objects
    """
    pygen = common.code_writers['python']
    prop = obj.properties
    id_name, id = pygen.generate_code_id(obj)
    choices = prop.get('choices', [])
    if obj.is_toplevel:
        l = ['self.%s = %s(self, %s, choices=%s)\n' % (obj.name, obj.klass,
                                                       id, repr(choices))]
        if id_name: l.append(id_name)
        return l, [], []
    size = pygen.generate_code_size(obj)
    if not obj.parent.is_toplevel: parent = 'self.%s' % obj.parent.name
    else: parent = 'self'
    style = prop.get("style", "0")
    init = ['self.%s = wxListBox(%s, %s, choices=%s, size=%s, style=%s)\n' %
            (obj.name, parent, id, repr(choices), size, style) ]
    if id_name: init.append(id_name)
    props_buf = []
    selection = prop.get('selection')
    if selection is not None:
        props_buf.append('self.%s.SetSelection(%s)\n' % (obj.name, selection))
    if prop.has_key('foreground'):
        props_buf.append(pygen.generate_code_foreground(obj))
    if prop.has_key('background'):
        props_buf.append(pygen.generate_code_background(obj))
    if prop.has_key('font'): props_buf.append(pygen.generate_code_font(obj))
    return init, props_buf, []

    
def initialize():
    """\
    initialization function for the module: returns a wxBitmapButton to be
    added to the main palette.
    """
    common.widgets['EditListBox'] = builder
    common.widgets_from_xml['EditListBox'] = xml_builder
    common.class_names['EditListBox'] = 'wxListBox'

    # python code generation functions
    pygen = common.code_writers.get("python")
    if pygen:
        pygen.add_widget_handler('wxListBox', code_generator)
        pygen.add_property_handler('choices', ChoicesCodeHandler)

    return common.make_object_button('EditListBox', 'icons/list_box.xpm')
