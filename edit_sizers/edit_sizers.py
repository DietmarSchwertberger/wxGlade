# edit_sizers.py: hierarchy of Sizers supported by wxGlade
# 
# Copyright (c) 2002-2003 Alberto Griggio <albgrig@tiscalinet.it>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

from widget_properties import *
from tree import Tree, WidgetTree
import common, math, misc, sys

class SizerSlot:
    "a window to represent a slot in a sizer"
    def __init__(self, parent, sizer, pos=0):
        self.widget = None # reference to the widget resembling the slot
        self.sizer = sizer
        self.parent = parent
        self.pos = pos
        self.menu = None

    def create_widget(self):
        self.widget = wxPanel(self.parent.widget, -1, size=(20, 20))
        self.widget.SetBackgroundColour(wxLIGHT_GREY)
        self.widget.SetAutoLayout(True)
        EVT_PAINT(self.widget, self.on_paint)
        EVT_RIGHT_DOWN(self.widget, self.popup_menu)
        EVT_LEFT_DOWN(self.widget, self.drop_widget)
        EVT_MIDDLE_DOWN(self.widget, self.select_and_paste)
        EVT_ENTER_WINDOW(self.widget, self.on_enter)

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

    def show_widget(self, yes):
        if yes and not self.widget: self.create_widget()
        if self.widget: self.widget.Show(yes)

    def on_enter(self, event):
        if common.adding_widget: self.widget.SetCursor(wxCROSS_CURSOR)
        else: self.widget.SetCursor(wxNullCursor)
        
    def on_paint(self, event):
        dc = wxPaintDC(self.widget)
        dc.BeginDrawing()
        dc.SetBrush(wxBrush("black", wxFDIAGONAL_HATCH))
        dc.SetPen(wxBLACK_PEN)
        w, h = self.widget.GetClientSize()
        dc.DrawRectangle(0, 0, w, h)
        dc.EndDrawing()

    def on_size(self, event):
        self.widget.Refresh()

    def popup_menu(self, event):
        if not self.menu:
            self.menu = wxMenu('Options')
            REMOVE_ID, PASTE_ID = wxNewId(), wxNewId()
            misc.append_item(self.menu, REMOVE_ID, 'Remove\tDel', 'remove.xpm')
            misc.append_item(self.menu, PASTE_ID, 'Paste\tCtrl+V', 'paste.xpm')
            EVT_MENU(self.widget, REMOVE_ID, self.remove)
            EVT_MENU(self.widget, PASTE_ID, self.clipboard_paste)            
        self.widget.PopupMenu(self.menu, event.GetPosition())

    def remove(self, *args):
        self.sizer.remove_item(self)
        self.delete()

    def drop_widget(self, event):
        """\
        replaces self with a widget in self.sizer. This method is called
        to add every non-toplevel widget or sizer, and in turn calls the
        appropriate builder function (found in the ``common.widgets'' dict)
        """
        if not common.adding_widget:
            misc.focused_widget = self
            self.widget.SetFocus()
            return
        common.adding_widget = False
        common.adding_sizer = False
        self.widget.SetCursor(wxNullCursor)
        # call the appropriate builder
        common.widgets[common.widget_to_add](self.parent, self.sizer, self.pos)
        common.widget_to_add = None
        common.app_tree.app.saved = False # update the status of the app

    def clipboard_paste(self, *args):
        import clipboard
        if clipboard.paste(self.parent, self.sizer, self.pos):
            common.app_tree.app.saved = False # update the status of the app
            #print misc.focused_widget

    def select_and_paste(self, *args):
        """\
        Middle-click event handler: selects the slot and, if the clipboard is
        not empty, pastes its content here
        """
        misc.focused_widget = self
        self.widget.SetFocus()
        self.clipboard_paste()

    def delete(self, delete_widget=True):
        if self.menu: self.menu.Destroy()
        if delete_widget and self.widget: self.widget.Destroy()
        if misc.focused_widget is self: misc.focused_widget = None

    def update_pos(self, value):
        """\
        called by self.sizer.change_item_pos to update the item's position
        when another widget is moved
        """
        self.pos = value

# end of class SizerSlot


class SizerHandleButton(wxButton):
    """\
    Provides a ``handle'' to activate a Sizer and to access its popup menu 
    """
    def __init__(self, parent, id, sizer, menu):
        # menu: list of 2-tuples: (label, function)
        wxButton.__init__(self, parent.widget, id, '', size=(5, 5))
        self.sizer = sizer
        self.menu = menu
        self._rmenu = None
##         # provide popup menu for removal
##         REMOVE_ID = wxNewId() 
##         self._rmenu = misc.wxGladePopupMenu(sizer.name)
##         #self._rmenu.Append(REMOVE_ID, 'Remove\tDel')
##         misc.append_item(self._rmenu, REMOVE_ID, 'Remove\tDel', 'remove.xpm')
##         EVT_MENU(self, REMOVE_ID, self._remove)
##         for item in menu:
##             id = wxNewId()
##             #self._rmenu.Append(id, item[0])
##             bmp = None
##             if len(item) > 2: bmp = item[2]
##             misc.append_item(self._rmenu, id, item[0], bmp)
##             EVT_MENU(self, id, item[1])
##         self.sizer._rmenu = self._rmenu
        EVT_RIGHT_DOWN(self, self.popup_menu)

##         def remove():
##             if common.focused_widget is not None:
##                 common.focused_widget.remove()
##         table = [(0, WXK_DELETE, remove)]
        def on_key_down(event):
            evt_flags = 0
            if event.ControlDown(): evt_flags = wxACCEL_CTRL
            evt_key = event.GetKeyCode()
            for flags, key, function in misc.accel_table:
                if evt_flags == flags and evt_key == key:
                    misc.wxCallAfter(function)
                    break
            event.Skip()
        EVT_KEY_DOWN(self, on_key_down)

        def on_set_focus(event):
            misc.focused_widget = self
            event.Skip()
        EVT_SET_FOCUS(self, on_set_focus)

    def set_menu_title(self, title):
        if self._rmenu: self._rmenu.SetTitle(title)

    def popup_menu(self, event):
        if not self._rmenu:
            # provide popup menu for removal
            REMOVE_ID = wxNewId() 
            self._rmenu = misc.wxGladePopupMenu(self.sizer.name)
            #self._rmenu.Append(REMOVE_ID, 'Remove\tDel')
            misc.append_item(self._rmenu, REMOVE_ID, 'Remove\tDel',
                             'remove.xpm')
            EVT_MENU(self, REMOVE_ID, self._remove)
            for item in self.menu:
                id = wxNewId()
                #self._rmenu.Append(id, item[0])
                bmp = None
                if len(item) > 2: bmp = item[2]
                misc.append_item(self._rmenu, id, item[0], bmp)
                EVT_MENU(self, id, item[1])
            self.sizer._rmenu = self._rmenu
            del self.menu
        self.PopupMenu(self._rmenu, event.GetPosition())

    def _remove(self, *args):
        # removes the sizer from his parent, if it has one
        if self.sizer.toplevel:
            window = self.sizer.window
            common.app_tree.remove(self.sizer.node)
            window.set_sizer(None)
            return
        self.sizer.sizer.free_slot(self.sizer.pos)
        common.app_tree.remove(self.sizer.node)
    # needed for consistency (common.focused_widget.remove)
    remove = _remove

    def Destroy(self):
        if self._rmenu: self._rmenu.Destroy()
        wxButton.Destroy(self)
        if misc.focused_widget is self: misc.focused_widget = None

# end of class SizerHandleButton


class SizerItem:
    """\
    Represents a child of a sizer
    """
    def __init__(self, item, pos, option=0, flag=0, border=0, size=None):
        self.item = item
        self.item.pos = pos
        self.option = option
        self.flag = flag
        self.border = border
        self.size = size

# end of class SizerItem


#---------- 2002-10-07 --------------------------------------------------------

class SizerClassDialog:
    choices = [
        ('EditBoxSizerV', 'wxBoxSizer (wxVERTICAL)'),
        ('EditBoxSizerH', 'wxBoxSizer (wxHORIZONTAL)'),
        ('EditStaticBoxSizerV', 'wxStaticBoxSizer (wxVERTICAL)'),
        ('EditStaticBoxSizerH', 'wxStaticBoxSizer (wxHORIZONTAL)'),
        ('EditGridSizer', 'wxGridSizer'),
        ('EditFlexGridSizer', 'wxFlexGridSizer')
        ]
    def __init__(self, owner, parent):
        self.owner = owner
        self.parent = parent
        self.dialog = None

    def ShowModal(self):
        name = self.owner.__class__.__name__
        if hasattr(self.owner, 'orient'):
            if self.owner.orient == wxHORIZONTAL: name += 'H'
            else: name += 'V'
        choices = [ b for a, b in self.choices if a != name ]
        self.dialog = wxSingleChoiceDialog(self.parent, "Select sizer type",
                                           "Select sizer type", choices)
        return self.dialog.ShowModal()

    def get_value(self):
        return self.dialog.GetStringSelection()

# end of class SizerClassDialog
            

def change_sizer(old, new, which_page=0):
    """\
    changes 'old' sizer to 'new'
    Params:
      - old: SizerBase instance to replace
      - new: string selection that identifies the new instance
      - which_page: index of the notebook page of the property window to
                    display: this is used only by set_growable_(rows|cols)
    """
    constructors = {
        'wxBoxSizer (wxVERTICAL)':
        lambda : EditBoxSizer(old.name, old.window, wxVERTICAL, 0,
                              old.toplevel),
        'wxBoxSizer (wxHORIZONTAL)':
        lambda : EditBoxSizer(old.name, old.window, wxHORIZONTAL, 0,
                              old.toplevel),
        'wxStaticBoxSizer (wxVERTICAL)':
        lambda : EditStaticBoxSizer(old.name, old.window, wxVERTICAL,
                                    getattr(old, 'label', old.name),
                                    0, old.toplevel),
        'wxStaticBoxSizer (wxHORIZONTAL)':
        lambda : EditStaticBoxSizer(old.name, old.window, wxHORIZONTAL,
                                    getattr(old, 'label', old.name),
                                    0, old.toplevel),
        'wxGridSizer':
        lambda : EditGridSizer(old.name, old.window, rows=0, cols=0,
                               toplevel=old.toplevel),
        'wxFlexGridSizer':
        lambda : EditFlexGridSizer(old.name, old.window, rows=0, cols=0,
                                   toplevel=old.toplevel)
    }
    szr = constructors[new]()
    szr.children.extend(old.children[1:])
    szr.node = old.node
    if isinstance(szr, GridSizerBase):
        szr.set_rows(getattr(old, 'rows', 1))
        szr.set_cols(getattr(old, 'cols', len(szr.children)-1))
        szr.set_hgap(getattr(old, 'hgap', 0))
        szr.set_vgap(getattr(old, 'vgap', 0))
        if isinstance(szr, EditFlexGridSizer):
            try:
                grow_r = old.grow_rows
                grow_c = old.grow_cols
                if grow_r:
                    szr.grow_rows = grow_r
                    szr.properties['growable_rows'].toggle_active(True)
                    szr.properties['growable_rows'].set_value(
                        szr.get_growable_rows())
                if grow_c:
                    szr.grow_cols = grow_c
                    szr.properties['growable_cols'].toggle_active(True)
                    szr.properties['growable_cols'].set_value(
                        szr.get_growable_cols())
            except (AttributeError, KeyError):
                pass
    szr.show_widget(True, dont_set=True)
    for c in szr.children[1:]:
        widget = c.item
        widget.sizer = szr
        if not isinstance(widget, SizerSlot):
            szr.widget.Insert(widget.pos, widget.widget,
                              int(widget.get_option()), widget.get_int_flag(),
                              int(widget.get_border()))
    if not szr.toplevel:
        szr.sizer = old.sizer
        szr.option = old.option
        szr.flag = old.flag
        szr.border = old.border
        szr.pos = old.pos
        szr.sizer.children[szr.pos].item = szr
        if szr.sizer.widget:
            elem = szr.sizer.widget.GetChildren()[szr.pos]
            elem.SetSizer(szr.widget)
    import common
    common.app_tree.change_node(szr.node, szr)
    old.toplevel = False
    szr.show_properties()
    szr.notebook.SetSelection(which_page)
    for c in old.widget.GetChildren():
        if c and c.IsSizer(): c.SetSizer(None)
    old.widget.Clear()
    old.children = old.children[:1]
    old.delete()
    if szr.toplevel:
        szr.window.set_sizer(szr)
    szr.layout(True)

#------------------------------------------------------------------------------


class InsertDialog(wxDialog):
    def __init__(self, max_val):
        wxDialog.__init__(self, None, -1, "Select a position")
        self.pos = 0
        pos_prop = SpinProperty(self, 'position', self, r=(0, max_val))
        szr = wxBoxSizer(wxVERTICAL)
        szr.Add(pos_prop.panel, 0, wxEXPAND)
        szr.Add(wxButton(self, wxID_OK, "OK"), 0, wxALL|wxALIGN_CENTER, 3)
        self.SetAutoLayout(True)
        self.SetSizer(szr)
        szr.Fit(self)

    def __getitem__(self, name):
        def set_pos(v): self.pos = int(v)
        return (lambda : self.pos, set_pos)

# end of class InsertDialog


class SizerBase:
    """\
    Base class for every Sizer handled by wxGlade
    """
    def __init__(self, name, klass, window, toplevel=True, show=True,
                 menu=None):
        self.id = wxNewId()
        self.name = name
        self.klass = klass
        self.base = klass
        self.pos = 0 # for sub-sizers, the position inside the parent
        self.properties = {}
        self.property_window = window.property_window 
        self.window = window # window this sizer is responsible
                             # for the layout of

        self.widget = None # this is the actual wxSizer instance

        # toplevel: if True, self is not inside another sizer, but it is the
        # responsible of the layout of self.window
        self.toplevel = toplevel
        if not self.toplevel:
            self.option = 1
            self.flag = wxEXPAND
            self.border = 0
            
        self.menu = menu
        if self.menu is None:
            self.menu = [('Add slot', self.add_slot),
                         ('Insert slot...', self.insert_slot)]
        if not self.toplevel:
            self.menu.extend([('Copy\tCtrl+C', self.clipboard_copy,'copy.xpm'),
                              ('Cut\tCtrl+X', self.clipboard_cut, 'cut.xpm')
                              ])

        self._btn = None # SizerHandleButton

        self.notebook = None
        self._property_setup()

        self.children = [] # list of widgets added to the sizer

    def create_widget(self):
        """\
        Creates the wxSizer self.widget
        """
        raise NotImplementedError

    def show_widget(self, yes, dont_set=False):
        if not yes or self.widget:
            return # nothing to do if the sizer has already been created
        self._btn = SizerHandleButton(self.window, self.id, self, self.menu)
        # ScreenToClient used by WidgetTree for the popup menu
        EVT_BUTTON(self._btn, self.id, self.show_properties)
        self.create_widget()
        self.widget.Refresh = self.refresh
        self.widget.GetBestSize = self.widget.GetMinSize
        self.widget.ScreenToClient = self._btn.ScreenToClient
        if self.toplevel and not dont_set: self.window.set_sizer(self)

    def _property_setup(self):
        """\
        Setup of the Properties of self.
        """
        self.flags_pos = [ wxALL, wxLEFT, wxRIGHT, wxTOP, wxBOTTOM,
                           wxEXPAND, wxALIGN_RIGHT, wxALIGN_BOTTOM,
                           wxALIGN_CENTER_HORIZONTAL, wxALIGN_CENTER_VERTICAL ]

        self.access_functions = {
            'name' : (lambda : self.name, self.set_name),
            'class' : (lambda : self.klass, self.change) #lambda v: None)
            }
        if not self.toplevel:
            self.access_functions['option'] = (self.get_option,self.set_option)
            self.access_functions['flag'] = (self.get_flag, self.set_flag)
            self.access_functions['border'] = (self.get_border,self.set_border)
            self.access_functions['pos'] = (self.get_pos, self.set_pos)

        self.name_prop = TextProperty(self, 'name', None)
        #self.klass_prop = TextProperty(self, 'class', None, readonly=True)
        dialog = SizerClassDialog(self, None)
        self.klass_prop = DialogProperty(self, 'class', None, dialog)
        if not self.toplevel:
            prop = self.sizer_properties = {}
            prop['option'] = SpinProperty(self, 'option', None, 0, (0, 1000))
            flag_labels = ['#section#Border', 'wxALL',
                           'wxLEFT', 'wxRIGHT', 'wxTOP', 'wxBOTTOM',
                           '#section#Alignment', 'wxEXPAND', 'wxALIGN_RIGHT',
                           'wxALIGN_BOTTOM', 'wxALIGN_CENTER_HORIZONTAL',
                           'wxALIGN_CENTER_VERTICAL']
            prop['flag'] = CheckListProperty(self, 'flag', None, flag_labels)
            prop['border'] = SpinProperty(self, 'border', None, 0, (0, 1000))
            pos_p = prop['pos'] = SpinProperty(self, 'pos', None, 0, (0, 1000))
            def write(*args, **kwds): pass
            pos_p.write = write

    def get_pos(self): return self.pos - 1
    def set_pos(self, value):
        self.sizer.change_item_pos(self, min(value + 1,
                                             len(self.sizer.children) - 1))

    def update_pos(self, value):
        self.sizer_properties['pos'].set_value(value-1)
        self.pos = value

    def change(self, *args):
        # if wxPython < 2.3.3, wxCallAfter is defined in misc.py
        misc.wxCallAfter(change_sizer, self, self.klass_prop.get_value())

    def create_properties(self):
        """\
        Displays the Properties of self
        """
        self.notebook = wxNotebook(common.property_panel, -1)
        nb_sizer = wxNotebookSizer(self.notebook)
        self.notebook.sizer = nb_sizer
        self.notebook.SetAutoLayout(True)
        panel = wxScrolledWindow(self.notebook, -1)
        sizer_tmp = wxBoxSizer(wxVERTICAL)
        self.name_prop.display(panel)
        self.klass_prop.display(panel)
        self.klass_prop.text.SetEditable(False)
        sizer_tmp.Add(self.name_prop.panel, 0, wxEXPAND)
        sizer_tmp.Add(self.klass_prop.panel, 0, wxEXPAND)
        if not self.toplevel:
            prop = self.sizer_properties
            prop['option'].display(panel)
            prop['flag'].display(panel)
            prop['border'].display(panel)
            prop['pos'].display(panel)
            sizer_tmp.Add(prop['pos'].panel, 0, wxEXPAND)
            sizer_tmp.Add(prop['option'].panel, 0, wxEXPAND)
            sizer_tmp.Add(prop['border'].panel, 0, wxEXPAND)
            sizer_tmp.Add(prop['flag'].panel, 0, wxEXPAND)
        else:
            # button to Fit parent
            FIT_ID = wxNewId()
            self.fit_btn = wxButton(panel, FIT_ID, 'Fit parent')
            EVT_BUTTON(self.fit_btn, FIT_ID, self.fit_parent)
            sizer_tmp.Add(self.fit_btn, 0, wxALL|wxEXPAND, 5)
        panel.SetAutoLayout(True)
        panel.SetSizer(sizer_tmp)
        sizer_tmp.Fit(panel)
        
        w, h = panel.GetClientSizeTuple()
        self.notebook.AddPage(panel, "Common")
        panel.SetScrollbars(1, 5, 1, math.ceil(h/5.0))

    def popup_menu(self, event):
        """\
        pops up a menu to add or remove slots from self, or to remove self
        from the application.
        """
        if self._btn: self._btn.popup_menu(event)
        #self._btn.PopupMenu(self._btn._rmenu, event.GetPosition())

    def set_name(self, value):
        self.name = value
        self._btn.set_menu_title(value)
        try: common.app_tree.set_name(self.node, self.name)
        except AttributeError:
            import traceback; traceback.print_exc()
            
    def __getitem__(self, value):
        return self.access_functions[value]

    def show_properties(self, *args):
        """\
        Updates common.property_panel to show the notebook with the Properties
        of self
        """
        if not self.window.is_visible(): return
        if not self.notebook:
            self.create_properties()
        sizer_tmp = self.property_window.GetSizer()
        sizer_tmp = wxPyTypeCast(sizer_tmp, "wxBoxSizer")
        child = wxPyTypeCast(sizer_tmp.GetChildren()[0], "wxSizerItem")
        w = wxPyTypeCast(child.GetWindow(), "wxWindow")
        if w is self.notebook: return
        w.Hide()
        child.SetWindow(self.notebook)
        self.property_window.Layout()
        self.property_window.SetTitle('Properties - <%s>' % self.name)
        if hasattr(self, 'node'): common.app_tree.select_item(self.node)
        self.notebook.Show()
        try: self._btn.SetFocus()
        except AttributeError: pass
        
    def fit_parent(self, *args):
        """\
        Tell the sizer to resize the window to match the sizer's minimal size
        """
        if self.widget and self.window.widget:
            self.widget.Fit(self.window.widget)
            #self.widget.SetSizeHints(self.window.widget)
            self.window.widget.Layout()
    
    def add_item(self, item, pos=None, option=0, flag=0, border=0, size=None,
                 force_layout=True):
        """\
        Adds an item to self.
        """
        option = int(option); flag = int(flag); border = int(border)
        if pos is None:
            pos = len(self.children)
            self.children.append(SizerItem(item, pos, option, flag, border,
                                           size))
            self.add_slot()
        try:
            old_child = self.children[pos]
            if isinstance(old_child.item, SizerSlot):
                old_child.item.delete(False)            
            self.children[pos] = SizerItem(item, pos, option, flag, border,
                                           size)
        except IndexError: # this shouldn't happen!
            import traceback; traceback.print_exc()
            print self.children, pos
            raise SystemExit

        item.sizer = self
        item.pos = pos

        self._add_item_widget(item, pos, option, flag, border, size,
                              force_layout)
        
    def _add_item_widget(self, item, pos, option, flag, border, size,
                         force_layout):
        if not self.widget: return # nothing more to do
        if not item.widget: return

        try:
            elem = self.widget.GetChildren()[pos]
        except IndexError: # this happens after loading from xml
            # I have to set wxADJUST_MINSIZE to handle a bug that I'm not
            # able to detect (yet): if the width or height of a widget is -1,
            # the layout is messed up!
            self.widget.Add(item.widget, option, flag, border)
            if size: w, h = size
            else: w, h = item.widget.GetBestSize()
            if w == -1: w = item.widget.GetBestSize()[0]
            if h == -1: h = item.widget.GetBestSize()[1]
            self.widget.SetItemMinSize(item.widget, w, h)
            return
        
        if elem.IsWindow(): # remove the previous item at pos
            w = elem.GetWindow()
            elem.SetWindow(None)
            w.Destroy()
        try: # let's see if the item to add is a window
            elem.SetWindow(item.widget)
        except TypeError: # suppose the item to add is a sizer
            elem.SetSizer(item.widget)
        elem.SetOption(option)
        elem.SetFlag(flag)
        elem.SetBorder(border)
        try: # if the item was a window, set its size to a reasonable value
            if size: w, h = size
            else: w, h = item.widget.GetBestSize()
            if w == -1: w = item.widget.GetBestSize()[0]
            if h == -1: h = item.widget.GetBestSize()[1]
            self.widget.SetItemMinSize(item.widget, w, h)
        except: pass
        if force_layout: self.layout() # update the layout of self

    def _fix_notebook(self, pos, notebook_sizer, force_layout=True):
        """\
        Replaces the widget at 'pos' with 'notebook_sizer': this is intended
        to be used by wxNotebook widgets, to add the notebook sizer to this
        sizer.
        This is a hack, but it's the best I could find without having to
        rewrite too much code :-(
        """
        # no error checking at all, this is a "protected" method, so it should
        # be safe to assume the caller knows how to use it
        item = self.widget.GetChildren()[pos]
        item.SetWindow(None)
        item.SetSizer(notebook_sizer)
        if force_layout:
            self.layout()
       
    def set_item(self, pos, option=None, flag=None, border=None, size=None,
                 force_layout=True):
        """\
        Updates the layout of the item at the given pos.
        """
        try: item = self.children[pos]
        except IndexError: # this shouldn't happen
            import traceback; traceback.print_exc()
            raise SystemExit
        if option is not None:
            option = int(option)
            item.option = option
        if flag is not None:
            flag = int(flag)
            item.flag = flag
        if border is not None:
            border = int(border)
            item.border = border
        if size is not None: item.size = size

        self._set_item_widget(pos, option, flag, border, size, force_layout)

    def _set_item_widget(self, pos, option, flag, border, size, force_layout):
        if not self.widget: return
        
        try: elem = self.widget.GetChildren()[pos]
        except IndexError: return # this may happen during xml loading
        
        if option is not None: elem.SetOption(option)
        if flag is not None: elem.SetFlag(flag)
        if border is not None: elem.SetBorder(border)
        if elem.IsWindow():
            if size is None: size = elem.GetSize()
            item = elem.GetWindow()
            w, h = size
            if w == -1: w = item.GetBestSize()[0]
            if h == -1: h = item.GetBestSize()[1]
            self.widget.SetItemMinSize(item, w, h)
        if force_layout:
            self.layout(True)
            #try: self.sizer.Layout()
            #except AttributeError: pass

    def remove_item(self, elem, force_layout=True):
        """\
        Removes elem from self.
        """
        if elem:
            for c in self.children[elem.pos+1:]: c.item.pos -= 1
            del self.children[elem.pos]
        if self.widget and elem.widget:
            self.widget.Remove(elem.widget)
            if force_layout:
                self.layout(True)
                #if not self.toplevel: self.sizer.Layout()
    Remove = remove_item # maybe this is needed, I have to check...

    def layout(self, recursive=True):
        #if not self.widget or not self.window.is_visible(): return
        if not self.widget: return

        from edit_windows import TopLevelBase
        if self.toplevel and not isinstance(self.window, TopLevelBase):
            if not self.window.properties['size'].is_active():
                szr = self.window.sizer.widget
                w, h = self.window.widget.GetBestSize()
                szr.SetItemMinSize(self.window.widget, w, h)            
            if self.window.sizer is not self:
                self.window.sizer.layout(False)
            else:
                szr.Layout()
            return
        self.widget.SetMinSize(self.widget.CalcMin())
        self.widget.Layout()
        for c in self.children:
            try:
##                 w, h = c.item.widget.GetBestSize()
##                 self.widget.SetItemMinSize(c.item.widget, w, h)
                c.item.widget.Refresh()
            except Exception, e: pass
        if recursive:
            if hasattr(self, 'sizer'):
                self.sizer.layout(recursive)

    # 2002-10-09 -------------------------------------------------------------
    def change_item_pos(self, item, new_pos, force_layout=True):
        """\
        Changes the position of the 'item' so that it is at 'new_pos'
        'new_pos' must be a valid position
        """
        if not self.widget: return
        
        old_pos = item.pos
        import copy
        new_item = copy.copy(self.children[old_pos])
        if old_pos > new_pos:
            for c in self.children[new_pos:old_pos]:
                c.item.update_pos(c.item.pos + 1)
            self.children.insert(new_pos, new_item)
            del self.children[old_pos+1]
        else:
            for c in self.children[old_pos+1:new_pos+1]:
                c.item.update_pos(c.item.pos - 1)
            del self.children[old_pos]
            self.children.insert(new_pos+1, new_item)
        item.update_pos(new_pos)

        elem = self.widget.GetChildren()[old_pos]
        # always set the sizer to None because otherwise it will be Destroy'd
        elem.SetSizer(None)
        # this fake_win trick seems necessary because wxSizer::Remove(int pos)
        # doesn't seem to work with grid sizers :-\
        fake_win = wxWindow(self.window.widget, -1)
        elem.SetWindow(fake_win)
        self.widget.Remove(fake_win)
        fake_win.Destroy()
        self.widget.Insert(new_pos, item.widget, int(item.get_option()),
                           item.get_int_flag(), int(item.get_border()))

        common.app_tree.change_node_pos(item.node, new_pos-1)
        common.app_tree.select_item(item.node)

        if force_layout:
            self.layout()
            if wxPlatform == '__WXMSW__': self.window.widget.Refresh()
    # ------------------------------------------------------------------------

    def set_option(self, value):
        """\
        If self is not a toplevel sizer, update the layout to reflect the value
        of the option property
        """
        self.option = int(value)
        try:
            self.sizer.set_item(self.pos, option=self.option)
        except AttributeError, e: pass
        self.finish_set()

    def set_flag(self, value):
        """\
        If self is not a toplevel sizer, update the layout to reflect the
        value of the flag property
        """
        value = self.sizer_properties['flag'].prepare_value(value)
        flags = 0
        for v in range(len(value)):
            if value[v]:
                flags |= self.flags_pos[v]
        self.flag = flags
        try: self.sizer.set_item(self.pos, flag=flags)
        except AttributeError, e: pass
        self.finish_set()

    def set_border(self, value):
        """\
        If self is not a toplevel sizer, update the layout to reflect
        value of the border property
        """
        self.border = int(value)
        try: self.sizer.set_item(self.pos, border=self.border)
        except AttributeError, e: print e

    def get_option(self):
        if not hasattr(self, 'sizer'): return '0'
        return str(self.option)

    def get_flag(self):
        retval = [0] * len(self.flags_pos)
        if not hasattr(self, 'sizer'): return retval
        try:
            flag = self.flag
            for i in range(len(self.flags_pos)):
                if flag & self.flags_pos[i]: retval[i] = 1
            # patch to make wxALL work
            if retval[1:5] == [1, 1, 1, 1]:
                retval[0] = 1; retval[1:5] = [0, 0, 0, 0]
            else:
                retval[0] = 0
        except AttributeError: pass
        return retval

    def get_int_flag(self): return self.flag

    def get_border(self):
        if not hasattr(self, 'sizer'): return '0'
        return str(self.border)

    def remove(self):
        # this function is here for clipboard compatibility
        if not self._btn: return
        self._btn._remove()

    def delete(self):
        """\
        ``Destructor''
        """
        self._rmenu = None
        if self._btn: self._btn.Destroy()
        if self.notebook:
            for p in self.properties.itervalues():
                if p.panel: p.panel.Destroy()
            if self.name_prop.panel: self.name_prop.panel.Destroy()
            if self.klass_prop.panel: self.klass_prop.panel.Destroy()
            if hasattr(self, 'sizer_properties'):
                for p in self.sizer_properties.itervalues():
                    if p.panel: p.panel.Destroy()
            nb_szr = self.notebook.sizer
            self.notebook.Destroy()
            nb_szr.Destroy()
        for c in self.children:
            if c.item and isinstance(c.item, SizerSlot): c.item.delete()
        if self.toplevel:
            self.window.set_sizer(None)

    if wxPlatform == '__WXMSW__':
        def finish_set(self):
            for c in self.children:
                if c.item.widget:
                    try: c.item.widget.Refresh()
                    except AttributeError: pass # sizers have no Refresh
    else:
        def finish_set(self): pass

    def refresh(self, *args):
        # this will be self.widget.Refresh
        for c in self.children:
            if c.item.widget: 
                try: c.item.widget.Refresh()
                except AttributeError: pass

    def update_view(self, *args): pass

    def add_slot(self, *args, **kwds):
        """\
        adds a slot to the sizer, i.e. a fake window that will accept the
        dropping of widgets
        """
        if not self.widget: return
        tmp = SizerSlot(self.window, self, len(self.children))
        item = SizerItem(tmp, len(self.children), 1, wxEXPAND)
        self.children.append(item)
        tmp.show_widget(True) # create the actual SizerSlot widget
        self.widget.Add(tmp.widget, 1, wxEXPAND)
        self.widget.SetItemMinSize(tmp.widget, 20, 20)
        force_layout = kwds.get('force_layout', True)
        if force_layout: self.layout(True)
        common.app_tree.app.saved = False

    def insert_slot(self, *args, **kwds):
        """\
        inserts a slot into the sizer: the user will be asked for a position
        before which to insert the SizerSlot object. This method is meaningful
        only in an interactive session
        """
        if not self.widget: return

        dialog = InsertDialog(len(self.children)-1)
        dialog.ShowModal()
        pos = dialog.pos + 1
        tmp = SizerSlot(self.window, self, pos)
        for c in self.children[pos:]:
            c.item.pos += 1
        self.children.insert(pos, SizerItem(tmp, pos, 1, wxEXPAND, 0))
        tmp.show_widget(True) # create the actual SizerSlot
        self.widget.Insert(pos, tmp.widget, 1, wxEXPAND)
        self.widget.SetItemMinSize(tmp.widget, 20, 20)
        force_layout = kwds.get('force_layout', True)
        if force_layout: self.layout(True)
        common.app_tree.app.saved = False
        dialog.Destroy()

    def free_slot(self, pos, force_layout=True):
        """\
        Replaces the element at pos with an empty slot
        """
        tmp = SizerSlot(self.window, self, pos)
        item = SizerItem(tmp, pos, 1, wxEXPAND, 0)
        self.children[pos] = item
        if self.widget:
            tmp.show_widget(True) # create the actual SizerSlot
            elem = self.widget.GetChildren()[pos]
            elem.SetWindow(tmp.widget)
            elem.SetSizer(None)
            elem.SetOption(1)
            elem.SetBorder(0)
            elem.SetFlag(wxEXPAND)
            if force_layout: self.layout()

    def is_visible(self):
        return self.window.is_visible()
            
    def clipboard_copy(self, *args):
        """\
        returns a copy of self to be inserted in the clipboard
        """
        if not self.toplevel:
            import clipboard
            clipboard.copy(self)

    def clipboard_cut(self, *args):
        if not self.toplevel:
            import clipboard
            clipboard.cut(self)

    def post_load(self):
        """\
        Called after the loading of an app from an XML file, before showing
        the hierarchy of widget for the first time. 
        This is used only for container widgets, to adjust their size
        appropriately.
        """
        if not self.toplevel: return
        if not self.window.properties['size'].is_active():
            self.fit_parent()
            import config
            w, h = self.widget.GetSize()
            prefix = ''
            if config.preferences.use_dialog_units:
                w, h = self.window.widget.ConvertPixelSizeToDialog(
                    self.widget.GetSize())
                prefix = 'd'
            self.window.set_size('%s, %s%s' % (w, h, prefix))

# end of class SizerBase


class wxGladeBoxSizer(wxBoxSizer):
    def SetItemMinSize(self, item, w, h):
        try:
            w2, h2 = item.GetBestSize()
            if w == -1: w = w2
            if h == -1: h = h2
        except AttributeError:
            pass
        wxBoxSizer.SetItemMinSize(self, item, w, h)

# end of class wxGladeBoxSizer


class EditBoxSizer(SizerBase):
    """\
    Class to handle wxBoxSizer objects
    """
    def __init__(self, name, window, orient=wxVERTICAL, elements=3,
                 toplevel=True, show=True):
        SizerBase.__init__(self, name, 'wxBoxSizer', window, toplevel, show)
        self.access_functions['orient'] = (self.get_orient, self.set_orient)
        self.properties = {'orient': HiddenProperty(self, 'orient',
                                                    (orient==wxHORIZONTAL and
                                                     'wxHORIZONTAL' or
                                                     'wxVERTICAL')) }
        class Dummy: widget = None
        # add to self.children the SizerItem for self._btn
        self.children = [SizerItem(Dummy(), 0, 0, wxEXPAND)]
        for i in range(1, elements+1):
            tmp = SizerSlot(self.window, self, i)
            self.children.append(SizerItem(tmp, i, 1, wxEXPAND))
        
        self.orient = orient

    def create_widget(self):
        self.widget = wxGladeBoxSizer(self.orient)
        self.widget.Add(self._btn, 0, wxEXPAND)
        for c in self.children[1:]: # we've already added self._btn
            c.item.show_widget(True)
            if isinstance(c.item, SizerSlot):
                self.widget.Add(c.item.widget, 1, wxEXPAND)
                self.widget.SetItemMinSize(c.item.widget, 20, 20)
            else:
                sp = c.item.properties.get('size')
                if sp and sp.is_active():
                    size = sp.get_value().strip()
                    if size[-1] == 'd':
                        size = size[:-1]
                        use_dialog_units = True
                    else: use_dialog_units = False
                    w, h = [ int(v) for v in size.split(',') ]
                    if use_dialog_units:
                        w, h = wxDLG_SZE(c.item.widget, (w, h))
                else: w, h = c.item.widget.GetBestSize()
                self.widget.SetItemMinSize(c.item.widget, w, h)
        if not self.toplevel and hasattr(self, 'sizer'):
            # hasattr(self, 'sizer') is False only in case of a 'change_sizer'
            # call
            self.sizer.add_item(self, self.pos, self.option, self.flag,
                                self.border, self.widget.GetMinSize())

    def get_orient(self):
        od = { wxHORIZONTAL: 'wxHORIZONTAL',
               wxVERTICAL: 'wxVERTICAL' }
        return od.get(self.orient)
    
    def set_orient(self, value):
        od = { 'wxHORIZONTAL': wxHORIZONTAL,
               'wxVERTICAL': wxVERTICAL }
        self.orient = od.get(value, wxVERTICAL)

# end of class EditBoxSizer


class wxGladeStaticBoxSizer(wxStaticBoxSizer):
    def SetItemMinSize(self, item, w, h):
        try:
            w2, h2 = item.GetBestSize()
            if w == -1: w = w2
            if h == -1: h = h2
        except AttributeError:
            pass
        wxStaticBoxSizer.SetItemMinSize(self, item, w, h)

# end of class wxGladeStaticBoxSizer
    

class EditStaticBoxSizer(SizerBase):
    """\
    Class to handle wxStaticBoxSizer objects
    """
    def __init__(self, name, window, orient=wxVERTICAL, label='', elements=3,
                 toplevel=True, show=True):
        self.label = label
        self.orient = orient
        SizerBase.__init__(self, name, 'wxStaticBoxSizer', window, toplevel,
                           show)
        self.access_functions['orient'] = (self.get_orient, self.set_orient)
        self.properties['orient'] = HiddenProperty(self, 'orient',
                                                   (orient==wxHORIZONTAL and
                                                    'wxHORIZONTAL' or
                                                    'wxVERTICAL'))
        class Dummy: widget = None
        # add to self.children the SizerItem for self._btn
        self.children = [SizerItem(Dummy(), 0, 0, wxEXPAND)]
        for i in range(1, elements+1):
            tmp = SizerSlot(self.window, self, i)
            self.children.append(SizerItem(tmp, i, 1, wxEXPAND))

    def create_widget(self):
        self.widget = wxGladeStaticBoxSizer(wxStaticBox(self.window.widget, -1,
                                                        self.label),
                                            self.orient)
        self.widget.Add(self._btn, 0, wxEXPAND)
        for c in self.children[1:]: # we've already added self._btn
            c.item.show_widget(True)
            if isinstance(c.item, SizerSlot):
                self.widget.Add(c.item.widget, 1, wxEXPAND)
                self.widget.SetItemMinSize(c.item.widget, 20, 20)
            else:
                sp = c.item.properties.get('size')
                if sp and sp.is_active():
                    size = sp.get_value().strip()
                    if size[-1] == 'd':
                        size = size[:-1]
                        use_dialog_units = True
                    else: use_dialog_units = False
                    w, h = [ int(v) for v in size.split(',') ]
                    if use_dialog_units:
                        w, h = wxDLG_SZE(c.item.widget, (w, h))
                else: w, h = c.item.widget.GetBestSize()
                self.widget.SetItemMinSize(c.item.widget, w, h)
        self.layout()
        if not self.toplevel and hasattr(self, 'sizer'):
            # hasattr(self, 'sizer') is False only in case of a 'change_sizer'
            # call
            self.sizer.add_item(self, self.pos, self.option, self.flag,
                                self.border, self.widget.GetMinSize())

    def _property_setup(self):
        SizerBase._property_setup(self)
        self.access_functions['label'] = (self.get_label, self.set_label)
        lbl = self.properties['label'] = TextProperty(self, 'label', None)
        def write(outfile, tabs):
            import widget_properties
            outfile.write('    ' * tabs + '<label>')
            outfile.write(widget_properties.escape(widget_properties._encode(
                self.get_label())))
            outfile.write('</label>\n')
        # we must consider also "" a valid value
        lbl.write = write

    def create_properties(self):
        SizerBase.create_properties(self)
        panel = self.notebook.GetPage(0)
        sizer = panel.GetSizer()
        self.properties['label'].display(panel)
        sizer.Add(self.properties['label'].panel, 0, wxEXPAND)
        sizer.Layout()
        w, h = sizer.GetMinSize()
        panel.SetScrollbars(1, 5, 1, math.ceil(h/5.0))

    def set_label(self, value):
        """\
        Sets the label of the static box
        """
        self.label = str(value)
        if self.widget: self.widget.GetStaticBox().SetLabel(self.label)

    def get_label(self): return self.label

    def delete(self):
        if self.widget: self.widget.GetStaticBox().Destroy()
        SizerBase.delete(self)
        
    def get_orient(self):
        od = { wxHORIZONTAL: 'wxHORIZONTAL',
               wxVERTICAL: 'wxVERTICAL' }
        return od.get(self.orient)
    
    def set_orient(self, value):
        od = { 'wxHORIZONTAL': wxHORIZONTAL,
               'wxVERTICAL': wxVERTICAL }
        self.orient = od.get(value, wxVERTICAL)

# end of class EditStaticBoxSizer


class CustomSizer(wxBoxSizer):
    """\
    Custom wxSizer class used to implement a GridSizer with an additional
    handle button
    """
    def __init__(self, parent, factory, rows, cols, vgap, hgap):
        wxBoxSizer.__init__(self, wxVERTICAL)
        self.parent = parent
        self._grid = factory(rows, cols, vgap, hgap)
        wxBoxSizer.Add(self, self.parent._btn, 0, wxEXPAND)
        wxBoxSizer.Add(self, self._grid, 1, wxEXPAND)

    def __getattr__(self, name):
        return getattr(self._grid, name)

    def GetBestSize(self):
        return self._grid.GetMinSize()
    
    def Add(self, *args, **kwds): self._grid.Add(*args, **kwds)
    def Insert(self, pos, *args, **kwds):
        self._grid.Insert(pos-1, *args, **kwds)
    def Remove(self, *args, **kwds): self._grid.Remove(*args, **kwds)
    def SetItemMinSize(self, item, w, h): #*args, **kwds):
        try:
            w2, h2 = item.GetBestSize()
            if w == -1: w = w2
            if h == -1: h = h2
        except AttributeError:
            pass
        self._grid.SetItemMinSize(item, w, h)

    def GetChildren(self):
        return [None] + self._grid.GetChildren()

    def Layout(self):
        self._grid.Layout()
        wxBoxSizer.Layout(self)

# end of class CustomSizer


class GridSizerBase(SizerBase):
    """\
    Base class for Grid sizers. Must not be instantiated.
    """
    def __init__(self, name, klass, window, rows=3, cols=3, vgap=0, hgap=0,
                 toplevel=True, show=True):
        self.rows = rows; self.cols = cols
        self.vgap = vgap; self.hgap = hgap
        if self.cols or self.rows:
            if not self.rows: self.rows = 1
            elif not self.cols: self.cols = 1
        menu = [('Add slot', self.add_slot),
                ('Insert slot...', self.insert_slot),
                ('Add row', self.add_row),
                ('Add column', self.add_col),
                ('Insert row...', self.insert_row),
                ('Insert column...', self.insert_col)]
        SizerBase.__init__(self, name, klass, window, toplevel, show, menu)

        class Dummy: widget = None
        # add to self.children the SizerItem for self._btn
        self.children = [SizerItem(Dummy(), 0, 0, wxEXPAND)]
        for i in range(1, self.rows*self.cols+1):
            tmp = SizerSlot(self.window, self, i)
            self.children.append(SizerItem(tmp, i, 1, wxEXPAND))

    def create_widget(self):
        """\
        This must be overriden and called at the end of the overriden version
        """
        for c in self.children[1:]: # we've already added self._btn
            c.item.show_widget(True)
            if isinstance(c.item, SizerSlot):
                self.widget.Add(c.item.widget, 1, wxEXPAND)
                self.widget.SetItemMinSize(c.item.widget, 20, 20)
            else:
                sp = c.item.properties.get('size')
                if sp and sp.is_active():
                    size = sp.get_value().strip()
                    if size[-1] == 'd':
                        size = size[:-1]
                        use_dialog_units = True
                    else: use_dialog_units = False
                    w, h = [ int(v) for v in size.split(',') ]
                    if use_dialog_units:
                        w, h = wxDLG_SZE(c.item.widget, (w, h))
                else: w, h = c.item.widget.GetBestSize()
                self.widget.SetItemMinSize(c.item.widget, w, h)
        self.widget.Layout()

    def _property_setup(self):
        SizerBase._property_setup(self)
        self.access_functions['rows'] = (self.get_rows, self.set_rows)
        self.access_functions['cols'] = (self.get_cols, self.set_cols)
        self.access_functions['hgap'] = (self.get_hgap, self.set_hgap)
        self.access_functions['vgap'] = (self.get_vgap, self.set_vgap)
        props = { 'rows': SpinProperty(self, 'rows', None),
                  'cols': SpinProperty(self, 'cols', None),
                  'hgap': SpinProperty(self, 'hgap', None),
                  'vgap': SpinProperty(self, 'vgap', None) }
        self.properties = props

    def create_properties(self):
        SizerBase.create_properties(self)
        page = wxScrolledWindow(self.notebook, -1)
        sizer = wxBoxSizer(wxVERTICAL)
        props = self.properties
        props['rows'].display(page)
        props['cols'].display(page)
        props['vgap'].display(page)
        props['hgap'].display(page)
        sizer.Add(props['rows'].panel, 0, wxEXPAND)
        sizer.Add(props['cols'].panel, 0, wxEXPAND)
        sizer.Add(props['vgap'].panel, 0, wxEXPAND)
        sizer.Add(props['hgap'].panel, 0, wxEXPAND)
        page.SetAutoLayout(True)
        page.SetSizer(sizer)
        sizer.Fit(page)
        self.notebook.AddPage(page, "Grid")

    def get_rows(self): return self.rows
    def get_cols(self): return self.cols
    def get_vgap(self): return self.vgap
    def get_hgap(self): return self.hgap

    def set_rows(self, rows):
        self.rows = int(rows)
        if self.widget:
            self.widget.SetRows(self.rows)
            self.layout(True)

    def set_cols(self, cols):
        self.cols = int(cols)
        if self.widget:
            self.widget.SetCols(self.cols)
            self.layout(True)

    def set_hgap(self, hgap):
        self.hgap = int(hgap)
        if self.widget:
            self.widget.SetHGap(self.hgap)
            self.layout()

    def set_vgap(self, vgap):
        self.vgap = int(vgap)
        if self.widget:
            self.widget.SetVGap(self.vgap)
            self.layout()

    def fit_parent(self, *args):
        """\
        Tell the sizer to resize the window to match the sizer's minimal size
        """
        if self.widget and self.window.widget:
            self.widget.Fit(self.window.widget)
            self.widget.SetSizeHints(self.window.widget)
        
    def insert_slot(self, *args, **kwds):
        """\
        inserts a slot into the sizer: the user will be asked for a position
        before which to insert the SizerSlot object
        """
        if not self.widget: return

        if kwds.get('interactive', True):
            dialog = InsertDialog(len(self.children))
            dialog.ShowModal()
            pos = dialog.pos+1
        else: pos = kwds['pos']
        tmp = SizerSlot(self.window, self, pos)
        for c in self.children[pos:]:
            c.item.pos += 1
        self.children.insert(pos, SizerItem(tmp, pos, 1, wxEXPAND, 0))
        tmp.show_widget(True) # create the actual SizerSlot
        self.widget.Insert(pos, tmp.widget, 1, wxEXPAND)
        self.widget.SetItemMinSize(tmp.widget, 20, 20)
        force_layout = kwds.get('force_layout', True)
        if force_layout: self.layout(True)
        common.app_tree.app.saved = False

    def add_row(self, *args, **kwds):
        if not self.widget: return
##         self.set_rows(self.rows+1)
##         self.properties['rows'].set_value(self.rows)
##         slots = [SizerSlot(self.window, self, len(self.children)+i) for i in
##                  range(self.cols)]
##         items = [SizerItem(slots[i], len(self.children)+i, 1, wxEXPAND) for i
##                  in range(self.cols)]
##         self.children.extend(items)
##         for s in slots:
##             s.show_widget(True) # create the actual SizerSlot widget
##             self.widget.Add(s.widget, 1, wxEXPAND)
##             self.widget.SetItemMinSize(s.widget, 20, 20)
##         force_layout = kwds.get('force_layout', True)
##         if force_layout: self.layout(True)
##         common.app_tree.app.saved = False
        self._insert_row(self.widget.GetRows()+1)

    def insert_row(self, *args):
        if not self.widget: return
        dialog = InsertDialog(self.widget.GetRows())
        dialog.ShowModal()
        self._insert_row(dialog.pos + 1)
        dialog.Destroy()
        
    def _insert_row(self, pos):
        rows = self.widget.GetRows()
        cols = self.widget.GetCols()
        pos = (pos-1) * cols + 1
        self.set_rows(rows+1)
        for i in range(cols):
            self.insert_slot(interactive=False, pos=pos+i, force_layout=False)
        self.properties['rows'].set_value(self.rows)
        self.layout(True)
        common.app_tree.app.saved = False

    def add_col(self, *args, **kwds):
##         if not self.widget: return
##         rows = self.widget.GetRows()
##         cols = self.widget.GetCols()
##         self.set_cols(self.cols+1)
##         for i in range(rows):
##             self.insert_slot(interactive=False, pos=self.cols * (i+1),
##                              #pos=cols + self.cols * i,
##                              force_layout=False)
##         self.properties['cols'].set_value(self.cols)
##         force_layout = kwds.get('force_layout', True)
##         if force_layout: self.layout(True)
        if not self.widget: return
        self._insert_col(self.widget.GetCols()+1)

    def insert_col(self, *args):
        if not self.widget: return
        dialog = InsertDialog(self.widget.GetCols())
        dialog.ShowModal()
        self._insert_col(dialog.pos + 1)
        dialog.Destroy()

    def _insert_col(self, pos):
        rows = self.widget.GetRows()
        cols = self.widget.GetCols()
        self.set_cols(cols+1)
        for i in range(rows):
            self.insert_slot(interactive=False, pos=pos + self.cols * i,
                             #pos=cols + self.cols * i,
                             force_layout=False)
        self.properties['cols'].set_value(self.cols)
        self.layout(True)
        common.app_tree.app.saved = False
        
# end of class GridSizerBase


class EditGridSizer(GridSizerBase):
    """\
    Class to handle wxGridSizer objects
    """
    def __init__(self, name, window, rows=3, cols=3, vgap=0, hgap=0,
                 toplevel=True, show=True):
        GridSizerBase.__init__(self, name, 'wxGridSizer', window, rows, cols,
                               vgap, hgap, toplevel, show)
        
    def create_widget(self):
        self.widget = CustomSizer(self, wxGridSizer, self.rows, self.cols,
                                  self.vgap, self.hgap)
        if not self.toplevel and hasattr(self, 'sizer'):
            # hasattr(self, 'sizer') is False only in case of a 'change_sizer'
            # call
            self.sizer.add_item(self, self.pos, self.option, self.flag,
                                self.border) #, self.widget.GetMinSize())
        GridSizerBase.create_widget(self)

# end of class EditGridSizer

class CheckListDialogProperty(DialogProperty):
    dialog = [None]
    def __init__(self, owner, name, parent, title, message, callback,
                 can_disable=True):
        self.title = title
        self.message = message
        if not self.dialog[0]:
            class Dialog(wxDialog):
                def __init__(self):
                    wxDialog.__init__(self, parent, -1, title)
                    sizer = wxBoxSizer(wxVERTICAL)
                    self.message = wxStaticText(self, -1, "")
                    sizer.Add(self.message, 0, wxTOP|wxLEFT|wxRIGHT|wxEXPAND,
                              10)
                    self.choices = wxCheckListBox(self, -1, choices=[])
                    sizer.Add(self.choices, 1, wxEXPAND|wxLEFT|wxRIGHT, 10)
                    sizer.Add(wxStaticLine(self, -1), 0, wxEXPAND|wxALL, 10)
                    sz2 = wxBoxSizer(wxHORIZONTAL)
                    sz2.Add(wxButton(self, wxID_OK, "OK"), 0, wxALL, 10)
                    sz2.Add(wxButton(self, wxID_CANCEL, "Cancel"), 0,wxALL, 10)
                    sizer.Add(sz2, 0, wxALIGN_CENTER)
                    self.SetAutoLayout(True)
                    self.SetSizer(sizer)
                    sizer.Fit(self)

                def get_value(self):
                    ret = []
                    for c in range(self.choices.Number()):
                        if self.choices.IsChecked(c): ret.append(str(c))
                    return ",".join(ret)

                def set_choices(self, values):
                    if wxPlatform != '__WXGTK__':
                        self.choices.Set(values)
                    else:
                        self.choices.Clear()
                        for v in values:
                            self.choices.Append(v)

                def set_descriptions(self, title, message):
                    self.SetTitle(title)
                    self.message.SetLabel(message)
                    
            # end of class Dialog
            self.dialog[0] = Dialog()
            
        DialogProperty.__init__(self, owner, name, parent, self.dialog[0],
                                can_disable)
        self.choices_setter = callback

    def display_dialog(self, event):
        self.set_choices(self.choices_setter())
        self.dialog.set_descriptions(self.title, self.message)
        DialogProperty.display_dialog(self, event)

    def set_choices(self, values):
        self.dialog.set_choices(values)

# end of class CheckListDialogProperty

class EditFlexGridSizer(GridSizerBase):
    """\
    Class to handle wxFlexGridSizer objects
    """
    def __init__(self, name, window, rows=3, cols=3, vgap=0, hgap=0,
                 toplevel=True, show=True):
        GridSizerBase.__init__(self, name, 'wxFlexGridSizer', window, rows,
                               cols, vgap, hgap, toplevel, show)

    def create_widget(self):
        self.widget = CustomSizer(self, wxFlexGridSizer, self.rows, self.cols,
                                  self.vgap, self.hgap)
        GridSizerBase.create_widget(self)
        for r in self.grow_rows:
            self.widget.AddGrowableRow(r)
        for c in self.grow_cols:
            self.widget.AddGrowableCol(c)
        if not self.toplevel and hasattr(self, 'sizer'):
            # hasattr(self, 'sizer') is False only in case of a 'change_sizer'
            # call
            self.sizer.add_item(self, self.pos, self.option, self.flag,
                                self.border) #, self.widget.GetMinSize())

    def _property_setup(self):
        GridSizerBase._property_setup(self)
        self.grow_rows = []
        self.access_functions['growable_rows'] = (self.get_growable_rows,
                                                  self.set_growable_rows)
        self.grow_cols = []
        self.access_functions['growable_cols'] = (self.get_growable_cols,
                                                  self.set_growable_cols)
        def rows_setter():
            return map(str, range(self.get_rows()))
        pr = CheckListDialogProperty(self, 'growable_rows', None,
                                     'Growable Rows', 'Select growable rows',
                                     rows_setter)
        self.properties['growable_rows'] = pr
        def cols_setter():
            return map(str, range(self.get_cols()))
        pr = CheckListDialogProperty(self, 'growable_cols', None,
                                     'Growable Columns',
                                     'Select growable columns',
                                     cols_setter)
        self.properties['growable_cols'] = pr

    def create_properties(self):
        GridSizerBase.create_properties(self)
        page = self.notebook.GetPage(1)
        sizer = page.GetSizer()
        props = self.properties
        props['growable_rows'].display(page)
        props['growable_cols'].display(page)
        sizer.Add(props['growable_rows'].panel, 0, wxEXPAND)
        sizer.Add(props['growable_cols'].panel, 0, wxEXPAND)
        sizer.Layout()
        sizer.Fit(page)
        
    def set_growable_rows(self, value):
        try: self.grow_rows = [int(i) for i in value.split(',')]
        except:
            if not value.strip(): self.grow_rows = []
            else:
                self.properties['growable_rows'].set_value(
                    self.get_growable_rows())
                return
        if self.widget:
            if self.notebook: page = self.notebook.GetSelection()
            else: page = 0
            misc.wxCallAfter(change_sizer, self, self.klass_prop.get_value(),
                             page)
##             for i in range(self.widget.GetRows()):
##                 self.widget.RemoveGrowableRow(i)
##             else:
##                 for r in self.grow_rows:
##                     try: self.widget.AddGrowableRow(r)
##                     except:
##                         import traceback; traceback.print_exc()

    def set_growable_cols(self, value):
        try: self.grow_cols = [int(i) for i in value.split(',')]
        except:
            if not value.strip(): self.grow_cols = []
            else:
                self.properties['growable_cols'].set_value(
                    self.get_growable_cols())
                return
        if self.widget:
            if self.notebook: page = self.notebook.GetSelection()
            else: page = 0
            misc.wxCallAfter(change_sizer, self, self.klass_prop.get_value(),
                             page)
##             for i in range(self.widget.GetCols()):
##                 self.widget.RemoveGrowableCol(i)
##             else:
##                 for c in self.grow_cols:
##                     try: self.widget.AddGrowableCol(c)
##                     except:
##                         import traceback; traceback.print_exc()

    def get_growable_rows(self): return ','.join(map(str, self.grow_rows))
    def get_growable_cols(self): return ','.join(map(str, self.grow_cols))

# end of class EditFlexGridSizer


def _builder(parent, sizer, pos, orientation=wxVERTICAL, slots=1,
             is_static=False, label="", number=[1], show=True):
    num = slots
    name = 'sizer_%d' % number[0]
    while common.app_tree.has_name(name):
        number[0] += 1
        name = 'sizer_%d' % number[0]
    if sizer is not None: topl = 0
    else: topl = 1
    if is_static:
        sz = EditStaticBoxSizer(name, parent, orientation, label, num, topl)
    else:
        sz = EditBoxSizer(name, parent, orientation, num, topl)
    if sizer is not None:
        sizer.add_item(sz, pos, 1, wxEXPAND)
        node = Tree.Node(sz)
        sz.node = node
        common.app_tree.insert(node, sizer.node, pos-1)
        common.adding_sizer = False
    else:
        parent.set_sizer(sz)
        node = Tree.Node(sz)
        sz.node = node
        if pos is None: common.app_tree.add(node, parent.node)
        else:
            common.app_tree.insert(node, parent.node, pos-1)
            sz.pos = pos

    sz.show_widget(show) #True)
    if sizer is not None:
        sz.sizer_properties['flag'].set_value('wxEXPAND')
        sz.sizer_properties['pos'].set_value(pos-1)
   

def builder(parent, sizer, pos, number=[1], show=True):
    """\
    factory function for box sizers.
    """
    class SizerDialog(wxDialog):
        def __init__(self, parent):
            wxDialog.__init__(self, misc.get_toplevel_parent(parent), -1,
                              'Select sizer type')
            tmp = wxFlexGridSizer(2, 2)
            tmp.Add(wxStaticText(self, -1, 'Orientation'), 0,
                    wxALL|wxALIGN_CENTER_VERTICAL, 3)
            self.orientation = wxChoice(self, -1, choices=['Horizontal',
                                                           'Vertical'])
            self.orientation.SetSelection(0)
            tmp.Add(self.orientation, 0, wxALL|wxEXPAND, 3)
            tmp.Add(wxStaticText(self, -1, 'Slots'), 0,
                    wxALL|wxALIGN_CENTER_VERTICAL, 3)
            self.num = wxSpinCtrl(self, -1)
            self.num.SetRange(1, 100)
            self.num.SetValue(1)
            tmp.Add(self.num, 0, wxALL, 3)
            szr = wxBoxSizer(wxVERTICAL)
            szr.Add(tmp)
            CHECK_ID = wxNewId()
            self.check = wxCheckBox(self, CHECK_ID, 'Has a Static Box')
            self.label = wxTextCtrl(self, -1, "")
            self.label.Enable(False)
            EVT_CHECKBOX(self, CHECK_ID, self.on_check_statbox)
            szr.Add(self.check, 0, wxALL|wxEXPAND, 4)
            tmp = wxBoxSizer(wxHORIZONTAL)
            tmp.Add(wxStaticText(self, -1, "Label: "))
            tmp.Add(self.label, 1)
            szr.Add(tmp, 0, wxALL|wxEXPAND, 4)
            
            btn = wxButton(self, wxID_OK, 'OK')
            btn.SetDefault()
            szr.Add(btn, 0, wxALL|wxALIGN_CENTER, 10)
            self.SetAutoLayout(1)
            self.SetSizer(szr)
            szr.Fit(self)

        def reset(self):
            self.orientation.SetSelection(0);
            self.num.SetValue(1)
            self.check.SetValue(0)
            self.label.SetValue("")
            self.label.Enable(False)

        def on_check_statbox(self, event):
            self.label.Enable(event.IsChecked())

    # end of class SizerDialog

    dialog = SizerDialog(parent)
    dialog.ShowModal()
    if dialog.orientation.GetStringSelection() == 'Horizontal':
        orientation = wxHORIZONTAL
    else: orientation = wxVERTICAL
    num = dialog.num.GetValue()
    
    _builder(parent, sizer, pos, orientation, num, dialog.check.GetValue(),
             dialog.label.GetValue())
##     name = 'sizer_%d' % number[0]
##     while common.app_tree.has_name(name):
##         number[0] += 1
##         name = 'sizer_%d' % number[0]
##     if sizer is not None: topl = 0
##     else: topl = 1
##     if dialog.check.GetValue():
##         sz = EditStaticBoxSizer(name, parent, orientation,
##                                 dialog.label.GetValue(), num, topl)
##     else:
##         sz = EditBoxSizer(name, parent, orientation, num, topl)
##     if sizer is not None:
##         sizer.add_item(sz, pos, 1, wxEXPAND)
##         node = Tree.Node(sz)
##         sz.node = node
##         common.app_tree.insert(node, sizer.node, pos-1)
##         common.adding_sizer = False
##     else:
##         parent.set_sizer(sz)
##         node = Tree.Node(sz)
##         sz.node = node
##         if pos is None: common.app_tree.add(node, parent.node)
##         else:
##             common.app_tree.insert(node, parent.node, pos-1)
##             sz.pos = pos

##     sz.show_widget(show) #True)
##     if sizer is not None:
##         sz.sizer_properties['flag'].set_value('wxEXPAND')
##         sz.sizer_properties['pos'].set_value(pos-1)
    dialog.Destroy()


def xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    """\
    factory function to build EditBoxSizer objects from an xml file
    """
    from xml_parse import XmlParsingError
    try: name = attrs['name']
    except KeyError: raise XmlParsingError, "'name' attribute missing"
    orientation = wxVERTICAL # default value
    if sizer is not None: topl = False
    else: topl = True
    if attrs['base'] == 'EditStaticBoxSizer':
        sz = EditStaticBoxSizer(name, parent, orientation, '', 0, topl)
    else:
        sz = EditBoxSizer(name, parent, orientation, 0, topl)
    if sizer is not None:
        if sizeritem is None:
            raise XmlParsingError, "'sizeritem' object not found"
        sizer.add_item(sz, pos=pos, option=sizeritem.option,
                       flag=sizeritem.flag, border=sizeritem.border) 
        node = Tree.Node(sz)
        sz.node = node
        if pos is None: common.app_tree.add(node, sizer.node)
        else: common.app_tree.insert(node, sizer.node, pos-1)
    else:
        parent.set_sizer(sz)
        node = Tree.Node(sz)
        sz.node = node
        common.app_tree.add(node, parent.node)
    return sz


def grid_builder(parent, sizer, pos, number=[1], show=True):
    """\
    factory function for grid sizers
    """
    class Dialog(wxDialog):
        def __init__(self, parent):
            wxDialog.__init__(self, misc.get_toplevel_parent(parent), -1,
                              'Select sizer attributes')
            self.rows = SpinProperty(self, 'rows', self)
            self.cols = SpinProperty(self, 'cols', self)
            self.vgap = SpinProperty(self, 'vgap', self)
            self.hgap = SpinProperty(self, 'hgap', self)
            self.flex = wxCheckBox(self, -1, '')

            self.rows.set_value(3)
            self.cols.set_value(3)
            self.vgap.set_value(0)
            self.hgap.set_value(0)

            szr = wxBoxSizer(wxHORIZONTAL)
            szr.Add(wxStaticText(self, -1, 'Flexible'), 2,
                    wxALL|wxALIGN_CENTER_VERTICAL, 4)
            szr.Add(self.flex, 5, wxALL, 4)

            sizer = wxBoxSizer(wxVERTICAL)
            sizer.Add(self.rows.panel, 0, wxLEFT|wxRIGHT|wxTOP|wxEXPAND, 10)
            sizer.Add(self.cols.panel, 0, wxLEFT|wxRIGHT|wxEXPAND, 10)
            sizer.Add(self.vgap.panel, 0, wxLEFT|wxRIGHT|wxEXPAND, 10)
            sizer.Add(self.hgap.panel, 0, wxLEFT|wxRIGHT|wxEXPAND, 10)
            sizer.Add(szr, 0, wxLEFT|wxRIGHT|wxEXPAND, 10)
            szr = wxBoxSizer(wxHORIZONTAL)
            btn = wxButton(self, wxID_OK, 'OK')
            btn.SetDefault()            
            szr.Add(btn)
            sizer.Add(szr, 0, wxALL|wxALIGN_CENTER, 10)
            self.SetAutoLayout(True)
            self.SetSizer(sizer)
            sizer.Fit(self)

        def __getitem__(self, name):
            return (lambda : 0, lambda v: None)

    # end of inner class

    dialog = Dialog(parent)
    dialog.ShowModal()
    rows = int(dialog.rows.get_value())
    cols = int(dialog.cols.get_value())
    vgap = int(dialog.vgap.get_value())
    hgap = int(dialog.hgap.get_value())

    name = 'grid_sizer_%d' % number[0]
    while common.app_tree.has_name(name):
        number[0] += 1
        name = 'grid_sizer_%d' % number[0]
    topl = True
    if dialog.flex.GetValue(): constructor = EditFlexGridSizer
    else: constructor = EditGridSizer
    if sizer is not None: topl = False
    sz = constructor(name, parent, rows, cols, vgap, hgap, topl)
    if sizer is not None:
        sizer.add_item(sz, pos, 1, wxEXPAND)
        node = Tree.Node(sz)
        sz.node = node
        common.app_tree.insert(node, sizer.node, pos-1)
        common.adding_sizer = False
    else:
        parent.set_sizer(sz)
        node = Tree.Node(sz)
        sz.node = node
        if pos is None: common.app_tree.add(node, parent.node)
        else:
            common.app_tree.insert(node, parent.node, pos-1)
            sz.pos = pos

    sz.show_widget(show) #True)
    if sizer is not None:
        sz.sizer_properties['flag'].set_value('wxEXPAND')
        sz.sizer_properties['pos'].set_value(pos-1)
    
    dialog.Destroy()


def grid_xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    """\
    factory function to build EditGridSizer objects from an xml file
    """
    from xml_parse import XmlParsingError
    try: name = attrs['name']
    except KeyError: raise XmlParsingError, "'name' attribute missing"
    if attrs['base'] == 'EditGridSizer': constructor = EditGridSizer
    else: constructor = EditFlexGridSizer
    if sizer is not None: 
        sz = constructor(name, parent, rows=0, cols=0, toplevel=False)
        if sizeritem is None:
            raise XmlParsingError, "'sizeritem' object not found"
        sizer.add_item(sz, pos=pos, option=sizeritem.option,
                       flag=sizeritem.flag, border=sizeritem.border)
        node = Tree.Node(sz)
        sz.node = node
        if pos is None: common.app_tree.add(node, sizer.node)
        else: common.app_tree.insert(node, sizer.node, pos-1)
    else: 
        sz = constructor(name, parent, rows=0, cols=0, toplevel=True)
        parent.set_sizer(sz)
        node = Tree.Node(sz)
        sz.node = node
        common.app_tree.add(node, parent.node)
    return sz
        

def init_all():
    """\
    module initialization function: returns a list of buttons (to add to the
    main palette) to add the various sizers
    """
    cw = common.widgets
    cw['EditBoxSizer'] = builder
    cw['EditGridSizer'] = grid_builder

    cwx = common.widgets_from_xml
    cwx['EditBoxSizer'] = xml_builder
    cwx['EditStaticBoxSizer'] = xml_builder
    cwx['EditGridSizer'] = grid_xml_builder
    cwx['EditFlexGridSizer'] = grid_xml_builder

    from tree import WidgetTree
    import os.path
    WidgetTree.images['EditStaticBoxSizer'] = os.path.join(common.wxglade_path,
                                                           'icons/sizer.xpm')
    WidgetTree.images['EditFlexGridSizer'] = os.path.join(
        common.wxglade_path, 'icons/grid_sizer.xpm')

    return [common.make_object_button('EditBoxSizer', 'icons/sizer.xpm'),
            common.make_object_button('EditGridSizer', 'icons/grid_sizer.xpm')]



