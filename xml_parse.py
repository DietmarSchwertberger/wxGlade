# xml_parse.py: parsers used to load an app and to generate the code
# from an xml file.
#
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: GPL (see license.txt)
#
# NOTE: custom tag handler interface (called by XmlWidgetBuilder)
# class CustomTagHandler:
#     def start_elem(self, name, attrs): pass
#     def end_elem(self, name):
#         return True -> the handler must be removed from the Stack
#     def char_data(self, data):
#         return False -> no further processing needed

import common, widget_properties, tree, edit_sizers, misc
from xml.sax import SAXException, make_parser
from xml.sax.handler import ContentHandler
from wxPython.wx import *
import traceback

class XmlParsingError(SAXException):
    """\
    Custom exception to report problems during parsing
    """
    locator = None
    def __init__(self, msg):
        if self.locator:
            l = self.locator
            msg += ' (line: %s, column:  %s)' % (l.getLineNumber(),
                                                 l.getColumnNumber())
        SAXException.__init__(self, msg)

# end of class XmlParsingError


class XmlParser(ContentHandler):
    """\
    'abstract' base class of the parsers used to load an app and to generate
    the code
    """
    def __init__(self):
        self._objects = Stack() # stack of 'alive' objects
        self._windows = Stack() # stack of window objects (derived by wxWindow)
        self._sizers = Stack()  # stack of sizer objects
        self._sizer_item = Stack() # stack of sizer items
        self._curr_prop = None # name of the current property
        self._curr_prop_val = [] # value of the current property (list into
                                 # which the various pieces of char data
                                 # collected are inserted)
        self._appl_started = False
        self.top = self._objects.top
        self.parser = make_parser()
        self.parser.setContentHandler(self)
        self.locator = None # document locator
        
    def parse(self, source):
        self.parser.parse(source)

    def parse_string(self, source):
        from cStringIO import StringIO
        source = StringIO(source)
        self.parser.parse(source)
        source.close()

    def setDocumentLocator(self, locator):
        self.locator = locator
        XmlParsingError.locator = locator
    
    def startElement(self, name, attrs):
        raise NotImplementedError
    
    def endElement(self, name, attrs):
        raise NotImplementedError

    def characters(self, data):
        raise NotImplementedError

    def pop(self):
        try: return self._objects.pop().pop()
        except AttributeError: return None

# end of class XmlParser


class XmlWidgetBuilder(XmlParser):
    """\
    parser used to build the tree of widgets from an xml file
    """
    def startElement(self, name, attrs):
        if name == 'application':
            # get properties of the app
            self._appl_started = True
            app = common.app_tree.app
            path = attrs.get("path")
            if path:
                app.output_path = path
                app.outpath_prop.set_value(path)
            name = attrs.get("name")
            if name:
                app.name = name
                app.name_prop.toggle_active(True)
                app.name_prop.set_value(name)
            klass = attrs.get("class")
            if klass:
                app.klass = klass
                app.klass_prop.toggle_active(True)
                app.klass_prop.set_value(klass)
            option = attrs.get("option")
            if option:
                try: option = int(option)
                except ValueError: option = 0
                app.codegen_opt = option
                app.codegen_prop.set_value(option)
            top_win = attrs.get("top_window")
            if top_win: self.top_window = top_win
            return
        if not self._appl_started:
            raise XmlParsingError("the root of the tree must be <application>")
        if name == 'object':
            # create the object and push it on the appropriate stacks
            XmlWidgetObject(attrs, self)
        else:
            # handling of the various properties
            try:
                # look for a custom handler to push on the stack
                handler = self.top().obj.get_property_handler(name)
                if handler: self.top().prop_handlers.push(handler)
                # get the top custom handler and use it if there's one
                handler = self.top().prop_handlers.top()
                if handler: handler.start_elem(name, attrs)
            except AttributeError: pass
            self._curr_prop = name

    def endElement(self, name):
        if name == 'application':
            self._appl_started = False
            if hasattr(self, 'top_window'):
                common.app_tree.app.top_window = self.top_window
                common.app_tree.app.top_win_prop.SetStringSelection(
                    self.top_window)
            return
        if name == 'object':
            # remove last object from the stack
            obj = self.pop()
            if obj.klass == 'sizeritem': return
            si = self._sizer_item.top()
            if si is not None and si.parent == obj.parent:
                sprop = obj.obj.sizer_properties
                # update the values
                sprop['option'].set_value(si.obj.option)
                sprop['flag'].set_value(si.obj.flag_str())
                sprop['border'].set_value(si.obj.border)
                # call the setter functions
                obj.obj['option'][1](si.obj.option)
                obj.obj['flag'][1](si.obj.flag_str())
                obj.obj['border'][1](si.obj.border)
##                 if not int(si.obj.option):
##                     sz = obj.obj.properties.get('size')
##                     if sz is not None and not sz.is_active():
##                         # update the item size, if it was not specified
##                         obj.obj.sizer.set_item(obj.obj.pos,
##                                                size=obj.obj.GetBestSize())
        else:
            # end of a property or error
            # 1: set _curr_prop value
            data = misc._encode("".join(self._curr_prop_val))
            if data:
                handler = self.top().prop_handlers.top()
                if not handler or handler.char_data(data):
                    # if char_data returned False,
                    # we don't have to call add_property
                    self.top().add_property(self._curr_prop, data)
            # 2: call custom end_elem handler
            try:
                # if there is a custom handler installed for this property,
                # call its end_elem function: if this returns True, remove
                # the handler from the Stack
                handler = self.top().prop_handlers.top()
                if handler.end_elem(name):
                    self.top().prop_handlers.pop()
            except AttributeError: pass
            self._curr_prop = None
            self._curr_prop_val = []

    def characters(self, data):
        if not data or data.isspace():
            return
        if self._curr_prop is None:
            raise XmlParsingError("character data can be present only " \
                                  "inside properties")
        self._curr_prop_val.append(data)

# end of class XmlWidgetBuilder


class ProgressXmlWidgetBuilder(XmlWidgetBuilder):
    """\
    Adds support for a progress dialog to the widget builder parser 
    """
    def __init__(self, *args, **kwds):
        self.input_file = kwds.get('input_file')
        if self.input_file:
            del kwds['input_file']
            self.size = len(self.input_file.readlines())
            self.input_file.seek(0)
            self.progress = wxProgressDialog("Loading...", "Please wait "
                                             "while loading the app", 20)
            self.step = 4
            self.i = 1
        else:
            self.size = 0
            self.progress = None
        XmlWidgetBuilder.__init__(self, *args, **kwds)

    def endElement(self, name):
        if self.progress:
            if name == 'application': self.progress.Destroy()
            else:
                if self.locator:
                    where = self.locator.getLineNumber()
                    value = int(round(where*20.0/self.size))
                else:
                    # we don't have any information, so we update the progress
                    # bar ``randomly''
                    value = (self.step*self.i) % 20
                    self.i += 1
                self.progress.Update(value)
        XmlWidgetBuilder.endElement(self, name)

    def parse(self, *args):
        try: XmlWidgetBuilder.parse(self, *args)
        finally:
            if self.progress: self.progress.Destroy()

    def parse_string(self, *args):
        try: XmlWidgetBuilder.parse_string(self, *args)
        finally:
            if self.progress: self.progress.Destroy()

# end of class ProgressXmlWidgetBuilder


class ClipboardXmlWidgetBuilder(XmlWidgetBuilder):
    """\
    Parser used to cut&paste widgets. The differences with XmlWidgetBuilder
    are:
      - No <application> tag in the piece of xml to parse
      - Fake parent, sizer and sizeritem objects to push on the three stacks:
        they keep info about the destination of the hierarchy of widgets (i.e.
        the target of the 'paste' command)
      - The first widget built must be hidden and shown again at the end of
        the operation
    """
    def __init__(self, parent, sizer, pos, option, flag, border):
        XmlWidgetBuilder.__init__(self)
        class XmlClipboardObject:
            def __init__(self, **kwds):
                self.__dict__.update(kwds)
        szr = XmlClipboardObject(obj=sizer, parent=parent) # fake sizer object
        par = XmlClipboardObject(obj=parent, parent=parent) # fake window obj
        sizeritem = Sizeritem()
        sizeritem.option = option
        sizeritem.flag = flag
        sizeritem.border = border
        sizeritem.pos = pos
        si = XmlClipboardObject(obj=sizeritem, parent=parent) # fake sizer item
        # push the fake objects on the stacks
        self._objects.push(par); self._windows.push(par)
        self._objects.push(szr); self._sizers.push(szr)
        self._objects.push(si); self._sizer_item.push(si)
        self.depth_level = 0
        self._appl_started = True # no application tag when parsing from the
                                  # clipboard

    def startElement(self, name, attrs):
        XmlWidgetBuilder.startElement(self, name, attrs)
        if name == 'object':
            if not self.depth_level:
                try:
                    self.top_obj = self.top().obj
                except AttributeError:
                    print 'Exception! obj: %s' % self.top_obj
                    traceback.print_exc()
            self.depth_level += 1

    def endElement(self, name):
        if name == 'object':
            # generate a unique name for the copy
            obj = self.top()
            if obj.klass != 'sizeritem':
                widget = obj.obj
                newname = widget.name + '_copy'
                i = 1
                while common.app_tree.has_name(newname):
                    newname = '%s_copy_%s' % (widget.name, i)
                    i += 1
                widget.name = newname
                widget.name_prop.set_value(newname)
                common.app_tree.set_name(widget.node, newname)
            
            self.depth_level -= 1
            if not self.depth_level:
                try:
                    # show the first object and update its layout
                    common.app_tree.show_widget(self.top_obj.node)
                    self.top_obj.show_properties()
                    common.app_tree.select_item(self.top_obj.node)
                except AttributeError:
                    print 'Exception! obj: %s' % self.top_obj
                    traceback.print_exc()
        XmlWidgetBuilder.endElement(self, name)

# end of class ClipboardXmlWidgetBuilder


class XmlWidgetObject:
    """\
    A class to encapsulate a widget read from an xml file: its purpose is to
    store various widget attributes until the widget can be created 
    """
    def __init__(self, attrs, parser):
        # prop_handlers is a stack of custom handler functions to set
        # properties of this object
        self.prop_handlers = Stack()
        self.parser = parser
        self.in_windows, self.in_sizers = False, False
        try:
            base = attrs.get('base', None)
            self.klass = attrs['class']
        except KeyError:
            raise XmlParsingError("'object' items must have a 'class' " \
                                  "attribute")
                  
        if base is not None:
            # if base is not None, the object is a widget (or sizer), and not a
            # sizeritem
            sizer = self.parser._sizers.top()
            parent = self.parser._windows.top()
            if parent is not None: parent = self.parent = parent.obj
            else: self.parent = None
            sizeritem = self.parser._sizer_item.top()
            if sizeritem is not None: sizeritem = sizeritem.obj
            if sizer is not None:
                # we must check if the sizer on the top of the stack is
                # really the one we are looking for: to check this
                if sizer.parent != parent:
                    sizer = None
                else: sizer = sizer.obj
            if hasattr(sizeritem, 'pos'):
                pos = sizeritem.pos
            else: pos = None
            
            # build the widget
            self.obj = common.widgets_from_xml[base](attrs, parent, sizer,
                                                     sizeritem, pos)
            try:
                self.obj.klass = self.klass
                self.obj.klass_prop.set_value(self.klass)
            except AttributeError: pass
            
            # push the object on the appropriate stack
            import edit_sizers
            if isinstance(self.obj, edit_sizers.SizerBase):
                self.parser._sizers.push(self)
                self.in_sizers = True
            else:
                self.parser._windows.push(self)
                self.in_windows = True

        elif self.klass == 'sizeritem':
            self.obj = Sizeritem()
            self.parent = self.parser._windows.top().obj
            self.parser._sizer_item.push(self)
            
        # push the object on the _objects stack
        self.parser._objects.push(self)

    def pop(self):
        if self.in_windows: return self.parser._windows.pop()
        elif self.in_sizers: return self.parser._sizers.pop()
        else: return self.parser._sizer_item.pop()

    def add_property(self, name, val):
        """\
        adds a property to this widget. This method is not called if there
        was a custom handler for this property, and its char_data method
        returned False
        """
        try:
            self.obj[name][1](val) # call the setter for this property
            try:
                prop = self.obj.properties[name]
                prop.set_value(val)
                prop.toggle_active(True)
            except AttributeError: pass
        except KeyError:
            # unknown property for this object
            raise XmlParsingError("property '%s' not supported by this object"\
                                  " ('%s') " % (name, self.obj))

#end of class XmlWidgetObject


class CodeWriter(XmlParser):
    """parser used to produce the source from a given xml file"""
    def __init__(self, writer, input, from_string=False):
        # writer: object that actually writes the code
        XmlParser.__init__(self)
        self._toplevels = Stack() # toplevel objects, i.e. instances of a
                                  # custom class
        self.app_attrs = {} # attributes of the app (name, class, top_window)
        self.top_win = ''   # class name of the top window of the app (if any)
        
        self.tabs = 0 # current indentation level
        self.code_writer = writer

        if from_string: self.parse_string(input)
        else:
            input = open(input)
            self.parse(input)
            input.close()

    def startElement(self, name, attrs_impl):
        attrs = {}
        # turn all the attribute values from unicode to str objects
        for attr, val in attrs_impl.items():
            attrs[attr] = misc._encode(val)
        if name == 'application':
            # get the code generation options
            self._appl_started = True
            if attrs.get('name') or attrs.get('class'):
                self.app_attrs = attrs
            try: use_multiple_files = int(attrs['option']) and True
            except (KeyError, ValueError): use_multiple_files = False
            try: out_path = attrs['path']
            except KeyError:
                raise XmlParsingError("'path' attribute missing: could "
                                      "not generate code")
            # initialize the writer
            self.code_writer.initialize(out_path, use_multiple_files)
            return
        if not self._appl_started:
            raise XmlParsingError("the root of the tree must be <application>")
        if name == 'object':
            # create the CodeObject which stores info about the current widget
            CodeObject(attrs, self)
            if attrs.has_key('name') and \
                   attrs['name'] == self.app_attrs.get('top_window', ''):
                self.top_win = attrs['class']
        else:
            # handling of the various properties
            try:
                # look for a custom handler to push on the stack
                w = self.top()
                handler = self.code_writer.get_property_handler(name, w.base)
                if handler: w.prop_handlers.push(handler)
                # get the top custom handler and use it if there's one
                handler = w.prop_handlers.top()
                if handler: handler.start_elem(name, attrs)
            except AttributeError:
                print 'ATTRIBUTE ERROR!!'
                traceback.print_exc()
            self._curr_prop = name

    def endElement(self, name):
        if name == 'application':
            self._appl_started = False
            if self.app_attrs:
                self.code_writer.add_app(self.app_attrs, self.top_win)
            # call the finalization function of the code writer
            self.code_writer.finalize()
            return
        if name == 'object':
            obj = self.pop()
            if obj.klass == 'sizeritem': return
            # at the end of the object, we have all the information to add it
            # to its toplevel parent, or to generate the code for the custom
            # class
            if obj.is_toplevel and not obj.in_sizers:
                self.code_writer.add_class(obj)
            topl = self._toplevels.top()
            if topl:
                self.code_writer.add_object(topl, obj)
                # if the object is not a sizeritem, check wether it
                # belongs to some sizer (in this case,
                # self._sizer_item.top() doesn't return None): if so,
                # write the code to add it to the sizer at the top of
                # the stack
                si = self._sizer_item.top()
                if si is not None and si.parent == obj.parent:
                    szr = self._sizers.top()
                    if not szr: return
                    self.code_writer.add_sizeritem(topl, szr.name, obj.name,
                                                   si.obj.option,
                                                   si.obj.flag_str(),
                                                   si.obj.border)
        else:
            # end of a property or error
            # 1: set _curr_prop value
            data = misc._encode(u"".join(self._curr_prop_val))
            if data:
                handler = self.top().prop_handlers.top()
                if not handler or handler.char_data(data):
                    # if char_data returned False,
                    # we don't have to call add_property
                    self.top().add_property(self._curr_prop, data)
            # 2: call custom end_elem handler
            try:
                # if there is a custom handler installed for this property,
                # call its end_elem function: if this returns True, remove
                # the handler from the stack
                obj = self.top()
                handler = obj.prop_handlers.top()
                if handler.end_elem(name, obj):
                    obj.prop_handlers.pop()
            except AttributeError: pass
            self._curr_prop = None
            self._curr_prop_val = []

    def characters(self, data):
        if not data or data.isspace(): return
        if self._curr_prop is None:
            raise XmlParsingError("character data can only appear inside " \
                                  "properties")
        self._curr_prop_val.append(data)

# end of class CodeWriter


class CodeObject:
    """\
    A class to store information needed to generate the code for a given object
    """
    def __init__(self, attrs, parser):
        self.parser = parser
        self.in_windows = self.in_sizers = 0
        self.is_toplevel = 0 # if True, the object is a toplevel one:
                             # for window objects, this means that they are
                             # instances of a custom class, for sizers, that
                             # they are at the top of the hierarchy
        self.properties = {} # properties of the widget/sizer
        # prop_handlers is a stack of custom handler functions to set
        # properties of this object
        self.prop_handlers = Stack()
        try:
            base = attrs.get('base', None)
            self.klass = attrs['class']
        except KeyError:
            raise XmlParsingError("'object' items must have a 'class' " \
                                  "attribute")
        self.parser._objects.push(self)
        self.parent = self.parser._windows.top()
        self.base = None
        if base is not None: # this is a ``real'' object, not a sizeritem
            self.name = attrs['name']
            self.base = common.class_names[base]
            if self.klass != self.base:
                self.is_toplevel = True 
                self.parser._toplevels.push(self)  
            # temporary hack: to detect a sizer, check wether the name
            # of its class contains the string 'Sizer': TODO: find a
            # better way!!
            if base.find('Sizer') != -1:
                self.in_sizers = True
                if not self.parser._sizers.count(): self.is_toplevel = True
                else:
                    # the sizer is a toplevel one if its parent has not a
                    # sizer yet
                    sz = self.parser._sizers.top()
                    if sz.parent != self.parent: self.is_toplevel = True
                self.parser._sizers.push(self)
            else:
                self.parser._windows.push(self) 
                self.in_windows = True
        else: # the object is a sizeritem
            self.obj = Sizeritem()
            self.parser._sizer_item.push(self)

    def __str__(self):
        return "<xml_code_object: %s, %s, %s>" % (self.name, self.base,
                                                  self.klass)

    def add_property(self, name, value):
        if hasattr(self, 'obj'): # self is a sizeritem
            try:
                if name == 'flag':
                    flag = 0
                    for f in value.split('|'):
                        flag |= Sizeritem.flags[f.strip()]
                    setattr(self.obj, name, flag)
                else: setattr(self.obj, name, int(value))
            except: raise XmlParsingError("property '%s' not supported by " \
                                          "'%s' objects" % (name, self.klass))
        self.properties[name] = value

    def pop(self):
        if self.is_toplevel and not self.in_sizers:
            self.parser._toplevels.pop()
        if self.in_windows: return self.parser._windows.pop()
        elif self.in_sizers: return self.parser._sizers.pop()
        else: return self.parser._sizer_item.pop()

# end of class CodeObject


class Stack:
    def __init__(self):
        self._repr = []

    def push(self, elem):
        self._repr.append(elem)

    def pop(self):
        try: return self._repr.pop()
        except IndexError: return None

    def top(self):
        try: return self._repr[-1]
        except IndexError: return None

    def count(self):
        return len(self._repr)

# end of class Stack


class Sizeritem:
    flags = { 'wxEXPAND': wxEXPAND, 'wxALIGN_RIGHT': wxALIGN_RIGHT,
              'wxALIGN_BOTTOM': wxALIGN_BOTTOM,
              'wxALIGN_CENTER_HORIZONTAL': wxALIGN_CENTER_HORIZONTAL,
              'wxALIGN_CENTER_VERTICAL': wxALIGN_CENTER_VERTICAL,
              'wxLEFT': wxLEFT, 'wxRIGHT': wxRIGHT, 'wxTOP': wxTOP,
              'wxBOTTOM': wxBOTTOM }

    def __init__(self):
        self.option = self.border = 0
        self.flag = 0

    def __getitem__(self, name):
        if name != 'flag':
            return (None, lambda v: setattr(self, name, v))
        return (None,
                lambda v: setattr(self, name,
                                  reduce(lambda a,b: a|b,
                                         [Sizeritem.flags[t] for t in
                                          v.split("|")])))

    def flag_list(self):
        # returns the flag attribute as a list of boolean values, to
        # update the appropriate CheckListProperty
        return [ (v & self.flag) for v in self.flags.values() ]
    
    def flag_str(self):
        # returns the flag attribute as a string of tokens separated
        # by a '|' (used during the code generation)
        try:
            tmp = '|'.join([ k for k in self.flags if \
                             self.flags[k] & self.flag ])
        except:
            print 'EXCEPTION: self.flags = %s, self.flag = %s' % \
                  (self.flags, repr(self.flag))
            raise
        if tmp: return tmp
        else: return '0'

# end of class Sizeritem

