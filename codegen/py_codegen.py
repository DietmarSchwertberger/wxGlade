"""\
Python code generator

@copyright: John Dubery
@copyright: 2002-2007 Alberto Griggio
@copyright: 2012-2016 Carsten Grohmann
@copyright: 2016-2019 Dietmar Schwertberger
@license: MIT (see LICENSE.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import os, os.path, random, re
from codegen import BaseLangCodeWriter, BaseSourceFileContent
import wcodegen
import compat


class SourceFileContent(BaseSourceFileContent):

    rec_block_start = re.compile(
        r'^(?P<spaces>\s*)'                     # leading spaces
        r'#\s*'                                 # comment sign
        r'begin\s+wxGlade:\s*'                  # "begin wxGlade:" statement and tailing spaces
        r'(?P<classname>[a-zA-Z_]+\w*)??'       # class or function name (non-greedy)
        r'[.]?'                                 # separator between class and function / block (non-greedy)
        r'(?P<block>\w+)'                       # function / block name
        r'\s*$' )                               # tailing spaces

    rec_block_end = re.compile(
        r'^\s*'                                 # leading spaces
        r'#\s*'                                 # comment sign
        r'end\s+wxGlade'                        # "end exGlade" statement
        r'\s*$' )                               # tailing spaces

    # Less precise regex, but matches definitions with base classes having module qualified names.
    rec_class_decl = re.compile(
        r'^\s*'                                        # leading spaces
        r'class\s+([a-zA-Z_]\w*)\s*(\([\s\w.,]*\))?:'  # "class <name>" statement
        r'\s*$' )                                      # tailing spaces

    rec_event_handler = re.compile(
        r'^\s+'                                            # leading spaces (mandatory)
        r'def\s+(?P<handler>[A-Za-z_]+\w*)'                # event handler name
        r'\s*'                                             # optional spaces
        r'\(.*\):'                                         # function parameters
        r'\s*'                                             # optional spaces
        r'#\s*wxGlade:\s*(?P<class>\w+)\.<event_handler>'  # wxGlade event handler statement with class name
        r'\s*$' )                                          # tailing spaces

    def build_untouched_content(self):
        BaseSourceFileContent.build_untouched_content(self)
        inside_block = False
        inside_triple_quote = False
        triple_quote_str = None
        tmp_in = self._load_file(self.name)
        out_lines = []
        for line in tmp_in:
            if line.endswith("\r\n"):  # normalize line ending for files on Windows
                line = "%s\n"%line[:-2]
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
                    quote_index, tmp_quote_str = min( (triple_squote_index, "'''"),
                                                      (triple_dquote_index, '"""') )

            if not inside_triple_quote and quote_index != -1:
                inside_triple_quote = True
                triple_quote_str = tmp_quote_str
            if inside_triple_quote:
                end_index = line.rfind(triple_quote_str)
                if quote_index < end_index and end_index != -1:
                    inside_triple_quote = False

            result = self.rec_class_decl.match(line)
            if not inside_triple_quote and not inside_block and result:
                if not self.class_name:
                    # this is the first class declared in the file: insert the new ones before this
                    out_lines.append('<%swxGlade insert new_classes>' % self.nonce)
                    self.new_classes_inserted = True
                self.class_name = result.group(1)
                self.class_name = self.format_classname(self.class_name)
                self.classes[self.class_name] = 1  # add the found class to the list of classes of this module
                out_lines.append(line)
            elif not inside_block:
                result = self.rec_block_start.match(line)
                if not inside_triple_quote and result:
                    # replace the lines inside a wxGlade block with a tag that  will be used later by add_class
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
                        out_lines.append('<%swxGlade replace %s>' % (self.nonce, which_block))
                    else:
                        out_lines.append('<%swxGlade replace %s %s>' % (self.nonce, which_class, which_block))
                else:
                    result = self.rec_event_handler.match(line)
                    if not inside_triple_quote and result:
                        which_handler = result.group('handler')
                        which_class = self.format_classname(result.group('class'))
                        self.event_handlers.setdefault(which_class, {})[which_handler] = 1
                    if self.class_name and self.is_end_of_class(line):
                        # add extra event handlers here...
                        out_lines.append('<%swxGlade event_handlers %s>' % (self.nonce, self.class_name))
                    out_lines.append(line)
                    if self.is_import_line(line):
                        # add a tag to allow extra modules
                        out_lines.append('<%swxGlade extra_modules>\n' % self.nonce)
            else:
                # ignore all the lines inside a wxGlade block
                if self.rec_block_end.match(line):
                    inside_block = False
        if not self.new_classes_inserted:
            # if we are here, the previous ``version'' of the file did not  contain any class,
            # so we must add the new_classes tag at the end of the file
            out_lines.append('<%swxGlade insert new_classes>' % self.nonce)
        # set the ``persistent'' content of the file
        self.content = out_lines #"".join(out_lines)

    def is_import_line(self, line):
        return line.startswith('import wx')

    def format_classname(self, class_name):
        """Format class name read from existing source file.
        If we're in a subpackage, we should include the package name in the class name."""
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


class PythonCodeWriter(BaseLangCodeWriter, wcodegen.PythonMixin):
    "Code writer class for writing Python code out of the designed GUI elements"

    _code_statements = {'backgroundcolour': "%(objname)s.SetBackgroundColour(%(value)s)\n",
                        'contentnotfound':  "pass",
                        'disabled':         "%(objname)s.Enable(False)\n",
                        'extraproperties':  "%(objname)s.Set%(propname_cap)s(%(value)s)\n",
                        'focused':          "%(objname)s.SetFocus()\n",
                        'foregroundcolour': "%(objname)s.SetForegroundColour(%(value)s)\n",
                        'hidden':           "%(objname)s.Hide()\n",
                        'setfont':          "%(objname)s.SetFont(%(cnfont)s(%(size)s, %(family)s, "
                                            "%(style)s, %(weight)s, %(underlined)s, %(face)s))\n",
                        'tooltip':          "%(objname)s.SetToolTipString(%(tooltip)s)\n",
                        'wxcolour':         "wxColour(%(value)s)",
                        'wxnullcolour':     "wxNullColour"}
    if compat.IS_CLASSIC:
        _code_statements['wxsystemcolour'] = "wxSystemSettings_GetColour(%(value)s)"
        _code_statements['tooltip_3'     ] = "%(objname)s.SetToolTip(wx.ToolTip(%(tooltip)s))\n"
    else:
        _code_statements['wxsystemcolour'] = "wxSystemSettings.GetColour(%(value)s)"
        _code_statements['tooltip_3'     ] = "%(objname)s.SetToolTip(%(tooltip)s)\n"

    class_separator = '.'

    indent_level_func_body = 2

    name_ctor = '__init__'

    shebang = '#!/usr/bin/env python\n'

    SourceFileContent = SourceFileContent

    tmpl_encoding = "# -*- coding: %s -*-\n#\n"
    tmpl_class_end = '\n%(comment)s end of class %(klass)s\n'
    tmpl_class_end_nomarker = '\n'
    tmpl_func_empty = '%(tab)spass\n'
    tmpl_sizeritem = '%s.Add(%s, %s, %s, %s)\n'
    tmpl_gridbagsizeritem = '%s.Add(%s, %s, %s, %s, %s)\n'
    if compat.IS_CLASSIC:
        tmpl_gridbagsizerspacer = '%s.Add((%s, %s), %s, %s, %s, %s)\n'
    else:
        tmpl_gridbagsizerspacer = '%s.Add(%s, %s, %s, %s, %s, %s)\n'
    tmpl_style = '%(tab)skwds["style"] = %(style)s\n'
    tmpl_toplevel_style = '%(tab)skwds["style"] = kwds.get("style", 0) | %(style)s\n'
    tmpl_style0 = '%(tab)skwds["style"] = 0\n'
    tmpl_toplevel_style0 = '%(tab)skwds["style"] = kwds.get("style", 0)\n'
    tmpl_appfile = """\
%(overwrite)s\
%(header_lines)s\
%(import_gettext)s\
from %(top_win_module)s import %(top_win_class)s\n\n"""

    def _get_app_template(self, app, top_win):
        'build template string for application'
        klass = app.klass
        if not self.app_name and not app.klass: return None
        ret = ['']

        if klass:
            # create application class
            if top_win and top_win.base=="wxDialog":
                # use ShowModal()/Destroy for dialogs
                show_code = ['%(tab)s%(tab)sself.%(top_win)s.ShowModal()',
                            '%(tab)s%(tab)sself.%(top_win)s.Destroy()']
            else:
                # use Show() for other toplevel windows
                show_code = ['%(tab)s%(tab)sself.%(top_win)s.Show()']

            ret += ['class %(klass)s(%(cn_wxApp)s):',
                    '%(tab)sdef OnInit(self):',
                    '%(tab)s%(tab)sself.%(top_win)s = %(top_win_class)s(None, %(cn_wxIDANY)s, "")',
                    '%(tab)s%(tab)sself.SetTopWindow(self.%(top_win)s)'
                    ] + show_code + [
                    '%(tab)s%(tab)sreturn True',
                    '']
            if self._mark_blocks:
                ret.append( '# end of class %(klass)s\n' )

        if self.app_name:
            # instantiate application class or PySimpleApp
            ret.append( 'if __name__ == "__main__":' )
    
            if self._use_gettext:
                ret.append( '%(tab)sgettext.install("%(textdomain)s") # replace with the appropriate catalog name\n' )
    
            if klass:
                ret.append( '%(tab)s%(name)s = %(klass)s(0)' )
                ret.append( '%(tab)s%(name)s.MainLoop()' )
            else:
                # use PySimpleApp
                if top_win and top_win.base=="wxDialog":
                    show_code = ['%(tab)s%(top_win)s.ShowModal()',
                                 '%(tab)s%(top_win)s.Destroy()']
                else:
                    show_code = ['%(tab)s%(top_win)s.Show()']
    
                ret += ['%(tab)s%(name)s = wx.PySimpleApp()',
                        '%(tab)s%(top_win)s = %(top_win_class)s(None, %(cn_wxIDANY)s, "")',
                        '%(tab)s%(name)s.SetTopWindow(%(top_win)s)'
                        ] + show_code + [
                        '%(tab)s%(name)s.MainLoop()']
            ret.append('')
        return '\n'.join(ret)

    def init_lang(self, app):
        if self.preview and compat.PYTHON2:
            self.header_lines.append('from __future__ import print_function\n')
        self.header_lines.append('import wx\n')

    def add_app(self, app, top_win):
        # add language specific mappings
        self.lang_mapping = { 'cn_wxApp': self.cn('wxApp'), 'cn_wxIDANY': self.cn('wxID_ANY'), 'import_gettext': ''}

        # Add gettext import statements
        if self._use_gettext:
            if self.multiple_files:
                self.lang_mapping['import_gettext'] = 'import gettext\n'
            else:
                self.dependencies['import gettext\n'] = 1

        BaseLangCodeWriter.add_app(self, app, top_win)

    def generate_code_ctor(self, code_obj, is_new, tab):
        # generate code for the class constructor, including all children
        code_lines = []
        write = code_lines.append

        builder = self.obj_builders[code_obj.base]
        mycn = getattr(builder, 'cn', self.cn)
        mycn_f = getattr(builder, 'cn_f', self.cn_f)
        fmt_klass = self.cn_class(code_obj.klass)

        # custom base classes support
        custom_base = getattr(code_obj, 'custom_base', getattr(code_obj, 'custom_base', None) )
        if self.preview or (custom_base and not custom_base.strip()):
            custom_base = None

        # generate constructor code
        if is_new:
            base = mycn(code_obj.base)
            if custom_base:
                base = ", ".join([b.strip() for b in custom_base.split(',')])
            if self.preview and code_obj.klass == base:
                klass = code_obj.klass + ('_%d' % random.randrange(10 ** 8, 10 ** 9))
            else:
                klass = code_obj.klass
            write('\nclass %s(%s):\n' % (self.get_class(fmt_klass), base))
            write(self.tabs(1) + 'def __init__(self, *args, **kwds):\n')
        elif custom_base:
            # custom base classes set, but "overwrite existing sources" not set. Issue a warning about this
            self.warning( '%s has custom base classes, but you are not overwriting '
                          'existing sources: please check that the resulting code is correct!' % code_obj.name )

        if self._mark_blocks:
            # __init__ begin tag
            write(self.tmpl_block_begin % {'class_separator': self.class_separator, 'comment_sign': self.comment_sign,
                                           'function':self.name_ctor, 'klass':fmt_klass, 'tab':tab} )

        style_p = code_obj.properties.get("style")
        if style_p:
            style = style_p.get_string_value()
            m_style = mycn_f( style )
            stmt_style = self._format_style(style, code_obj)
            if stmt_style:
                write(stmt_style % {'style': m_style, 'tab': tab} )

        # initialise custom base class
        if custom_base:
            bases = [b.strip() for b in custom_base.split(',')]
            for i, b in enumerate(bases):
                if not i:
                    write(tab + '%s.__init__(self, *args, **kwds)\n' % b)
                else:
                    write(tab + '%s.__init__(self)\n' % b)
        else:
            write(tab + '%s.__init__(self, *args, **kwds)\n' % mycn(code_obj.base))

        # set size here to avoid problems with splitter windows
        if 'size' in code_obj.properties and code_obj.properties["size"].is_active():
            write( tab + self.generate_code_size(code_obj) )

        for l in builder.get_properties_code(code_obj):
            write(tab + l)

        for l in self.classes[code_obj].init:
            write(tab + l)

        if self.classes[code_obj].final:
            write(tab + "\n")
            for l in self.classes[code_obj].final:
                write(tab + l)

        for l in builder.get_layout_code(code_obj):
            write(tab + l)

        return code_lines

    def generate_code_event_bind(self, code_obj, tab, event_handlers):
        code_lines = []
        write = code_lines.append

        if event_handlers:
            write('\n')

        for win_id, event, handler, unused in event_handlers:
            if win_id is None: continue  # bound already, the entry is just for creation of the method stub
            if win_id.startswith('#'):
                win_id = win_id[1:]
            else:
                win_id = 'id=%s' % win_id
            
            if not handler.startswith("lambda "):
                handler = 'self.%s'%handler

            if 'EVT_NAVIGATION_KEY' in event:
                tmpl = '%(tab)sself.Bind(%(event)s, %(handler)s)\n'
            else:
                tmpl = '%(tab)sself.Bind(%(event)s, %(handler)s, %(win_id)s)\n'
            details = {'tab':tab, 'event':self.cn(event), 'handler':handler, 'win_id':win_id}
            write(tmpl % details)

        return code_lines

    def generate_code_event_handler(self, code_obj, is_new, tab, prev_src, event_handlers):
        # generate default event handler, calling event.Skip()
        # Python has two indentation levels
        #  1st) for function declaration
        #  2nd) for function body
        stub = [self.tabs(1), "def %(handler)s(self, event):"]
        if self._mark_blocks: stub.append("  # wxGlade: %(klass)s.<event_handler>")
        stub.append( """\n%(tab)sprint("Event handler '%(handler)s' not implemented!")\n""" )
        stub.append( '%(tab)sevent.Skip()\n' )
        self.tmpl_func_event_stub = "".join(stub)

        event_handlers = [handler for handler in event_handlers if not handler[2].startswith("lambda ")]
        return BaseLangCodeWriter.generate_code_event_handler( self, code_obj, is_new, tab, prev_src, event_handlers )

    def generate_code_id(self, obj, id=None):
        if obj and self.preview:
            return '', '-1'  # never generate ids for preview code
        if id is None:
            id = obj.window_id
        if not id:
            if obj is not None and "stockitem" in obj.properties and obj.stockitem:
                return '', self.cn("wxID_" + obj.stockitem)
            return '', self.cn('wxID_ANY')
        id = str(id)
        tokens = id.split('=', 1)
        if len(tokens) != 2:
            return '', self.cn(tokens[0])   # we assume name is declared elsewhere
        name, val = tokens
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
            return '%s = %s\n' % (name, val), name
        return 'global %s; %s = %s\n' % (name, name, val), name

    def generate_code_size(self, obj, size=None):
        objname = self.format_generic_access(obj)
        if size is None:
            size = obj.properties["size"].get_string_value()
        use_dialog_units = (size[-1] == 'd')
        if not obj.parent_window:
            method = 'SetSize'
        else:
            method = 'SetMinSize'
        if use_dialog_units:
            if compat.IS_CLASSIC:
                return '%s.%s(%s(%s, (%s)))\n' % ( objname, method, self.cn('wxDLG_SZE'), objname, size[:-1] )
            else:
                return '%s.%s(%s(%s, %s(%s)))\n' % ( objname, method, self.cn('wxDLG_UNIT'), objname, self.cn("wxSize"), size[:-1] )
        else:
            return '%s.%s((%s))\n' % (objname, method, size)

    def _quote_str(self, s):
        """\
        Escape all unicode characters to there unicode code points in form
        of \\uxxxx. The returned string is a pure ascii string.

        Normal ascii characters like \\n or \\t won't be escaped.

        @note: wxGlade don't handles file encoding well currently. Thereby
               we escape all unicode characters.

        @note: The string 's' is encoded with L{self.app_encoding} already.

        @see: L{BaseLangCodeWriter._quote_str} for additional details
        @see: L{_recode_x80_xff()}
        """
        # convert all strings to unicode first
        if not isinstance(s, compat.unicode):
            s = s.decode(self.app_encoding)

        # check if it's pure ascii
        try:
            dummy = s.encode('ascii')
            if self._use_gettext:
                return '_("%s")' % s
            else:
                return '"%s"' % s
        except UnicodeError:
            pass

        # escape the unicode characters if given encoding requires it
        try:
            s.encode(self.app_encoding)
        except UnicodeEncodeError:
            s = s.encode('raw-unicode-escape')
            s = self._recode_x80_xff(s)
            s = s.decode("ASCII")

        # convert unicode strings to pure ascii
        # use "raw-unicode-escape" just escaped unicode characters and not default escape sequences
        if self._use_gettext:
            return '_(u"%s")' % s # XXX omit u for Python 3
        else:
            return 'u"%s"' % s # XXX omit u for Python 3

    def add_object_format_name(self, name):
        return '#self.%s' % name

    def _format_classattr(self, obj):
        res = BaseLangCodeWriter._format_classattr(self, obj)
        if not res:
            return res
        elif obj.name.startswith('self.'):
            return obj.name
        # spacer.name is "<width>, <height>" already, but wxPython expect a tuple instead of two single values
        elif obj.klass in ('spacer','sizerslot'):
            return '(%s)' % obj.name
        elif self.store_as_attr(obj):
            return 'self.%s' % obj.name
        return obj.name

    def _format_import(self, klass):
        return 'from %s import %s\n' % (klass, self.get_class(klass))

    def _get_class_filename(self, klass):
        return os.path.join( self.out_dir, klass.replace('.', os.sep) + '.py' )

    def format_generic_access(self, obj):
        if obj.IS_CLASS:
            return 'self'
        return self._format_classattr(obj)


writer = PythonCodeWriter()  # The code writer is an instance of L{PythonCodeWriter}.
language = writer.language   # Language generated by this code generator
