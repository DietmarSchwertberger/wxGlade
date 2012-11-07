"""\
Common code used by all code generators

@copyright: 2011-2012 Carsten Grohmann <mail@carstengrohmann.de>
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import cStringIO
import os
import os.path
import random
import re
import sys
import time
import types

import common
import config
from xml_parse import XmlParsingError


class DummyPropertyHandler(object):
    """Empty handler for properties that do not need code"""

    def __init__(self):
        self.handlers = {}
        self.event_name = None
        self.curr_handler = []

    def start_elem(self, name, attrs):
        pass

    def end_elem(self, name, code_obj):
        return True

    def char_data(self, data):
        pass

# end of class DummyPropertyHandler


class EventsPropertyHandler(DummyPropertyHandler):
    """\
    Handler for event properties
    """

    def start_elem(self, name, attrs):
        if name == 'handler':
            self.event_name = attrs['event']

    def end_elem(self, name, code_obj):
        if name == 'handler':
            if self.event_name and self.curr_handler:
                self.handlers[self.event_name] = ''.join(self.curr_handler)
            self.event_name = None
            self.curr_handler = []
        elif name == 'events':
            code_obj.properties['events'] = self.handlers
            return True

    def char_data(self, data):
        data = data.strip()
        if data:
            self.curr_handler.append(data)

# end of class EventsPropertyHandler


class ExtraPropertiesPropertyHandler(DummyPropertyHandler):

    def __init__(self):
        DummyPropertyHandler.__init__(self)
        self.props = {}
        self.curr_prop = []
        self.prop_name = None

    def start_elem(self, name, attrs):
        if name == 'property':
            name = attrs['name']
            if name and name[0].islower():
                name = name[0].upper() + name[1:]
            self.prop_name = name

    def end_elem(self, name, code_obj):
        if name == 'property':
            if self.prop_name and self.curr_prop:
                self.props[self.prop_name] = ''.join(self.curr_prop)
            self.prop_name = None
            self.curr_prop = []
        elif name == 'extraproperties':
            code_obj.properties['extraproperties'] = self.props
            return True  # to remove this handler

    def char_data(self, data):
        data = data.strip()
        if data:
            self.curr_prop.append(data)

# end of class ExtraPropertiesPropertyHandler


# custom property handlers
class FontPropertyHandler(object):
    """Handler for font properties"""

    font_families = {'default': 'wxDEFAULT', 'decorative': 'wxDECORATIVE',
                     'roman': 'wxROMAN', 'swiss': 'wxSWISS',
                     'script': 'wxSCRIPT', 'modern': 'wxMODERN',
                     'teletype': 'wxTELETYPE'}
    font_styles = {'normal': 'wxNORMAL', 'slant': 'wxSLANT',
                   'italic': 'wxITALIC'}
    font_weights = {'normal': 'wxNORMAL', 'light': 'wxLIGHT',
                    'bold': 'wxBOLD'}

    def __init__(self):
        self.dicts = {'family': self.font_families, 'style': self.font_styles,
                      'weight': self.font_weights}
        self.attrs = {'size': '0', 'style': '0', 'weight': '0', 'family': '0',
                       'underlined': '0', 'face': ''}
        self.current = None
        self.curr_data = []

    def start_elem(self, name, attrs):
        self.curr_data = []
        if name != 'font' and name in self.attrs:
            self.current = name
        else:
            self.current = None

    def end_elem(self, name, code_obj):
        if name == 'font':
            code_obj.properties['font'] = self.attrs
            return True
        elif self.current is not None:
            decode = self.dicts.get(self.current)
            if decode:
                val = decode.get("".join(self.curr_data), '0')
            else:
                val = "".join(self.curr_data)
            self.attrs[self.current] = val

    def char_data(self, data):
        self.curr_data.append(data)

# end of class FontPropertyHandler


class BaseSourceFileContent(object):
    """\
    Keeps info about an existing file that has to be updated, to replace only
    the lines inside a wxGlade block, an to keep the rest of the file as it was

    @ivar classes:        Classes declared in the file
    @ivar class_name:     Name of the current processed class
    @ivar content:        Content of the source file, if it existed
                          before this session of code generation
    @ivar event_handlers: List of event handlers for each class

    @ivar name:           Name of the file
    @ivar new_classes:    New classes to add to the file (they are inserted
                          BEFORE the old ones)

    @ivar new_classes_inserted: Flag if the placeholder for new classes has
                                been inserted in source file already
    @type new_classes_inserted: Boolean

    @ivar spaces:         Indentation level for each class

    @cvar rec_block_start:   Regexp to match the begin of a wxglade block
    @cvar rec_block_end:     Regexp to match the end of a wxGlade block
    @cvar rec_class_decl:    Regexp to match class declarations
    @cvar rec_event_handler: Regexp to match event handlers
    """

    def __init__(self, name=None, content=None, classes=None, nonce=None,
                 out_dir=None, multiple_files=None):

        self.name = name
        self.content = content
        self.new_classes = []
        if classes:
            self.classes = classes
        else:
            self.classes = {}
        self.spaces = {}
        self.event_handlers = {}
        self.nonce = nonce
        self.out_dir = out_dir
        self.multiple_files = multiple_files
        if not self.content:
            self.build_untouched_content()
        self.class_name = None
        self.new_classes_inserted = False

    def build_untouched_content(self):
        """\
        Builds a string with the contents of the file that must be left as is,
        and replaces the wxGlade blocks with tags that in turn will be replaced
        by the new wxGlade blocks
        """
        self.class_name = None
        self.new_classes_inserted = False

    def format_classname(self, class_name):
        """\
        Format class name read from existing source file

        @param class_name: Class name
        @type class_name:  String

        @rtype: String

        @note: You may overwrite this function in the derivated class
        """
        return class_name

    def is_end_of_class(self, line):
        """True if the line is the marker for class end"""
        return line.strip().startswith('# end of class ')

    def is_import_line(self, line):
        """\
        True if the line imports wx

        @note: You may overwrite this function in the derivated class
        """
        return False

    def _load_file(self, filename):
        """\
        Load a file and return the content

        @note: Separated for debugging purposes

        @rtype: List of strings
        """
        fh = open(filename)
        lines = fh.readlines()
        fh.close()
        return lines

# end of class BaseSourceFileContent


class BaseWidgetHandler(object):
    """\
    Interface the various code generators for the widgets must implement
    """

    import_modules = []
    """\
    List of modules to import (eg. ['use Wx::Grid;\n'])
    """

    def __init__(self):
        """\
        Initialise instance variables
        """
        self.import_modules = []

    def get_code(self, obj):
        """\
        Handler for normal widgets (non-toplevel): returns 3 lists of strings,
        init, properties and layout, that contain the code for the
        corresponding methods of the class to generate
        """
        return [], [], []

    def get_properties_code(self, obj):
        """\
        Handler for the code of the set_properties method of toplevel objects.
        Returns a list of strings containing the code to generate
        """
        return []

    def get_init_code(self, obj):
        """\
        Handler for the code of the constructor of toplevel objects.  Returns a
        list of strings containing the code to generate.  Usually the default
        implementation is ok (i.e. there are no extra lines to add). The
        generated lines are appended at the end of the constructor
        """
        return []

    def get_layout_code(self, obj):
        """\
        Handler for the code of the do_layout method of toplevel objects.
        Returns a list of strings containing the code to generate.
        Usually the default implementation is ok (i.e. there are no
        extra lines to add)
        """
        return []

# end of class BaseWidgetHandler


class BaseCodeWriter(object):
    """\
    Dictionary of objects used to generate the code in a given language.

    A code writer object B{must} implement those interface and set those
    variables:
      - L{initialize()}
      - L{finalize()}
      - L{language}
      - L{add_app()}
      - L{add_class()}
      - L{add_object()}
      - L{add_property_handler()}
      - L{add_sizeritem()}
      - L{add_widget_handler()}
      - L{generate_code_background()}
      - L{generate_code_font()}
      - L{generate_code_foreground()}
      - L{generate_code_id()}
      - L{generate_code_size()}
      - L{_get_code_name()}
      - L{code_statements}

    A code writer object B{could} implement those interfaces and set those
    variables:
      - L{setup()}
      - L{quote_str()}
      - L{quote_path()}
      - L{cn()}
      - L{cn_f()}

    @ivar app_encoding: Encoding of the application
    @type app_encoding: String

    @ivar app_filename: File name to store the application start code within
                        multi file projects
    @type app_filename: String

    @ivar app_mapping: Language specific mapping of template variables for
                       substituting in templates
    @type app_mapping: Dictionary

    @ivar app_name: Application name
    @type app_name: String

    @ivar classes: Dictionary that maps the lines of code of a class to the
                   name of such class:
                   the lines are divided in 3 categories: '__init__',
                   '__set_properties' and '__do_layout'
    @type classes: Dictionary

    @ivar curr_tab: Current indentation level
    @type curr_tab: Integer

    @ivar init_lines: Code to instantiate child widgets (see:
                      L{ClassLines.init})
    @type init_lines: List of strings

    @ivar for_version: wx version we are generating code for (e.g. C{(2, 6)})
    @type for_version: Tuple of major and minor version number

    @ivar header_lines: Lines common to all the generated files
                        (import of wxCL, ...)
    @type header_lines: List of strings

    @ivar multiple_files: If True, generate a file for each custom class
    @type multiple_files: Boolean

    @ivar nonce: Random number used to be sure that the replaced tags in the
                 sources are the right ones (see L{BaseSourceFileContent},
                 L{add_class} and L{create_nonce})
    @type nonce: String

    @ivar obj_builders: "writers" for the various objects
    @type obj_builders: Dictionary

    @ivar obj_properties: "property writer" functions, used to set the
                          properties of a toplevel object
    @type obj_properties: Dictionary

    @ivar out_dir: If not None, it is the directory inside which the output
                   files are saved
    @type out_dir: None or string

    @ivar output_file: Output string buffer for the code
    @type output_file: None or StringIO

    @ivar output_file_name: Name of the output file
    @type output_file_name: String

    @ivar previous_source: If not None, it is an instance of
                           L{BaseSourceFileContent} that keeps info about the
                           previous version of the source to generate
    @type previous_source: None or a derivated class of L{BaseSourceFileContent}

    @ivar _app_added: True after wxApp instance has been generated
    @type _app_added: Boolean

    @ivar _current_extra_code: Set of lines for extra code to add to the
                               current file
    @type _current_extra_code: List of strings

    @ivar _current_extra_modules: Set of lines of extra modules to add to the
                                  current file
    @type _current_extra_modules: List of strings

    @ivar _overwrite: If True, overwrite any previous version of the source
                      file instead of updating only the wxGlade blocks
    @type _overwrite: Boolean

    @ivar _property_writers: Dictionary of dictionaries of property handlers
                             specific for a widget the keys are the class
                             names of the widgets (E.g.
                             _property_writers['wxRadioBox'] = {'choices',
                             choices_handler})
    @type _property_writers: Dictionary

    @ivar _use_gettext: If True, enable gettext support
    @type _use_gettext: Boolean

    @ivar _widget_extra_modules: Map of widget class names to a list of extra
                                 modules needed for the widget (e.g.
                                 C{'wxGrid': 'from wxLisp.grid import *\\n'}).
    @type _widget_extra_modules: Dictionary
    """

    code_statements = {}
    """\
    Language specific code templates for for small statements

    @type: Dictionary of strings
    @see: L{_generic_code()}
    @see: L{generate_code_extraproperties()}
    """

    comment_sign = ''
    """\
    Character(s) to start a comment (e.g. C{#} for Python and Perl or
    C{;;;} for lisp).

    @type: String
    """

    default_extensions = []
    """\
    Default extensions for generated files: a list of file extensions

    @type: List of strings
    """

    global_property_writers = {}
    """\
    Custom handlers for widget properties

    @type: Dictionary
    """

    indent_amount = 4
    """\
    An indentation level is L{indent_symbol} * L{indent_amount}

    @type: Integer
    """

    indent_symbol = ' '
    """\
    Character to use for identation

    @type: String
    """

    language = None
    """\
    Language generated by this code generator

    @type: String
    """

    language_note = ""
    """\
    Language specific notice written into every file header

    @note: Please add a newline sequence to the end of the language note.
    @type: String
    @see:  L{save_file()}
    """

    shebang = None
    """\
    Shebang line, the first line of the generated main files.

    @note: Please add a newline sequence to the end of the shebang.
    @type: String
    @see:  L{save_file()}
    """

    tmpl_encoding = None
    """\
    Template of the encoding notices

    The file encoding will be added to the output in L{save_file()}.

    @type: String
    @see: {app_encoding}
    """

    tmpl_generated_by = \
        "%(comment_sign)s %(generated_by)s\n%(comment_sign)s\n"
    """\
    Template of the "generated by ..." message

    @type: String
    @see: L{create_generated_by()}
    @see: L{save_file()}
    """

    tmpl_overwrite = \
        "%(comment_sign)s This is an automatically generated file.\n" \
        "%(comment_sign)s Manual changes will be overwritten without " \
        "warning!\n\n"
    """\
    Template of the overwrite message in all standalone app files.

    @type: String
    @see: L{add_app()}
    """

    tmpl_appfile = None
    """\
    Template of the file header for standalone files with application start
    code.
    
    A standalone file will be created if a separate file for each class is
    selected.
    
    @type: None or string
    @see: L{add_app}
    """
    
    tmpl_detailed = None
    """\
    Template for detailed application start code without gettext support
    
    @type: None or string
    @see: L{add_app}
    """
        
    tmpl_gettext_detailed = None
    """\
    Template for detailed application start code with gettext support
    
    @type: None or string
    @see: L{add_app}
    """
        
    tmpl_simple = None
    """\
    Template for simplified application start code without gettext support
    
    @type: None or string
    @see: L{add_app}
    """
        
    tmpl_gettext_simple = None
    """\
    Template for simplified application start code with gettext support
    
    @type: None or string
    @see: L{add_app}
    """
    
    _quote_str_pattern = re.compile(r'\\[natbv"]?')

    _show_warnings = True
    """\
    Enable or disable printing of warning messages

    @type: Boolean
    @see: L{self.warning()}
    """

    class ClassLines(object):
        """\
        Stores the lines of source code for a custom class

        @ivar dependencies:      Names of the modules this class depends on
        @ivar event_handlers:    Lines to bind events
        @ivar extra_code:        Extra code to output before this class
        @ivar done:              If True, the code for this class has already
                                 been generated
        @ivar init:              Lines of code to insert in the __init__ method
                                 (for children widgets)
        @ivar layout:            Lines to insert in the __do_layout method
        @ivar parents_init:      Lines of code to insert in the __init__ for
                                 container widgets (panels, splitters, ...)
        @ivar props:             Lines to insert in the __set_properties method
        @ivar sizers_init :      Lines related to sizer objects declarations
        """
        def __init__(self):
            self.child_order = []
            self.dependencies = {}
            self.deps = []
            self.done = False
            self.event_handlers = []
            self.extra_code = []
            self.init = []
            self.init_lines = {}
            self.layout = []
            self.parents_init = []
            self.props = []
            self.sizers_init = []

    # end of class ClassLines

    DummyPropertyHandler = DummyPropertyHandler
    EventsPropertyHandler = EventsPropertyHandler
    ExtraPropertiesPropertyHandler = ExtraPropertiesPropertyHandler
    FontPropertyHandler = FontPropertyHandler

    def __init__(self):
        """\
        Initialise only instance variables using there defaults.
        """
        self.app_encoding = 'ISO-8859-1'
        self.app_filename = None
        self.app_mapping = {}
        self.app_name = None
        self.classes = {}
        self.curr_tab = 0
        self.for_version = (2, 6)
        self.header_lines = []
        self.init_lines = []
        self.multiple_files = False
        self.nonce = None
        self.obj_builders = {}
        self.obj_properties = {}
        self.out_dir = None
        self.output_file_name = None
        self.output_file = None
        self.previous_source = None
        self._app_added = False
        self._current_extra_code = []
        self._current_extra_modules = {}
        self._overwrite = False
        self._property_writers = {}
        self._use_gettext = False
        self._widget_extra_modules = {}

    def initialize(self, app_attrs):
        """\
        Code generator initialization function.
        """
        # this is to be more sure to replace the right tags
        self.nonce = self.create_nonce()

        self.multiple_files = app_attrs['option']

        # application name
        self.app_name = app_attrs.get('name')
        if not self.app_name:
            self.app_name = 'app'
        self.app_filename = '%s.%s' % (self.app_name, self.default_extensions[0])

        # file encoding
        try:
            self.app_encoding = app_attrs['encoding'].upper()
            # wx doesn't like latin-1
            if self.app_encoding == 'latin-1':
                self.app_encoding = 'ISO-8859-1'
        except (KeyError, ValueError):
            # set back to default
            self.app_encoding = 'ISO-8859-1'

        # Inentation level based on the project options
        try:
            self.indent_symbol = app_attrs['indent_symbol']
            if self.indent_symbol == 'tab':
                self.indent_symbol = '\t'
            elif self.indent_symbol == 'space':
                self.indent_symbol = ' '
            else:
                self.indent_symbol = ' '
        except (KeyError, ValueError):
            self.indent_symbol = ' '

        try:
            self.indent_amount = int(app_attrs['indent_amount'])
        except (KeyError, ValueError):
            self.indent_amount = 4

        try:
            self._use_gettext = int(app_attrs['use_gettext'])
        except (KeyError, ValueError):
            self._use_gettext = False

        try:
            self._overwrite = int(app_attrs['overwrite'])
        except (KeyError, ValueError):
            self._overwrite = False

        try:
            self.for_version = tuple([int(t) for t in
                                 app_attrs['for_version'].split('.')[:2]])
        except (KeyError, ValueError):
            if common.app_tree is not None:
                self.for_version = common.app_tree.app.for_version

        self.classes = {}
        self._current_extra_modules = {}
        self.header_lines = []

        # extra lines to generate (see the 'extracode' property of top-level
        # widgets)
        self._current_extra_code = []

    def finalize(self):
        """\
        Code generator finalization function.
        """
        if self.previous_source:
            # insert all the new custom classes inside the old file
            tag = '<%swxGlade insert new_classes>' % self.nonce
            if self.previous_source.new_classes:
                code = "".join(self.previous_source.new_classes)
            else:
                code = ""
            self.previous_source.content = self.previous_source.content.replace(tag, code)
            tag = '<%swxGlade extra_modules>\n' % self.nonce
            code = "".join(self._current_extra_modules.keys())
            self.previous_source.content = self.previous_source.content.replace(tag, code)

            # module dependecies of all classes
            tag = '<%swxGlade replace dependencies>' % self.nonce
            dep_list = self.dependencies.keys()
            dep_list.sort()
            code = self._tagcontent('dependencies', dep_list)
            self.previous_source.content = \
                self.previous_source.content.replace(tag, code)

            # extra code (see the 'extracode' property of top-level widgets)
            tag = '<%swxGlade replace extracode>' % self.nonce
            code = self._tagcontent(
                'extracode',
                self._current_extra_code
                )
            self.previous_source.content = \
                self.previous_source.content.replace(tag, code)

            # now remove all the remaining <123415wxGlade ...> tags from the
            # source: this may happen if we're not generating multiple files,
            # and one of the container class names is changed
            self.previous_source.content = self._content_notfound(
                self.previous_source.content,
                self.previous_source.spaces.get(tag[1], 0)
                )

            tags = re.findall(
                '<%swxGlade event_handlers \w+>' % self.nonce,
                self.previous_source.content
                )
            for tag in tags:
                self.previous_source.content = self.previous_source.content.replace(tag, "")

            # write the new file contents to disk
            self.save_file(
                self.previous_source.name,
                self.previous_source.content,
                content_only=True
                )

        elif not self.multiple_files:
            em = "".join(self._current_extra_modules.keys())
            content = self.output_file.getvalue().replace(
                '<%swxGlade extra_modules>\n' % self.nonce, em)

            # module dependecies of all classes
            tag = '<%swxGlade replace dependencies>' % self.nonce
            dep_list = self.dependencies.keys()
            dep_list.sort()
            code = self._tagcontent('dependencies', dep_list)
            content = content.replace(tag, code)

            # extra code (see the 'extracode' property of top-level widgets)
            tag = '<%swxGlade replace extracode>' % self.nonce
            code = self._tagcontent('extracode', self._current_extra_code)
            content = content.replace(tag, code)

            self.output_file.close()
            self.save_file(self.output_file_name, content, self._app_added)
            del self.output_file

    def add_app(self, app_attrs, top_win_class):
        """\
        Generates the code for a wxApp instance.
        If the file to write into already exists, this function does nothing.
        
        If gettext support is requested and there is not template with
        gettext support but there is a template without gettext support,
        template without gettext support will be used.
        
        This fallback mechanism works bidirectional.

        @see: L{tmpl_appfile}
        @see: L{tmpl_detailed}
        @see: L{tmpl_gettext_detailed}
        @see: L{tmpl_simple}
        @see: L{tmpl_gettext_simple}
        """
        self._app_added = True

        if not self.multiple_files:
            prev_src = self.previous_source
        else:
            # overwrite apps file always
            prev_src = None

        # do nothing if the file exists
        if prev_src:
            return

        klass = app_attrs.get('class')
        top_win = app_attrs.get('top_window')

        # do nothing if there is no top window
        if not top_win:
            return

        # check for templates for detailed startup code
        if klass and self._use_gettext:
            if self.tmpl_gettext_detailed:
                tmpl = self.tmpl_gettext_detailed
            elif self.tmpl_detailed:
                tmpl = self.tmpl_detailed
            else:
                self.warning(
                    _("Skip generating detailed startup code "
                      "because no suitable template found.")
                    )
                return

        elif klass and not self._use_gettext:
            if self.tmpl_detailed:
                tmpl = self.tmpl_detailed
            elif self.tmpl_gettext_detailed:
                tmpl = self.tmpl_gettext_detailed
            else:
                self.warning(
                    _("Skip generating detailed startup code "
                      "because no suitable template found.")
                    )
                return

        # check for templates for simple startup code
        elif not klass and self._use_gettext:
            if self.tmpl_gettext_simple:
                tmpl = self.tmpl_gettext_simple
            elif self.tmpl_simple:
                tmpl = self.tmpl_simple
            else:
                self.warning(
                    _("Skip generating simple startup code "
                      "because no suitable template found.")
                    )
                return
        elif not klass and not self._use_gettext:
            if self.tmpl_simple:
                tmpl = self.tmpl_simple
            elif self.tmpl_gettext_simple:
                tmpl = self.tmpl_gettext_simple
            else:
                self.warning(
                    _("Skip generating simple startup code "
                      "because no suitable template found.")
                    )
                return
        else:
            self.warning(
                _('No application code template for klass "%(klass)s" '
                  'and gettext "%(gettext)s" found!' % \
                        (klass, self._use_gettext)
                  ))
            return

        # map to substitude template variables
        mapping = {
            'cn_wxApp': self.cn('wxApp'),
            'cn_wxIDANY': self.cn('wxID_ANY'),
            'cn_wxInitAll': self.cn('wxInitAllImageHandlers'),
            'cn_wxPySimpleApp': self.cn('wxPySimpleApp'),
            'comment_sign': self.comment_sign,
            'header_lines': ''.join(self.header_lines),
            'klass': klass,
            'name': self.app_name,
            'overwrite': self.tmpl_overwrite % {'comment_sign': self.comment_sign},
            'tab': self.tabs(1),
            'top_win_class': top_win_class,
            'top_win': top_win,
            }
            
        # extend default mapping with language specific mapping
        if self.app_mapping:
            mapping.update(self.app_mapping)

        code = tmpl % (mapping)

        if self.multiple_files:
            filename = os.path.join(self.out_dir, self.app_filename)
            code = "%s%s" % (
                self.tmpl_appfile % (mapping),
                code,
                )
            # write the wxApp code
            self.save_file(filename, code, True)
        else:
            self.output_file.write(code)

    def add_class(self, code_obj):
        """\
        Add class behaves very differently for XRC output than for other
        lanaguages (i.e. pyhton): since custom classes are not supported in
        XRC, this has effect only for true toplevel widgets, i.e. frames and
        dialogs. For other kinds of widgets, this is equivalent to add_object
        """
        raise NotImplementedError

    def add_object(self, top_obj, sub_obj):
        """\
        Adds the code to build 'sub_obj' to the class body of 'top_obj'.
        """
        raise NotImplementedError

    def add_property_handler(self, property_name, handler, widget_name=None):
        """\
        Sets a function to parse a portion of XML to get the value of the
        property property_name. If widget_name is not None, the function is
        called only if the property in inside a widget whose class is
        widget_name.
        """
        if not widget_name:
            self.global_property_writers[property_name] = handler
        else:
            try:
                self._property_writers[widget_name][property_name] = handler
            except KeyError:
                self._property_writers[widget_name] = {property_name: handler}

    def add_sizeritem(self, toplevel, sizer, obj, option, flag, border):
        """\
        Writes the code to add the object 'obj' to the sizer 'sizer' in the
        'toplevel' object.
        """
        raise NotImplementedError

    def add_widget_handler(self, widget_name, handler, *args, **kwds):
        self.obj_builders[widget_name] = handler

    def create_generated_by(self):
        """\
        Create I{generated by wxGlade} string without leading comment
        characters and without tailing new lines

        @rtype:  String
        """
        if config.preferences.write_timestamp:
            msg = 'generated by wxGlade %s on %s%s' % (
                common.version,
                time.asctime(),
                common.generated_from(),
                )
        else:
            msg = 'generated by wxGlade %s%s' % (
                common.version,
                common.generated_from(),
                )
        return msg

    def create_nonce(self):
        """\
        Create a random number used to be sure that the replaced tags in the
        sources are the right ones (see SourceFileContent and add_class)

        @return: A random nonce
        @rtype:  String
        """
        nonce = '%s%s' % (str(time.time()).replace('.', ''),
                          random.randrange(10 ** 6, 10 ** 7))
        return nonce

    def get_property_handler(self, property_name, widget_name):
        """\
        Return the widget specific property handler

        @see: L{add_property_handler}
        @see: L{global_property_writers}
        @see: L{_property_writers}
        """
        try:
            cls = self._property_writers[widget_name][property_name]
        except KeyError:
            cls = self.global_property_writers.get(property_name, None)
        if cls:
            return cls()
        return None

    def generate_code_background(self, obj):
        """\
        Returns the code fragment that sets the background colour of
        the given object.

        @rtype: String

        @see: L{_get_colour()}
        """
        # check if there is an code template for this property
        if 'backgroundcolour' not in self.code_statements:
            msg = " %s WARNING: no code template for property '%s' " \
                  "registered!\n" % (self.comment_sign, 'backgroundcolour')
            self.warning(msg)
            return msg

        objname = self._get_code_name(obj)
        color = self._get_colour(obj.properties['background'])
        tmpl = self.code_statements['backgroundcolour']
        stmt = tmpl % {
            'objname': objname,
            'value':   color,
            }
        return stmt

    def generate_code_disabled(self, obj):
        """\
        Returns the code fragment that disables the given object.

        @rtype: String
        """
        return self._generic_code(obj, 'disabled')

    def generate_code_extraproperties(self, obj):
        """\
        Returns a code fragment that set extra properties for the given object

        @rtype: List of strings
        """
        if not 'extraproperties' in self.code_statements:
            return []
        objname = self._get_code_name(obj)
        prop = obj.properties['extraproperties']
        ret = []
        for name in sorted(prop):
            tmpl = self.code_statements['extraproperties']
            stmt = tmpl % {
                'klass':    obj.klass,
                'objname':  objname,
                'propname': name,
                'value':    prop[name],
                }
            ret.append(stmt)
        return ret

    def generate_code_focused(self, obj):
        """\
        Returns the code fragment that get the focus to the given object.

        @rtype: String
        """
        return self._generic_code(obj, 'focused')

    def generate_code_font(self, obj):
        """\
        Returns the code fragment that sets the font of the given object.

        @rtype: String
        """
        stmt = None

        # check if there is an code template for this property
        if 'setfont' not in self.code_statements:
            msg = " %s WARNING: no code template for property '%s' " \
                  "registered!\n" % (self.comment_sign, 'setfont')
            self.warning(msg)
            return msg

        objname = self._get_code_name(obj)
        cnfont = self.cn('wxFont')
        font = obj.properties['font']
        family = self.cn(font['family'])
        face = '"%s"' % font['face'].replace('"', r'\"')
        size = font['size']
        style = self.cn(font['style'])
        underlined = font['underlined']
        weight = self.cn(font['weight'])

        tmpl = self.code_statements['setfont']
        stmt = tmpl % {
            'objname':    objname,
            'cnfont':     cnfont,
            'face':       face,
            'family':     family,
            'size':       size,
            'style':      style,
            'underlined': underlined,
            'weight':     weight,
            }
        return stmt

    def generate_code_foreground(self, obj):
        """\
        Returns the code fragment that sets the foreground colour of
        the given object.

        @rtype: String

        @see: L{_get_colour()}
        """
        # check if there is an code template for this property
        if 'foregroundcolour' not in self.code_statements:
            msg = " %s WARNING: no code template for property '%s' " \
                  "registered!\n" % (self.comment_sign, 'foregroundcolour')
            self.warning(msg)
            return msg

        objname = self._get_code_name(obj)
        color = self._get_colour(obj.properties['foreground'])
        tmpl = self.code_statements['foregroundcolour']
        stmt = tmpl % {
            'objname': objname,
            'value':   color,
            }
        return stmt

    def generate_code_hidden(self, obj):
        """\
        Returns the code fragment that hides the given object.

        @rtype: String
        """
        return self._generic_code(obj, 'hidden')

    def generate_code_id(self, obj, id=None):
        """\
        Generate the code for the widget ID.

        The parameter C{id} is evaluated first. An empty string for
        C{id} returns C{'', 'wxID_ANY'}.

        Returns a tuple of two string. The two strings are:
         1. A line to the declare the variable. It's empty if the object id
            is a constant
         2. The value of the id

        @param obj: An instance of L{xml_parse.CodeObject}
        @param id:  Widget ID definition as String.

        @rtype: Tuple of two strings
        """
        raise NotImplementedError

    def generate_code_size(self, obj):
        """\
        Returns the code fragment that sets the size of the given object.

        @rtype: String
        """
        raise NotImplementedError

    def generate_code_tooltip(self, obj):
        """\
        Returns the code fragment that sets the tooltip of the given object.

        @rtype: String
        """
        return self._generic_code(obj, 'tooltip')

    def generate_common_properties(self, widget):
        """\
        generates the code for various properties common to all widgets
        (background and foreground colors, font, ...)

        @return: a list of strings containing the generated code
        @rtype: List of strings

        @see: L{generate_code_background()}
        @see: L{generate_code_disabled()}
        @see: L{generate_code_extraproperties()}
        @see: L{generate_code_focused()}
        @see: L{generate_code_font()}
        @see: L{generate_code_foreground()}
        @see: L{generate_code_hidden()}
        @see: L{generate_code_size()}
        @see: L{generate_code_tooltip()}
        """
        prop = widget.properties
        out = []
        if prop.get('size', '').strip():
            out.append(self.generate_code_size(widget))
        if prop.get('background'):
            out.append(self.generate_code_background(widget))
        if prop.get('foreground'):
            out.append(self.generate_code_foreground(widget))
        if prop.get('font'):
            out.append(self.generate_code_font(widget))
        # tooltip
        if prop.get('tooltip'):
            out.append(self.generate_code_tooltip(widget))
        # trivial boolean properties
        if prop.get('disabled'):
            out.append(self.generate_code_disabled(widget))
        if prop.get('focused'):
            out.append(self.generate_code_focused(widget))
        if prop.get('hidden'):
            out.append(self.generate_code_hidden(widget))
        if prop.get('extraproperties') and not widget.preview:
            out.extend(self.generate_code_extraproperties(widget))
        return out

    def cn(self, name):
        """\
        Return the class name properly formatted for the selected name space.

        @see: L{cn_f()}
        """
        return name

    def cn_f(self, flags):
        """\
        Return the flags properly formatted for the selected name space.
        """
        return flags

    def quote_str(self, s, translate=True, escape_chars=True):
        """\
        returns a quoted version of 's', suitable to insert in a python source
        file as a string object. Takes care also of gettext support

        @param s:             String to quote
        @param translate:     Encapsulate string into a gettext statement,
                              if L{_use_gettext} is True
        @param escape_chars:  Escape special meaning characters like backspace
                              or quotes

        @rtype: String
        """
        raise NotImplementedError

    def quote_path(self, s):
        """\
        escapes all quotation marks and backslashes,
        thus making a path suitable to insert in a list source file

        @note: You may overwrite this function in the derivated class
        @rtype: String
        """  # " ALB: to avoid emacs going insane with colorization..
        s = s.replace('\\', '\\\\')
        s = s.replace('"', r'\"')
        s = s.replace('$', r'\$')  # sigh
        s = s.replace('@', r'\@')
        return '"%s"' % s

    def save_file(self, filename, content, mainfile=False, content_only=False):
        """\
        Store the content in a file.

        A L{shebang} is added in top of all mainfiles. The permissions
        of mainfiles will be set to C{0755} too.

        L{common.save_file()} is used for storing content.

        @param filename:     File name
        @type filename:      String
        @param content:      File content
        @type content:       String
        @param mainfile:     Mainfiles gets a L{shebang} and C{0755} permissions.
        @type mainfile:      Boolean
        @param content_only: Write only content to the file
        @type content_only:  Boolean

        @see: L{common.save_file()}
        """
        # create an temporary StringIO file to add header
        tmp = ""

        # write additional information to file header
        if not content_only:
            # add shebang to main file
            if self.shebang and mainfile or self.language == 'C++':
                tmp += self.shebang
                tmp += "%s\n" % self.comment_sign

            # add file encoding notice
            if self.tmpl_encoding and self.app_encoding:
                tmp += self.tmpl_encoding % self.app_encoding
                tmp += "%s\n" % self.comment_sign

            # add created by notice
            if self.tmpl_generated_by:
                tmp += self.tmpl_generated_by % {
                    'comment_sign': self.comment_sign,
                    'generated_by': self.create_generated_by(),
                    }

            # add language specific note
            if self.language_note:
                tmp += "%s" % self.language_note
                tmp += "%s\n" % self.comment_sign

            # add a empty line
            tmp += "\n"

        # add original file content
        tmp += content

        try:
            common.save_file(filename, tmp, 'codegen')
        except IOError, e:
            raise XmlParsingError(str(e))
        except:
            import traceback
            traceback.print_exc()
        if mainfile and sys.platform in ['linux2', 'darwin']:
            try:
                # make the file executable
                os.chmod(filename, 0755)
            except OSError, e:
                # this isn't necessarily a bad errror
                self.warning(
                    _('Changing permission of main file "%s" failed: %s') % (
                        filename, str(e)
                        )
                    )

    def test_attribute(self, obj):
        """\
        Returns True if 'obj' should be added as an attribute of its parent's
        class, False if it should be created as a local variable of
        C{__do_layout}.
        To do so, tests for the presence of the special property 'attribute'

        @rtype: Boolean
        """
        try:
            return int(obj.properties['attribute'])
        except (KeyError, ValueError):
            return True  # this is the default

    def tabs(self, number):
        """\
        Return a proper formatted string for indenting lines

        @rtype: String
        """
        return self.indent_symbol * self.indent_amount * number

    def warning(self, msg):
        """\
        Show a warning message

        @param msg: Warning message
        @type msg:  String
        @see: L{common.message}
        """
        if self._show_warnings:
            common.message("WARNING", msg)

    def _content_notfound(self, source, indent=""):
        """\
        Remove all the remaining <123415wxGlade ...> tags from the source
        and add a warning instead.

        This may happen if we're not generating multiple files, and one of
        the container class names is changed.

        @param source: Source content with tags to replace
        @type source:  String

        @param indent: Indentation of the warning message
        @type indent:  String

        @return: Changed content
        @rtype:  String
        """
        tags = re.findall(
            '(<%swxGlade replace ([a-zA-Z_]\w*) +[.\w]+>)' % self.nonce,
            source
            )
        for tag in tags:
            comment = '%(indent)s%(comment_sign)s Content of this block not found. ' \
                      'Did you rename this class?\n'
            if 'contentnotfound' in self.code_statements:
                comment += '%(indent)s%(command)s\n'
                command = self.code_statements['contentnotfound']
            else:
                command = ""
            comment = comment % {
                'command':      command,
                'comment_sign': self.comment_sign,
                'indent':       indent,
                }
            source = source.replace(tag[0], comment)
        return source

    def _do_replace(self, match):
        """\
        Escape double backslashed in first RE match group
        """
        if match.group(0) == '\\':
            return '\\\\'
        else:
            return match.group(0)

    def _file_exists(self, filename):
        """\
        Check if the file exists

        @note: Separated for debugging purposes

        @rtype: Boolean
        """
        return os.path.isfile(filename)

    def _generic_code(self, obj, prop_name):
        """\
        Create a code statement for calling a method e.g. to hide a widget.

        @param obj:       Instance of L{xml_parse.CodeObject}
        @param prop_name: Name of the property to set
        @type prop_name:  String

        @return: Code statement as string or None

        @see: L{code_statements}
        """
        stmt = None
        value = None

        # check if there is an code template for this prop_name
        if prop_name not in self.code_statements:
            msg = " %s WARNING: no code template for property '%s' " \
                  "registered!\n" % (self.comment_sign, prop_name)
            self.warning(msg)
            return msg

        # collect detail informaton
        if prop_name in ['disabled', 'focused', 'hidden']:
            try:
                value = int(obj.properties[prop_name])
            except (KeyError, ValueError):
                # nothing to do
                return None
        elif prop_name == 'tooltip':
            value = self.quote_str(obj.properties['tooltip'])
        else:
            raise AssertionError("Unknown property name: %s" % prop_name)

        objname = self._get_code_name(obj)
        tmpl = self.code_statements[prop_name]
        stmt = tmpl % {
            'objname': objname,
            'tooltip': value,
            }
        return stmt

    def _get_code_name(self, obj):
        """\
        Returns the language specific name of the variable e.g. C{self}
        or C{$self}.

        @rtype: String
        """
        raise NotImplementedError

    def _get_colour(self, colourvalue):
        """\
        Returns the language specific colour statement
        """
        # check if there is an code template for this properties
        if 'wxcolour' not in self.code_statements:
            msg = " %s WARNING: no code template for property '%s' " \
                  "registered!\n" % (self.comment_sign, 'wxcolour')
            self.warning(msg)
            return msg
        if 'wxsystemcolour' not in self.code_statements:
            msg = " %s WARNING: no code template for property '%s' " \
                  "registered!\n" % (self.comment_sign, 'wxsystemcolour')
            self.warning(msg)
            return msg
        try:
            value = self._string_to_colour(colourvalue)
            func = self.cn(self.code_statements['wxcolour'])
        except (IndexError, ValueError):  # the color is from system settings
            value = self.cn(colourvalue)
            func = self.cn(self.code_statements['wxsystemcolour'])
        stmt = func % {
            'value': value,
            }
        return stmt

    def _setup(self):
        """\
        Load language specific code generators
        """
        # scan widgets.txt for widgets, load language specific code generators
        widgets_file = os.path.join(common.widgets_path, 'widgets.txt')
        if not os.path.isfile(widgets_file):
            self.warning("widgets file (%s) doesn't exist" % widgets_file)
            return
        sys.path.append(common.widgets_path)
        modules = open(widgets_file)
        for line in modules:
            module_name = line.strip()
            if not module_name or module_name.startswith('#'):
                continue
            module_name = module_name.split('#')[0].strip()
            try:
                fqmn = "%s.%s_codegen" % (module_name, self.language)
                m = __import__(
                    fqmn, {}, {}, ['initialize'])
                m.initialize()
            except (ImportError, AttributeError):
                pass
##                 print 'ERROR loading "%s"' % module_name
##                 import traceback;
##                 traceback.print_exc()
##             else:
##                 print 'initialized %s generator for %s' % (self.language, module_name)
        modules.close()

    def _string_to_colour(self, s):
        """\
        Convert a colour values out of a hex string to comma separated
        decimal values.

        B{Example:}

            >>> self._string_to_colour('#FFFFFF')
            '255, 255, 255'
            >>> self._string_to_colour('#ABCDEF')
            '171, 205, 239'

        @rtype:  String
        """
        return '%d, %d, %d' % (
            int(s[1:3], 16),
            int(s[3:5], 16),
            int(s[5:], 16)
            )

    def _tagcontent(self, tag, content, newline=False):
        """\
        Content embeded between C{begin wxGlade} and C{end wxGlade} sequence.

        @return: Embedded content
        @rtype:  String

        @param tag: Tag is used in C{begin wxGlade} statement for
                    separate different blocks
        @type tag:  String

        @param content: Content to enter
        @type content:  String or List of strings

        @param newline: Add a tailing empty line
        @type newline:  Boolean
        """
        code_list = []
        code_list.append(
            '%s begin wxGlade: %s' % (self.comment_sign, tag)
            )
        if type(content) == types.ListType:
            for entry in content:
                code_list.append(entry.rstrip())
        elif type(content) in types.StringTypes:
            # don't append empty content
            _content = content.rstrip()
            if _content:
                code_list.append(_content)
        else:
            raise AssertionError('Unknown content type: %s' % type(content))
        code_list.append(
            '%s end wxGlade' % self.comment_sign
            )
        # newline for "end wxGlade" line
        code_list.append('')
        if newline:
            code_list.append('')
        return "\n".join(code_list)

# end of class BaseCodeWriter
