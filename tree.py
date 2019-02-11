"""\
Classes to handle and display the structure of a wxGlade app

@copyright: 2002-2007 Alberto Griggio
@copyright: 2014-2016 Carsten Grohmann
@copyright: 2016-2019 Dietmar Schwertberger
@license: MIT (see LICENSE.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import logging, os.path
import wx
import misc, common, compat, config, clipboard

DEBUG = config.debugging and False
if DEBUG:
    import utilities

class WidgetTree(wx.TreeCtrl):#, Tree):
    "Tree with the ability to display the hierarchy of widgets"
    images = {} # Dictionary of icons of the widgets displayed
    _logger = None # Class specific logging instance
    def __init__(self, parent, application):
        self._logger = logging.getLogger(self.__class__.__name__)
        style = wx.TR_DEFAULT_STYLE|wx.TR_HAS_VARIABLE_ROW_HEIGHT
        style |= wx.TR_EDIT_LABELS
        if wx.Platform == '__WXGTK__':    style |= wx.TR_NO_LINES|wx.TR_FULL_ROW_HIGHLIGHT
        elif wx.Platform == '__WXMAC__':  style &= ~wx.TR_ROW_LINES
        wx.TreeCtrl.__init__(self, parent, -1, style=style)
        self.cur_widget = None  # reference to the selected widget
        self.root = application
        image_list = wx.ImageList(21, 21)
        image_list.Add(wx.Bitmap(os.path.join(config.icons_path, 'application.xpm'), wx.BITMAP_TYPE_XPM))
        for w in WidgetTree.images:
            WidgetTree.images[w] = image_list.Add(misc.get_xpm_bitmap(WidgetTree.images[w]))
        self.AssignImageList(image_list)
        application.item = self.AddRoot(_('Application'), 0)
        self._SetItemData(application.item, application)
        self.skip_select = 0  # necessary to avoid an infinite loop on win32, as SelectItem fires an
                              # EVT_TREE_SEL_CHANGED event

        self.drop_target = clipboard.DropTarget(self, toplevel=True)
        self.SetDropTarget(self.drop_target)
        self._drag_ongoing = False
        self.auto_expand = True  # this control the automatic expansion of  nodes: it is set to False during xml loading
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_change_selection)
        self.Bind(wx.EVT_RIGHT_DOWN, self.popup_menu)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_dclick)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_click) # allow direct placement of widgets
        self.Bind(wx.EVT_MENU, self.on_menu)  # for handling the selection of the first item
        self._popup_menu_widget = None  # the widget for the popup menu
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.begin_drag)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_events)

        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.begin_edit_label)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.end_edit_label)
        #self.Bind(wx.EVT_KEY_DOWN, misc.on_key_down_event)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down_event)
        #self.Bind(wx.EVT_CHAR_HOOK, self.on_char)  # on wx 2.8 the event will not be delivered to the child
        self.Bind(wx.EVT_TREE_DELETE_ITEM, self.on_delete_item)

    def on_char(self, event):
        "called from main: start label editing on F2; skip events while editing"
        if event.GetKeyCode()==wx.WXK_F2 and self.cur_widget and self.cur_widget._label_editable():
            # start label editing
            self.EditLabel( self.cur_widget.item )
            return True
        if isinstance(self.FindFocus(), wx.TextCtrl):
            # currently editing
            event.Skip()
            return True
        return False

    def on_key_down_event(self, event):
        #if event.GetKeyCode()==13:
            ## go to property editor
            #common.property_panel.SetFocus()
            #return
        if event.GetKeyCode()==wx.WXK_WINDOWS_MENU and self.cur_widget:
            # windows menu key pressed -> display context menu for selected item
            item = self.RootItem  if self.cur_widget is self.app else  self.cur_widget.item
            if item:
                rect = self.GetBoundingRect(item, textOnly=True)
                if rect is not None:
                    pos = (rect.right, (rect.top+rect.bottom)//2)
                    self.cur_widget.popup_menu(event, pos=pos)
                    return
        #misc.on_key_down_event(event)
        event.Skip()

    def begin_drag(self, evt):
        # start drag & drop
        item = evt.GetItem()
        widget = self._GetItemData(item)
        if widget is self.root or widget.IS_SLOT: return  # application and slots can't be dragged
        self._drag_ongoing = True
        clipboard.begin_drag(self, widget)
        self._drag_ongoing = False

    def begin_edit_label(self, evt):
        # Begin editing a label. This can be prevented by calling Veto()
        widget = self._GetItemData( evt.Item )
        if not widget._label_editable(): evt.Veto()

    def _split_name_label(self, new_value):
        # split user input into name and label; if there's no colon but a quotation mark, it's just a label
        new_name = new_label = None
        new_value = new_value.strip()
        if new_value.endswith("'") and ": '" in new_value:
            new_name, new_label = new_value.split(": '", 1)
            new_label = new_label[:-1]
        elif new_value.endswith('"') and ': "' in new_value:
            new_name, new_label = new_value.split(': "', 1)
            new_label = new_label[:-1]
        elif new_value and (new_value[0] in ["'",'"'] or new_value[-1] in ["'",'"']):
            # just a label; for this we accept errors, we just want at least one quotation mark
            if new_value[0]==new_value[-1] and len(new_value)>2:
                new_label = new_value[1:-1]
            elif new_value[0] in ["'",'"']:
                new_label = new_value[1:]
            elif new_value[-1] in ["'",'"']:
                new_label = new_value[:-1]
        elif not ":" in new_value:
            new_name = new_value
        return new_name, new_label

    def end_edit_label(self, evt):
        # Finish editing a label. This can be prevented by calling Veto()
        if evt.IsEditCancelled(): return
        item = evt.Item
        widget = self._GetItemData( item )
        if "name" not in widget.properties: return

        new_value = evt.Label
        if new_value==widget._get_tree_label(): return

        new_name = new_label = new_title = new_tab = new_class = None
        
        if widget.klass != widget.base and widget.klass != 'wxScrolledWindow':
            if new_value.count("(")==1 and new_value.count(")")==1:
                pre, new_class = new_value.split("(")
                new_class, post = new_class.split(")")
                if pre.endswith(" "): pre = pre[:-1]
                new_value = pre+post

        if "label" in widget.properties and widget._label_editable():
            new_name, new_label = self._split_name_label(new_value)
        elif "label" in widget.properties:
            # label is not editable, but name may have changed
            new_name, dummy = self._split_name_label(new_value)
        elif getattr(widget, "has_title", None):
            new_name, new_title = self._split_name_label(new_value)
        elif getattr(widget, "parent", None) and widget.parent.klass=="wxNotebook" and "]" in new_value:
            # notebook pages: include page title: "[title] name"
            new_tab, new_name = new_value.rsplit("]",1)
            if "[" in new_tab: new_tab = new_tab.split("[",1)[-1]
            new_name = new_name.strip()
        else:
            new_name = new_value

        # check name
        if new_name:
            name_p = widget.properties["name"]
            if new_name==name_p.get(): new_name = None
        if new_name:
            # check
            OK = name_p.check(new_name)
            if not OK: new_name = None

        # check class/klass
        if new_class:
            class_p = widget.properties["klass"]
            if new_class==class_p.get(): new_class = None
        if new_class:
            # check
            OK = class_p.check(new_class)
            if not OK: new_class = None

        # check label
        if new_label is not None:
            label_p = widget.properties["label"]
            if new_label==label_p.get(): new_label = None
        if not new_name and new_label is None and new_title is None and new_tab is None and new_class is None:
            # no change or an error
            wx.Bell()
            evt.Veto()
            return
        # check title
        if new_title is not None:
            title_p = widget.properties["title"]
            if new_title==title_p.get(): new_title = None
        # check notabook tab
        if new_tab is not None:
            notebook = widget.parent
            tabs_p = notebook.properties["tabs"]
            if widget in notebook.children:
                index = notebook.children.index(widget)
                if notebook.tabs[index][0]==new_tab:
                    new_tab = None
                else:
                    new_tabs = notebook.tabs[:]
                    new_tabs[index][0] = new_tab
            else:
                new_tab = None

        # actually modify the values
        modified = set()
        if new_name:
            name_p.previous_value = name_p.value
            name_p.set(new_name, notify=False)
            modified.add("name")
        if new_class:
            class_p.previous_value = class_p.value
            class_p.set(new_class, notify=False)
            modified.add("class")
        if new_label:
            label_p.previous_value = label_p.value
            label_p.set(new_label, notify=False)
            modified.add("label")
        if new_title:
            title_p.previous_value = title_p.value
            title_p.set(new_title, notify=False)
            modified.add("title")
        if modified:
            widget.properties_changed(modified)
            self.root.saved = False  # update the status of the app
        if new_tab:
            tabs_p.previous_value = tabs_p.value
            tabs_p.set(new_tabs, notify=True)
        wx.CallAfter( self.refresh, widget, refresh_label=True)  # setting from within the event handler does not work

    if compat.IS_CLASSIC:
        def _SetItemData(self, item, data):
            self.SetPyData(item, data)
        def _GetItemData(self, item):
            if not bool(item): return None
            return self.GetPyData(item)
    else:
        def _SetItemData(self, item, data):
            self.SetItemData(item, data)
        def _GetItemData(self, item):
            if not bool(item): return None
            return self.GetItemData(item)

    def add2(self, child, parent=None, index=None, item=None):
        "appends child to the list of parent's children"
        image = self.images.get( child._get_tree_image(), -1)
        label = child._get_tree_label()
        if item is None:
            if index is None:
                item = child.item = self.AppendItem(parent.item, label, image)
            else:
                
                item = child.item = compat.wx_Tree_InsertItemBefore(self, parent.item, index, label, image)
        else:
            # re-use
            child.item = item
            self.refresh(child)
        self._SetItemData(item, child)
        if self.auto_expand:
            self.Expand(parent.item)
        if DEBUG:
            print("added item", utilities.hx(item), child, child.item)
        return item

    def remove(self, node):
        # just remove the mutual references between editor and tree item
        if node.item is None: return  # could be during common.root.clear() when there is an error on loading
        self._SetItemData(node.item, None)
        node.item = None

    ####################################################################################################################
    # new implementation:
    def on_delete_item(self, event):
        item = event.GetItem()
        editor = self.GetItemData( item )
        if DEBUG:
            print("on_delete_item", utilities.hx(item), editor, editor and editor.item or None)
        if editor is not None and editor.item is item:
            editor.item = None

    def _get_children_items(self, item):
        items = []
        child_item, cookie = self.GetFirstChild(item)
        while child_item.IsOk():
            items.append(child_item)
            child_item, cookie = self.GetNextChild(item, cookie)
        return items

    def _build_children(self, widget, item, recursive=True):
        # XXX a better algorithm would be nice
        # currently it's checked from the start and from the end how many are matching; all inbetween are replaced
        if DEBUG: print("_build_children", widget)
        children = widget.get_all_children()
        items = self._get_children_items(widget.item)
        if DEBUG: print("children", children)
        if DEBUG: print("items", items)
        item_editors = []
        for child_item in items:
            editor = self._GetItemData(child_item)
            if editor is not None and (not children or not editor in children):
                self._SetItemData(child_item, None)
                if editor.item is child_item:
                    if DEBUG: print("removed editor.item", utilities.hx(editor), utilities.hx(editor.item))
                    editor.item = None  # is probably None already
                item_editors.append(None)
            else:
                item_editors.append(editor)
        if DEBUG: print("item_editors", item_editors)
        if DEBUG: print()
        match_beginning = 0
        for c,child in enumerate(children):
            if c<len(item_editors) and item_editors[c] is child:
                match_beginning = c+1
            else:
                break
        match_end = 0
        c = -1
        while match_beginning+match_end<len(children):
            if match_end<len(item_editors) and item_editors[c] is children[c]:
                match_end += 1
            else:
                break
            c -= 1

        if len(children) > len(item_editors):
            # insert or add items, right after match_beginning
            for n in range( len(children) - len(item_editors) ):
                index = match_beginning + n
                child = children[index]
                item = self.add2(child, parent=widget, index=index)
                items.insert(index, item)
        elif len(children) < len(item_editors):
            # remove items, right after match_beginning
            for n in range( len(item_editors) - len(children) ):
                index = match_beginning 
                child_item = items[index]
                self.Delete(child_item)
                del items[match_beginning]
        if match_beginning+match_end<len(children):
            # length matches, re-use item in the middle
            for index in range(match_beginning, len(children)-match_end):
                child = children[index]
                item = self.add2(child, parent=widget, index=index, item=items[index])
        
        if not recursive:
            # update labels and images, called e.g. when notebook pages change
            for child in children:
                self.refresh(child)
            return
        for child, item in zip(children, items):
            self._build_children(child, item)

    def build(self, widget=None, recursive=True):
        if DEBUG:
            print("="*80)
            print("build", widget, recursive)
        # (re-)build tree from data structure
        # e.g. .build(control)
        # XXX if recursive is not True, ensure that all children are refreshed, as e.g. slot numbers may have changed
        self.Freeze()
        try:
    
            if widget is None:
                widget = self.root
                item = self.GetRootItem()
            else:
                item = widget.item
                if item is None and widget.parent.item:
                    # check whether at the same position there is an item already without an editor
                    pos = widget.parent._get_child_pos(widget)
                    items = self._get_children_items(widget.parent.item)
                    if len(items)>pos and self._GetItemData(items[pos]) is None:
                        item = items[pos]
                        widget.item = item
                        self._SetItemData(item, widget)
                        self.refresh(widget)
                while item is None:
                    widget = widget.parent
                    item = widget.item
            self._build_children(widget, item, recursive)
        finally:
            self.Thaw()
        #if config.debugging or DEBUG:
        if DEBUG:
            import utilities
            utilities.TreePrinter(self)

    def refresh(self, widget, refresh_label=True, refresh_image=True):
        # refresh label and/or image
        if widget.item is None: return
        if refresh_label:
            self.SetItemText(widget.item, widget._get_tree_label())
        if refresh_image:
            image = self.images.get( widget._get_tree_image(), -1)
            self.SetItemImage(widget.item, image)

    def select_item(self, node):
        self.skip_select = True
        self.SelectItem(node.item)
        self.skip_select = False
        self._set_cur_widget(node)
        misc.set_focused_widget(self.cur_widget)

    def _set_cur_widget(self, widget):
        # set self.cur_widget; adjust label colors and bold if required (on Windows)
        if self.cur_widget and wx.Platform == "__WXMSW__" and self.cur_widget.item:
            item = self.cur_widget.item
            self.SetItemTextColour(item, wx.NullColour)
            self.SetItemBold( item, False )
        self.cur_widget = widget
        item = widget.item
        self.EnsureVisible(item)
        # ensure that the icon is visible
        text_rect = self.GetBoundingRect(item, True)
        if text_rect.x<22:
            self.SetScrollPos(wx.HORIZONTAL, self.GetScrollPos(wx.HORIZONTAL) - 22 + text_rect.x)
        if wx.Platform == "__WXMSW__":
            self.SetItemBold(item, True)
            self.SetItemTextColour(item, wx.BLUE)
        s = widget._get_tooltip_string()
        common.main.user_message( s and s.replace("\n", " ") or "" )

    def set_current_widget(self, widget):
        # interface from common.set_focused_widget
        if widget is None or widget is self.cur_widget: return
        self.skip_select = True
        self.SelectItem(widget.item)
        self.skip_select = False
        self._set_cur_widget(widget)

    def on_change_selection(self, event):
        if self.skip_select: return  # triggered by self.SelectItem in self.set_current_widget
        item = event.GetItem()
        widget = self._GetItemData(item)
        self._set_cur_widget(widget)
        misc.set_focused_widget(widget)
        if not self.IsExpanded(item):
            self.Expand(item)
        self.SetFocus()

    def on_left_click(self, event):
        if not common.adding_widget: return event.Skip()
        widget = self._find_node_by_pos( *event.GetPosition() )
        if not widget: return event.Skip()

        compatible, message = widget.check_drop_compatibility()
        if not compatible:
            event.Skip()
            misc.error_message(message)
            return

        common.adding_window = event.GetEventObject().GetTopLevelParent()
        if widget.IS_SLOT:
            widget.on_drop_widget(event)
        elif common.adding_sizer or True:
            widget.drop_sizer()
        common.adding_window = None

    def on_left_dclick(self, event):
        x, y = event.GetPosition()
        widget = self._find_node_by_pos(x, y)
        if not widget:
            event.Skip()
            return
        if widget.WX_CLASS=='wxMenuBar':
            widget.properties["menus"].edit_menus()
        elif widget.WX_CLASS=='wxToolBar':
            widget.properties["tools"].edit_tools()
        elif widget.IS_TOPLEVEL:
            self.show_toplevel(None, widget)
        else:
            event.Skip()

    def on_leave_window(self, event):
        self.SetCursor(wx.STANDARD_CURSOR)
        event.Skip()

    def on_menu(self, event):
        # the first entry in the popup menu, i.e. the name was selected
        if self._popup_menu_widget is None: return
        if self._popup_menu_widget.IS_TOPLEVEL_WINDOW:
            self.show_toplevel( None, self._popup_menu_widget )

    def on_mouse_events(self, event):
        if not self._drag_ongoing and not event.IsButton():
            message = None
            # set cursor to indicate a possible drop
            x,y = event.GetPosition()
            widget = self._find_node_by_pos(x, y, toplevels_only=False)
            if widget is not None:
                if not common.adding_widget:
                    self.SetCursor(wx.STANDARD_CURSOR)
                else:
                    # check whether the item can be dropped here
                    compatible, message = widget.check_drop_compatibility()
                    if compatible:
                        self.SetCursor(wx.CROSS_CURSOR) # a Cursor instance
                    else:
                        compat.SetCursor(self, wx.CURSOR_NO_ENTRY)
            else:
                self.SetCursor(wx.STANDARD_CURSOR)
            compat.SetToolTip(self, message or "")
        event.Skip()

    def popup_menu(self, event, pos=None):
        widget = self._find_node_by_pos(*event.GetPosition())
        if not widget: return
        self.select_item(widget)
        self._popup_menu_widget = widget
        widget.popup_menu(event, pos)
        self._popup_menu_widget = None

    def _show_widget_toplevel(self, widget):
        # creates/shows the widget of the given toplevel node and all its children
        assert not config.debugging or not wx.IsBusy()
        wx.BeginBusyCursor()
        widget.create_widgets()
        self.ExpandAllChildren(widget.item)
        wx.EndBusyCursor()

    def show_toplevel(self, event, widget=None):
        "Event handler for left double-clicks: if the click is above a toplevel widget and this is hidden, shows it"
        if widget is None:
            try: x, y = event.GetPosition()
            except AttributeError:
                # if we are here, event is a CommandEvent and not a MouseEvent
                widget = self._GetItemData(self.GetSelection())
                self.ExpandAllChildren(widget.item)  # if we are here, the widget must be shown
            else:
                widget = self._find_node_by_pos(x, y, toplevels_only=True)

        if widget is None or widget.IS_ROOT: return

        # the actual toplevel widget may be one level higher, e.g. for a Panel, which is embedded in a Frame
        set_size = None
        if widget.IS_TOPLEVEL:
            # toplevel window or a menu/status bar
            toplevel_widget = widget.widget
            if widget.check_prop("size") and widget.check_prop("toolbar") and widget.toolbar:
                # apply workaround for size changes due to a toolbar; this would cause problems with automatic testing
                set_size = widget.properties.get("size").get_size()
        else:
            toplevel_widget = widget.widget.GetParent()

        if not widget.is_visible():
            # added by rlawson to expand node on showing top level widget
            self.ExpandAllChildren(widget.item)
            self._show_widget_toplevel(widget)
            if wx.Platform != '__WXMSW__' and set_size is not None:
                toplevel_widget = widget.widget  # above it was not yet created
                wx.CallAfter(toplevel_widget.SetSize, set_size)
        else:
            widget.hide_widget()
            #toplevel_widget.GetTopLevelParent().Hide()
            if event: event.Skip()
        if "design" in widget.properties: widget.design.update_label()

    def _find_node_by_pos(self, x, y, toplevels_only=False):
        """Finds the node which is displayed at the given coordinates. Returns None if there's no match.
        If toplevels_only is True, scans only root's children"""
        item, flags = self.HitTest((x, y))
        if item and flags & (wx.TREE_HITTEST_ONITEMLABEL | wx.TREE_HITTEST_ONITEMICON):
            node = self._GetItemData(item)
            if not toplevels_only or node.parent is self.root:
                return node
        return None

    def find_widget_by_pos(self, x, y, toplevels_only=False):
        node = self._find_node_by_pos(x, y, toplevels_only)
        if node is None: return None
        # expand node if user remains at position
        last_pos = getattr(self, "_last_find_widget_pos", None)
        self._last_find_widget_pos = (x,y)
        if last_pos and last_pos==(x,y) and not self.IsExpanded(node.item): self.Expand(node.item)
        return node

    def change_node(self, old, new, keep_children=False):
        self._SetItemData(old.item, new)
        if not keep_children:
            old_children = old.children
            for c in old_children or []:
                self.Delete(c.item)
        new.item = old.item
        old.item = None
        self.refresh(new)

    def get_selected_path(self, w=None, include_position=True):
        """returns a list of widget names, from the toplevel to the selected one
        Example: ['frame_1', 'sizer_1', 'panel_1', 'sizer_2', 'button_1']
                 if button_1 is the currently selected widget"""
        ret = []
        if w is None: w = self.cur_widget
        oldw = None  # the toplevel, to get the position
        while w:
            if w.IS_TOPLEVEL: oldw = w
            if w.IS_SLOT:
                ret.append("SLOT %d"%w.pos)
            else:
                ret.append(w.name)
            w = w.parent
        ret.reverse()
        # ALB 2007-08-28: remember also the position of the toplevel window in the selected path
        if include_position and oldw is not None and oldw.widget is not None:
            assert oldw.widget
            toplevel = misc.get_toplevel_parent(oldw.widget)
            if toplevel:
                ret[0] = (ret[0], toplevel.GetPosition())
        return ret

    def get_widget_path(self, w):
        return self.get_selected_path(w, include_position=False)

    def select_path(self, path):
        "sets the selected widget from a path_list, which should be in the form returned by get_selected_path"
        widget = common.root.find_widget_from_path(path)
        if not widget: return
        item = widget.item
        self._set_cur_widget(widget)
        self.Expand(widget.item)
        self.select_item(widget)
        if widget.IS_ROOT: return
        self._show_widget_toplevel(widget.toplevel_parent)

        if len(path)>=2 and isinstance(path[0], tuple) and widget.widget:
            # a position
            pos = path[0][1]
            misc.get_toplevel_parent(widget.widget).SetPosition(pos)
