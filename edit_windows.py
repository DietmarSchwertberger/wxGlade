# edit_windows.py: base classes for windows used by wxGlade
# $Id: edit_windows.py,v 1.57 2004/08/15 12:01:45 agriggio Exp $
# 
# Copyright (c) 2002-2003 Alberto Griggio <albgrig@tiscalinet.it>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

from wxPython.wx import *
from widget_properties import *
from tree import Tree, WidgetTree
import math, misc, common, sys, config
import re


class EditBase:
    """\
    Base class of every window available in the builder.
    """
    def __init__(self, name, klass, parent, id, property_window, show=True,
                 custom_class=True):
        # property_window: widget inside which Properties of this object
        #                  are displayed
        # name: name of the object
        # klass: name of the object's class
        # custom_class: if true, the user can chage the value of the 'class'
        #               property
        
        # dictionary of properties relative to this object; the properties that
        # control the layout (i.e. the behaviour when inside a sizer) are not
        # contained here, but in a separate list (see ManagedBase)
        # the keys of the dict are the names of the properties
        self.properties = {}
        self.parent = parent
        # id used for internal purpose events
        self.id = id
        self.name = name
        self.klass = klass
        self.base = klass
        self.custom_class = custom_class

        self._dont_destroy = False

        self.access_functions = {
            'name' : (lambda : self.name, self.set_name),
            'class' : (lambda : self.klass, self.set_klass)
            }

        # these two properties are special and are not listed in
        # 'self.properties'
        self.name_prop = TextProperty(self, 'name', None)
        self.klass_prop = TextProperty(self, 'class', None,
                                       readonly=not custom_class)
        if custom_class:
            self.klass_prop.tooltip = "If you change the default value, " \
                                      "it will be interpreted as the name " \
                                      "of the subclass of the widget. " \
                                      "How this name affects code generation "\
                                      "depends on the kind (i.e. language) " \
                                      "of output. See the docs for " \
                                      "more details."
        self.notebook = None
        self.property_window = property_window

        # popup menu
        self._rmenu = None

        # this is the reference to the actual wxWindow widget; it is created
        # only if needed, i.e. when it should become visible
        self.widget = None

        if show:
            self.show_widget(True)
            property_window.SetSize((250, 340))
            property_window.Show(True)

    def show_widget(self, yes):
        if yes and self.widget is None:
            self.create_widget()
            self.finish_widget_creation()
        if self.widget: self.widget.Show(yes)
    
    def create_widget(self):
        """\
        Initializes self.widget and shows it
        """
        raise NotImplementedError

    def finish_widget_creation(self, *args, **kwds):
        """\
        Creates the popup menu and connects some event handlers to self.widgets
        """
        EVT_RIGHT_DOWN(self.widget, self.popup_menu)

    def delete(self):
        """\
        Destructor. Deallocates the popup menu, the notebook and all the
        properties. Why we need explicit deallocation? Well, basically because
        otherwise we get a lot of memory leaks... :)
        """
        # first, destroy the popup menu...
        if wxPlatform != '__WXMAC__':
            if self._rmenu: self._rmenu.Destroy()
        # ...then, destroy the property notebook...
        if self.notebook:
            nb_szr = self.notebook.sizer
            self.notebook.DeleteAllPages()
            self.notebook.Destroy()
            nb_szr.Destroy()
        # ...finally, destroy our widget (if needed)
        if self.widget and not self._dont_destroy:
            self.widget.Destroy()
        if misc.focused_widget is self: misc.focused_widget = None
            
    def create_properties(self):
        """\
        Creates the notebook with the properties of self
        """
        self.notebook = wxNotebook(self.property_window, -1)

        nb_sizer = wxNotebookSizer(self.notebook)
        self.notebook.SetAutoLayout(True)
        self.notebook.sizer = nb_sizer
        self.notebook.Hide()

        self._common_panel = panel = wxScrolledWindow(self.notebook, -1,
                                                      style=wxTAB_TRAVERSAL)

        self.name_prop.display(panel)
        self.klass_prop.display(panel)

    def __getitem__(self, value):
        return self.access_functions[value]

    def set_name(self, value):
        value = "%s" % value
        if not config.preferences.allow_duplicate_names and \
               (self.widget and common.app_tree.has_name(value)):
            wxMessageBox('Name "%s" is already in use.\n'
                         'Please enter a different one.' % value, "Error",
                         wxOK|wxICON_ERROR)
            self.name_prop.set_value(self.name)
            return
        if not re.match(self.set_name_pattern, value):
            self.name_prop.set_value(self.name)
        else:
            self.name = value
            if self._rmenu: self._rmenu.SetTitle(self.name)
            try: common.app_tree.set_name(self.node, self.name)
            except AttributeError: pass
            self.property_window.SetTitle('Properties - <%s>' % self.name)
    set_name_pattern = re.compile('^[a-zA-Z]+[\w0-9]*$')

    def set_klass(self, value):
        value = "%s" % value
        if not re.match(self.set_klass_pattern, value):
            self.klass_prop.set_value(self.klass)
        else:
            self.klass = value
    set_klass_pattern = re.compile('^[a-zA-Z]+[\w:.0-9]*$')

    def popup_menu(self, event):
        if self.widget:
            if not self._rmenu:
                COPY_ID, REMOVE_ID, CUT_ID = [wxNewId() for i in range(3)]
                self._rmenu = misc.wxGladePopupMenu(self.name)
                misc.append_item(self._rmenu, REMOVE_ID, 'Remove\tDel',
                                 'remove.xpm')
                misc.append_item(self._rmenu, COPY_ID, 'Copy\tCtrl+C',
                                 'copy.xpm')
                misc.append_item(self._rmenu, CUT_ID, 'Cut\tCtrl+X',
                                 'cut.xpm')
                EVT_MENU(self.widget, REMOVE_ID, self.remove)
                EVT_MENU(self.widget, COPY_ID, self.clipboard_copy)
                EVT_MENU(self.widget, CUT_ID, self.clipboard_cut)
                
            self.widget.PopupMenu(self._rmenu, event.GetPosition())

    def remove(self, *args):
        self._dont_destroy = False # always destroy when explicitly asked
        common.app_tree.remove(self.node)

    def show_properties(self, *args):
        """\
        Updates property_window to display the properties of self
        """
        if not self.is_visible(): return # don't do anything if self is hidden
        # create the notebook the first time the function is called: this
        # allows us to create only the notebooks we really need
        if self.notebook is None: self.create_properties()
        sizer_tmp = self.property_window.GetSizer()
        sizer_tmp = wxPyTypeCast(sizer_tmp, "wxBoxSizer")
        child = wxPyTypeCast(sizer_tmp.GetChildren()[0], "wxSizerItem")
        w = child.GetWindow()
        if w is self.notebook: return
        w.Hide()

        self.notebook.Reparent(self.property_window)
        child.SetWindow(self.notebook)
        w.Reparent(misc.hidden_property_panel)
        
        self.property_window.Layout()
        self.property_window.SetTitle('Properties - <%s>' % self.name)
        try: common.app_tree.select_item(self.node)
        except AttributeError: pass
        self.notebook.Show()
        self.widget.SetFocus()
        
    def on_set_focus(self, event):
        """\
        Event handler called when a window receives the focus: this in fact is
        connected to a EVT_LEFT_DOWN and not to an EVT_FOCUS, but the effect
        is the same
        """
        self.show_properties()
        misc.focused_widget = self
        #if wxPlatform != '__WXMSW__': event.Skip()

    def get_property_handler(self, prop_name):
        """\
        returns a custom handler function for the property 'prop_name', used
        when loading this object from an xml file. handler must provide
        three methods: 'start_elem', 'end_elem' and 'char_data'
        """
        return None

    def clipboard_copy(self, *args):
        """\
        returns a copy of self to be inserted in the clipboard
        """
        import clipboard
        clipboard.copy(self)

    def clipboard_cut(self, *args):
        import clipboard
        clipboard.cut(self)

    def is_visible(self):
        if not self.widget: return False
        if not self.widget.IsShown(): return False
        if self.widget.IsTopLevel():
            return self.widget.IsShown()
        parent = self.parent
        if parent: return parent.is_visible()
        return self.widget.IsShown()

    def update_view(self, selected):
        """\
        updates the widget's view to reflect its state, i.e. shows which widget
        is currently selected; the default implementation does nothing.
        """
        pass

    def post_load(self):
        """\
        Called after the loading of an app from an XML file, before showing
        the hierarchy of widget for the first time. The default implementation
        does nothing.
        """
        pass

# end of class EditBase


class WindowBase(EditBase):
    """\
    Extends EditBase with the addition of the common properties available to
    almost every window: size, background and foreground colors, and font
    """
    def __init__(self, name, klass, parent, id, property_window, show=True):
        EditBase.__init__(self, name, klass, parent, id, property_window,
                          show=False)
        # 'property' id (editable by the user) 
        self.window_id = -1

        def set_id(value):
            self.window_id = value
        self.access_functions['id'] = (lambda s=self: s.window_id, set_id)
        self.size = '-1, -1'
        self.access_functions['size'] = (self.get_size, self.set_size)
        self.background = ''
        self.access_functions['background'] = (self.get_background,
                                               self.set_background)
        self.foreground = ''
        self.access_functions['foreground'] = (self.get_foreground,
                                               self.set_foreground)
        # this is True if the user has selected a custom font
        self._font_changed = False
        self.font = self._build_from_font(wxSystemSettings_GetSystemFont(
            wxSYS_DEFAULT_GUI_FONT))
        self.font[1] = 'default'
        
        self.access_functions['font'] = (self.get_font, self.set_font)

        # properties added 2002-08-15
        self.tooltip = ''
        self.access_functions['tooltip'] = (self.get_tooltip, self.set_tooltip)

        min_x = wxSystemSettings_GetSystemMetric(wxSYS_WINDOWMIN_X)
        min_y = wxSystemSettings_GetSystemMetric(wxSYS_WINDOWMIN_Y)
        max_x = wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_X)
        max_y = wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_Y)

        self._original = {'background': None, 'foreground': None,
                          'font': None}        

        prop = self.properties
        prop['id'] = TextProperty(self, 'id', None, can_disable=True)
        prop['size'] = TextProperty(self, 'size', None, can_disable=True)
        prop['background'] = ColorDialogProperty(self, "background", None)
        prop['foreground'] = ColorDialogProperty(self, "foreground", None)
        prop['font'] = FontDialogProperty(self, "font", None)

        # properties added 2002-08-15
        prop['tooltip'] = TextProperty(self, 'tooltip', None, can_disable=True)

        # properties added 2003-05-15
        self.disabled_p = False
        self.access_functions['disabled'] = (self.get_disabled,
                                             self.set_disabled)
        prop['disabled'] = CheckBoxProperty(self, 'disabled', None)
        
        self.focused_p = False
        self.access_functions['focused'] = (self.get_focused, self.set_focused)
        prop['focused'] = CheckBoxProperty(self, 'focused', None)

        self.hidden_p = False
        self.access_functions['hidden'] = (self.get_hidden, self.set_hidden)
        prop['hidden'] = CheckBoxProperty(self, 'hidden', None)

    def finish_widget_creation(self, *args, **kwds):
        self._original['background'] = self.widget.GetBackgroundColour()
        self._original['foreground'] = self.widget.GetForegroundColour()
        fnt = self.widget.GetFont()
        if not fnt.Ok():
            fnt = wxSystemSettings_GetSystemFont(wxSYS_DEFAULT_GUI_FONT)
        self._original['font'] = fnt
        
        prop = self.properties
        size = prop['size'].get_value()
        if size:
            #self.widget.SetSize([int(s) for s in size.split(',')])
            self.set_size(size)
        else:
            prop['size'].set_value('%s, %s' % tuple(self.widget.GetSize()))
        if prop['background'].is_active():
            self.set_background(prop['background'].get_value())
        else:
            color = misc.color_to_string(self.widget.GetBackgroundColour())
            self.background = color
            prop['background'].set_value(color)
        if prop['foreground'].is_active():
            self.set_foreground(prop['foreground'].get_value())
        else:
            color = misc.color_to_string(self.widget.GetForegroundColour())
            self.foreground = color
            prop['foreground'].set_value(color)
        if prop['font'].is_active():
            self.set_font(prop['font'].get_value())
        EditBase.finish_widget_creation(self)
        EVT_SIZE(self.widget, self.on_size)
        # after setting various Properties, we must Refresh widget in order to
        # see changes
        self.widget.Refresh()

        def on_key_down(event):
            evt_flags = 0
            if event.ControlDown(): evt_flags = wxACCEL_CTRL
            evt_key = event.GetKeyCode()
            for flags, key, function in misc.accel_table:
                if evt_flags == flags and evt_key == key:
                    misc.wxCallAfter(function)
                    break
            event.Skip()
        EVT_KEY_DOWN(self.widget, on_key_down)

    def create_properties(self):
        EditBase.create_properties(self)
        min_x = wxSystemSettings_GetSystemMetric(wxSYS_WINDOWMIN_X)
        min_y = wxSystemSettings_GetSystemMetric(wxSYS_WINDOWMIN_Y)
        max_x = wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_X)
        max_y = wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_Y)

        panel = self._common_panel
            
        prop = self.properties
        prop['id'].display(panel)
        prop['size'].display(panel)
        
        prop['background'].display(panel) 
        prop['foreground'].display(panel)
        try: prop['font'].display(panel) 
        except KeyError: pass
        # new properties 2002-08-15
        prop['tooltip'].display(panel)
        # new properties 2003-05-15
        prop['disabled'].display(panel)
        prop['focused'].display(panel)
        prop['hidden'].display(panel)

        sizer_tmp = wxBoxSizer(wxVERTICAL)
        sizer_tmp.Add(self.name_prop.panel, 0, wxEXPAND)
        sizer_tmp.Add(self.klass_prop.panel, 0, wxEXPAND)
        sizer_tmp.Add(prop['id'].panel, 0, wxEXPAND)
        sizer_tmp.Add(prop['size'].panel, 0, wxEXPAND)
        sizer_tmp.Add(prop['background'].panel, 0, wxEXPAND)
        sizer_tmp.Add(prop['foreground'].panel, 0, wxEXPAND)
        try: sizer_tmp.Add(prop['font'].panel, 0, wxEXPAND)
        except KeyError: pass
        sizer_tmp.Add(prop['tooltip'].panel, 0, wxEXPAND)
        sizer_tmp.Add(prop['disabled'].panel, 0, wxEXPAND)
        sizer_tmp.Add(prop['focused'].panel, 0, wxEXPAND)
        sizer_tmp.Add(prop['hidden'].panel, 0, wxEXPAND)
        
        panel.SetAutoLayout(1)
        panel.SetSizer(sizer_tmp)
        sizer_tmp.Layout()
        sizer_tmp.Fit(panel)

        w, h = panel.GetClientSize()
        self.notebook.AddPage(panel, "Common")
        self.property_window.Layout()
        panel.SetScrollbars(1, 5, 1, int(math.ceil(h/5.0)))


    def on_size(self, event):
        """\
        update the value of the 'size' property
        """
        try:
            w_1, h_1 = 0, 0
            sz = self.properties['size']
            if sz.is_active():
                # try to preserve the user's choice
                try: use_dialog_units = (sz.get_value().strip()[-1] == 'd')
                except IndexError: use_dialog_units = False
                val = sz.get_value()
                if use_dialog_units: val = val[:-1]
                w_1, h_1 = [int(t) for t in val.split(',')]
            else: use_dialog_units = config.preferences.use_dialog_units #False
            if use_dialog_units:
                w, h = self.widget.ConvertPixelSizeToDialog(
                    self.widget.GetSize())
            else:
                w, h = self.widget.GetSize()
            if w_1 == -1: w = -1
            if h_1 == -1: h = -1
            size = "%s, %s" % (w, h)
            if use_dialog_units: size += "d"
            self.properties['size'].set_value(size)
            self.size = size
        except KeyError: pass
        event.Skip()

    def get_tooltip(self):
        return self.tooltip

    def set_tooltip(self, value):
        self.tooltip = misc.wxstr(value)

    def get_background(self):
        return self.background

    def get_foreground(self):
        return self.foreground

    def set_background(self, value):
        oldval = self.background
        self.background = value        
        if not self.widget: return
        value = value.strip()
        if value in ColorDialogProperty.str_to_colors:
            self.widget.SetBackgroundColour(wxSystemSettings_GetSystemColour(
                ColorDialogProperty.str_to_colors[value]))
        else:
            try:
                color = misc.string_to_color(value)
                self.widget.SetBackgroundColour(color)
            except:
                self.background = oldval
                self.properties['background'].set_value(self.get_background())
                return
        self.widget.Refresh()
            
    def set_foreground(self, value):
        oldval = self.foreground
        self.foreground = value
        if not self.widget: return
        value = value.strip()
        if value in ColorDialogProperty.str_to_colors:
            self.widget.SetForegroundColour(wxSystemSettings_GetSystemColour(
                ColorDialogProperty.str_to_colors[value]))
        else:
            try:
                color = misc.string_to_color(value)
                self.widget.SetForegroundColour(color)
            except:
                self.foreground = oldval
                self.properties['foreground'].set_value(self.get_foreground())
                return
        self.foreground = value
        self.widget.Refresh()

    def get_font(self):
        return str(self.font)
    
    def _build_from_font(self, font):
        families = FontDialogProperty.font_families_from
        styles = FontDialogProperty.font_styles_from
        weights = FontDialogProperty.font_weights_from
        return [ str(font.GetPointSize()),
                 families.get(font.GetFamily(), 'default'),
                 styles.get(font.GetStyle(), 'normal'),
                 weights.get(font.GetWeight(), 'normal'),
                 str(int(font.GetUnderlined())), font.GetFaceName() ]

    def set_font(self, value):
        #if not self.widget: return
        families = FontDialogProperty.font_families_to
        styles = FontDialogProperty.font_styles_to
        weights = FontDialogProperty.font_weights_to
        try:
            value = eval(value)
            f = wxFont(int(value[0]), families[value[1]], styles[value[2]],
                       weights[value[3]], int(value[4]), value[5])
        except:
            #import traceback; traceback.print_exc()
            self.properties['font'].set_value(self.get_font())
        else:
            self.font = value
            if self.widget:
                old_size = self.widget.GetSize()
                self.widget.SetFont(f)
                size = self.widget.GetSize()
                if size != old_size:
                    self.sizer.set_item(self.pos, size=size)

    def set_width(self, value):
        self.set_size((int(value), -1))

    def set_height(self, value):
        self.set_size((-1, int(value)))

    def set_size(self, value):
        #if not self.widget: return
        if self.properties['size'].is_active():
            v = self.properties['size'].get_value().strip()
            use_dialog_units = v and v[-1] == 'd'
        else:
            use_dialog_units = config.preferences.use_dialog_units #False
        try: "" + value
        except TypeError: pass
        else: # value is a string-like object
            if value and value.strip()[-1] == 'd':
                use_dialog_units = True
                value = value[:-1]
        try:
            size = [int(t.strip()) for t in value.split(',', 1)]
        except:
            self.properties['size'].set_value(self.size)
        else:
            if use_dialog_units and value[-1] != 'd': value += 'd'
            self.size = value
            if self.widget:
                if use_dialog_units: size = wxDLG_SZE(self.widget, size)
                self.widget.SetSize(size)
                try:
                    self.sizer.set_item(self.pos, size=self.widget.GetSize())
                except AttributeError: pass

    def get_size(self):
        return self.size

    def get_property_handler(self, name):
        if name == 'font':
            class FontHandler:
                def __init__(self, owner):
                    self.owner = owner
                    self.props = [ '' for i in range(6) ]
                    self.index = 0
                def start_elem(self, name, attrs):
                    index = { 'size': 0, 'family': 1, 'style': 2, 'weight': 3,
                              'underlined': 4, 'face': 5 }
                    self.index = index.get(name, 5)
                def end_elem(self, name):
                    if name == 'font':
                        self.owner.properties['font'].set_value(
                            repr(self.props))
                        self.owner.properties['font'].toggle_active(True)
                        self.owner.set_font(repr(self.props))
                        return True # to remove this handler
                def char_data(self, data):
                    self.props[self.index] = str(data.strip())
            # end of class FontHandler
            return FontHandler(self)
        return None

    def get_disabled(self):
        return self.disabled_p

    def set_disabled(self, value):
        try: self.disabled_p = bool(int(value))
        except ValueError: pass

    def get_focused(self):
        return self.focused_p

    def set_focused(self, value):
        try: self.focused_p = bool(int(value))
        except ValueError: pass

    def get_hidden(self):
        return self.hidden_p

    def set_hidden(self, value):
        try: self.hidden_p = bool(int(value))
        except ValueError: pass

# end of class WindowBase


class ManagedBase(WindowBase):
    """\
    Base class for every managed window used by the builder: extends WindowBase
    with the addition of properties relative to the layout of the window:
    option, flag, and border
    """
    def __init__(self, name, klass, parent, id, sizer, pos, property_window,
                 show=True):
        WindowBase.__init__(self, name, klass, parent, id, property_window,
                            show=show)
        # if True, the user is able to control the layout of the widget
        # inside the sizer (proportion, borders, alignment...)
        self._has_layout = not sizer.is_virtual()
        # selection markers
        self.sel_marker = None
        # dictionary of properties relative to the sizer which
        # controls this window
        self.sizer_properties = {}
        # attributes to keep the values of the sizer_properties
        self.option = 0
        self.flag = 0
        self.border = 0
        
        self.sizer = sizer
        self.pos = pos
        self.access_functions['option'] = (self.get_option, self.set_option)
        self.access_functions['flag'] = (self.get_flag, self.set_flag)
        self.access_functions['border'] = (self.get_border, self.set_border)
        self.access_functions['pos'] = (self.get_pos, self.set_pos)
        self.flags_pos = (wxALL,
                          wxLEFT, wxRIGHT, wxTOP, wxBOTTOM,
                          wxEXPAND, wxALIGN_RIGHT, wxALIGN_BOTTOM,
                          wxALIGN_CENTER_HORIZONTAL, wxALIGN_CENTER_VERTICAL,
                          wxSHAPED, wxADJUST_MINSIZE)
        sizer.add_item(self, pos)

        szprop = self.sizer_properties
        szprop['option'] = SpinProperty(self, "option", None, 0, (0, 1000))
        flag_labels = ('#section#Border',
                       'wxALL',
                       'wxLEFT', 'wxRIGHT',
                       'wxTOP', 'wxBOTTOM',
                       '#section#Alignment', 'wxEXPAND', 'wxALIGN_RIGHT',
                       'wxALIGN_BOTTOM', 'wxALIGN_CENTER_HORIZONTAL',
                       'wxALIGN_CENTER_VERTICAL', 'wxSHAPED',
                       'wxADJUST_MINSIZE')
        szprop['flag'] = CheckListProperty(self, 'flag', None, flag_labels)
        szprop['border'] = SpinProperty(self, 'border', None, 0, (0, 1000))
        pos_p = szprop['pos'] = SpinProperty(self, 'pos', None, 0, (0, 1000))
        def write(*args, **kwds): pass
        pos_p.write = write # no need to save the position

    def finish_widget_creation(self, sel_marker_parent=None):
        if sel_marker_parent is None: sel_marker_parent = self.parent.widget
        self.sel_marker = misc.SelectionMarker(self.widget, sel_marker_parent)
        WindowBase.finish_widget_creation(self)
        EVT_LEFT_DOWN(self.widget, self.on_set_focus)
        EVT_MOVE(self.widget, self.on_move)
        # re-add the item to update it
        self.sizer.add_item(self, self.pos, self.option, self.flag,
                            self.border, self.widget.GetSize())
        # set the value of the properties
        szp = self.sizer_properties
        szp['option'].set_value(self.get_option())
        szp['flag'].set_value(self.get_flag())
        szp['border'].set_value(self.get_border())
        szp['pos'].set_value(self.pos-1)

    def create_properties(self):
        WindowBase.create_properties(self)
        if not self._has_layout: return
        panel = wxScrolledWindow(self.notebook, -1, style=wxTAB_TRAVERSAL)

        min_x = wxSystemSettings_GetSystemMetric(wxSYS_WINDOWMIN_X)
        min_y = wxSystemSettings_GetSystemMetric(wxSYS_WINDOWMIN_Y)
        max_x = wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_X)
        max_y = wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_Y)

        szprop = self.sizer_properties
        szprop['option'].display(panel)
        szprop['flag'].display(panel)
        szprop['border'].display(panel)
        szprop['pos'].display(panel)

        sizer_tmp = wxBoxSizer(wxVERTICAL)
        sizer_tmp.Add(szprop['pos'].panel, 0, wxEXPAND)
        sizer_tmp.Add(szprop['option'].panel, 0, wxEXPAND)
        sizer_tmp.Add(szprop['border'].panel, 0, wxEXPAND)
        sizer_tmp.Add(szprop['flag'].panel, 0, wxEXPAND, 5)
        panel.SetAutoLayout(True)
        panel.SetSizer(sizer_tmp)
        sizer_tmp.Layout()
        sizer_tmp.Fit(panel)

        w, h = panel.GetClientSize()
        self.notebook.AddPage(panel, "Layout")
        panel.SetScrollbars(1, 5, 1, int(math.ceil(h/5.0)))
        
    def update_view(self, selected):
        if self.sel_marker: self.sel_marker.Show(selected)

    def on_move(self, event): self.sel_marker.update()
    def on_size(self, event):
        WindowBase.on_size(self, event)
        self.sel_marker.update()

    def set_option(self, value):
        self.option = value = int(value)
        if not self.widget: return
        try:
            sz = self.properties['size']
            if value or sz.is_active():
                size = sz.get_value().strip()
                if size[-1] == 'd':
                    size = size[:-1]
                    use_dialog_units = True
                else: use_dialog_units = False
                w, h = [ int(v) for v in size.split(',') ]
                if use_dialog_units:
                    w, h = wxDLG_SZE(self.widget, (w, h))
            else: w, h = self.widget.GetBestSize()
            self.sizer.set_item(self.pos, option=value, size=(w, h))
        except AttributeError, e:
            print e

    def set_flag(self, value):
        value = self.sizer_properties['flag'].prepare_value(value)
        flags = 0
        for v in range(len(value)):
            if value[v]:
                flags |= self.flags_pos[v]
        self.flag = flags
        if not self.widget: return
        try:
            try:
                sp = self.properties['size']
                size = sp.get_value().strip()
                if size[-1] == 'd':
                    size = size[:-1]
                    use_dialog_units = True
                else: use_dialog_units = False
                w, h = [ int(v) for v in size.split(',') ]
                if use_dialog_units:
                    w, h = wxDLG_SZE(self.widget, (w, h))
                size = [w, h]
            except ValueError:
                size = None
            if not (flags & wxEXPAND) and \
               not self.properties['size'].is_active():
                size = list(self.widget.GetBestSize())
            self.sizer.set_item(self.pos, flag=flags, size=size)
        except AttributeError, e:
            import traceback; traceback.print_exc()

    def set_border(self, value):
        self.border = int(value)
        if not self.widget: return
        try:
            sp = self.properties['size']
            size = sp.get_value().strip()
            if size[-1] == 'd':
                size = size[:-1]
                use_dialog_units = True
            else: use_dialog_units = False
            w, h = [ int(v) for v in size.split(',') ]
            if use_dialog_units:
                w, h = wxDLG_SZE(self.widget, (w, h))
            if w == -1: w = self.widget.GetSize()[0]
            if h == -1: h = self.widget.GetSize()[1]
            self.sizer.set_item(self.pos, border=int(value), size=(w, h))
        except AttributeError, e:
            import traceback; traceback.print_exc()

    def get_option(self):
        return self.option

    def get_flag(self):
        retval = [0] * len(self.flags_pos)
        try:
            for i in range(len(self.flags_pos)):
                if self.flag & self.flags_pos[i]:
                    retval[i] = 1
            # patch to make wxALL work
            if retval[1:5] == [1, 1, 1, 1]:
                retval[0] = 1; retval[1:5] = [0, 0, 0, 0]
            else:
                retval[0] = 0
        except AttributeError: pass
        return retval

    def get_int_flag(self):
        return self.flag

    def get_border(self):
        return self.border

    def delete(self):
        if self.sel_marker:
            self.sel_marker.Destroy() # destroy the selection markers
        WindowBase.delete(self)

    def remove(self, *args):
        self.sizer.free_slot(self.pos)
        WindowBase.remove(self)

    def get_pos(self): return self.pos-1
    def set_pos(self, value):
        """setter for the 'pos' property: calls self.sizer.change_item_pos"""
        self.sizer.change_item_pos(self, min(value + 1,
                                             len(self.sizer.children) - 1))
        
    def update_pos(self, value):
        """\
        called by self.sizer.change_item_pos to update the item's position
        when another widget is moved
        """
        self.sizer_properties['pos'].set_value(value-1)
        self.pos = value

# end of class ManagedBase


class PreviewMixin:
    """Mixin class used to add preview to a widget"""
    def __init__(self):
        self.preview_button = None
        self.preview_widget = None

    def create_properties(self):
        panel = self.notebook.GetPage(0)
        sizer_tmp = panel.GetSizer()
        # add a preview button to the Common panel for top-levels
        self.preview_button = btn = wxButton(panel, -1, 'Preview')
        EVT_BUTTON(btn, -1, self.preview)
        sizer_tmp.Add(btn, 0, wxALL|wxEXPAND, 5)
        sizer_tmp.Layout()
        sizer_tmp.Fit(panel)
        w, h = panel.GetClientSize()
        self.property_window.Layout()
        import math
        panel.SetScrollbars(1, 5, 1, int(math.ceil(h/5.0)))

    def preview(self, event):
        #print 'frame class _> ', self.klass
        if self.preview_widget is None:
            self.preview_widget = common.app_tree.app.preview(self)
            self.preview_button.SetLabel('Close Preview')
        else:
            # Close triggers the EVT_CLOSE that does the real work
            # (see application.py -> preview)
            self.preview_widget.Close()

# end of class PreviewMixin


class TopLevelBase(WindowBase, PreviewMixin):
    """\
    Base class for every non-managed window (i.e. Frames and Dialogs).
    """
    _is_toplevel = True
    
    def __init__(self, name, klass, parent, id, property_window, show=True,
                 has_title=True):
        WindowBase.__init__(self, name, klass, parent, id, property_window,
                            show=show)
        self.has_title = has_title
        if self.has_title:
            self.title = self.name
            self.access_functions['title'] = (self.get_title, self.set_title)
            self.properties['title'] = TextProperty(self, 'title', None)
        self.sizer = None # sizer that controls the layout of the children
                          # of the window
        PreviewMixin.__init__(self)

    def finish_widget_creation(self, *args, **kwds):
        WindowBase.finish_widget_creation(self)
        if self.has_title:
            self.widget.SetTitle(self.properties['title'].get_value())
        EVT_LEFT_DOWN(self.widget, self.drop_sizer)
        EVT_ENTER_WINDOW(self.widget, self.on_enter)
        EVT_CLOSE(self.widget, self.hide_widget)
        if wxPlatform == '__WXMSW__':
            # MSW isn't smart enough to avoid overlapping windows, so
            # at least move it away from the 3 wxGlade frames
            self.widget.CenterOnScreen()

    def show_widget(self, yes):
        WindowBase.show_widget(self, yes)
        if yes and wxPlatform == '__WXMSW__':
            # more than ugly, but effective hack to properly layout the window
            # on Win32
            if self.properties['size'].is_active():
                w, h = self.widget.GetSize()
                self.widget.SetSize((-1, h+1))
                self.widget.SetSize((-1, h))
            elif self.sizer:
                self.sizer.fit_parent()

    def popup_menu(self, event):
        if self.widget:
            if not self._rmenu:
                REMOVE_ID, HIDE_ID = [wxNewId() for i in range(2)]
                self._rmenu = misc.wxGladePopupMenu(self.name)
                misc.append_item(self._rmenu, REMOVE_ID, 'Remove\tDel',
                                 'remove.xpm')
                misc.append_item(self._rmenu, HIDE_ID, 'Hide')
                EVT_MENU(self.widget, REMOVE_ID, self.remove)
                EVT_MENU(self.widget, HIDE_ID, self.hide_widget)
                # paste
                PASTE_ID = wxNewId()
                misc.append_item(self._rmenu, PASTE_ID, 'Paste\tCtrl+V',
                                 'paste.xpm')
                EVT_MENU(self.widget, PASTE_ID, self.clipboard_paste)
                
            self.widget.PopupMenu(self._rmenu, event.GetPosition())

    def clipboard_paste(self, *args):
        import clipboard, xml_parse
        size = self.widget.GetSize()
        try:
            if clipboard.paste(self, None, 0):
                common.app_tree.app.saved = False
                self.widget.SetSize(size)
        except xml_parse.XmlParsingError, e:
            print '\nwxGlade-WARNING: only sizers can be pasted here'

    def create_properties(self):
        WindowBase.create_properties(self)
        # don't display the title ourselves anymore, now it's a
        # duty of the subclass!
##         if self.has_title:
##             panel = self.notebook.GetPage(0)
##             sizer_tmp = panel.GetSizer()
##             self.properties['title'].display(panel)
##             sizer_tmp.Add(self.properties['title'].panel, 0, wxEXPAND)
        PreviewMixin.create_properties(self)
            
    def get_title(self):
        return self.title

    def set_title(self, value):
        self.title = misc.wxstr(value)
        if self.widget:
            self.widget.SetTitle(value)

    def set_sizer(self, sizer):
        self.sizer = sizer
        if self.sizer and self.sizer.widget and self.widget:
            self.widget.SetAutoLayout(True)
            self.widget.SetSizer(self.sizer.widget)
            self.widget.Layout()

    def on_enter(self, event):
        if not self.sizer and common.adding_sizer:
            self.widget.SetCursor(wxCROSS_CURSOR)
        else:
            self.widget.SetCursor(wxNullCursor)

    def drop_sizer(self, event):
        if self.sizer or not common.adding_sizer:
            self.on_set_focus(event) # default behaviour: call show_properties
            return
        common.adding_widget = common.adding_sizer = False
        self.widget.SetCursor(wxNullCursor)
        common.widgets[common.widget_to_add](self, None, None)
        common.widget_to_add = None

    def hide_widget(self, *args):
        self.widget.Hide()
        common.app_tree.expand(self.node, False)
        common.app_tree.select_item(self.node.parent)
        common.app_tree.app.show_properties()

    def on_size(self, event):
        WindowBase.on_size(self, event)
        if self.sizer and self.widget:
            self.sizer.refresh()

    def set_name(self, name):
        if not misc.streq(self.name, name):
            common.app_tree.app.update_top_window_name(self.name, name)
        WindowBase.set_name(self, name)

    def delete(self, *args):
        if self.preview_widget is not None:
            self.preview_widget.Destroy()
            self.preview_widget = None
        WindowBase.delete(self, *args)

# end of class TopLevelBase


