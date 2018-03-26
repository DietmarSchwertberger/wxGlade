"""\
wxToggleButton objects

@copyright: 2002-2007 Alberto Griggio
@copyright: 2016 Carsten Grohmann
@copyright: 2016 Dietmar Schwertberger
@license: MIT (see LICENSE.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import wx

import common, config
from edit_windows import ManagedBase, EditStylesMixin
from gui_mixins import BitmapMixin
from tree import Node
import new_properties as np


class EditToggleButton(ManagedBase, EditStylesMixin, BitmapMixin):
    "Class to handle wxToggleButton objects"

    _PROPERTIES = ["Widget", "label", "value",
                   "bitmap", "disabled_bitmap", "pressed_bitmap", "current_bitmap", "focus_bitmap",
                   "style"]
    PROPERTIES = ManagedBase.PROPERTIES + _PROPERTIES + ManagedBase.EXTRA_PROPERTIES
    _PROPERTY_LABELS = {"value":"Clicked"}

    def __init__(self, name, parent, id, label, sizer, pos):
        ManagedBase.__init__(self, name, 'wxToggleButton', parent, id, sizer, pos)
        EditStylesMixin.__init__(self)

        # initialise instance variable
        self.label = np.TextProperty("", multiline="grow")
        self.value = np.CheckBoxProperty(False, default_value=False)
        # XXX bitmaps are only for >= 3.0
        self.bitmap          = np.BitmapPropertyD()
        self.disabled_bitmap = np.BitmapPropertyD()
        self.pressed_bitmap  = np.BitmapPropertyD()
        self.current_bitmap  = np.BitmapPropertyD()
        self.focus_bitmap    = np.BitmapPropertyD()

    def create_widget(self):
        self.widget = wx.ToggleButton(self.parent.widget, self.id, self.label)
        self.widget.SetValue(self.value)
        self.widget.Bind(wx.EVT_TOGGLEBUTTON, self.on_set_focus, id=self.id)
        BitmapMixin._set_preview_bitmaps(self)

    def properties_changed(self, modified):
        if not modified or "value" in modified and self.widget:
            self.widget.SetValue(self.value)

        if not modified or "label" in modified:
            if self.widget:
                self.widget.SetLabel(self.label)
                self._set_widget_best_size()
            common.app_tree.refresh(self.node, refresh_label=True)

        if self.widget and modified:
            BitmapMixin._properties_changed(self, modified)
            if self.label and any( "bitmap" in p_name for p_name in modified):
                self._set_widget_best_size()

        EditStylesMixin.properties_changed(self, modified)
        ManagedBase.properties_changed(self, modified)


def builder(parent, sizer, pos, number=[1]):
    "factory function for EditToggleButton objects"
    label = u'button_%d' % number[0]
    while common.app_tree.has_name(label):
        number[0] += 1
        label = u'button_%d' % number[0]
    with parent.frozen():
        button = EditToggleButton(label, parent, wx.NewId(), label, sizer, pos)
        button.properties["style"].set_to_default()
        button.check_defaults()
        node = Node(button)
        button.node = node
        if parent.widget: button.create()
    common.app_tree.insert(node, sizer.node, pos-1)


def xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    "factory to build EditToggleButton objects from a XML file"
    from xml_parse import XmlParsingError
    try:
        label = attrs['name']
    except KeyError:
        raise XmlParsingError(_("'name' attribute missing"))
    if sizer is None or sizeritem is None:
        raise XmlParsingError(_("sizer or sizeritem object cannot be None"))
    button = EditToggleButton(label, parent, wx.NewId(), '', sizer, pos)
    #sizer.set_item(button.pos, proportion=sizeritem.proportion, span=sizeritem.span, flag=sizeritem.flag, border=sizeritem.border)
    node = Node(button)
    button.node = node
    if pos is None:
        common.app_tree.add(node, sizer.node)
    else:
        common.app_tree.insert(node, sizer.node, pos-1)
    return button


def initialize():
    "initialization function for the module: returns a wxBitmapButton to be added to the main palette"
    common.widgets['EditToggleButton'] = builder
    common.widgets_from_xml['EditToggleButton'] = xml_builder

    return common.make_object_button('EditToggleButton', 'toggle_button.xpm')
