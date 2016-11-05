"""\
Classes to handle and display the structure of a wxGlade app

@copyright: 2002-2007 Alberto Griggio
@copyright_ 2014-2016 Carsten Grohmann
@copyright_ 2016      Dietmar Schwertberger
@license: MIT (see LICENSE.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import logging, os.path, sys, time
import wx
import misc, common, compat, config, clipboard
import edit_sizers, application


class Node(object):
    __empty_win = None

    def __init__(self, widget=None, children=None):
        self.widget = widget      # e.g. EditPanel or EditBoxSizer
        self.children = children  # list of Node or SlotNode instances
        self.parent = None        # parent node; will be set in Tree.add/insert

    @classmethod
    def remove_rec(cls, node):
        "recursively remove node and it's children"
        for child_node in (node.children or []):
            cls.remove_rec(child_node)
        node.children = None
        if node.widget is not None:
            # call the widget's ``destructor''
            node.widget.delete()
        node.widget = None

    def remove(self):
        self.remove_rec(self)
        try:
            self.parent.children.remove(self)
        except:
            pass

    def has_ancestor(self, node):
        # returns True if node is parent or parents parent ...
        parent = self.parent
        if parent is None: return False
        while True:
            if node is parent: return True
            if parent.parent is None: return False
            parent = parent.parent

    #def __repr__(self):
        #try: return self.widget.name
        #except AttributeError: return repr(self.widget)

    def write(self, outfile, tabs, class_names=None):
        "Writes the xml code for the widget to the given output file"
        # XXX move this to the widget
        import edit_sizers
        fwrite = outfile.write
        assert self.widget is not None

        # write object tag, including class, name, base
        classname = getattr(self.widget, '_classname', self.widget.__class__.__name__)
        # to disable custom class code generation (for panels...)
        if getattr(self.widget, 'no_custom_class', False):
            no_custom = u' no_custom_class="1"'
        else:
            no_custom = ""
        outer_tabs = u'    ' * tabs
        fwrite(u'%s<object %s %s %s%s>\n' % ( outer_tabs,
                                              common.format_xml_attrs(**{'class': self.widget.klass}),
                                              common.format_xml_attrs(name=self.widget.name),
                                              common.format_xml_attrs(base=classname),
                                              no_custom) )

        # write properties, but without name and class
        # XXX be 100% compatible to 0.7.2, where option is written into the object; remove later
        properties = self.widget.get_properties(without=set(edit_sizers.SizerBase.MANAGED_PROPERTIES))
        #properties = self.widget.get_properties(without=set(["pos","flag","border"]))
        for prop in properties:
            prop.write(outfile, tabs+1)

        if class_names is not None and self.widget.__class__.__name__ != 'CustomWidget':
            class_names.add(self.widget.klass)

        if isinstance(self.widget, edit_sizers.SizerBase):
            for child in self.children or []:
                if not isinstance(child, SlotNode):# hasattr(child, 'widget'):
                    inner_xml = compat.StringIO()

                    for name in edit_sizers.SizerBase.MANAGED_PROPERTIES:
                        name = child.widget.properties[name]
                        if name is not None:
                            name.write(inner_xml, tabs+2)

                    child.write(inner_xml, tabs+2, class_names)
                    stmt = common.format_xml_tag( u'object', inner_xml.getvalue(), tabs+1,
                                                  is_xml=True, **{'class': 'sizeritem'} )
                    fwrite(stmt)
                else:
                    child.write(outfile, tabs+1)
        elif self.children is not None:
            for child in self.children:
                child.write(outfile, tabs+1, class_names)
        fwrite(u'%s</object>\n' % outer_tabs)

    def get_image(self, image=None):
        # get an image for this node
        if image is not None:
            return image

        name = self.widget.__class__.__name__
        widget = self.widget

        if name=="SizerSlot":
            name = "EditSizerSlot"
            if hasattr(self.parent.widget, "orient"):
                sizer_orient = self.parent.widget.orient
                if sizer_orient is not None:
                    if sizer_orient==wx.VERTICAL:
                        name = "EditVerticalSizerSlot"
                    elif sizer_orient==wx.HORIZONTAL:
                        name = "EditHorizontalSizerSlot"
            elif hasattr(self.parent.widget, "orientation"):
                if self.parent.widget.orientation=="wxSPLIT_VERTICAL":
                    name = 'EditSplitterSlot-Left'  if widget.pos==1 else  'EditSplitterSlot-Right'
                else:
                    name = 'EditSplitterSlot-Top'   if widget.pos==1 else  'EditSplitterSlot-Bottom'

        elif name in ("EditStaticBoxSizer", "EditBoxSizer"):
            # with or without label, horizontal/vertical
            if widget.orient & wx.VERTICAL:
                name = "EditVerticalSizer"
            elif widget.orient & wx.HORIZONTAL:
                name = "EditHorizontalSizer"
            else:
                name = "EditSpacer"

        elif name == "EditSplitterWindow":
            if widget.orientation=="wxSPLIT_HORIZONTAL":
                name = 'EditSplitterWindow-h'

        index = WidgetTree.images.get(name, -1)
        return index


class SlotNode(Node):
    "Placeholder for an empty sizer slot"
    def write(self, outfile, tabs, class_names=None):
        if self.widget.sizer.is_virtual(): return
        stmt = common.format_xml_tag( u'object', '', tabs, **{'class': 'sizerslot'})
        outfile.write(stmt)


class Tree(object):
    "A class to represent a hierarchy of widgets"

    def __init__(self, root=None, app=None):
        # initialise instance logger
        self._logger = logging.getLogger(self.__class__.__name__)

        # initialise instance
        self.root = root
        if self.root is None: self.root = Node()
        self.current = self.root
        self.app = app   # reference to the app properties
        self.names = {}  # dictionary of names of the widgets: each entry is a dictionary, one for each toplevel widget

    def _find_toplevel(self, node):
        assert node is not None, _("None node in _find_toplevel")
        if node.parent is self.root:
            return node
        while node.parent is not self.root:
            node = node.parent
        return node

    def get_all_class_names(self, node=None):
        if node is None: node = self.root
        ret = []
        for c in node.children or []:
            name = getattr(c.widget, "klass", None)
            if name: ret.append(name)
            ret += self.get_all_class_names(c)

        return ret

    def get_all_names(self):
        ret = set()
        for n in self.names:
            ret.update(self.names[n].keys())
        return ret

    def has_name(self, name, node=None):
        if node is None:
            for n in self.names:
                if name in self.names[n]:
                    return True
            return False
        else:
            node = self._find_toplevel(node) # node is a name
            return name in self.names[node]

    def add(self, child, parent=None):
        if parent is None: parent = self.root
        if parent.children is None: parent.children = []
        parent.children.append(child)
        child.parent = parent
        self.current = child
        self.names.setdefault(self._find_toplevel(child), {})[str(child.widget.name)] = 1
        if parent is self.root and getattr(child.widget.__class__, '_is_toplevel', False):
            self.app.add_top_window(child.widget.name)

    def insert(self, child, parent, index):
        # if at index there is a SlotNode, replace this, otherwise insert
        if parent is None: parent = self.root
        if parent.children is None:
            parent.children = []
        parent.children.insert(index, child)
        child.parent = parent
        self.current = child
        self.names.setdefault(self._find_toplevel(child), {})[str(child.widget.name)] = 1
        if parent is self.root:
            self.app.add_top_window(child.widget.name)

    def clear_name_rec(self, n):
        if n.parent is self.root:
            del self.names[n]
            return
        try:
            del self.names[self._find_toplevel(n)][str(n.widget.name)]
        except (KeyError, AttributeError):
            pass

        for c in (n.children or []):
            self.clear_name_rec(c)

    def remove(self, node=None):
        if node is not None:
            self.clear_name_rec(node)
            if node.parent is self.root and getattr(node.widget, "_is_toplevel", False):
                self.app.remove_top_window(node.widget.name)
            node.remove()
        elif self.root.children:
            for n in self.root.children:
                n.remove()
            self.root.children = None
            self.names = {}

    def write(self, outfile=None, tabs=0):
        """Writes the xml equivalent of this tree to the given output file.
        This function writes unicode to the outfile."""
        # XXX move this to application.Application
        if outfile is None:
            outfile = sys.stdout
        outfile.write( u'<?xml version="1.0"?>\n'
                       u'<!-- generated by wxGlade %s on %s -->\n\n' % (config.version, time.asctime()) )
        outpath = os.path.normpath( os.path.expanduser(self.app.output_path.strip()) )

        attrs = ["name","class","language","top_window","encoding","use_gettext", "overwrite",
                 "for_version","is_template","indent_amount"]

        attrs = dict( (prop,self.app.properties[prop].get_str_value()) for prop in attrs )
        attrs["option"] = self.app.properties["multiple_files"].get_str_value()
        attrs["indent_symbol"] = self.app.properties["indent_mode"].get_str_value()
        attrs["path"] = outpath
        attrs['use_new_namespace'] = 1
        # add a . to the file extensions
        attrs["source_extension"] = '.' + self.app.properties["source_extension"].get_str_value()
        attrs["header_extension"] = '.' + self.app.properties["header_extension"].get_str_value()

        inner_xml = compat.StringIO()

        if self.app.is_template and getattr(self.app, 'template_data', None):
            self.app.template_data.write(inner_xml, tabs+1)

        class_names = set()
        if self.root.children is not None:
            for c in self.root.children:
                c.write(inner_xml, tabs+1, class_names)

        stmt = common.format_xml_tag( u'application', inner_xml.getvalue(), is_xml=True, **attrs )
        outfile.write(stmt)

        return class_names

    def change_node(self, node, widget):
        "Changes the node 'node' so that it refers to 'widget'"
        try:
            del self.names[self._find_toplevel(node)][node.widget.name]
        except KeyError:
            pass
        node.widget = widget
        self.names.setdefault(self._find_toplevel(node), {})[widget.name] = 1

    def change_node_pos(self, node, new_pos, index=None):
        if index is None: index = node.parent.children.index(node)
        if index >= new_pos:
            node.parent.children.insert(new_pos, node)
            del node.parent.children[index + 1]
        else:
            del node.parent.children[index]
            node.parent.children.insert(new_pos+1, node)

    def _find_widget(self, widget, node):
        if node.widget is None or node.widget.widget is None:
            return
        if widget is node.widget.widget: return node
        button = getattr(node.widget.widget, "_btn", None)
        if button is not None and widget is button: return node
        if hasattr(node.widget.widget, "GetStaticBox"):
            if widget is node.widget.widget.GetStaticBox(): return node
        if node.children:
            for child in node.children:
                found = self._find_widget(widget, child)
                if found is not None:
                    return found
        return None

    def find_widget(self, widget, node=None):
        # returns node
        nodes = [node] if node is not None else self.root.children
        for node in nodes:
            found = self._find_widget(widget, node)
            if found is not None:
                return found

    def _prn(self, node, level):
        if isinstance(node, SlotNode):
            print("  "*level, "SLOT")
        else:
            print("  "*level, node.widget)
            if node.children:
                for c in node.children:
                    self._prn(c, level+1)

    def prn(self, start_node=None):
        "print structure to stdout for debugging"
        if start_node is None: start_node = self.root
        self._prn(start_node, 0)



class WidgetTree(wx.TreeCtrl, Tree):
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
        root_node = Node(application)
        application.node = root_node
        self.cur_widget = None  # reference to the selected widget
        Tree.__init__(self, root_node, application)
        image_list = wx.ImageList(21, 21)
        image_list.Add(wx.Bitmap(os.path.join(config.icons_path, 'application.xpm'), wx.BITMAP_TYPE_XPM))
        for w in WidgetTree.images:
            WidgetTree.images[w] = image_list.Add(misc.get_xpm_bitmap(WidgetTree.images[w]))
        self.AssignImageList(image_list)
        root_node.item = self.AddRoot(_('Application'), 0)
        self.SetPyData(root_node.item, root_node)
        self.skip_select = 0  # necessary to avoid an infinite loop on win32, as SelectItem fires an
                              # EVT_TREE_SEL_CHANGED event
        self.title = ' '
        self.set_title(self.title)

        self.drop_target = clipboard.DropTarget(self, toplevel=True)
        self.SetDropTarget(self.drop_target)
        self._drag_ongoing = False
        self.auto_expand = True  # this control the automatic expansion of  nodes: it is set to False during xml loading
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_change_selection)
        self.Bind(wx.EVT_RIGHT_DOWN, self.popup_menu)
        self.Bind(wx.EVT_LEFT_DCLICK, self.show_toplevel)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_click) # allow direct placement of widgets
        self.Bind(wx.EVT_MENU, self.show_toplevel)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.begin_drag)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_events)
        
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.begin_edit_label)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.end_edit_label)
        #self.Bind(wx.EVT_KEY_DOWN, misc.on_key_down_event)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down_event)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char)

    def _label_editable(self, widget=None):
        if widget is None: widget = self.cur_widget
        if widget is None: return False
        if not "name" in widget.properties: return False
        if not "label" in widget.properties: return True
        label = widget.label
        # no editing in case of special characters
        if "\n" in label or "\t" in label or "'" in label or '"' in label: return False
        if len(label)>24: return False
        return True

    def on_char(self, event):
        if event.GetKeyCode()==wx.WXK_F2 and self.cur_widget and self._label_editable():
            # start label editing
            self.EditLabel( self.cur_widget.node.item )
            return
        event.Skip()

    def on_key_down_event(self, event):
        #if event.GetKeyCode()==13:
            ## go to property editor
            #common.property_panel.SetFocus()
            #return
        if event.GetKeyCode()==wx.WXK_WINDOWS_MENU and self.cur_widget:
            # windows menu key pressed -> display context menu for selected item
            item = self.RootItem  if self.cur_widget is self.app else  self.cur_widget.node.item
            if item:
                rect = self.GetBoundingRect(item, textOnly=True)
                if rect is not None:
                    pos = (rect.right, (rect.top+rect.bottom)//2)
                    self.cur_widget.popup_menu(event, pos=pos)
                    return
        misc.on_key_down_event(event)

    def begin_drag(self, evt):
        # start drag & drop
        item = evt.GetItem()
        node = self.GetPyData(item)
        if node is self.root or isinstance(node, SlotNode):  # application and slots can't be dragged
            return
        widget = node.widget
        self._drag_ongoing = True
        clipboard.begin_drag(self, widget)
        self._drag_ongoing = False

    def begin_edit_label(self, evt):
        # Begin editing a label. This can be prevented by calling Veto()
        widget = self.GetPyData( evt.Item ).widget
        #if "name" not in widget.properties: evt.Veto()
        if not self._label_editable(widget): evt.Veto()

    def end_edit_label(self, evt):
        # Finish editing a label. This can be prevented by calling Veto()
        if evt.IsEditCancelled(): return
        item = evt.Item
        node = self.GetPyData( item )
        widget = node.widget
        if "name" not in widget.properties: return

        new_value = evt.Label
        if "label" in widget.properties and self._label_editable(widget):
            # split user input into name and label
            new_value = new_value.strip()
            if new_value.endswith("'") and ": '" in new_value:
                new_name, new_label = new_value.split(": '", 1)
            elif new_value.endswith('"') and ': "' in new_value:
                new_name, new_label = new_value.split(': "', 1)
            else:
                wx.Bell()
                evt.Veto()
                return
            new_label = new_label[:-1]
            label_p = widget.properties["label"]
            label_modified = new_label!=label_p.get()
        else:
            new_name = new_value
            label_modified = False

        name_p = widget.properties["name"]
        old_name = name_p.get()

        # check
        name_OK = name_p.check(new_name)
        if not name_OK:
            wx.Bell()
        if not name_OK or (new_value==old_name and not label_modified):
            evt.Veto()
            return

        # actually modify the values
        modified = set()
        if new_name!=old_name:
            name_p.previous_value = name_p.value
            name_p.set(new_name, notify=False)
            modified.add("name")
        if label_modified:
            label_p.previous_value = label_p.value
            label_p.set(new_label, notify=False)
            modified.add("label")
        widget.properties_changed(modified)

    def _build_label(self, node):
        # get a label for node
        import notebook
        if isinstance(node.widget, edit_sizers.SizerSlot):
            if node.widget.label: return node.widget.label
            pos = node.widget.pos
            if node.widget.sizer and isinstance(node.widget.sizer, edit_sizers.GridSizerBase):
                # row/col
                sizer = node.widget.sizer
                row = (pos-1) // sizer.cols + 1  # 1 based at the moment
                col = (pos-1) %  sizer.cols + 1
                return "SLOT  %d/%d"%(row, col)
            elif isinstance(node.widget.sizer, notebook.notebook.NotebookVirtualSizer):
                return "Notebook Page %d"%(pos)
            else:
                return "SLOT %d"%(pos)
        s = node.widget.name
        if node.widget.klass != node.widget.base and node.widget.klass != 'wxScrolledWindow':
            # special case...
            s += ' (%s)' % node.widget.klass
        elif "label" in node.widget.properties and node.widget.properties["label"].is_active():
            # include label of control
            label = node.widget.label
            label = label.replace("\n","\\n").replace("\t","\\t")
            if '"' in label:
                if len(label)>24:
                    s += ": '%s..."%(label[:18])
                else:
                    s += ": '%s'"%label
            else:
                if len(label)>24:
                    s += ': "%s...'%(label[:18])
                else:
                    s += ': "%s"'%label
        elif getattr(node.widget, "has_title", None):
            # include title
            s += ': "%s"'%node.widget.title
        return s

    def add(self, child, parent=None):
        "appends child to the list of parent's children"
        assert isinstance(child, Node)

        Tree.add(self, child, parent)
        image = child.get_image()
        if parent is None: parent = parent.item = self.GetRootItem()
        child.item = self.AppendItem(parent.item, self._build_label(child), image)
        self.SetPyData(child.item, child)
        if self.auto_expand:
            self.Expand(parent.item)
            self.select_item(child)

        if not isinstance(child.widget, edit_sizers.SizerSlot):
            self.app.check_codegen(child.widget)

    def insert(self, child, parent, index):
        "inserts child to the list of parent's children at index; a SlotNode at index is overwritten"
        assert isinstance(child, Node)
        # pos is index
        if parent is None:
            # XXX check whether this is called at all
            parent = self.GetPyData( self.GetRootItem() )
        assert isinstance(parent, Node)

        # parent is a Node, i.e. Dummy or Button are not in parent.children
        if parent.children is None or index>=len(parent.children):
            self.add(child, parent)
            return

        if isinstance( parent.children[index], SlotNode ):
            if not isinstance(child, SlotNode):
                self.remove( parent.children[index] )

        Tree.insert(self, child, parent, index)
        image = child.get_image()
        child.item = compat.wx_Tree_InsertItemBefore(self, parent.item, index, self._build_label(child), image)
        self.SetPyData(child.item, child)
        if self.auto_expand:
            self.Expand(parent.item)
            self.select_item(child)
        if not isinstance(child.widget, edit_sizers.SizerSlot):
            #child.widget.show_properties()
            self.app.check_codegen(child.widget)

    def remove(self, node=None, delete=True):
        self.app.saved = False  # update the status of the app
        Tree.remove(self, node)
        if node is not None:
            if delete:
                if self.cur_widget:
                    misc.set_focused_widget(node.parent and node.parent.widget or None)
                self.Delete(node.item)
        else:
            wx.TreeCtrl.Destroy(self)

    def clear(self):
        self.skip_select = True
        if self.root.children:
            while self.root.children:
                c = self.root.children[-1]
                if c.widget: c.widget.remove()
            self.root.children = None
        self.skip_select = False
        self.app.reset()

    def refresh_name(self, node, previous_name=None):
        names = self.names.setdefault(self._find_toplevel(node), {})
        if previous_name is not None and previous_name in names:
            del names[previous_name]
        names[node.widget.name] = 1
        self.SetItemText(node.item, self._build_label(node))

    def refresh(self, node, refresh_label=True, refresh_image=True):
        # refresh label and/or image
        if refresh_label:
            self.SetItemText(node.item, self._build_label(node))
        if refresh_image:
            image = node.get_image()
            self.SetItemImage(node.item, image)

    def select_item(self, node):
        self.skip_select = True
        self.SelectItem(node.item)
        self.skip_select = False
        self.cur_widget = node.widget
        misc.set_focused_widget(self.cur_widget)

    def set_current_widget(self, widget):
        # interface from common.set_focused_widget
        if widget is None:
            #self.cur_widget = None
            return
        if widget is self.cur_widget: return
        if widget is self.root.widget:
            node = self.root
        else:
            node = widget.node
        self.skip_select = True
        self.SelectItem(node.item)
        self.skip_select = False
        self.cur_widget = widget

    def on_change_selection(self, event):
        if self.skip_select: return  # triggered by self.SelectItem in self.set_current_widget
        item = event.GetItem()
        widget = self.GetPyData(item).widget
        self.cur_widget = widget
        misc.set_focused_widget(widget)
        if not self.IsExpanded(item):
            self.Expand(item)
        self.SetFocus()

    def on_left_click(self, event):
        if not common.adding_widget:
            event.Skip()
            return
        node = self._find_node_by_pos(*event.GetPosition())
        if not node:
            event.Skip()
            return
        item = node.widget
        import edit_sizers
        if isinstance(item, edit_sizers.SizerSlot):
            item.on_drop_widget(event)
            return
        if common.adding_sizer:
            item.drop_sizer()
            return
        event.Skip()

    def on_leave_window(self, event):
        self.SetCursor(wx.STANDARD_CURSOR)
        event.Skip()

    def on_mouse_events(self, event):
        if not self._drag_ongoing and not event.IsButton():
            # set cursor to indicate a possible drop
            x,y = event.GetPosition()
            item = self._find_node_by_pos(x, y, toplevels_only=False)
            if item is not None:
                if not common.adding_widget:
                    self.SetCursor(wx.STANDARD_CURSOR)
                else:
                    # check whether the item can be dropped here
                    if item.widget.check_drop_compatibility():
                        self.SetCursor(wx.CROSS_CURSOR)
                    else:
                        self.SetCursor(wx.StockCursor(wx.CURSOR_NO_ENTRY)) # https://wxpython.org/docs/api/wx.Cursor-class.html
            else:
                self.SetCursor(wx.STANDARD_CURSOR)
        event.Skip()

    def popup_menu(self, event, pos=None):
        node = self._find_node_by_pos(*event.GetPosition())
        if not node:
            return
        self.select_item(node)
        item = node.widget
        item.popup_menu(event, pos)

    def expand(self, node=None, yes=True):
        "expands or collapses the given node"
        if node is None: node = self.root
        if yes: self.Expand(node.item)
        else: self.Collapse(node.item)

    def set_title(self, value):
        if value is None: value = ""
        self.title = value
        try:
            self.GetParent().SetTitle(_('wxGlade: Tree %s') % value)
        except:
            pass

    def get_title(self):
        if not self.title: self.title = ' '
        return self.title

    def create_widgets(self, node):
        "Shows the widget of the given node and all its children"
        node.widget.create()
        self.expand(node, True)
        if node.children:
            for c in node.children:
                self.create_widgets(c)
        node.widget.post_load()

    def _show_widget_toplevel(self, node):
        # creates/shows the widget of the given toplevel node and all its children
        if not wx.IsBusy(): wx.BeginBusyCursor()
        if not node.widget.widget:
            node.widget.create_widget()
            node.widget.finish_widget_creation()
            node.widget.drop_target = clipboard.DropTarget(node.widget)
            node.widget.widget.SetDropTarget(node.widget.drop_target)
    
        if node.children:
            for c in node.children:
                self.create_widgets(c)
        node.widget.post_load()
        node.widget.create()
        node.widget.widget.Show()
        misc.set_focused_widget(node.widget)

        node.widget.widget.Raise()
        # set the best size for the widget (if no one is given)
        props = node.widget.properties
        if 'size' in props and not props['size'].is_active() and node.widget.sizer:
            node.widget.sizer.fit_parent()
        if wx.IsBusy(): wx.EndBusyCursor()

    def show_toplevel(self, event, widget=None):
        "Event handler for left double-clicks: if the click is above a toplevel widget and this is hidden, shows it"
        if widget is None:
            try: x, y = event.GetPosition()
            except AttributeError:
                # if we are here, event is a CommandEvent and not a MouseEvent
                node = self.GetPyData(self.GetSelection())
                self.expand(node)  # if we are here, the widget must be shown
            else:
                node = self._find_node_by_pos(x, y, True)
        else:
            node = widget.node

        if node is None or node is self.root: return

        if node.widget.widget:
            # window widget has been created already; just show it
            if not node.widget.is_visible():
                node.widget.widget.Show()
            else:
                node.widget.widget.Hide()
            return

        if not node.widget.is_visible():
            # added by rlawson to expand node on showing top level widget
            self.expand(node)
            self._show_widget_toplevel(node)
        else:
            node.widget.create()
            node.widget.widget.Show()
            # added by rlawson to collapse only the toplevel node, not collapse back to root node
            self.select_item(node)
            misc.set_focused_widget(node.widget)
            event.Skip()
        #event.Skip()

    def _find_node_by_pos(self, x, y, toplevels_only=False):
        """Finds the node which is displayed at the given coordinates. Returns None if there's no match.
        If toplevels_only is True, scans only root's children"""
        item, flags = self.HitTest((x, y))
        if item and flags & (wx.TREE_HITTEST_ONITEMLABEL | wx.TREE_HITTEST_ONITEMICON):
            node = self.GetPyData(item)
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
        return node.widget

    def change_node(self, node, widget, new_node=None):
        if new_node is not None:
            # this is a bit of a hack to replace the old widget node with a SlotNode
            # XXX probably it would be better to modify the Node class to take care of SizerSlot instances
            parent = new_node.parent = node.parent
            index = parent.children.index(node)
            parent.children[index] = new_node
            new_node.item = node.item
            self.SetPyData(node.item, new_node)
            old_children = node.children
            self.remove(node, delete=False)  # don't delete the node, as we just want to modify it
            for c in old_children or []:           # but the children
                self.Delete(c.item)
            node = new_node
            self.names.setdefault(Tree._find_toplevel(self, node), {})[str(node.widget.name)] = 1
        Tree.change_node(self, node, widget)
        self.SetItemImage(node.item, node.get_image() )
        self.SetItemText(node.item, self._build_label(node))

    def _append_rec(self, parent, node):
        # helper for the next method
        idx = WidgetTree.images.get(node.widget.__class__.__name__, -1)
        node.item = self.AppendItem( parent.item, self._build_label(node), idx )
        self.SetPyData(node.item, node)
        if node.children:
            for c in node.children:
                self._append_rec(node, c)
        self.Expand(node.item)

    def change_node_pos(self, node, new_pos):
        if new_pos >= self.GetChildrenCount(node.parent.item, False):
            return
        index = node.parent.children.index(node)
        Tree.change_node_pos(self, node, new_pos, index)
        old_item = node.item
        image = self.GetItemImage(node.item)
        self.Freeze()
        if index >= new_pos:
            node.item = compat.wx_Tree_InsertItemBefore( self, node.parent.item, new_pos, self._build_label(node), image )
        else:
            node.item = compat.wx_Tree_InsertItemBefore( self, node.parent.item, new_pos+1, self._build_label(node), image )
        self.SetPyData(node.item, node)

        if node.children:
            for c in node.children:
                self._append_rec(node, c)
        self.Expand(node.item)
        self.Delete(old_item)
        self.Thaw()

    def get_selected_path(self, w=None):
        """returns a list of widget names, from the toplevel to the selected one
        Example: ['frame_1', 'sizer_1', 'panel_1', 'sizer_2', 'button_1']
                 if button_1 is the currently selected widget"""
        ret = []
        if w is None: w = self.cur_widget
        oldw = None
        while w is not None:
            oldw = w
            if isinstance(w, edit_sizers.SizerSlot):
                ret.append("SLOT %d"%w.pos)
            else:
                ret.append(w.name)
            sizer = getattr(w, 'sizer', None)
            if getattr(w, 'parent', "") is None:
                w = w.parent
            elif sizer is not None and not sizer.is_virtual():
                w = sizer
            else:
                if isinstance(w, edit_sizers.SizerBase):
                    w = w.window
                elif isinstance(w, application.Application):
                    w = None
                else:
                    w = w.parent
        ret.reverse()
        # ALB 2007-08-28: remember also the position of the toplevel window in the selected path
        if oldw is not None and oldw.widget is not None:
            assert oldw.widget
            pos = misc.get_toplevel_parent(oldw.widget).GetPosition()
            ret[0] = (ret[0], pos)
        return ret

    def select_path(self, path):
        "sets the selected widget from a path_list, which should be in the form returned by get_selected_path"
        index = 0
        item, cookie = self._get_first_child(self.GetRootItem())
        itemok = None
        parent = None
        pos = None
        while item.Ok() and index < len(path):
            widget = self.GetPyData(item).widget
            name = path[index]
            if index == 0 and isinstance(name, tuple):
                name, pos = name
            if misc.streq(widget.name, name):
                #self.EnsureVisible(item)
                itemok = item
                if parent is None:
                    parent = self.GetPyData(itemok)
                self.cur_widget = widget
                item, cookie = self._get_first_child(item)
                index += 1
            else:
                item = self.GetNextSibling(item)
        if itemok is not None:
            node = self.GetPyData(itemok)
            if parent is not None:
                self._show_widget_toplevel(parent)
                if pos is not None:
                    misc.get_toplevel_parent(parent.widget).SetPosition(pos)
            self.select_item(node)

    def _get_first_child(self, item):
        return self.GetFirstChild(item)
