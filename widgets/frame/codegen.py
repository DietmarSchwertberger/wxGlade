# codegen.py: code generator functions for wxFrame objects
#
# Copyright (c) 2002-2003 Alberto Griggio <albgrig@tiscalinet.it>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

import common
from MenuTree import *


class PythonStatusbarCodeGenerator:
    def get_code(self, obj):
        pygen = common.code_writers['python']
        labels, widths = obj.properties['statusbar']
        init = [ 'self.%s = self.CreateStatusBar(%s)\n' % \
                 (obj.name, len(labels)) ]
        props = []
        append = props.append
        append('self.%s.SetStatusWidths(%s)\n' % (obj.name, repr(widths)))
        append('# statusbar fields\n')
        append('%s_fields = [%s]\n' % \
               (obj.name, ', '.join([pygen.quote_str(l) for l in labels])))
        append('for i in range(len(%s_fields)):\n' % obj.name)
        append('    self.%s.SetStatusText(%s_fields[i], i)\n' % \
               (obj.name, obj.name))
        return init, props, []

# end of class PythonStatusbarCodeGenerator


class PythonFrameCodeGenerator:
    def get_code(self, obj):
        return [], [], []
    
    def get_properties_code(self, frame):
        prop = frame.properties
        pygen = common.code_writers['python']
        out = []
        title = prop.get('title')
        if title: out.append('self.SetTitle(%s)\n' % pygen.quote_str(title))
        out.extend(pygen.generate_common_properties(frame))
        return out

    def get_layout_code(self, frame):
        return ['self.Layout()\n']

# end of class PythonFrameCodeGenerator


# property handlers for code generation

class StatusFieldsHandler:
    """Handler for statusbar fields"""
    def __init__(self):
        self.labels = []
        self.widths = []
        self.curr_label = []
        
    def start_elem(self, name, attrs):
        if name == 'field':
            self.widths.append(int(attrs.get('width', -1)))
            
    def end_elem(self, name, code_obj):
        if name == 'fields':
            code_obj.properties['statusbar'] = (self.labels, self.widths)
            return True
        self.labels.append("".join(self.curr_label))
        self.curr_label = []
        
    def char_data(self, data):
        self.curr_label.append(data)

# end of class StatusFieldsHandler


def xrc_frame_code_generator(obj):
    xrcgen = common.code_writers['XRC']
    class FrameXrcObject(xrcgen.DefaultXrcObject):
        def write_child_prologue(self, child, out_file, tabs):
            if child.code_obj.in_sizers:
                # XRC doesn't like sizers for Frames, so we add a Panel
                out_file.write('    '*tabs + '<object class="wxPanel">\n')

        def write_child_epilogue(self, child, out_file, tabs):
            if child.code_obj.in_sizers:
                # end of the fake panel
                out_file.write('    '*tabs + '</object>\n')

        def write(self, outfile, tabs):
            if self.properties.has_key('menubar'):
                del self.properties['menubar']
            if self.properties.has_key('statusbar'):
                del self.properties['statusbar']
            if self.properties.has_key('toolbar'):
                del self.properties['toolbar']
            xrcgen.DefaultXrcObject.write(self, outfile, tabs)

    # end of class FrameXrcObject
    
    return FrameXrcObject(obj)
                

class CppStatusBarCodeGenerator:
    def get_code(self, obj):
        """\
        function that generates code for the statusbar of a wxFrame.
        """
        cppgen = common.code_writers['C++']
        labels, widths = obj.properties['statusbar']
        init = [ '%s = CreateStatusBar(%s);\n' % (obj.name, len(labels)) ]
        props = []
        append = props.append
        append('int %s_widths[] = { %s };\n' % (obj.name,
                                                ', '.join(map(str, widths))))
        append('%s->SetStatusWidths(%s, %s_widths);\n' % \
               (obj.name, len(widths), obj.name))
        labels = ',\n        '.join([cppgen.quote_str(l) for l in labels])
        append('const wxString %s_fields[] = {\n        %s\n    };\n' %
               (obj.name, labels))
        append('for(int i = 0; i < %s->GetFieldsCount(); ++i) {\n' % obj.name)
        append('    %s->SetStatusText(%s_fields[i], i);\n    }\n' % \
               (obj.name, obj.name))
        return init, [], props, []

# end of class CppStatusBarCodeGenerator


class CppFrameCodeGenerator:
    constructor = [('wxWindow*', 'parent'), ('int', 'id'),
                   ('const char*', 'title'),
                   ('const wxPoint&', 'pos', 'wxDefaultPosition'),
                   ('const wxSize&', 'size', 'wxDefaultSize'),
                   ('long', 'style', 'wxDEFAULT_FRAME_STYLE')]

    def get_code(self, obj):
        return [], [], [], [] # the frame can't be a children

    def get_properties_code(self, frame):
        """\
        generates the code for the various wxFrame specific properties.
        Returns a list of strings containing the generated code
        """
        prop = frame.properties
        cppgen = common.code_writers['C++']
        out = []
        title = prop.get('title')
        if title: out.append('SetTitle(%s);\n' % cppgen.quote_str(title))
        out.extend(cppgen.generate_common_properties(frame))
        return out

    def get_layout_code(self, frame):
        return ['Layout();\n']

# end of class CppFrameCodeGenerator


class CppMDIChildFrameCodeGenerator(CppFrameCodeGenerator):
    extra_headers = ['<wx/mdi.h>']

# end of class CppMDIChildFrameCodeGenerator


def initialize():
    cn = common.class_names
    cn['EditFrame'] = 'wxFrame'
    cn['EditMDIChildFrame'] = 'wxMDIChildFrame'
    cn['EditStatusBar'] = 'wxStatusBar'
    common.toplevels['EditFrame'] = 1
    common.toplevels['EditMDIChildFrame'] = 1

    pygen = common.code_writers.get('python')
    if pygen:
        awh = pygen.add_widget_handler
        awh('wxFrame', PythonFrameCodeGenerator())
        awh('wxMDIChildFrame', PythonFrameCodeGenerator())
        awh('wxStatusBar', PythonStatusbarCodeGenerator())
        aph = pygen.add_property_handler
        aph('statusbar', pygen.DummyPropertyHandler)
        aph('fields', StatusFieldsHandler)
        aph('menubar', pygen.DummyPropertyHandler)

    xrcgen = common.code_writers.get('XRC')
    if xrcgen:
        xrcgen.add_widget_handler('wxFrame', xrc_frame_code_generator)
        xrcgen.add_widget_handler('wxMDIChildFrame',
                                  xrcgen.NotImplementedXrcObject)
        xrcgen.add_widget_handler('wxStatusBar',
                                  xrcgen.NotImplementedXrcObject)
    cppgen = common.code_writers.get('C++')
    if cppgen:
        cppgen.add_widget_handler('wxFrame', CppFrameCodeGenerator())
        cppgen.add_widget_handler('wxMDIChildFrame',
                                  CppMDIChildFrameCodeGenerator())
        
        cppgen.add_widget_handler('wxStatusBar', CppStatusBarCodeGenerator())
        
        cppgen.add_property_handler('fields', StatusFieldsHandler)
        cppgen.add_property_handler('menubar', cppgen.DummyPropertyHandler)
        cppgen.add_property_handler('statusbar', cppgen.DummyPropertyHandler)
