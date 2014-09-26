"""\
Code generator functions for wxNotebook objects

@copyright: 2002-2007 Alberto Griggio
@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common
import wcodegen


class TabsCodeHandler:
    def __init__(self):
        self.tabs = []
        self.curr_tab_name = []
        self.tab_window = None

    def start_elem(self, name, attrs):
        if name == 'tab':
            window = attrs.get('window')
            if not window:
                return
            self.tab_window = window
            self.curr_tab_name = []

    def end_elem(self, name, code_obj):
        if name == 'tabs':
            code_obj.properties['tabs'] = self.tabs
            return True
        elif name == 'tab':
            tab_name = "".join(self.curr_tab_name)
            if self.tab_window:
                self.tabs.append((tab_name, self.tab_window))
        return False

    def char_data(self, data):
        self.curr_tab_name.append(data)

# end of class TabsCodeHandler


class PythonNotebookGenerator(wcodegen.PythonWidgetCodeWriter):
    def get_code(self, window):
        prop = window.properties
        id_name, id = self.codegen.generate_code_id(window)

        layout_props = []
        tabs = prop.get('tabs', [])
        for label, tab_win in tabs:
            layout_props.append('self.%s.AddPage(self.%s, %s)\n' %
                                (window.name, tab_win,
                                 self.codegen.quote_str(label)))

        if not window.parent.is_toplevel:
            parent = 'self.%s' % window.parent.name
        else:
            parent = 'self'
        if window.is_toplevel:
            l = []
            if id_name:
                l.append(id_name)
            l.append('self.%s = %s(%s, %s)\n' %
                     (window.name, self.codegen.without_package(window.klass),
                      parent, id))
            return l, [], []
        style = prop.get("style")
        if style:
            style = ", style=%s" % self.cn_f(style)
        else:
            style = ''
        klass = window.klass
        if window.preview:
            klass = 'wxNotebook'
        init = []
        if id_name:
            init.append(id_name)
        init.append(('self.%s = ' + self.cn(klass) + '(%s, %s%s)\n') %
                    (window.name, parent, id, style))

        props_buf = self.codegen.generate_common_properties(window)
        return init, props_buf, layout_props

    def get_properties_code(self, obj):
        prop = obj.properties
        props_buf = []
        tabs = prop.get('tabs', [])
        for label, window in tabs:
            props_buf.append('self.AddPage(self.%s, %s)\n' %
                             (window, self.codegen.quote_str(label)))
        props_buf.extend(self.codegen.generate_common_properties(obj))
        return props_buf

# end of class PythonNotebookGenerator


def xrc_code_generator(obj):
    xrcgen = common.code_writers['XRC']
    from xml.sax.saxutils import escape

    class NotebookXrcObject(xrcgen.DefaultXrcObject):

        def write(self, outfile, ntabs):
            # the "tabs" property contains the pages of a notebook
            # be carefully: tabs in context of code generation are white
            # spaces used for indenting lines!!
            if self.properties.has_key('tabs'):
                self.pages = self.properties['tabs']
                del self.properties['tabs']
            else:
                self.pages = []
            self.index = 0
            # always use a wxNotebookSizer
            self.properties['usenotebooksizer'] = '1'
            if 'no_custom_class' in self.properties:
                del self.properties['no_custom_class']
            xrcgen.DefaultXrcObject.write(self, outfile, ntabs)

        def write_child_prologue(self, child, outfile, ntabs):
            if self.pages:
                tab_s = '    ' * ntabs
                outfile.write(tab_s + '<object class="notebookpage">\n')
                outfile.write(tab_s + '<label>%s</label>\n' %
                              escape(self.pages[self.index][0]))
                self.index += 1

        def write_child_epilogue(self, child, outfile, ntabs):
            if self.tabs:
                outfile.write('    '*ntabs + '</object>\n')

    return NotebookXrcObject(obj)


class CppNotebookGenerator(wcodegen.CppWidgetCodeWriter):
    constructor = [('wxWindow*', 'parent'), ('int', 'id'),
                   ('const wxPoint&', 'pos', 'wxDefaultPosition'),
                   ('const wxSize&', 'size', 'wxDefaultSize'),
                   ('long', 'style', '0')]

    extra_headers = ['<wx/notebook.h>']

    def get_code(self, window):
        """\
        generates the C++ code for wxNotebook
        """
        prop = window.properties
        id_name, id = self.codegen.generate_code_id(window)
        if id_name:
            ids = [id_name]
        else:
            ids = []

        layout_props = []
        tabs = prop.get('tabs', [])
        for label, tab_win in tabs:
            layout_props.append('%s->AddPage(%s, %s);\n' %
                                (window.name, tab_win,
                                 self.codegen.quote_str(label)))

        if not window.parent.is_toplevel:
            parent = '%s' % window.parent.name
        else:
            parent = 'this'
        if window.is_toplevel:
            l = ['%s = new %s(%s, %s);\n' %
                 (window.name, window.klass, parent, id)]
            return l, ids, [], []
        style = prop.get('style')
        if style:
            style = ', wxDefaultPosition, wxDefaultSize, %s' % self.cn_f(
                style)
        else:
            style = ''
        init = ['%s = new %s(%s, %s%s);\n' %
                (window.name, window.klass, parent, id, style)]

        props_buf = self.codegen.generate_common_properties(window)

        return init, ids, props_buf, layout_props

    def get_properties_code(self, obj):
        prop = obj.properties
        props_buf = []
        tabs = prop.get('tabs', [])
        for label, window in tabs:
            props_buf.append('AddPage(%s, %s);\n' %
                             (window, self.codegen.quote_str(label)))
        props_buf.extend(self.codegen.generate_common_properties(obj))
        return props_buf

    def get_events(self, obj):
        return self.codegen.get_events_with_type(obj, 'wxNotebookEvent')

# end of class CppNotebookGenerator


def initialize():
    klass = 'wxNotebook'
    common.class_names['EditNotebook'] = klass
    common.class_names['NotebookPane'] = 'wxPanel'
    common.toplevels['EditNotebook'] = 1
    common.toplevels['NotebookPane'] = 1
    common.register('python', klass, PythonNotebookGenerator(klass),
                    'tabs', TabsCodeHandler, klass)
    common.register('C++', klass, CppNotebookGenerator(klass),
                    'tabs', TabsCodeHandler, klass)
    common.register('XRC', klass, xrc_code_generator,
                    'tabs', TabsCodeHandler, klass)
