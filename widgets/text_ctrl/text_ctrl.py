# text_ctrl.py: wxTextCtrl objects
#
# Copyright (c) 2002-2003 Alberto Griggio <albgrig@tiscalinet.it>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

from wxPython.wx import *
from edit_windows import ManagedBase
from tree import Tree
import common, misc
from widget_properties import *

class EditTextCtrl(ManagedBase):
    """\
    Class to handle wxTextCtrl objects
    """
    def __init__(self, name, parent, id, sizer, pos, property_window,
                 show=True):
        ManagedBase.__init__(self, name, 'wxTextCtrl', parent, id, sizer, pos,
                             property_window, show=show)
        self.value = ""
        self.style = 0
        self.access_functions['value'] = (self.get_value, self.set_value)
        self.access_functions['style'] = (self.get_style, self.set_style)
        prop = self.properties
        # value property
        prop['value'] = TextProperty(self, 'value', None,
                                     multiline=True)
        # style property
        self.style_pos  = (wxTE_PROCESS_ENTER, wxTE_PROCESS_TAB,
                           wxTE_MULTILINE,wxTE_PASSWORD, wxTE_READONLY,
                           wxHSCROLL, wxTE_RICH)
        style_labels = ('#section#Style', 'wxTE_PROCESS_ENTER',
                        'wxTE_PROCESS_TAB', 'wxTE_MULTILINE', 'wxTE_PASSWORD',
                        'wxTE_READONLY', 'wxHSCROLL', 'wxTE_RICH')
        prop['style'] = CheckListProperty(self, 'style', None, style_labels)

    def create_widget(self):
        value = self.value
        if self.style & wxTE_MULTILINE:
            value = value.replace('\\n', '\n')
        self.widget = wxTextCtrl(self.parent.widget, self.id, value=value)

    def create_properties(self):
        ManagedBase.create_properties(self)
        panel = wxScrolledWindow(self.notebook, -1, style=wxTAB_TRAVERSAL) 
        prop = self.properties
        prop['value'].display(panel)
        prop['style'].display(panel)
        szr = wxBoxSizer(wxVERTICAL)
        szr.Add(prop['value'].panel, 0, wxEXPAND)
        szr.Add(prop['style'].panel, 0, wxEXPAND)
        panel.SetAutoLayout(True)
        panel.SetSizer(szr)
        szr.Fit(panel)
        self.notebook.AddPage(panel, 'Widget')

    def get_value(self):
        return self.value

    def set_value(self, value):
        value = str(value)
        if value != self.value:
            self.value = value
            if self.style & wxTE_MULTILINE:
                value = value.replace('\\n', '\n')
            if self.widget: self.widget.SetValue(value)

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
        # the next line caused troubles with 2.3.3pre5 on GTK
        #if self.widget: self.widget.SetWindowStyleFlag(self.style)

# end of class EditTextCtrl


def builder(parent, sizer, pos, number=[1]):
    """\
    factory function for EditTextCtrl objects.
    """
    name = 'text_ctrl_%d' % number[0]
    while common.app_tree.has_name(name):
        number[0] += 1
        name = 'text_ctrl_%d' % number[0]
    text = EditTextCtrl(name, parent, wxNewId(), sizer, pos,
                        common.property_panel)
    node = Tree.Node(text)
    text.node = node
    text.show_widget(True)
    common.app_tree.insert(node, sizer.node, pos-1)

def xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    """\
    factory function to build EditTextCtrl objects from an xml file
    """
    from xml_parse import XmlParsingError
    try: name = attrs['name']
    except KeyError: raise XmlParsingError, "'name' attribute missing"
    if sizer is None or sizeritem is None:
        raise XmlParsingError, "sizer or sizeritem object cannot be None"
    text = EditTextCtrl(name, parent, wxNewId(), sizer, pos,
                        common.property_panel)
    sizer.set_item(text.pos, option=sizeritem.option, flag=sizeritem.flag,
                   border=sizeritem.border)
    node = Tree.Node(text)
    text.node = node
    if pos is None: common.app_tree.add(node, sizer.node)
    else: common.app_tree.insert(node, sizer.node, pos-1)
    return text


def initialize():
    """\
    initialization function for the module: returns a wxBitmapButton to be
    added to the main palette.
    """
    common.widgets['EditTextCtrl'] = builder
    common.widgets_from_xml['EditTextCtrl'] = xml_builder
        
    return common.make_object_button('EditTextCtrl', 'icons/text_ctrl.xpm')
