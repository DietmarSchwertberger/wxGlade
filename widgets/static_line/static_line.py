# static_line.py: wxStaticLine objects
#
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: Python 2.2 license (see license.txt)

from wxPython.wx import *
import common
from edit_windows import ManagedBase
from tree import Tree
from widget_properties import *

class EditStaticLine(ManagedBase):
    def __init__(self, name, parent, id, orientation, sizer, pos,
                 property_window, show=True):
        """\
        Class to handle wxStaticLine objects
        """
        self.orientation = orientation
        ManagedBase.__init__(self, name, 'wxStaticLine', parent, id, sizer,
                             pos, property_window, show=show)
        self.access_functions['style'] = (self.get_orientation,
                                          self.set_orientation)
        self.properties['style'] = HiddenProperty(self, 'style')
        self.removed_p = self.properties['font']

    def create_widget(self):
        #self.orientation = int(self.property['style'].get_value())
        self.widget = wxStaticLine(self.parent.widget, self.id,
                                   style=self.orientation)
        EVT_LEFT_DOWN(self.widget, self.on_set_focus)

    def finish_widget_creation(self):
        ManagedBase.finish_widget_creation(self)
        self.sel_marker.Reparent(self.parent.widget)        
        del self.properties['font']

    def create_properties(self):
        ManagedBase.create_properties(self)
        if self.removed_p.panel: self.removed_p.panel.Hide()

    def __getitem__(self, key):
        if key != 'font': return ManagedBase.__getitem__(self, key)
        return (lambda : "", lambda v: None)

    def get_orientation(self): 
        od = { wxLI_HORIZONTAL: 'wxLI_HORIZONTAL',
               wxLI_VERTICAL: 'wxLI_VERTICAL' }
        return od.get(self.orientation, 'wxLI_HORIZONTAL')
    
    def set_orientation(self, value):
        od = { 'wxLI_HORIZONTAL': wxLI_HORIZONTAL,
               'wxLI_VERTICAL': wxLI_VERTICAL }
        self.orientation = od.get(value, wxLI_HORIZONTAL)

# end of class EditStaticLine
        

def builder(parent, sizer, pos, number=[1]):
    """\
    factory function for EditStaticLine objects.
    """
    class Dialog(wxDialog):
        def __init__(self):
            wxDialog.__init__(self, None, -1, 'Select orientation')
            self.orientations = [ wxLI_HORIZONTAL, wxLI_VERTICAL ]
            self.orientation = wxLI_HORIZONTAL
            prop = RadioProperty(self, 'orientation', self,
                                 ['wxLI_HORIZONTAL', 'wxLI_VERTICAL'])
            szr = wxBoxSizer(wxVERTICAL)
            szr.Add(prop.panel, 0, wxALL|wxEXPAND, 10)
            btn = wxButton(self, wxID_OK, 'OK')
            btn.SetDefault()
            szr.Add(btn, 0, wxBOTTOM|wxALIGN_CENTER, 10)
            self.SetAutoLayout(True)
            self.SetSizer(szr)
            szr.Fit(self)
        def __getitem__(self, value):
            def set_orientation(o): self.orientation = self.orientations[o]
            return (lambda: self.orientation, set_orientation)
    # end of inner class

    dialog = Dialog()
    dialog.ShowModal()
    
    label = 'static_line_%d' % number[0]
    while common.app_tree.has_name(label):
        number[0] += 1
        label = 'static_line_%d' % number[0]
    static_line = EditStaticLine(label, parent, wxNewId(), dialog.orientation,
                                 sizer, pos, common.property_panel)
    node = Tree.Node(static_line)
    static_line.node = node
    static_line.set_flag("wxEXPAND")
    static_line.show_widget(True)
    common.app_tree.insert(node, sizer.node, pos-1) 


def xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    """\
    factory to build EditStaticLine objects from an xml file
    """
    from xml_parse import XmlParsingError
    try: name = attrs['name']
    except KeyError: raise XmlParsingError, "'name' attribute missing"
    if sizer is None or sizeritem is None:
        raise XmlParsingError, "sizer or sizeritem object cannot be None"
    static_line = EditStaticLine(name, parent, wxNewId(), 0, sizer,
                                 pos, common.property_panel)
    sizer.set_item(static_line.pos, option=sizeritem.option,
                   flag=sizeritem.flag, border=sizeritem.border)
    node = Tree.Node(static_line)
    static_line.node = node
    if pos is None: common.app_tree.add(node, sizer.node)
    else: common.app_tree.insert(node, sizer.node, pos-1)
    return static_line


def initialize():
    """\
    initialization function for the module: returns a wxBitmapButton to be
    added to the main palette.
    """
    common.widgets['EditStaticLine'] = builder
    common.widgets_from_xml['EditStaticLine'] = xml_builder
    
    return common.make_object_button('EditStaticLine', 'icons/static_line.xpm')
