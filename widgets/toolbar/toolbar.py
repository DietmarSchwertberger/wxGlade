# toolbar.py: wxToolBar objects
# $Id: toolbar.py,v 1.7 2003/07/18 16:43:52 agriggio Exp $
#
# Copyright (c) 2002-2003 Alberto Griggio <albgrig@tiscalinet.it>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

from wxPython.wx import *
from wxPython.lib.filebrowsebutton import FileBrowseButton

import common, math, misc, os
from tree import Tree
from tool import *
from widget_properties import *
from edit_windows import EditBase, TopLevelBase, PreviewMixin


class _MyBrowseButton(FileBrowseButton):
    def createBrowseButton( self):
        """Create the browse-button control"""
        ID = wxNewId()
        button =wxButton(self, ID, misc.wxstr(self.buttonText))
        button.SetToolTipString(misc.wxstr(self.toolTip))
        w = button.GetTextExtent(self.buttonText)[0] + 10
        button.SetSize((w, -1))
        EVT_BUTTON(button, ID, self.OnBrowse)
        return button

# end of class _MyBrowseButton


class ToolsDialog(wxDialog):
    def __init__(self, parent, items=None):
        wxDialog.__init__(self, parent, -1, "Toolbar editor",
                          style=wxDEFAULT_DIALOG_STYLE|wxRESIZE_BORDER)
        ADD_ID, REMOVE_ID, NAME_ID, LABEL_ID, ID_ID, CHECK_RADIO_ID, LIST_ID, \
                ADD_SEP_ID, MOVE_UP_ID, MOVE_DOWN_ID, HELP_STR_ID, \
                LONG_HELP_STR_ID, BITMAP1_ID, BITMAP2_ID \
                = [wxNewId() for i in range(14)]
        self.tool_items = wxListCtrl(self, LIST_ID, style=wxLC_REPORT | \
                                     wxLC_SINGLE_SEL|wxSUNKEN_BORDER,
                                     size=(300, -1))
        self.selected_index = -1 # index of the selected element in the 
                                 # wxListCtrl 
        self.tool_items.InsertColumn(0, "Label")
        self.tool_items.InsertColumn(1, "Id")
        self.tool_items.InsertColumn(2, "Normal Bitmap")
        self.tool_items.InsertColumn(3, "Second Bitmap")
        self.tool_items.InsertColumn(4, "Short Help")
        self.tool_items.InsertColumn(5, "Long Help")
        self.tool_items.InsertColumn(6, "Type")
        self.tool_items.SetColumnWidth(0, 100)
        self.tool_items.SetColumnWidth(2, 100)
        self.tool_items.SetColumnWidth(3, 150)
        self.tool_items.SetColumnWidth(4, 150)
        self.tool_items.SetColumnWidth(5, 100)
        self.tool_items.SetColumnWidth(6, 150)
        # tool fields
        self.id = wxTextCtrl(self, ID_ID)
        self.label = wxTextCtrl(self, LABEL_ID)
        self.help_str = wxTextCtrl(self, HELP_STR_ID)
        self.long_help_str = wxTextCtrl(self, LONG_HELP_STR_ID)
        self.bitmap1 = _MyBrowseButton(
            self, BITMAP1_ID, labelText='Normal Bitmap', buttonText='...',
            changeCallback=self.update_tool)
        self.bitmap2 = _MyBrowseButton(
            self, BITMAP2_ID, labelText='Second Bitmap', buttonText='...',
            changeCallback=self.update_tool)
        self.check_radio = wxRadioBox(
            self, CHECK_RADIO_ID, "Type",
            choices=['Normal', 'Checkable', 'Radio'], majorDimension=3)

        self.add = wxButton(self, ADD_ID, "Add")
        self.remove = wxButton(self, REMOVE_ID, "Remove")
        self.add_sep = wxButton(self, ADD_SEP_ID, "Add separator")

        # tools navigation
        self.move_up = wxButton(self, MOVE_UP_ID, "Up")
        self.move_down = wxButton(self, MOVE_DOWN_ID, "Down")

        self.ok = wxButton(self, wxID_OK, " OK ")
        self.cancel = wxButton(self, wxID_CANCEL, "Cancel")

        self.do_layout()
        # event handlers
        EVT_BUTTON(self, ADD_ID, self.add_tool)
        EVT_BUTTON(self, REMOVE_ID, self.remove_tool)
        EVT_BUTTON(self, ADD_SEP_ID, self.add_separator)
        EVT_BUTTON(self, MOVE_UP_ID, self.move_item_up)
        EVT_BUTTON(self, MOVE_DOWN_ID, self.move_item_down)
        EVT_KILL_FOCUS(self.label, self.update_tool)
        EVT_KILL_FOCUS(self.id, self.update_tool)
        EVT_KILL_FOCUS(self.help_str, self.update_tool)
        EVT_KILL_FOCUS(self.long_help_str, self.update_tool)
        EVT_RADIOBOX(self, CHECK_RADIO_ID, self.update_tool)
        EVT_LIST_ITEM_SELECTED(self, LIST_ID, self.show_tool)
        if items:
            self.add_tools(items)

    def do_layout(self):
        self.label.Enable(False)
        self.id.Enable(False)
        self.help_str.Enable(False)
        self.long_help_str.Enable(False)
        self.bitmap1.Enable(False)
        self.bitmap2.Enable(False)
        self.check_radio.Enable(False)
        
        sizer = wxBoxSizer(wxVERTICAL)
        sizer2 = wxStaticBoxSizer(wxStaticBox(self, -1, "Tool:"), \
                                  wxVERTICAL)
        self.label.SetSize((150, -1))
        self.id.SetSize((150, -1))
        self.help_str.SetSize((150, -1))
        self.long_help_str.SetSize((150, -1))
        szr = wxFlexGridSizer(0, 2)
        szr.Add(wxStaticText(self, -1, "Id   "))
        szr.Add(self.id)
        szr.Add(wxStaticText(self, -1, "Label  "))
        szr.Add(self.label)
        szr.Add(wxStaticText(self, -1, "Short Help  "))
        szr.Add(self.help_str)
        szr.Add(wxStaticText(self, -1, "Long Help  "))
        szr.Add(self.long_help_str)
        sizer2.Add(szr, 1, wxALL|wxEXPAND, 5)
        label_w = self.bitmap1.browseButton.GetTextExtent('...')[0]
        sizer2.Add(self.bitmap1, 0, wxEXPAND)
        sizer2.Add(self.bitmap2, 0, wxEXPAND)
        self.bitmap1.browseButton.SetSize((label_w + 4, -1))
        self.bitmap2.browseButton.SetSize((label_w + 4, -1))
        sizer2.Add(self.check_radio, 0, wxLEFT|wxRIGHT|wxBOTTOM, 4)
        szr = wxGridSizer(0, 2, 3, 3)
        szr.Add(self.add, 0, wxEXPAND); szr.Add(self.remove, 0, wxEXPAND)
        sizer2.Add(szr, 0, wxEXPAND)
        sizer2.Add(self.add_sep, 0, wxTOP|wxEXPAND, 3)

        sizer3 = wxBoxSizer(wxVERTICAL)
        sizer3.Add(self.tool_items, 1, wxALL|wxEXPAND, 5)
        sizer4 = wxBoxSizer(wxHORIZONTAL)

        sizer4.Add(self.move_up, 0, wxLEFT|wxRIGHT, 3)
        sizer4.Add(self.move_down, 0, wxLEFT|wxRIGHT, 5)
        sizer3.Add(sizer4, 0, wxALIGN_CENTER|wxALL, 5)
        szr = wxBoxSizer(wxHORIZONTAL)
        szr.Add(sizer3, 1, wxALL|wxEXPAND, 5) 
        szr.Add(sizer2, 0, wxTOP|wxBOTTOM|wxRIGHT, 5)
        sizer.Add(szr, 1, wxEXPAND)
        sizer2 = wxBoxSizer(wxHORIZONTAL)
        sizer2.Add(self.ok, 0, wxALL, 5)
        sizer2.Add(self.cancel, 0, wxALL, 5)
        sizer.Add(sizer2, 0, wxALL|wxALIGN_CENTER, 3)
        self.SetAutoLayout(1)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.SetSize((-1, 350))
        self.CenterOnParent()

    def add_tool(self, event):
        """\
        Event handler called when the Add button is clicked
        """
        index = self.selected_index = self.selected_index+1
        if not self.tool_items.GetItemCount():
            for s in (self.label, self.id, self.help_str, self.long_help_str,
                      self.bitmap1, self.bitmap2, self.check_radio):
                s.Enable(True)
        if index < 0: index = self.tool_items.GetItemCount()
        name, label, id, check_radio = "", "item", "", "0"
        bitmap1, bitmap2, help_str, long_help_str = [""] * 4
        self.tool_items.InsertStringItem(index, label)
        self.tool_items.SetStringItem(index, 1, id)
        self.tool_items.SetStringItem(index, 2, bitmap1)
        self.tool_items.SetStringItem(index, 3, bitmap2)
        self.tool_items.SetStringItem(index, 4, help_str)
        self.tool_items.SetStringItem(index, 5, long_help_str)
        self.tool_items.SetStringItem(index, 6, check_radio)
        self.tool_items.SetItemState(index, wxLIST_STATE_SELECTED,
                                     wxLIST_STATE_SELECTED)
        self.label.SetValue(label)
        self.id.SetValue(id)
        self.check_radio.SetSelection(int(check_radio))
        self.bitmap1.SetValue(bitmap1, False)
        self.bitmap2.SetValue(bitmap2, False)
        self.help_str.SetValue(help_str)
        self.long_help_str.SetValue(long_help_str)

    def add_separator(self, event):
        """\
        Event handler called when the Add Separator button is clicked
        """
        index = self.selected_index+1
        if not self.tool_items.GetItemCount():
            for s in (self.label, self.id, self.help_str, self.long_help_str,
                      self.bitmap1, self.bitmap2, self.check_radio):
                s.Enable(True)
        if index < 0: index = self.tool_items.GetItemCount() 
        self.tool_items.InsertStringItem(index, '---')#label)
        for i in range(1, 5):
            self.tool_items.SetStringItem(index, i, '---')
        self.tool_items.SetItemState(index, wxLIST_STATE_SELECTED,
                                     wxLIST_STATE_SELECTED)

    def show_tool(self, event):
        """\
        Event handler called when a tool in the list is selected
        """        
        self.selected_index = index = event.GetIndex()
        get_item = self.tool_items.GetItem
        if not self.tool_items.GetItem(index, 2).m_text == '---':
            # skip if the selected item is a separator
            for (s, i) in ((self.label, 0), (self.id, 1),
                           (self.help_str, 4), (self.long_help_str, 5)):
                s.SetValue(get_item(index, i).m_text)
            self.bitmap1.SetValue(get_item(index, 2).m_text, False)
            self.bitmap2.SetValue(get_item(index, 3).m_text, False)
            try:
                self.check_radio.SetSelection(
                    int(self.tool_items.GetItem(index, 6).m_text))
            except:
                self.check_radio.SetSelection(0)
        event.Skip()

    def update_tool(self, event):
        """\
        Event handler called when some of the properties of the current tool
        changes
        """        
        set_item = self.tool_items.SetStringItem
        index = self.selected_index
        if index < 0: return
        set_item(index, 0, self.label.GetValue())
        set_item(index, 1, self.id.GetValue())
        set_item(index, 2, self.bitmap1.GetValue())
        set_item(index, 3, self.bitmap2.GetValue())
        set_item(index, 4, self.help_str.GetValue())
        set_item(index, 5, self.long_help_str.GetValue())
        set_item(index, 6, str(self.check_radio.GetSelection()))
        try:
            event.Skip()
        except AttributeError:
            # this happens on wx2.4.0.1 for FileBrowseButton events
            pass
        # update the directory of the browse buttons
        directory = os.path.split(self.bitmap1.GetValue())[0]
        if not os.path.isdir(directory):
            directory = os.path.split(self.bitmap2.GetValue())[0]
        if os.path.isdir(directory):
            self.bitmap1.startDirectory = directory
            self.bitmap2.startDirectory = directory

    def remove_tool(self, event):
        """\
        Event handler called when the Remove button is clicked
        """        
        if self.selected_index >= 0:
            for s in (self.id, self.label, self.help_str, self.long_help_str):
                s.SetValue("")
            for s in (self.bitmap1, self.bitmap2):
                s.SetValue("", False)
            self.check_radio.SetSelection(0)
            self.tool_items.DeleteItem(self.selected_index)
            if not self.tool_items.GetItemCount():
                for s in (self.id, self.label, self.help_str,
                          self.long_help_str, self.bitmap1, self.bitmap2,
                          self.check_radio):
                    s.Enable(False)

    def add_tools(self, tools):
        """\
        adds the content of 'tools' to self.tool_items. tools is a sequence of
        (simple) tool items for the toolbar. At the moment there is no control
        support, but I hope to add it soon
        """
        set_item = self.tool_items.SetStringItem
        add_item = self.tool_items.InsertStringItem
        index = [0]
        def add(tool):
            i = index[0]
            add_item(i, misc.wxstr(tool.label))
            set_item(i, 1, misc.wxstr(tool.id))
            set_item(i, 2, misc.wxstr(tool.bitmap1))
            set_item(i, 3, misc.wxstr(tool.bitmap2))
            set_item(i, 4, misc.wxstr(tool.short_help))
            set_item(i, 5, misc.wxstr(tool.long_help))
            item_type = 0
            set_item(i, 6, misc.wxstr(tool.type))
            index[0] += 1
        for tool in tools:
            add(tool)
        if self.tool_items.GetItemCount():
            for s in (self.id, self.label, self.help_str, self.long_help_str,
                      self.bitmap1, self.bitmap2, self.check_radio):
                s.Enable(True)
            

    def get_tools(self):
        """\
        returns the contents of self.tool_items as a list of tools that
        describes the contents of the ToolBar
        """
        def get(i, j): return self.tool_items.GetItem(i, j).m_text
        tools = []
        def add(index):
            label = get(index, 0)
            id = get(index, 1)
            bitmap1 = get(index, 2)
            bitmap2 = get(index, 3)
            short_help = get(index, 4)
            long_help = get(index, 5)
            try:
                item_type = int(get(index, 6))
            except ValueError:
                item_type = 0
            tools.append(Tool(label=label, id=id, type=item_type,
                              short_help=short_help, long_help=long_help,
                              bitmap1=bitmap1, bitmap2=bitmap2))
        for index in range(self.tool_items.GetItemCount()):
            add(index)

        return tools

    def move_item_up(self, event):
        """\
        moves the selected tool before the previous one at the same level
        in self.tool_items
        """
        self.tool_items.SetFocus()
        if self.selected_index > 0:
            index = self.selected_index - 1
            vals1 = [ self.tool_items.GetItem(self.selected_index, i).m_text \
                      for i in range(7) ]
            vals2 = [ self.tool_items.GetItem(index, i).m_text \
                      for i in range(7) ]
            for i in range(7):
                self.tool_items.SetStringItem(index, i, vals1[i])
                self.tool_items.SetStringItem(self.selected_index, i, vals2[i])
            state = wxLIST_STATE_SELECTED | wxLIST_STATE_FOCUSED
            self.tool_items.SetItemState(index, state, state)
            self.selected_index = index

    def move_item_down(self, event):
        """\
        moves the selected tool after the next one at the same level
        in self.tool_items
        """
        self.tool_items.SetFocus()
        if self.selected_index < self.tool_items.GetItemCount()-1:
            index = self.selected_index + 1
            vals1 = [ self.tool_items.GetItem(self.selected_index, i).m_text \
                      for i in range(7) ]
            vals2 = [ self.tool_items.GetItem(index, i).m_text \
                      for i in range(7) ]
            for i in range(7):
                self.tool_items.SetStringItem(index, i, vals1[i])
                self.tool_items.SetStringItem(self.selected_index, i, vals2[i])
            state = wxLIST_STATE_SELECTED | wxLIST_STATE_FOCUSED
            self.tool_items.SetItemState(index, state, state)
            self.selected_index = index
                                                  
#end of class ToolsDialog


class ToolsProperty(Property):
    """\
    Property to edit the tools of an EditToolBar instance.
    """
    def __init__(self, owner, name, parent):
        Property.__init__(self, owner, name, parent)
        self.panel = None
        self.tools = {}
        if parent is not None: self.display(parent)

    def display(self, parent):
        self.panel = wxPanel(parent, -1)
        edit_btn_id = wxNewId()
        self.edit_btn = wxButton(self.panel, edit_btn_id, "Edit tools...")
        sizer = wxBoxSizer(wxHORIZONTAL)
        sizer.Add(self.edit_btn, 1, wxEXPAND|wxALIGN_CENTER|wxTOP|wxBOTTOM, 4)
        self.panel.SetAutoLayout(1)
        self.panel.SetSizer(sizer)
        self.panel.SetSize(sizer.GetMinSize())
        EVT_BUTTON(self.panel, edit_btn_id, self.edit_tools)

    def bind_event(*args): pass

    def edit_tools(self, event):
        dialog = ToolsDialog(self.panel, items=self.owner.get_tools())
        if dialog.ShowModal() == wxID_OK:
            self.owner.set_tools(dialog.get_tools())
            common.app_tree.app.saved = False # update the status of the app

    def write(self, outfile, tabs):
        fwrite = outfile.write
        fwrite('    ' * tabs + '<tools>\n')
        for tool in self.owner[self.name][0]():
            tool.write(outfile, tabs+1)
        fwrite('    ' * tabs + '</tools>\n')

# end of class MenuProperty


class EditToolBar(EditBase, PreviewMixin):
    def __init__(self, name, klass, parent, property_window):
        custom_class = parent is None
        EditBase.__init__(self, name, klass,
                          parent, wxNewId(), property_window,
                          custom_class=custom_class, show=False)
        def nil(*args): return ()
        self.tools = [] # list of Tool objects
        self._tb = None # the real toolbar
        self.style = 0
        self.access_functions['style'] = (self.get_style, self.set_style)
        self.style_pos  = [wxTB_FLAT, wxTB_DOCKABLE, wxTB_3DBUTTONS]
        if misc.check_wx_version(2, 3, 3):
            self.style_pos += [wxTB_TEXT, wxTB_NOICONS, wxTB_NODIVIDER,
                               wxTB_NOALIGN]
        style_labels = ['#section#Style', 'wxTB_FLAT', 'wxTB_DOCKABLE',
                        'wxTB_3DBUTTONS']
        if misc.check_wx_version(2, 3, 3):
            style_labels += ['wxTB_TEXT', 'wxTB_NOICONS',
                             'wxTB_NODIVIDER', 'wxTB_NOALIGN']
        self.properties['style'] = CheckListProperty(self, 'style', None,
                                                     style_labels)
        self.bitmapsize = '16, 15'
        self.access_functions['bitmapsize'] = (self.get_bitmapsize,
                                               self.set_bitmapsize)
        self.properties['bitmapsize'] = TextProperty(self, 'bitmapsize', None,
                                                     can_disable=True)
        self.margins = '0, 0'
        self.access_functions['margins'] = (self.get_margins, self.set_margins)
        self.properties['margins'] = TextProperty(self, 'margins', None,
                                                  can_disable=True)
        self.access_functions['tools'] = (self.get_tools, self.set_tools)
        prop = self.properties['tools'] = ToolsProperty(self, 'tools', None)
        self.packing = 1
        self.access_functions['packing'] = (self.get_packing, self.set_packing)
        self.properties['packing'] = SpinProperty(self, 'packing', None,
                                                  r=(0, 100), can_disable=True)
        self.separation = 5
        self.access_functions['separation'] = (self.get_separation,
                                               self.set_separation)
        self.properties['separation'] = SpinProperty(
            self, 'separation', None, r=(0, 100), can_disable=True)
        # 2003-05-07 preview support
        PreviewMixin.__init__(self)

    def create_widget(self):
        tb_style = wxTB_HORIZONTAL|self.style
        if wxPlatform == '__WXGTK__': tb_style |= wxTB_DOCKABLE|wxTB_FLAT
        if self.parent:
            self.widget = self._tb = wxToolBar(
                self.parent.widget, -1, style=tb_style)
            self.parent.widget.SetToolBar(self.widget)
        else:
            # "top-level" toolbar
            self.widget = wxFrame(None, -1, self.name)
            self.widget.SetClientSize((400, 30))
            self._tb = wxToolBar(self.widget, -1, style=tb_style)
            self.widget.SetToolBar(self._tb)
            self.widget.SetBackgroundColour(self._tb.GetBackgroundColour())
            EVT_CLOSE(self.widget, lambda e: self.hide_widget())
            EVT_LEFT_DOWN(self._tb, self.on_set_focus)
            if wxPlatform == '__WXMSW__':
                # MSW isn't smart enough to avoid overlapping windows, so
                # at least move it away from the 3 wxGlade frames
                self.widget.CenterOnScreen()
        EVT_LEFT_DOWN(self.widget, self.on_set_focus)
        # set the various property values
        prop = self.properties
        if prop['bitmapsize'].is_active():
            self.set_bitmapsize(self.bitmapsize, refresh=False)
        if prop['margins'].is_active():
            self.set_margins(self.margins, refresh=False)
        if prop['packing'].is_active():
            self.set_packing(self.packing, refresh=False)
        if prop['separation'].is_active():
            self.set_separation(self.separation, refresh=False)
        self.set_tools(self.tools) # show the menus

    def create_properties(self):
        EditBase.create_properties(self)
        page = self._common_panel
        sizer = page.GetSizer()
        self.properties['bitmapsize'].display(page)
        self.properties['margins'].display(page)
        self.properties['packing'].display(page)
        self.properties['separation'].display(page)
        self.properties['style'].display(page)
        self.properties['tools'].display(page)
        if not sizer:
            sizer = wxBoxSizer(wxVERTICAL)
            sizer.Add(self.name_prop.panel, 0, wxEXPAND)
            sizer.Add(self.klass_prop.panel, 0, wxEXPAND)
            page.SetAutoLayout(1)
            page.SetSizer(sizer)
        sizer.Add(self.properties['bitmapsize'].panel, 0, wxEXPAND)
        sizer.Add(self.properties['margins'].panel, 0, wxEXPAND)
        sizer.Add(self.properties['packing'].panel, 0, wxEXPAND)
        sizer.Add(self.properties['separation'].panel, 0, wxEXPAND)
        sizer.Add(self.properties['style'].panel, 0, wxEXPAND)
        sizer.Add(self.properties['tools'].panel, 0, wxALL|wxEXPAND, 3)
        sizer.Layout()
        sizer.Fit(page)
        w, h = page.GetClientSize()
        self.notebook.AddPage(page, "Common")
        if self.parent is not None:
            self.property_window.Layout()
            page.SetScrollbars(1, 5, 1, math.ceil(h/5.0))
        else:
            PreviewMixin.create_properties(self)
        
    def __getitem__(self, key):
        return self.access_functions[key]

    def get_style(self):
        retval = [0] * len(self.style_pos)
        try:
            for i in range(len(self.style_pos)):
                if self.style & self.style_pos[i]:
                    retval[i] = 1
        except AttributeError:
            pass
        return retval

    def set_style(self, value, refresh=True):
        value = self.properties['style'].prepare_value(value)
        self.style = 0
        for v in range(len(value)):
            if value[v]:
                self.style |= self.style_pos[v]
        if self._tb:
            self._tb.SetWindowStyleFlag(self.style)
            if refresh: self._refresh_widget()

    def get_margins(self):
        return self.margins

    def set_margins(self, value, refresh=True):
        try:
            margins = [int(t.strip()) for t in value.split(',')]
        except:
            self.properties['margins'].set_value(self.margins)
        else:
            self.margins = value
            if self._tb:
                self._tb.SetMargins(margins)
                if refresh: self._refresh_widget()

    def get_packing(self):
        return self.packing

    def set_packing(self, value, refresh=True):
        try:
            value = int(value)
        except:
            self.properties['packing'].set_value(self.packing)
        else:
            self.packing = value
            if self._tb:
                self._tb.SetToolPacking(self.packing)
                if refresh: self._refresh_widget()

    def get_separation(self):
        return self.separation

    def set_separation(self, value, refresh=True):
        try:
            value = int(value)
        except:
            self.properties['separation'].set_value(self.separation)
        else:
            self.separation = value
            if self._tb:
                self._tb.SetToolSeparation(self.separation)
                if refresh: self._refresh_widget()

    def get_bitmapsize(self):
        return self.bitmapsize
        
    def set_bitmapsize(self, value, refresh=True):
        try:
            size = [int(t.strip()) for t in value.split(',')]
        except:
            self.properties['bitmapsize'].set_value(self.bitmapsize)
        else:
            self.bitmapsize = value
            if self._tb:
                self._tb.SetToolBitmapSize(size)
                if refresh: self._refresh_widget()

    def get_tools(self):
        return self.tools

    def set_tools(self, tools):
        self.tools = tools
        if not self._tb: return # nothing left to do
        while self._tb.DeleteToolByPos(0):
            pass # clear the toolbar
        # now add all the tools
        for tool in self.tools:
            if misc.streq(tool.id, '---'): # the tool is a separator
                self._tb.AddSeparator()
            else:
                if tool.bitmap1:
                    bmp1 = wxBitmap(misc.wxstr(tool.bitmap1),
                                    wxBITMAP_TYPE_ANY)
                    if not bmp1.Ok(): bmp1 = wxEmptyBitmap(1, 1)
                else:
                    bmp1 = wxNullBitmap
                if tool.bitmap2:
                    bmp2 = wxBitmap(misc.wxstr(tool.bitmap2),
                                    wxBITMAP_TYPE_ANY)
                    if not bmp1.Ok(): bmp1 = wxEmptyBitmap(1, 1)
                else:
                    bmp2 = wxNullBitmap
                # signature of AddTool for 2.3.2.1:
                # wxToolBarToolBase *AddTool(
                #    int id, const wxBitmap& bitmap,
                #    const wxBitmap& pushedBitmap, bool toggle = FALSE,
                #    wxObject *clientData = NULL,
                #    const wxString& shortHelpString = wxEmptyString,
                #    const wxString& longHelpString = wxEmptyString)
                if not misc.check_wx_version(2, 3, 3):
                    # use the old signature, some of the entries are ignored
                    self._tb.AddTool(wxNewId(), bmp1, bmp2, tool.type == 1,
                                     shortHelpString=\
                                     misc.wxstr(tool.short_help),
                                     longHelpString=misc.wxstr(tool.long_help))
                else:
                    kinds = [wxITEM_NORMAL, wxITEM_CHECK, wxITEM_RADIO]
                    try:
                        kind = kinds[int(tool.type)]
                    except (ValueError, IndexError):
                        kind = wxITEM_NORMAL
                    self._tb.AddLabelTool(wxNewId(), misc.wxstr(tool.label),
                                          bmp1, bmp2, kind,
                                          misc.wxstr(tool.short_help),
                                          misc.wxstr(tool.long_help))
        # this is required to refresh the toolbar properly
        self._refresh_widget()

    def _refresh_widget(self):
        #print self._tb.GetSize(), self._tb.GetBestSize()
        self._tb.Realize()
        self._tb.SetSize((-1, self._tb.GetBestSize()[1]))
        if self.parent:
            widget = self.parent.widget
            w, h = widget.GetClientSize()
            widget.SetClientSize((w, h+1))
            widget.SetClientSize((w, h))
        else:
            widget = self.widget
            w = widget.GetClientSize()[0]
            h = self._tb.GetSize()[1] / 2
            widget.SetClientSize((w, h))
        
    def remove(self, *args, **kwds):
        if self.parent is not None:
            self.parent.properties['toolbar'].set_value(0)
            if kwds.get('do_nothing', False): # and wxPlatform == '__WXGTK__':
                # this probably leaks memory, but avoids segfaults
                self.widget = None
            else:
                if self.parent.widget:
                    self.parent.widget.SetToolBar(None)
        else:
            if self.widget:
                self.widget.Destroy()
                self.widget = None
        EditBase.remove(self)

    def popup_menu(self, event):
        if self.parent is not None:
            return # do nothing in this case
        if self.widget:
            if not self._rmenu:
                REMOVE_ID, HIDE_ID = [wxNewId() for i in range(2)]
                self._rmenu = misc.wxGladePopupMenu(self.name)
                misc.append_item(self._rmenu, REMOVE_ID, 'Remove\tDel',
                                 'remove.xpm')
                misc.append_item(self._rmenu, HIDE_ID, 'Hide')
                EVT_MENU(self.widget, REMOVE_ID, self.remove)
                EVT_MENU(self.widget, HIDE_ID, self.hide_widget)
                
            self.widget.PopupMenu(self._rmenu, event.GetPosition())

    def hide_widget(self, *args):
        if self.widget and self.widget is not self._tb:
            self.widget.Hide()
            common.app_tree.expand(self.node, False)
            common.app_tree.select_item(self.node.parent)
            common.app_tree.app.show_properties()

    def set_name(self, name):
        EditBase.set_name(self, name)
        if self.widget is not self._tb:
            self.widget.SetTitle(misc.wxstr(self.name))

    def get_property_handler(self, name):
        class ToolsHandler:
            itemattrs = ['label', 'id', 'short_help', 'long_help',
                         'bitmap1', 'bitmap2', 'type']
            def __init__(self, owner):
                self.owner = owner
                self.tools = []
                self.curr_tool = None
                self.curr_index = -1
            def start_elem(self, name, attrs):
                if name == 'tools': return
                if name == 'tool':
                    self.curr_tool = Tool()
                else:
                    try:
                        self.curr_index = self.itemattrs.index(name)
                    except ValueError:
                        self.curr_index = -1
                        pass # just ignore the attributes we don't know
##                         from xml_parse import XmlParsingError
##                         raise XmlParsingError, "invalid tool attribute"
            def end_elem(self, name):
                if name == 'tool':
                    self.tools.append(self.curr_tool)
                if name == 'tools':
                    self.owner.set_tools(self.tools)
                    return True
            def char_data(self, data):
                if self.curr_index >= 0:
                    setattr(self.curr_tool,
                            self.itemattrs[self.curr_index], data)
                
        if name == 'tools':
            return ToolsHandler(self)
        return None

# end of class EditToolBar


def builder(parent, sizer, pos, number=[0]):
    """\
    factory function for EditToolBar objects.
    """
    class Dialog(wxDialog):
        def __init__(self):
            wxDialog.__init__(self, None, -1, 'Select toolbar class')
            if not number[0]: self.klass = 'MyToolBar'
            else: self.klass = 'MyToolBar%s' % number[0]
            number[0] += 1
            klass_prop = TextProperty(self, 'class', self)
            szr = wxBoxSizer(wxVERTICAL)
            szr.Add(klass_prop.panel, 0, wxEXPAND)
            sz2 = wxBoxSizer(wxHORIZONTAL)
            sz2.Add(wxButton(self, wxID_OK, 'OK'), 0, wxALL, 3)
            sz2.Add(wxButton(self, wxID_CANCEL, 'Cancel'), 0, wxALL, 3)
            szr.Add(sz2, 0, wxALL|wxALIGN_CENTER, 3)
            self.SetAutoLayout(True)
            self.SetSizer(szr)
            szr.Fit(self)
            #self.SetSize((150, -1))

        def undo(self):
            number[0] -= 1

        def __getitem__(self, value):
            if value == 'class':
                def set_klass(c): self.klass = c
                return (lambda : self.klass, set_klass)
    # end of inner class

    dialog = Dialog()
    if dialog.ShowModal() == wxID_CANCEL:
        # cancel the operation
        dialog.undo()
        dialog.Destroy()
        return
    
    name = 'toolbar_%d' % number[0]
    while common.app_tree.has_name(name):
        number[0] += 1
        name = 'toolbar_%d' % number[0]

    tb = EditToolBar(name, dialog.klass, parent, common.property_panel)
    tb.node = Tree.Node(tb)
    common.app_tree.add(tb.node)
    tb.show_widget(True)
    tb.show_properties()
    

def xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    """\
    factory to build EditMenuBar objects from an xml file
    """
    name = attrs.get('name')
    if parent is not None:
        if name:
            parent.toolbar.set_name(name)
            parent.toolbar.name_prop.set_value(name)
        return parent.toolbar
    else:
        tb = EditToolBar(name, attrs.get('class', 'wxMenuBar'), None,
                         common.property_panel)
        tb.node = Tree.Node(tb)
        common.app_tree.add(tb.node)
        return tb


def initialize():
    """\
    initialization function for the module: returns a wxBitmapButton to be
    added to the main palette.
    """
    cwx = common.widgets_from_xml
    cwx['EditToolBar'] = xml_builder
    common.widgets['EditToolBar'] = builder
    
    return common.make_object_button('EditToolBar', 'icons/toolbar.xpm', 1)
