# misc.py: Miscellaneus stuff, used in many parts of wxGlade
# $Id: misc.py,v 1.28 2003/06/24 15:07:27 agriggio Exp $
# 
# Copyright (c) 2002-2003 Alberto Griggio <albgrig@tiscalinet.it>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

from wxPython.wx import *

if wxPlatform == '__WXMSW__':
    class wxGladeRadioButton(wxRadioButton):
        """
        custom wxRadioButton class which tries to implement a better
        GetBestSize than the default one for WXMSW (mostly copied from
        wxCheckBox::DoGetBestSize in checkbox.cpp)
        """
        __radio_size = None
        def GetBestSize(self):
            if not self.__radio_size:
                dc = wxScreenDC()
                dc.SetFont(wxSystemSettings_GetSystemFont(
                    wxSYS_DEFAULT_GUI_FONT))
                self.__radio_size = (3*dc.GetCharHeight())/2
            label = self.GetLabel()
            if label:
                w, h = self.GetTextExtent(label)
                w += self.__radio_size + self.GetCharWidth()
                if h < self.__radio_size: h = self.__radio_size
            else: w = h = self.__radio_size;
            return w, h

    # end of class wxGladeRadioButton
else: wxGladeRadioButton = wxRadioButton

#---------------------  Selection Markers  ----------------------------------

class SelectionTag(wxPanel):
    """\
    This is one of the small black squares that appear at the corners of the
    active widgets
    """
    def __init__(self, parent, pos=None):
        kwds = { 'size': (7, 7) }
        if pos: kwds['position'] = pos
        wxPanel.__init__(self, parent, -1, **kwds)
        self.SetBackgroundColour(wxBLACK)
        self.Hide()

# end of class SelectionTag

class SelectionMarker:
    """\
    Collection of the 4 SelectionTagS for each widget
    """
    def __init__(self, owner, parent, visible=False):
        self.visible = visible
        self.owner = owner
        self.parent = parent
        if wxPlatform == '__WXMSW__': self.parent = owner
        self.tags = [ SelectionTag(self.parent) for i in range(4) ]
        self.update()
        if visible:
            for t in self.tags: t.Show()

    def update(self, event=None):
        if self.owner is self.parent: x, y = 0, 0
        else: x, y = self.owner.GetPosition()
        w, h = self.owner.GetClientSize()
        def position(j):
            if not j: return x, y            # top-left
            elif j == 1: return x+w-7, y     # top-right
            elif j == 2: return x+w-7, y+h-7 # bottom-right
            else: return x, y+h-7            # bottom-left
        for i in range(len(self.tags)):
            self.tags[i].SetPosition(position(i))
        if event: event.Skip()

    def Show(self, visible):
        self.visible = visible
        for tag in self.tags: tag.Show(visible)

    def Destroy(self):
        for tag in self.tags: tag.Destroy()
        self.tags = None

    def Reparent(self, parent):
        self.parent = parent
        for tag in self.tags: tag.Reparent(parent)

# end of class SelectionMarker

#----------------------------------------------------------------------------

import common
_encode = common._encode_from_xml

def bound(number, lower, upper):
    return min(max(lower, number), upper)

def color_to_string(color):
    """\
    returns the hexadecimal string representation of the given color:
    for example: wxWHITE ==> #ffffff
    """
    import operator
    return '#' + reduce(operator.add, ['%02x' % bound(c, 0, 255) for c in
                                       color.Get()])

def string_to_color(color):
    """\
    returns the wxColour which corresponds to the given
    hexadecimal string representation:
    for example: #ffffff ==> wxColour(255, 255, 255)
    """
    if len(color) != 7: raise ValueError
    return apply(wxColour, [int(color[i:i+2], 16) for i in range(1, 7, 2)])

    
def get_toplevel_parent(obj):
    if not isinstance(obj, wxWindow): window = obj.widget
    else: window = obj
    while window and not window.IsTopLevel():
        window = window.GetParent()
    return window

if wxPlatform == '__WXGTK__':
    # default wxMenu seems to have probles with SetTitle on GTK
    class wxGladePopupMenu(wxMenu):
        def __init__(self, title):
            wxMenu.__init__(self)
            self.TITLE_ID = wxNewId()
            self.Append(self.TITLE_ID, title)
            self.AppendSeparator()

        def SetTitle(self, title):
            self.SetLabel(self.TITLE_ID, title)

else: wxGladePopupMenu = wxMenu

def check_wx_version(major, minor=0, release=0):
    """\
    returns True if the current wxPython version is at least
    major.minor.release
    """
    return wx.__version__ >= "%d.%d.%d" % (major, minor, release)
##     wx_major, wx_minor, wx_release = [int(t) for t in
##                                       wx.__version__.split('.')][:3]
##     return wx_major > major or \
##            (wx_major == major and wx_minor > minor) or \
##            (wx_major == major and wx_minor == minor and wx_release>=release)

if not check_wx_version(2, 3, 3):
    # the following is copied from wx.py of version 2.3.3, as 2.3.2 doesn't
    # have it
    _wxCallAfterId = None

    def wxCallAfter(callable, *args, **kw):
        """
        Call the specified function after the current and pending event
        handlers have been completed.  This is also good for making GUI
        method calls from non-GUI threads.
        """
        app = wxGetApp()
        assert app, 'No wxApp created yet'

        global _wxCallAfterId
        if _wxCallAfterId is None:
            _wxCallAfterId = wxNewId()
            app.Connect(-1, -1, _wxCallAfterId,
                  lambda event: apply(event.callable, event.args, event.kw) )
        evt = wxPyEvent()
        evt.SetEventType(_wxCallAfterId)
        evt.callable = callable
        evt.args = args
        evt.kw = kw
        wxPostEvent(app, evt)

#----------------------------------------------------------------------

use_menu_icons = None

_item_bitmaps = {}
def append_item(menu, id, text, xpm_file=None):
    global use_menu_icons
    if use_menu_icons is None:
        import config
        use_menu_icons = config.preferences.use_menu_icons
    import common, os.path
    item = wxMenuItem(menu, id, text)
    if wxPlatform == '__WXMSW__': path = 'icons/msw/'
    else: path = 'icons/gtk/'
    path = os.path.join(common.wxglade_path, path)
    if use_menu_icons and xpm_file is not None:
        try: bmp = _item_bitmaps[xpm_file]
        except KeyError:
            f = os.path.join(path, xpm_file)
            if os.path.isfile(f):
                bmp = _item_bitmaps[xpm_file] = wxBitmap(f, wxBITMAP_TYPE_XPM)
            else: bmp = None
        if bmp is not None:
            try: item.SetBitmap(bmp)
            except AttributeError: pass
    menu.AppendItem(item)


#----------- 2002-11-01 ------------------------------------------------------
# if not None, this is the currently selected widget - This is different from
# tree.WidgetTree.cur_widget because it takes into account also SizerSlot
# objects
# this is an implementation hack, used to handle keyboard shortcuts for
# popup menus properly (for example, to ensure that the object to remove is
# the currently highlighted one, ecc...)
focused_widget = None


def _remove():
    global focused_widget
    if focused_widget is not None:
        focused_widget.remove()
        focused_widget = None
        
def _cut():
    global focused_widget
    if focused_widget is not None:
        try: focused_widget.clipboard_cut()
        except AttributeError: pass
        else: focused_widget = None
        
def _copy():
    if focused_widget is not None:
        try: focused_widget.clipboard_copy()
        except AttributeError: pass

def _paste():
    if focused_widget is not None:
        try: focused_widget.clipboard_paste()
        except AttributeError: pass

# accelerator table to enable keyboard shortcuts for the popup menus of the
# various widgets (remove, cut, copy, paste)
accel_table = [(0, WXK_DELETE, _remove),
               (wxACCEL_CTRL, ord('C'), _copy),
               (wxACCEL_CTRL, ord('X'), _cut),
               (wxACCEL_CTRL, ord('V'), _paste)]
#-----------------------------------------------------------------------------

def _reverse_dict(src):
    """\
    Returns a dictionary whose keys are 'src' values and values 'src' keys.
    """
    ret = {}
    for key, val in src.iteritems():
        ret[val] = key
    return ret


#-----------------------------------------------------------------------------
def sizer_fixed_Insert(self, *args, **kw):
    """\
    This function fixes a bug in wxPython 2.4.0.2, which fails to call
    InsertSizer when the 2nd argument is a Sizer
    """
    if type(args[1]) == type(1):
        apply(self.InsertSpacer, args, kw)
    elif isinstance(args[1], wxSizerPtr):
        apply(self.InsertSizer, args, kw)
    else:
        apply(self.InsertWindow, args, kw)

#-----
# if not None, this is the SizerSlot wich has the "mouse focus": this is used
# to restore the mouse cursor if the user cancelled the addition of a widget
_currently_under_mouse = None


#-----------------------------------------------------------------------------
def get_geometry(win):
    x, y = win.GetPositionTuple()
    w, h = win.GetSizeTuple()
    return (x, y, w, h)

def set_geometry(win, geometry):
    if geometry is None: return
    try:
        if len(geometry) == 4:
            win.SetDimensions(*[int(x) for x in geometry])
        else:
            win.SetPosition([int(x) for x in geometry])
    except Exception, e:
        print e


#-----------------------------------------------------------------------------
# snagged out of the Python cookbook
def import_name(module_path, name):
    import imp, os
    path, mname = os.path.split(module_path)
    #print 'path, mname =', path, mname
    mname = os.path.splitext(mname)[0]
    #print 'mname:', mname
    try:
        mfile, pathname, description = imp.find_module(mname, [path])
        try:
            module = imp.load_module(mname, mfile, pathname, description)
        finally:
            mfile.close()
    except ImportError:
        import traceback; traceback.print_exc()
        return None
    return vars(module)[name]


#------------------------------------------------------------------------------
# helper functions to work with a Unicode-enabled wxPython
#------------------------------------------------------------------------------

def streq(s1, s2):
    """\
    Returns True if the strings or unicode objects s1 and s2 are equal, i.e.
    contain the same text. Appropriate encoding/decoding are performed to
    make the comparison
    """
    try:
        return s1 == s2
    except UnicodeError:
        if type(s1) == type(u''):
            s1 = s1.encode(common.app_tree.app.encoding)
        else:
            s2 = s2.encode(common.app_tree.app.encoding)
        return s1 == s2


def wxstr(s):
    """\
    Converts the string object s to str or unicode, according to what wxPython
    expects
    """
    if common.app_tree is None:
        return str(s)
    if wxUSE_UNICODE:
        if type(s) != type(u''):
            return unicode(str(s), common.app_tree.app.encoding)
        else:
            return s
    else:
        if type(s) == type(u''):
            return s.encode(common.app_tree.app.encoding)
        else:
            return str(s)


#------------------------------------------------------------------------------
# wxPanel used to reparent the property-notebooks when they are hidden. This
# has been added on 2003-06-22 to fix what seems to me a (wx)GTK2 bug
#------------------------------------------------------------------------------
hidden_property_panel = None
