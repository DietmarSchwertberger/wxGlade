# button.py: wxButton objects
#
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: Python 2.2 license (see license.txt)

from wxPython.wx import *
import common, misc
from edit_windows import ManagedBase
from tree import Tree
from widget_properties import *


class EditButton(ManagedBase):
    def __init__(self, name, parent, id, label, sizer, pos, property_window,
                 show=True):
        """\
        Class to handle wxButton objects
        """
        self.label = label
        self.default = False
        ManagedBase.__init__(self, name, 'wxButton', parent, id, sizer, pos,
                             property_window, show=show)
        self.access_functions['label'] = (self.get_label, self.set_label)
        self.properties['label'] = TextProperty(self, 'label', None)
        self.access_functions['default'] = (self.get_default, self.set_default)
        self.properties['default'] = CheckBoxProperty(self, 'default', None)

    def create_properties(self):
        ManagedBase.create_properties(self)
        panel = wxPanel(self.notebook, -1)
        self.properties['label'].display(panel)
        self.properties['default'].display(panel)
        szr = wxBoxSizer(wxVERTICAL)
        szr.Add(self.properties['label'].panel, 0, wxEXPAND)
        szr.Add(self.properties['default'].panel, 0, wxEXPAND)
        panel.SetAutoLayout(1)
        panel.SetSizer(szr)
        szr.Fit(panel)
        self.notebook.AddPage(panel, 'Widget')

    def get_label(self):
        return self.label

    def set_label(self, value):
        if value != self.label:
            if self.widget:
                self.widget.SetLabel(value)
                self.set_width(self.widget.GetBestSize()[0])
            self.label = value
            self.old_label = value

    def create_widget(self):
        self.widget = wxButton(self.parent.widget, self.id, self.label)

    def get_default(self):
        return self.default

    def set_default(self, value):
        self.default = bool(value)
        if value and self.widget:
            self.widget.SetDefault()

# end of class EditButton
        
def builder(parent, sizer, pos, number=[1]):
    """\
    factory function for EditButton objects.
    """
    label = 'button_%d' % number[0]
    while common.app_tree.has_name(label):
        number[0] += 1
        label = 'button_%d' % number[0]
    button = EditButton(label, parent, wxNewId(), misc._encode(label), sizer,
                        pos, common.property_panel)
    node = Tree.Node(button)
    button.node = node
    button.show_widget(True)
    common.app_tree.insert(node, sizer.node, pos-1)

def xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    """\
    factory to build EditButton objects from an xml file
    """
    from xml_parse import XmlParsingError
    try: label = attrs['name']
    except KeyError: raise XmlParsingError, "'name' attribute missing"
    if sizer is None or sizeritem is None:
        raise XmlParsingError, "sizer or sizeritem object cannot be None"
    button = EditButton(label, parent, wxNewId(), misc._encode(label), sizer,
                        pos, common.property_panel, show=False)
##     sizer.set_item(button.pos, option=sizeritem.option, flag=sizeritem.flag,
##                    border=sizeritem.border, size=button.GetBestSize())
    node = Tree.Node(button)
    button.node = node
    if pos is None: common.app_tree.add(node, sizer.node)
    else: common.app_tree.insert(node, sizer.node, pos-1)
    return button


def initialize():
    """\
    initialization function for the module: returns a wxBitmapButton to be
    added to the main palette.
    """
    common.widgets['EditButton'] = builder
    common.widgets_from_xml['EditButton'] = xml_builder

    return common.make_object_button('EditButton', 'icons/button.xpm')
