"""\
Python code generator

How the code is generated: every time the end of an object is reached during
the parsing of the xml tree, either the function 'add_object' or the function
'add_class' is called: the latter when the object is a toplevel one, the former
when it is not. In the last case, 'add_object' calls the appropriate ``writer''
function for the specific object, found in the 'obj_builders' dict. Such
function accepts one argument, the CodeObject representing the object for
which the code has to be written, and returns 3 lists of strings, representing
the lines to add to the '__init__', '__set_properties' and '__do_layout'
methods of the parent object.

@copyright: John Dubery
@copyright: 2002-2007 Alberto Griggio <agriggio@users.sourceforge.net>
@copyright: 2012 Carsten Grohmann <mail@carstengrohmann.de>
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import cStringIO
import os
import os.path
import random
import re

from codegen import BaseCodeWriter, \
                    BaseSourceFileContent, \
                    BaseWidgetHandler


class SourceFileContent(BaseSourceFileContent):

    rec_block_start = re.compile(
        r'^(?P<spaces>\s*)'                     # leading spaces
        r'#\s*'                                 # comment sign
        r'begin\s+wxGlade:\s*'                  # "begin wxGlade:" statement and tailing spaces
        r'(?P<classname>[a-zA-Z_]+\w*)??'       # class or function name (non-greedy)
        r'[.]?'                                 # separator between class and function / block (non-gready)
        r'(?P<block>\w+)'                       # function / block name
        r'\s*$'                                 # tailing spaces
        )

    rec_block_end = re.compile(
        r'^\s*'                                 # leading spaces
        r'#\s*'                                 # comment sign
        r'end\s+wxGlade'                        # "end exGlade" statement
        r'\s*$'                                 # tailing spaces
        )

    # Less precise regex, but matches definitions with base classes having
    # module qualified names.
    rec_class_decl = re.compile(
        r'^\s*'                                       # leading spaces
        r'class\s+([a-zA-Z_]\w*)\s*(\([\s\w.,]*\))?:' # "class <name>" statement
        r'\s*$'                                       # tailing spaces
        )

    rec_event_handler = re.compile(
        r'^\s+'                                            # leading spaces (mandatory)
        r'def\s+(?P<handler>[A-Za-z_]+\w*)'                # event handler name
        r'\s*'                                             # optional spaces
        r'\(.*\):'                                         # function parameters
        r'\s*'                                             # optional spaces
        r'#\s*wxGlade:\s*(?P<class>\w+)\.<event_handler>'  # wxGlade event handler statement with class name
        r'\s*$'                                            # tailing spaces
        )

    def __init__(self, name, code_writer):

        # initialise new variables first
        self.use_new_namespace = code_writer.use_new_namespace

        # call inherited constructor
        BaseSourceFileContent.__init__(self, name, code_writer)

    def build_untouched_content(self):
        BaseSourceFileContent.build_untouched_content(self)
        inside_block = False
        inside_triple_quote = False
        triple_quote_str = None
        tmp_in = self._load_file(self.name)
        out_lines = []
        for line in tmp_in:
            quote_index = -1
            if not inside_triple_quote:
                triple_dquote_index = line.find('"""')
                triple_squote_index = line.find("'''")
                if triple_squote_index == -1:
                    quote_index = triple_dquote_index
                    tmp_quote_str = '"""'
                elif triple_dquote_index == -1:
                    quote_index = triple_squote_index
                    tmp_quote_str = "'''"
                else:
                    quote_index, tmp_quote_str = min(
                        (triple_squote_index, "'''"),
                        (triple_dquote_index, '"""'))

            if not inside_triple_quote and quote_index != -1:
                inside_triple_quote = True
                triple_quote_str = tmp_quote_str
            if inside_triple_quote:
                end_index = line.rfind(triple_quote_str)
                if quote_index < end_index and end_index != -1:
                    inside_triple_quote = False

            result = self.rec_class_decl.match(line)
            if not inside_triple_quote and not inside_block and result:
##                print ">> class %r" % result.group(1)
                if not self.class_name:
                    # this is the first class declared in the file: insert the
                    # new ones before this
                    out_lines.append('<%swxGlade insert new_classes>' %
                                     self.nonce)
                    self.new_classes_inserted = True
                self.class_name = result.group(1)
                self.class_name = self.format_classname(self.class_name)
                self.classes[self.class_name] = 1  # add the found class to the list
                                              # of classes of this module
                out_lines.append(line)
            elif not inside_block:
                result = self.rec_block_start.match(line)
                if not inside_triple_quote and result:
##                     print ">> block %r %r %r" % (
##                         result.group('spaces'), result.group('classname'), result.group('block'))
                    # replace the lines inside a wxGlade block with a tag that
                    # will be used later by add_class
                    spaces = result.group('spaces')
                    which_class = result.group('classname')
                    which_block = result.group('block')
                    if not which_class:
                        which_class = self.class_name
                    else:
                        which_class = self.format_classname(which_class)
                    self.spaces[which_class] = spaces
                    inside_block = True
                    if not self.class_name:
                        out_lines.append('<%swxGlade replace %s>' % \
                                         (self.nonce, which_block))
                    else:
                        out_lines.append('<%swxGlade replace %s %s>' % \
                                         (self.nonce, which_class, which_block))
                else:
                    result = self.rec_event_handler.match(line)
                    if not inside_triple_quote and result:
                        which_handler = result.group('handler')
                        which_class = self.format_classname(result.group('class'))
                        self.event_handlers.setdefault(
                            which_class, {})[which_handler] = 1
                    if self.class_name and self.is_end_of_class(line):
                        # add extra event handlers here...
                        out_lines.append('<%swxGlade event_handlers %s>'
                                         % (self.nonce, self.class_name))
                    out_lines.append(line)
                    if self.is_import_line(line):
                        # add a tag to allow extra modules
                        out_lines.append('<%swxGlade extra_modules>\n'
                                         % self.nonce)
            else:
                # ignore all the lines inside a wxGlade block
                if self.rec_block_end.match(line):
##                     print 'end block'
                    inside_block = False
        if not self.new_classes_inserted:
            # if we are here, the previous ``version'' of the file did not
            # contain any class, so we must add the new_classes tag at the
            # end of the file
            out_lines.append('<%swxGlade insert new_classes>' % self.nonce)
        # set the ``persistent'' content of the file
        self.content = "".join(out_lines)

    def is_import_line(self, line):
        if self.use_new_namespace:
            return line.startswith('import wx')
        else:
            return line.startswith('from wxPython.wx import *')

    def format_classname(self, class_name):
        """\
        Format class name read from existing source file.

        If we're in a subpackage, we should include the package name in the
        class name.

        @param class_name: Class name
        @type class_name:  String

        @rtype: String
        """
        if not self.multiple_files:
            return class_name
        name = self.name
        if self.out_dir:
            name = name.replace(self.out_dir, '')
        pkg = os.path.dirname(name).replace(os.sep, '.')
        if pkg.startswith('.'):
            pkg = pkg[1:]
        if pkg:
            return pkg + '.' + class_name
        else:
            return class_name

# end of class SourceFileContent


class WidgetHandler(BaseWidgetHandler):
    pass

# end of class WidgetHandler


class PythonCodeWriter(BaseCodeWriter):
    """\
    Code writer class for writing Python code out of the designed GUI elements

    @ivar use_new_namespace: If True use the new name space (import wx)
    @type use_new_namespace: Boolean

    @see: L{BaseCodeWriter}
    """

    default_extensions = ['py', 'pyw']
    language = "python"

    code_statements = {
        'backgroundcolour': "%(objname)s.SetBackgroundColour(%(value)s)\n",
        'contentnotfound':  "pass",
        'disabled':         "%(objname)s.Enable(False)\n",
        'extraproperties':  "%(objname)s.Set%(propname)s(%(value)s)\n",
        'focused':          "%(objname)s.SetFocus()\n",
        'foregroundcolour': "%(objname)s.SetForegroundColour(%(value)s)\n",
        'hidden':           "%(objname)s.Hide()\n",
        'setfont':          "%(objname)s.SetFont(%(cnfont)s(%(size)s, %(family)s, "
                            "%(style)s, %(weight)s, %(underlined)s, %(face)s))\n",
        'tooltip':          "%(objname)s.SetToolTipString(%(tooltip)s)\n",
        'wxcolour':         "wxColour(%(value)s)",
        'wxsystemcolour':   "wxSystemSettings_GetColour(%(value)s)",
        }

    class_separator = '.'
    comment_sign = '#'

    global_property_writers = {
        'font':            BaseCodeWriter.FontPropertyHandler,
        'events':          BaseCodeWriter.EventsPropertyHandler,
        'extraproperties': BaseCodeWriter.ExtraPropertiesPropertyHandler,
        }

    indent_level_func_body = 2

    name_ctor = '__init__'

    shebang = '#!/usr/bin/env python\n'

    SourceFileContent = SourceFileContent

    tmpl_name_do_layout = '__do_layout'
    tmpl_name_set_properties = '__set_properties'

    tmpl_encoding = "# -*- coding: %s -*-\n"

    tmpl_class_end = '\n' \
                     '%(comment)s end of class %(klass)s\n'

    tmpl_ctor_call_layout = '\n' \
                            '%(tab)sself.__set_properties()\n' \
                            '%(tab)sself.__do_layout()\n'

    tmpl_func_empty = '%(tab)spass\n'

    tmpl_style = '%(tab)skwds["style"] = %(style)s\n'

    tmpl_appfile = """\
%(overwrite)s\
%(header_lines)s\
%(import_gettext)s\
from %(top_win_class)s import %(top_win_class)s\n\n"""

    tmpl_detailed = """\
class %(klass)s(%(cn_wxApp)s):
%(tab)sdef OnInit(self):
%(tab)s%(tab)s%(cn_wxInitAll)s()
%(tab)s%(tab)s%(top_win)s = %(top_win_class)s(None, %(cn_wxIDANY)s, "")
%(tab)s%(tab)sself.SetTopWindow(%(top_win)s)
%(tab)s%(tab)s%(top_win)s.Show()
%(tab)s%(tab)sreturn 1

# end of class %(klass)s

if __name__ == "__main__":
%(tab)s%(name)s = %(klass)s(0)
%(tab)s%(name)s.MainLoop()"""

    tmpl_gettext_detailed = """\
class %(klass)s(%(cn_wxApp)s):
%(tab)sdef OnInit(self):
%(tab)s%(tab)s%(cn_wxInitAll)s()
%(tab)s%(tab)s%(top_win)s = %(top_win_class)s(None, %(cn_wxIDANY)s, "")
%(tab)s%(tab)sself.SetTopWindow(%(top_win)s)
%(tab)s%(tab)s%(top_win)s.Show()
%(tab)s%(tab)sreturn 1

# end of class %(klass)s

if __name__ == "__main__":
%(tab)sgettext.install("%(name)s") # replace with the appropriate catalog name

%(tab)s%(name)s = %(klass)s(0)
%(tab)s%(name)s.MainLoop()"""

    tmpl_simple = """\
if __name__ == "__main__":
%(tab)s%(name)s = %(cn_wxPySimpleApp)s(0)
%(tab)s%(cn_wxInitAll)s()
%(tab)s%(top_win)s = %(top_win_class)s(None, %(cn_wxIDANY)s, "")
%(tab)s%(name)s.SetTopWindow(%(top_win)s)
%(tab)s%(top_win)s.Show()
%(tab)s%(name)s.MainLoop()"""

    tmpl_gettext_simple = """\
if __name__ == "__main__":
%(tab)sgettext.install("%(name)s") # replace with the appropriate catalog name

%(tab)s%(name)s = %(cn_wxPySimpleApp)s(0)
%(tab)s%(cn_wxInitAll)s()
%(tab)s%(top_win)s = %(top_win_class)s(None, %(cn_wxIDANY)s, "")
%(tab)s%(name)s.SetTopWindow(%(top_win)s)
%(tab)s%(top_win)s.Show()
%(tab)s%(name)s.MainLoop()"""

    def __init__(self):
        BaseCodeWriter.__init__(self)

    def cn(self, name):
        """\
        Return the name properly formatted for the selected name space.

        @see: L{use_new_namespace}
        @see: L{cn_f()}
        """
        if self.use_new_namespace:
            if name.startswith('wx'):
                return 'wx.' + name[2:]
            elif name.startswith('EVT_'):
                return 'wx.' + name
        return name

    def cn_f(self, flags):
        """\
        Return the flags properly formatted.

        @see: L{cn()}
        """
        return " | ".join([self.cn(f) for f in str(flags).split('|')])

    def cn_class(self, klass):
        """\
        Return the short class name 
        """
        return self.without_package(klass)

    def initialize(self, app_attrs):
        """\
        Writer initialization function.

        @keyword path: Output path for the generated code (a file if
                       multi_files is False, a dir otherwise)
        @keyword option: If True, generate a separate file for each custom
                         class
        """
        # initialise parent class
        BaseCodeWriter.initialize(self, app_attrs)
        out_path = app_attrs['path']

        try:
            self.use_new_namespace = int(app_attrs['use_new_namespace'])
        except (KeyError, ValueError):
            self.use_new_namespace = True

        if self.use_new_namespace:
            self.header_lines.append('import wx\n')
        else:
            self.header_lines.append('from wxPython.wx import *\n')

        if self.multiple_files:
            self.previous_source = None
            if not os.path.isdir(out_path):
                raise IOError("'path' must be a directory when generating"\
                                      " multiple output files")
            self.out_dir = out_path
        else:
            if not self._overwrite and self._file_exists(out_path):
                # the file exists, we must keep all the lines not inside a
                # wxGlade block. NOTE: this may cause troubles if out_path is
                # not a valid source file, so be careful!
                self.previous_source = SourceFileContent(out_path, self)
            else:
                # if the file doesn't exist, create it and write the ``intro''
                self.previous_source = None
                self.output_file = cStringIO.StringIO()
                self.output_file_name = out_path
                for line in self.header_lines:
                    self.output_file.write(line)
                self.output_file.write('<%swxGlade extra_modules>\n' % self.nonce)
                self.output_file.write('\n')
                self.output_file.write('<%swxGlade replace dependencies>\n' % self.nonce)
                self.output_file.write('<%swxGlade replace extracode>\n' % self.nonce)

    def add_app(self, app_attrs, top_win_class):
        # add language specific mappings
        self.lang_mapping = {
            'cn_wxApp': self.cn('wxApp'),
            'cn_wxIDANY': self.cn('wxID_ANY'),
            'cn_wxInitAll': self.cn('wxInitAllImageHandlers'),
            'cn_wxPySimpleApp': self.cn('wxPySimpleApp'),
            'import_gettext': '',
            }

        # Add gettext import statements
        if self._use_gettext:
            if self.multiple_files:
                self.lang_mapping['import_gettext'] = 'import gettext\n'
            else:
                self.dependencies['import gettext\n'] = 1

        BaseCodeWriter.add_app(self, app_attrs, top_win_class)

    def add_object(self, top_obj, sub_obj):
        # get top level source code object and the widget builder instance
        klass, builder = self._add_object_init(top_obj, sub_obj)
        if not klass or not builder:
            return

        try:
            init, props, layout = builder.get_code(sub_obj)
        except:
            print sub_obj
            raise  # this shouldn't happen

        if sub_obj.in_windows:  # the object is a wxWindow instance
            if sub_obj.is_container and not sub_obj.is_toplevel:
                init.reverse()
                klass.parents_init.extend(init)
            else:
                klass.init.extend(init)

            # Add a dependency of the current object on its parent
            klass.deps.append((sub_obj, sub_obj.parent))
            klass.child_order.append(sub_obj)
            klass.init_lines[sub_obj] = init

            mycn = getattr(builder, 'cn', self.cn)
            if hasattr(builder, 'get_events'):
                evts = builder.get_events(sub_obj)
                for id, event, handler in evts:
                    klass.event_handlers.append((id, mycn(event), handler))
            elif 'events' in sub_obj.properties:
                id_name, id = self.generate_code_id(sub_obj)
                if id == '-1' or id == self.cn('wxID_ANY'):
                    id = '#self.%s' % sub_obj.name
                for event, handler in sub_obj.properties['events'].iteritems():
                    klass.event_handlers.append((id, mycn(event), handler))

            # try to see if there's some extra code to add to this class
            if not sub_obj.preview:
                extra_code = getattr(builder, 'extracode',
                                     sub_obj.properties.get('extracode', ""))
                if extra_code:
                    extra_code = re.sub(r'\\n', '\n', extra_code)
                    klass.extra_code.append(extra_code)
                    # if we are not overwriting existing source, warn the user
                    # about the presence of extra code
                    if not self.multiple_files and self.previous_source:
                        self.warning(
                            '%s has extra code, but you are not '
                            'overwriting existing sources: please check '
                            'that the resulting code is correct!' % \
                            sub_obj.name
                            )

        else:  # the object is a sizer
            if sub_obj.base == 'wxStaticBoxSizer':
                i = init.pop(0)
                klass.parents_init.insert(1, i)

                # Add a dependency of the current object on its parent
                klass.deps.append((sub_obj, sub_obj.parent))
                klass.child_order.append(sub_obj)
                klass.init_lines[sub_obj] = [i]

            klass.sizers_init.extend(init)

        klass.props.extend(props)
        klass.layout.extend(layout)
        if self.multiple_files and \
               (sub_obj.is_toplevel and sub_obj.base != sub_obj.klass):
            key = 'from %s import %s\n' % (sub_obj.klass,
                                           self.without_package(sub_obj.klass))
            klass.dependencies[key] = 1
        for dep in getattr(self.obj_builders.get(sub_obj.base),
                           'import_modules', []):
            klass.dependencies[dep] = 1

    def add_sizeritem(self, toplevel, sizer, obj, option, flag, border):
        # an ugly hack to allow the addition of spacers: if obj_name can be
        # parsed as a couple of integers, it is the size of the spacer to add
        obj_name = obj.name
        try:
            w, h = [int(s) for s in obj_name.split(',')]
        except ValueError:
            if obj.in_windows:
                # attribute is a special property, which tells us if the object
                # is a local variable or an attribute of its parent
                if self.test_attribute(obj):
                    obj_name = 'self.' + obj_name
        else:
            obj_name = '(%d, %d)' % (w, h)  # it was the dimension of a spacer
        if toplevel.klass in self.classes:
            klass = self.classes[toplevel.klass]
        else:
            klass = self.classes[toplevel.klass] = self.ClassLines()
        buffer = '%s.Add(%s, %s, %s, %s)\n' % \
                 (sizer.name, obj_name, option, self.cn_f(flag), self.cn_f(border))
        klass.layout.append(buffer)

    def generate_code_ctor_stage1(self, code_obj, is_new, tab):
        code_lines = []
        write = code_lines.append
        
        builder = self.obj_builders[code_obj.base]
        mycn = getattr(builder, 'cn', self.cn)
        mycn_f = getattr(builder, 'cn_f', self.cn_f)

        # custom base classes support
        custom_base = getattr(code_obj, 'custom_base',
                              code_obj.properties.get('custom_base', None))
        if code_obj.preview or (custom_base and not custom_base.strip()):
            custom_base = None

        # generate constructor code
        if is_new:
            base = mycn(code_obj.base)
            if custom_base:
                base = ", ".join([b.strip() for b in custom_base.split(',')])
            if code_obj.preview and code_obj.klass == base:
                klass = code_obj.klass + \
                    ('_%d' % random.randrange(10 ** 8, 10 ** 9))
            else:
                klass = code_obj.klass
            write('\nclass %s(%s):\n' % (self.without_package(klass), base))
            write(self.tabs(1) + 'def __init__(self, *args, **kwds):\n')
        elif custom_base:
            # custom base classes set, but "overwrite existing sources" not
            # set. Issue a warning about this
            self.warning(
                '%s has custom base classes, but you are not overwriting '
                'existing sources: please check that the resulting code is '
                'correct!' % code_obj.name
                )

        # __init__ begin tag
        write(self.tmpl_block_begin % {
            'class_separator': self.class_separator,
            'comment_sign':    self.comment_sign,
            'function':        self.name_ctor, 
            'klass':           self.cn_class(code_obj.klass),
            'tab':             tab,
            })

        prop = code_obj.properties
        style = prop.get("style", None)
        if style:
            stmt_style = self._format_style(style, code_obj)
            write(stmt_style % {
                'style': mycn_f(style),
                'tab': tab,
                })

        # initialise custom base class
        if custom_base:
            bases = [b.strip() for b in custom_base.split(',')]
            for i, b in enumerate(bases):
                if not i:
                    write(tab + '%s.__init__(self, *args, **kwds)\n' % b)
                else:
                    write(tab + '%s.__init__(self)\n' % b)
        else:
            write(tab + '%s.__init__(self, *args, **kwds)\n' % \
                  mycn(code_obj.base))

        init_lines = self.classes[code_obj.klass].init
        parents_init = self.classes[code_obj.klass].parents_init

        # classes[code_obj.klass].deps now contains a mapping of child to
        # parent for all children we processed...
        object_order = []
        for obj in self.classes[code_obj.klass].child_order:
            # Don't add it again if already present
            if obj in object_order:
                continue

            object_order.append(obj)

            # Insert parent and ancestor objects before the current object
            current_object = obj
            for child, parent in self.classes[code_obj.klass].deps[:]:
                if child is current_object:
                    if parent not in object_order:
                        idx = object_order.index(current_object)
                        object_order.insert(idx, parent)
                    current_object = parent

                    # We processed the dependency: remove it
                    self.classes[code_obj.klass].deps.remove((child, parent))

        # Write out the initialisation in the order we just generated
        for obj in object_order:
            if obj in self.classes[code_obj.klass].init_lines:
                for l in self.classes[code_obj.klass].init_lines[obj]:
                    write(tab + l)

        return code_lines

    def generate_code_do_layout(self, builder, code_obj, is_new, tab):
        # Python has two indentation levels
        #  1st) for function declaration
        #  2nd) for function body
        self.tmpl_func_do_layout = '\n' + \
                              self.tabs(1) + 'def __do_layout(self):\n' + \
                              '%(content)s' + \
                              ''
        return BaseCodeWriter.generate_code_do_layout(
            self,
            builder,
            code_obj,
            is_new,
            tab,
            )

    def generate_code_event_bind(self, code_obj, tab, event_handlers):
        code_lines = []
        write = code_lines.append

        if event_handlers:
            write('\n')

        if not self.use_new_namespace:
            for win_id, event, handler in event_handlers:
                if win_id.startswith('#'):
                    win_id = '%s.GetId()' % win_id[1:]
                write('%(tab)s%(event)s(self, %(win_id)s, self.%(handler)s)\n' % {
                    'tab':     tab,
                    'event':   event,
                    'win_id':  win_id,
                    'handler': handler,
                    })
        else:
            for win_id, event, handler in event_handlers:
                if win_id.startswith('#'):
                    win_id = win_id[1:]
                write('%(tab)sself.Bind(%(event)s, self.%(handler)s, %(win_id)s)\n' % {
                    'tab': tab,
                    'event': event,
                    'handler': handler,
                    'win_id': win_id,
                    })
        
        return code_lines

    def generate_code_event_handler(self, code_obj, is_new, tab, prev_src, \
                                    event_handlers):
        # Python has two indentation levels
        #  1st) for function declaration
        #  2nd) for function body
        self.tmpl_func_event_stub = self.tabs(1) + """\
def %(handler)s(self, event):  # wxGlade: %(klass)s.<event_handler>
%(tab)sprint "Event handler '%(handler)s' not implemented!"
%(tab)sevent.Skip()
"""
        return BaseCodeWriter.generate_code_event_handler(
            self,
            code_obj,
            is_new,
            tab,
            prev_src,
            event_handlers,
            )

    def generate_code_id(self, obj, id=None):
        if obj and obj.preview:
            return '', '-1'  # never generate ids for preview code
        if id is None:
            id = obj.properties.get('id')
        if not id:
            return '', self.cn('wxID_ANY')
        tokens = id.split('=', 1)
        if len(tokens) == 2:
            name, val = tokens
        else:
            return '', self.cn(tokens[0])   # we assume name is declared elsewhere
        if not name:
            return '', self.cn(val)
        name = name.strip()
        val = val.strip()
        if val == '?':
            val = self.cn('wxNewId()')
        else:
            val = self.cn(val)
        # check to see if we have to make the var global or not...
        if '.' in name:
            return ('%s = %s\n' % (name, val), name)
        return ('global %s; %s = %s\n' % (name, name, val), name)

    def generate_code_set_properties(self, builder, code_obj, is_new, tab):
        # Python has two indentation levels
        #  1st) for function declaration
        #  2nd) for function body
        self.tmpl_func_set_properties = '\n' + \
                              self.tabs(1) + 'def __set_properties(self):\n' + \
                              '%(content)s' + \
                              ''        

        return BaseCodeWriter.generate_code_set_properties(
            self,
            builder,
            code_obj,
            is_new,
            tab,
            )

    def generate_code_size(self, obj):
        objname = self._get_code_name(obj)
        size = obj.properties.get('size', '').strip()
        use_dialog_units = (size[-1] == 'd')
        if not obj.parent:
            method = 'SetSize'
        else:
            method = 'SetMinSize'
        if use_dialog_units:
            return '%s.%s(%s(%s, (%s)))\n' % (
                objname,
                method,
                self.cn('wxDLG_SZE'),
                objname,
                size[:-1]
                )
        else:
            return '%s.%s((%s))\n' % (objname, method, size)

    def quote_str(self, s, translate=True, escape_chars=True):
        if not s:
            return '""'
        s = s.replace('"', r'\"')
        if escape_chars:
            s = self._quote_str_pattern.sub(self._do_replace, s)
        else:
            s = s.replace('\\', r'\\')  # just quote the backslashes
        try:
            unicode(s, 'ascii')
            if self._use_gettext and translate:
                return '_("%s")' % s
            else:
                return '"%s"' % s
        except UnicodeDecodeError:
            if self._use_gettext and translate:
                return '_(u"%s")' % s
            else:
                return 'u"%s"' % s

    def without_package(self, class_name):
        """\
        Removes the package name from the given class name
        """
        return class_name.split('.')[-1]

    def _get_class_filename(self, klass):
        filename = os.path.join(
            self.out_dir,
            klass.replace('.', os.sep) + '.py'
            )
        return filename

    def _get_code_name(self, obj):
        if obj.is_toplevel:
            return 'self'
        else:
            if self.test_attribute(obj):
                return 'self.%s' % obj.name
            else:
                return obj.name

# end of class PythonCodeWriter

writer = PythonCodeWriter()
"""\
The code writer is an instance of L{PythonCodeWriter}.
"""

language = writer.language
"""\
Language generated by this code generator
"""
