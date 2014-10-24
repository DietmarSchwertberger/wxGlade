"""\
Global variables

@copyright: 2002-2007 Alberto Griggio
@copyright: 2013-2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import ConfigParser
import logging
import os.path
import sys
import zipfile

import config


widgets = {}
"""\
Widgets dictionary: each key is the name of some EditWidget class; the mapped
value is a 'factory' function which actually builds the object. Each of these
functions accept 3 parameters: the parent of the widget, the sizer by which
such widget is controlled, and the position inside this sizer.

@type: dict
"""

widgets_from_xml = {}
"""\
Factory functions to build objects from a XML file

@type: dict
"""
widget_config = {
    'generic_styles': {

        # generic styles from wxSizer
        'wxALL': {
            'desc': _('from wxSizer'),
            'combination': 'wxLEFT|wxRIGHT|wxTOP|wxBOTTOM',
            },
        'wxTOP': {
            'desc': _('Apply the border to the top.'),
        },
        'wxBOTTOM': {
            'desc': _('Apply the border to the bottom.'),
        },
        'wxLEFT': {
            'desc': _('Apply the border to the left.'),
        },
        'wxRIGHT': {
            'desc': _('Apply the border to the right.'),
        },
        'wxALIGN_LEFT': {
            'desc': _('Align the item to the left.'),
        },
        'wxALIGN_RIGHT': {
            'desc': _('Align the item to the right.'),
        },
        'wxALIGN_CENTER': {
            'desc': _('Centre the item (horizontally).'),
            'combination': 'wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL',
        },
        'wxALIGN_CENTRE': {
            'desc': _('Centre the item (horizontally).'),
            'synonym': 'wxALIGN_CENTER',
            'rename_to': 'wxALIGN_CENTER',
            'combination': 'wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL',
        },
        'wxALIGN_TOP': {
            'desc': _('Align the item to the top.'),
        },
        'wxALIGN_BOTTOM': {
            'desc': _('Align the item to the bottom.'),
        },
        'wxALIGN_CENTER_VERTICAL': {
            'desc': _('Centre the item vertically.'),
        },
        'wxALIGN_CENTRE_VERTICAL': {
            'desc': _('Centre the item vertically.'),
            'synonym': 'wxALIGN_CENTER_VERTICAL',
            'rename_to': 'wxALIGN_CENTER_VERTICAL',
        },
        'wxALIGN_CENTER_HORIZONTAL': {
            'desc': _('Centre the item horizontally.'),
        },
        'wxALIGN_CENTRE_HORIZONTAL': {
            'desc': _('Centre the item horizontally.'),
            'synonym': 'wxALIGN_CENTER_HORIZONTAL',
            'rename_to': 'wxALIGN_CENTER_HORIZONTAL',
        },
        'wxEXPAND': {
            'desc': _('The item will be expanded to fill the space '
                      'assigned to the item.'),
        },
        'wxSHAPED': {
            'desc': _('The item will be expanded as much as possible while '
                      'also maintaining its aspect ratio.'),
        },
        'wxADJUST_MINSIZE': {
            'desc': _('This style was used in wxWidgets 2.4. Since wxWidgets '
                      '2.6 the behaviour is default. Select wxFIXED_MINSIZE '
                      'to use the old behaviour.'),
            'supported_by': ('wx2',)
        },
        'wxFIXED_MINSIZE': {
            'desc': _('Normally wxSizers will use GetAdjustedBestSize() '
                      'to determine what the minimal size of window items '
                      'should be, and will use that size to calculate the '
                      'layout. This allows layouts to adjust when an item '
                      'changes and its best size becomes different. If you '
                      'would rather have a window item stay the size it '
                      'started with then use wxFIXED_MINSIZE.'),
        },
        'wxRESERVE_SPACE_EVEN_IF_HIDDEN': {
            'desc': _("Normally wxSizers don't allocate space for hidden "
                      "windows or other items. This flag overrides this "
                      "behaviour so that sufficient space is allocated for "
                      "the window even if it isn't visible. This makes it "
                      "possible to dynamically show and hide controls "
                      "without resizing parent dialog, for example. "
                      "This function is new since wxWidgets version 2.8."),
            'supported_by': ('wx3',),
        },

        # generic styles from wxWindow
        'wxTAB_TRAVERSAL': {
            'desc': _('Use this to enable tab traversal for non-dialog '
                      'windows.'),
        },
        'wxFULL_REPAINT_ON_RESIZE': {
            'desc': _('Use this style to force a complete redraw of the '
                      'window whenever it is resized instead of redrawing '
                      'just the part of the window affected by resizing. '),
        },
        'wxNO_FULL_REPAINT_ON_RESIZE': {
            'desc': _('On Windows, this style used to disable repainting '
                      'the window completely when its size is changed. '
                      'Since this behaviour is now the default, the style '
                      'is now obsolete and no longer has an effect.'),
        },
        'wxCLIP_CHILDREN': {
            'desc': _('Use this style to eliminate flicker caused by the '
                      'background being repainted, then children being '
                      'painted over them. Windows only.'),
        },
        'wxWANTS_CHARS': {
            'desc': _("Use this to indicate that the window wants to get "
                      "all char/key events for all keys - even for keys "
                      "like TAB or ENTER which are usually used for "
                      "dialog navigation and which wouldn't be generated "
                      "without this style. If you need to use this style "
                      "in order to get the arrows or etc., but would still "
                      "like to have normal keyboard navigation take place, "
                      "you should call Navigate in response to the key "
                      "events for Tab and Shift-Tab."),
        },

        # Generic border styles
        'wxBORDER_DEFAULT': {
            'desc': _('The window class will decide the kind of border to '
                      'show, if any.'),
            'supported_by': ('wx3',)
        },
        'wxSIMPLE_BORDER': {
            'desc': _('Displays a thin border around the window. '
                      'wxSIMPLE_BORDER is the old name for this style.'),
            'rename_to': 'wxBORDER_SIMPLE',
        },
        'wxBORDER_SIMPLE': {
            'desc': _('Displays a thin border around the window. '
                      'wxSIMPLE_BORDER is the old name for this style.'),
        },
        'wxSUNKEN_BORDER': {
            'desc': _('Displays a sunken border. wxSUNKEN_BORDER is the '
                      'old name for this style.'),
            'rename_to': 'wxBORDER_SUNKEN'
        },
        'wxBORDER_SUNKEN': {
            'desc': _('Displays a sunken border. wxSUNKEN_BORDER is the '
                      'old name for this style.'),
        },
        'wxRAISED_BORDER': {
            'desc': _('Displays a raised border. wxRAISED_BORDER is the '
                      'old name for this style.'),
            'rename_to': 'wxBORDER_RAISED',
        },
        'wxBORDER_RAISED': {
            'desc': _('Displays a raised border. wxRAISED_BORDER is the '
                      'old name for this style.'),
        },
        'wxSTATIC_BORDER': {
            'desc': _('Displays a border suitable for a static control. '
                      'wxSTATIC_BORDER is the old name for this style. '
                      'Windows only.'),
            'rename_to': 'wxBORDER_STATIC',
        },
        'wxBORDER_STATIC': {
            'desc': _('Displays a border suitable for a static control. '
                      'wxSTATIC_BORDER is the old name for this style. '
                      'Windows only.'),
            'rename_to': '',
        },
        'wxBORDER_THEME': {
            'desc': _('Displays a native border suitable for a control, on '
                      'the current platform. On Windows XP or Vista, this '
                      'will be a themed border; on most other platforms a '
                      'sunken border will be used. For more information for '
                      'themed borders on Windows, please see Themed borders '
                      'on Windows.'),
        },
        'wxNO_BORDER': {
            'desc': _('Displays no border, overriding the default border '
                      'style for the window. wxNO_BORDER is the old name '
                      'for this style.'),
            'rename_to': 'wxBORDER_NONE',
        },
        'wxBORDER_NONE': {
            'desc': _('Displays no border, overriding the default border '
                      'style for the window. wxNO_BORDER is the old name '
                      'for this style.'),
        },
        'wxDOUBLE_BORDER': {
            'desc': _('Displays a double border. wxDOUBLE_BORDER is the '
                      'old name for this style. Windows and Mac only.'),
            'rename_to': 'wxBORDER_DOUBLE',
        },
        'wxBORDER_DOUBLE': {
            'desc': _('Displays a double border. wxDOUBLE_BORDER is the '
                      'old name for this style. Windows and Mac only.'),
            'obsolete': _('since wx3.0'),
        },

        # wxDialog styles
        'wxNO_3D': {
            'desc': _('Under Windows, specifies that the child '
                      'controls should not have 3D borders unless '
                      'specified in the control.'),
            'obsolete': _("This style is obsolete and doesn't do anything "
                          "any more, don't use it in any new code."),
            'supported_by': ('wx2',),
        },
        'wxCAPTION': {
            'desc': _('Puts a caption on the dialog box.'),
        },
        'wxCLOSE_BOX': {
            'desc': _('Displays a close box on the frame.'),
        },
        'wxMAXIMIZE_BOX': {
            'desc': _('Displays a maximize box on the dialog.'),
        },
        'wxMINIMIZE_BOX': {
            'desc': _('Displays a minimize box on the dialog.'),
        },
        'wxRESIZE_BORDER': {
            'desc': _('Display a thick frame around the window.'),
        },
        'wxSTAY_ON_TOP': {
            'desc': _('The dialog stays on top of all other windows.'),
        },
        'wxSYSTEM_MENU': {
            'desc': _('Display a system menu.'),
        },
    }
}

"""\
Dictionary to store widget generic widget details like tooltips, different
names, ...

Example::
    config = {
        'wxSplitterWindow' = {
            'supported_by': ('wx28', 'wx3'),
            'style_defs': {
                'wxSP_3D': {
                    'desc': _('Draws a 3D effect border and sash'),
                    'combination': 'wxSP_3DBORDER|wxSP_3DSASH',
            },
        },
        'wxHyperlinkCtrl': {
            'supported_by': ('wx28', 'wx3'),
        },
        'wxDialog': {
            'style_defs': {
                'wxNO_3D': {
                    'desc': _('Under Windows, specifies that the child '
                              'controls should not have 3D borders unless '
                              'specified in the control.'),
                    'supported_by': ('wx2',),
                },
            },
        },
        'generic_styles': {
            'wxALL': {
                'desc': _('from wxSizer'),
                'combination': 'wxLEFT|wxRIGHT|wxTOP|wxBOTTOM',
            },
        },
    }

Elements:
  - I{supported_by} - This widget is only available at the listed wx
    versions. An empty list or a non-existing entry means the widgets is
    always available.

  - I{styles} - Dictionary with style specific settings

  - I{generic_styles} - Generic item to concentrate styles that are not
    part of a specific widget e.g. sizer styles.

  - I{box_label} - Title of the widget style box

  - I{default_style} - Default style for new created widgets

  - I{style_list} - List of all styles to show within the style box

Style attributes:
  - I{'desc':} I{<description>} - Short style description

  - I{'combination':} I{<styles joined by '|'>} - The style is defined as
    a combination of different other styles.

  - I{'synonym':} I{<alternative name>} - Short notice about an alternative
    style name shown in style tooltip

  - I{'rename_to:} I{<new style name>} - The style will be renamed into the
    given style name

  - I{'supported_by':} I{(<supported version>)}- List of versions
    supporting this style

  - I{'obsolete':} I{<text>} - This style is obsolete. A short notice will
    shown in the style tooltip.

Use gettext (C{_()}) for the attributes content of "box_label", "desc" and
"obsolete".

@type: dict
"""

property_panel = None
"""\
property_panel wxPanel: container inside which Properties of the current
focused widget are displayed
"""

app_tree = None
"""\
app_tree Tree: represents the widget hierarchy of the application; the
root is the application itself
"""

adding_widget = False
"""\
If True, the user is adding a widget to some sizer
"""

adding_sizer = False
"""\
Needed to add toplevel sizers
"""

widget_to_add = None
"""\
Reference to the widget that is being added: this is a key in the
'widgets' dictionary
"""

palette = None
"""\
Reference to the main window (the one which contains the various buttons to
add the different widgets)
"""

refs = {}
"""\
Dictionary which maps the ids used in the event handlers to the
corresponding widgets: used to call the appropriate builder function
when a dropping of a widget occurs, knowing only the id of the event

@type: dict
"""

class_names = {}
"""\
Dictionary which maps the name of the classes used by wxGlade to the
correspondent classes of wxWindows

@type: dict
"""

toplevels = {}
"""\
Names of the Edit* classes that can be toplevels, i.e. widgets for which to
generate a class declaration in the code

@type: dict
"""

code_writers = {}
"""\
Dictionary of objects used to generate the code in a given language.

@note: A code writer object must implement this interface:
 - initialize(out_path, multi_files)
 - language
 - setup
 - add_widget_handler(widget_name, handler[, properties_handler])
 - add_property_handler(property_name, handler[, widget_name])
 - add_object(top_obj, sub_obj)
 - add_class(obj)
 - add_sizeritem(toplevel, sizer, obj_name, option, flag, border)
 - add_app(app_attrs, top_win_class)
 - ...

@type: dict[str, BaseLangCodeWriter]
"""


def load_code_writers():
    """\
    Fills the common.code_writers dictionary: to do so, loads the modules
    found in the 'codegen/' subdir
    """
    codegen_path = os.path.join(config.wxglade_path, 'codegen')
    sys.path.insert(0, codegen_path)
    for module in os.listdir(codegen_path):
        name, ext = os.path.splitext(module)
        # skip __init__
        if name == "__init__":
            continue
        # allow regular files only
        if not os.path.isfile(os.path.join(codegen_path, module)):
            continue
        # ignore none python files
        if ext not in ['.py', '.pyo', '.pyc']:
            continue
        # skip already imported modules
        if name in sys.modules:
            continue
        # import file and initiate code writer
        try:
            writer = __import__(name).writer
        except (AttributeError, ImportError, NameError, SyntaxError,
                ValueError):
            logging.exception(
                _('"%s" is not a valid code generator module'), module
                )
        else:
            code_writers[writer.language] = writer
            if config.use_gui:
                logging.info(
                    _('loaded code generator for %s'),
                    writer.language
                )


def load_config():
    """\
    Load widget configuration.

    @see: L{load_widgets_from_dir()}
    """
    # load the "built-in" widgets
    core_buttons = load_widgets_from_dir(
        config.widgets_path,
        'wconfig'
    )

    # load the "user" widgets
    local_buttons = load_widgets_from_dir(
        config.preferences.local_widget_path,
        'wconfig'
        )

    return


def load_widgets():
    """\
    Load core and user widgets.

    Scans the application 'widgets/' directory as well as the user widgets
    directory to find the installed widgets.

    It loads built-in widgets and "user" widgets. The build-in widgets are
    load from path in L{config.widgets_path}. The user widget path is stored
    in C{config.preferences.local_widget_path}.

    If wxGlade has been started in GUI mode, the function returns two lists
    of wxBitmapButton objects to handle them. The first contains the
    built-in widgets and the second one the user widgets.

    Both lists are empty in the batch mode.

    If widget ZIP files are found, they will be process first and the default
    Python imports will be the second.

    @see: L{load_widgets_from_dir()}
    """
    # load the "built-in" widgets
    core_buttons = load_widgets_from_dir(
        config.widgets_path,
    )

    # load the "user" widgets
    local_buttons = load_widgets_from_dir(
        config.preferences.local_widget_path,
        )

    # load (remaining) widget code generators
    # Python, C++ and XRC are often loaded via load_widgets_from_dir() above
    for path in [config.widgets_path,
                 config.preferences.local_widget_path]:
        for lang in ['perl', 'lisp']:
            if lang not in code_writers:
                continue
            codegen_name = '%s_codegen' % code_writers[lang].lang_prefix
            load_widgets_from_dir(
                path,
                submodule=codegen_name,
            )
    return core_buttons, local_buttons


def load_widgets_from_dir(widget_dir, submodule=None, logger=None):
    """\
    Load and initialise the all widgets listed in widgets.txt in the given
    directory.

    The names of the modules to import, are read from the file widgets.txt.

    If you need to import a submodule instead, just specify the name of the
    submodule and "<module name>.<submodule>" will be imported. This is
    useful to import language specific code generators.

    If wxGlade run in the GUI mode, the imported module returns a
    wxBitmapButton object. A list of such objects will be returned. In batch
    mode or if submodules are imported, an empty list will be returned.

    @param widget_dir: Directory to search for widgets
    @type widget_dir:  str

    @param submodule: Submodule to import
    @type submodule:  str

    @param logger: Logger instance to use. The default logger will be used,
                   if no logging instance is given.
    @type logger:  logging.Logger

    @rtype: list

    @see: L{_import_module()}
    @see: L{config.use_gui} - for "GUI" or "batch" mode
    """
    buttons = []

    if not logger:
        logger = logging.getLogger()

    is_codegen = bool(submodule and 'codegen' in submodule)

    # test if the "widgets.txt" file exists
    widgets_filename = os.path.join(widget_dir, 'widgets.txt')
    if not os.path.isfile(widgets_filename):
        logger.debug(_('File %s not found.'), widgets_filename)
        return []
    try:
        widgets_file = open(widgets_filename)
        module_list = widgets_file.readlines()
        widgets_file.close()
    except (IOError, OSError), inst:
        logger.warning(
            _("Can't read file %s file: %s"),
            widgets_filename,
            inst
        )
        return []

    # add widget directory to the sys.path
    if widget_dir not in sys.path:
        sys.path.append(widget_dir)

    if config.use_gui and not is_codegen:
        logger.info(_('Found widgets listing -> %s'), widgets_filename)
        logger.info(_('Loading widget modules:'))
    for module_name in module_list:
        module_name = module_name.strip()
        widget_button = None

        if not module_name or module_name.startswith('#'):
            continue
        module_name = module_name.split('#')[0].strip()

        try:
            if submodule:
                fqmn = "%s.%s" % (module_name, submodule)
            else:
                fqmn = "%s" % module_name

            module = _import_module(widget_dir, fqmn)
            if not module:
                logger.info(_('Module %s not found.'), fqmn)
                continue

            if hasattr(module, 'initialize'):
                # use individual initialisation
                widget_button = module.initialize()
            elif submodule:

                # load and store generic widget details
                if submodule == 'wconfig':
                    if hasattr(module, 'config'):
                        config_dict = getattr(module, 'config')

                        # check mandatory attributes
                        if 'wxklass' not in config_dict:
                            logger.warning(
                                _('Missing mandatory configuration item '
                                  '"wxklass". Ignoring whole configuration '
                                  'settings')
                            )
                            continue
                        widget_config[config_dict['wxklass']] = config_dict
                    else:
                        logger.debug(
                            _('Missing configuration in module %s'), fqmn
                        )
                        continue
                elif not hasattr(module, 'initialize'):
                    logger.warning(
                        _('Missing function "initialize()" in imported '
                          'module %s'),
                        fqmn
                    )
                continue
            else:
                # use generic initialisation
                # initialise Python code generator
                codegen_name = '%s.codegen' % module_name
                codegen_module = _import_module(widget_dir, codegen_name)
                codegen_module.initialize()

                # initialise GUI part
                if config.use_gui:
                    gui_name = '%s.%s' % (module_name, module_name)
                    gui_module = _import_module(widget_dir, gui_name)
                    widget_button = gui_module.initialize()
            if config.use_gui and widget_button and not submodule:
                buttons.append(widget_button)

        except (AttributeError, ImportError, NameError, SyntaxError,
                ValueError):
            logger.exception(_('ERROR loading module "%s"'), module_name)
        except:
            logger.exception(
                _('Unexpected error during import of widget module %s'),
                module_name
            )
        else:
            if config.use_gui and not is_codegen:
                logger.info('\t%s', module_name)
            else:
                logger.debug(
                    _('Widget %s imported'),
                    module_name,
                    )
    return buttons


def _import_module(widget_dir, module):
    """\
    Import a single module from a ZIP file or from the directory structure.

    The consistency of ZIP files will be checked by calling L{is_valid_zip()}.

    If widget ZIP files are found, they will be process first and the default
    Python imports will be the second.

    Example::
        >>> _import_module('./mywidgets', 'static_text')
       <module 'static_text' from 'mywidgets/static_text.zip/static_text/__init__.pyc'>

    @param widget_dir: Directory to search for widgets
    @type widget_dir:  str

    @param module: Name of the module to import
    @type module:  str

    @return: Imported module or None in case of errors
    @rtype:  Module or None

    @see: L{is_valid_zip()}
    """
    # split module name into module name and sub module name
    basemodule = module.split('.', 1)[0]

    zip_filename = os.path.join(widget_dir, '%s.zip' % basemodule)

    if os.path.exists(zip_filename):
        # check ZIP file formally
        if not is_valid_zip(zip_filename, basemodule):
            logging.warning(
                _('ZIP file %s is not a valid ZIP file. Ignoring it.'),
                zip_filename
            )
            zip_filename = None
        else:
            # add module to Python search path temporarily
            sys.path.insert(0, zip_filename)
    else:
        zip_filename = None

    # import module
    try:
        try:
            imported_module = __import__(module, {}, {},
                                         ['just_not_empty'])
            return imported_module
        except ImportError:
            logging.info(_('Module %s not found.'), module)
            return None
        except (AttributeError, NameError, SyntaxError, ValueError):
            if zip_filename:
                logging.exception(
                    _('Importing widget "%s" from ZIP file %s failed'),
                    module,
                    zip_filename
                )
            else:
                logging.exception(
                    _('Importing widget "%s" failed'),
                    module
                )
            return None
        except:
            logging.exception(
                _('Unexpected error during import of widget module %s'),
                module
            )
            return None

    finally:
        # remove zip file from Python search path
        if zip_filename and zip_filename in sys.path:
            sys.path.remove(zip_filename)


def is_valid_zip(filename, module_name):
    """\
    Check the consistency of the given ZIP files. It's a formal check as well
    as a check of the content.

    @param filename: Name of the ZIP file to check
    @type filename:  str

    @param module_name: Name of the module to import
    @type module_name:  str

    @return: True, if the ZIP is a valid widget zip file
    @rtype:  bool
    """
    if not os.path.exists(filename):
        logging.debug(_('File %s does not exists.'), filename)
        return False

    if not zipfile.is_zipfile(filename):
        logging.warning(_('ZIP file %s is not a ZIP file.'), filename )
        return False

    zfile = None
    try:
        try:
            zfile = zipfile.ZipFile(filename)
        except zipfile.BadZipfile, inst:
            logging.warning(
                _('ZIP file %s is corrupt (%s). Ignoring ZIP file.'),
                filename,
                inst
            )
            return False
        except zipfile.LargeZipFile, inst:
            logging.warning(
                _('ZIP file %s is bigger than 4GB (%s). Ignoring ZIP file.'),
                filename,
                inst
            )
            return False

        #  check content of ZIP file
        zfile = zipfile.ZipFile(filename)
        content = zfile.namelist()
        zfile.close()

        # check for codegen.py[co]
        found_file = False
        for ext in ['.py', '.pyc', '.pyo']:
            name = '%s/codegen%s' % (module_name, ext)
            if name in content:
                found_file = True
                break
        if not found_file:
            logging.warning(
                _('Missing file %s/codegen.py[co] in ZIP file %s. Ignoring '
                  'ZIP file.'),
                module_name,
                filename
            )
            return False

        # check for GUI module
        found_file = False
        for ext in ['.py', '.pyc', '.pyo']:
            name = '%s/%s%s' % (module_name, module_name, ext)
            if name in content:
                found_file = True
                break
        if not found_file:
            logging.warning(
                _('Missing file %s/%s.py[co] in ZIP file %s. Ignoring '
                  'ZIP file.'),
                module_name,
                module_name,
                filename
            )
            return False
    finally:
        if zfile:
            zfile.close()
    return True


def register(lang, klass_name, code_writer, property_name=None,
             property_handler=None, widget_name=None):
    """\
    Initialise and register widget code generator instance. The property
    handler will registered additionally.

    @param lang:             Code code_writer language
    @param klass_name:       wxWidget class name
    @param code_writer:      Code generator class
    @param property_name:    Property name
    @param property_handler: Property handler
    @param widget_name:      Widget name

    @see: L{codegen.BaseLangCodeWriter.add_widget_handler()}
    @see: L{codegen.BaseLangCodeWriter.add_property_handler()}
    """
    codegen = code_writers[lang]
    if codegen:
        codegen.add_widget_handler(klass_name, code_writer)
        if property_name and property_handler:
            codegen.add_property_handler(property_name, property_handler,
                                         widget_name)


def load_sizers():
    """\
    Load and initialise the sizer support modules.

    @return: A list of BitmapButton objects to handle sizer buttons

    @see: L{edit_sizers}
    """
    for lang in code_writers.keys():
        module_name = 'edit_sizers.%s_sizers_codegen' % \
                      code_writers[lang].lang_prefix
        try:
            codegen_module = _import_module(config.wxglade_path, module_name)
            codegen_module.initialize()
        except (AttributeError, ImportError, NameError, SyntaxError,
                ValueError):
            logging.exception(_('ERROR loading module "%s"'), module_name)
        except:
            logging.exception(
                _('Unexpected error during import of widget module %s'),
                module_name
            )

    # initialise sizer GUI elements
    import edit_sizers
    return edit_sizers.init_gui()

def init_codegen():
    """\
    Load available code generators, core and user widgets as well as sizers

    If wxGlade has been started in GUI mode, the function returns three lists
    of wxBitmapButton objects to handle them. The first contains the
    built-in widgets and the second one the user widgets and the third list
    contains the sizers.

    @return: List of core buttons, list of local buttons and list of sizer
             buttons

    @see: L{load_config()}
    @see: L{load_code_writers()}
    @see: L{load_widgets()}
    @see: L{load_sizers()}
    """
    load_config()
    load_code_writers()
    core_buttons, local_buttons = load_widgets()
    sizer_buttons = load_sizers()

    return core_buttons, local_buttons, sizer_buttons

def add_object(event):
    """\
    Adds a widget or a sizer to the current app.
    """
    global adding_widget, adding_sizer, widget_to_add
    adding_widget = True
    adding_sizer = False
    tmp = event.GetId()
    widget_to_add = refs[tmp]
    # TODO: find a better way
    if widget_to_add.find('Sizer') != -1:
        adding_sizer = True


def add_toplevel_object(event):
    """\
    Adds a toplevel widget (Frame or Dialog) to the current app.
    """
    widgets[refs[event.GetId()]](None, None, 0)
    app_tree.app.saved = False


def make_object_button(widget, icon_path, toplevel=False, tip=None):
    """\
    Creates a button for the widgets toolbar.

    Function used by the various widget modules to add a button to the
    widgets toolbar.

    @param widget: (name of) the widget the button will add to the app
    @param icon_path: path to the icon used for the button
    @param toplevel: true if the widget is a toplevel object (frame, dialog)
    @param tip: tool tip to display
    @return: The newly created wxBitmapButton
    """
    import wx
    import misc
    from tree import WidgetTree

    widget_id = wx.NewId()
    if not os.path.isabs(icon_path):
        icon_path = os.path.join(config.wxglade_path, icon_path)
    if wx.Platform == '__WXGTK__':
        style = wx.NO_BORDER
    else:
        style = wx.BU_AUTODRAW
    bmp = misc.get_xpm_bitmap(icon_path)
    tmp = wx.BitmapButton(palette, widget_id, bmp, size=(31, 31), style=style)
    if not toplevel:
        wx.EVT_BUTTON(tmp, widget_id, add_object)
    else:
        wx.EVT_BUTTON(tmp, widget_id, add_toplevel_object)
    refs[widget_id] = widget
    if not tip:
        tip = _('Add a %s') % widget.replace(_('Edit'), '')
    tmp.SetToolTip(wx.ToolTip(tip))

    WidgetTree.images[widget] = icon_path

    # add support for ESC key. We bind the handler to the button, because
    # (at least on GTK) EVT_CHAR are not generated for wxFrame objects...
    def on_char(event):
        #logging.debug('on_char')
        if event.HasModifiers() or event.GetKeyCode() != wx.WXK_ESCAPE:
            event.Skip()
            return
        global adding_widget, adding_sizer, widget_to_add
        adding_widget = False
        adding_sizer = False
        widget_to_add = None
        import misc
        if misc._currently_under_mouse is not None:
            misc._currently_under_mouse.SetCursor(wx.STANDARD_CURSOR)
        event.Skip()

    wx.EVT_CHAR(tmp, on_char)

    return tmp


def encode_from_xml(label, encoding=None):
    """\
    Returns a str which is the encoded version of the unicode label
    """
    if encoding is None:
        encoding = app_tree.app.encoding
    return label.encode(encoding, 'replace')


def encode_to_xml(label, encoding=None):
    """\
    returns a utf-8 encoded representation of label. This is equivalent to:
    str(label).decode(encoding).encode('utf-8')
    """
    if encoding is None:
        encoding = app_tree.app.encoding
    if type(label) == type(u''):
        return label.encode('utf-8')
    return str(label).decode(encoding).encode('utf-8')


def save_file(filename, content, which='wxg'):
    """\
    Save I{content} to file named I{filename} and, if user's preferences say
    so and I{filename} exists, makes a backup copy of it.

    @note: Exceptions that may occur while performing the operations are not
           handled.

    @see: L{config._backed_up}

    @param filename: Name of the file to create
    @param content:  String to store into 'filename'
    @param which:    Kind of backup: 'wxg' or 'codegen'
    """
    if which == 'wxg':
        do_backup = config.preferences.wxg_backup
    elif which == 'codegen':
        do_backup = config.preferences.codegen_backup
    else:
        raise NotImplementedError(
            'Unknown value "%s" for parameter "which"!' % which
            )
    try:
        if do_backup and \
           filename not in config._backed_up and \
           os.path.isfile(filename):
            # make a backup copy of filename
            infile = open(filename)
            outfile = open(filename + config.preferences.backup_suffix, 'w')
            outfile.write(infile.read())
            infile.close()
            outfile.close()
            config._backed_up[filename] = True
        # save content to file (but only if content has changed)
        savecontent = True
        if os.path.isfile(filename):
            oldfile = open(filename)
            savecontent = (oldfile.read() != content)
            oldfile.close()
        if savecontent:
            directory = os.path.dirname(filename)
            if directory and not os.path.isdir(directory):
                os.makedirs(directory)
            outfile = open(filename, 'w')
            outfile.write(content)
            outfile.close()
    finally:
        if 'infile' in locals():
            infile.close()
        if 'outfile' in locals():
            outfile.close()
        if 'oldfile' in locals():
            oldfile.close()


def get_name_for_autosave(filename=None):
    if filename is None:
        filename = app_tree.app.filename
    if not filename:
        path, name = config.home_path, ""
    else:
        path, name = os.path.split(filename)
    ret = os.path.join(path, "#~wxg.autosave~%s#" % name)
    return ret


def autosave_current():
    if app_tree.app.saved:
        return False         # do nothing in this case...
    try:
        outfile = open(get_name_for_autosave(), 'w')
        app_tree.write(outfile)
        outfile.close()
    except Exception:
        logging.exception(_('Internal Error'))
        return False
    return True


def remove_autosaved(filename=None):
    autosaved = get_name_for_autosave(filename)
    if os.path.exists(autosaved):
        try:
            os.unlink(autosaved)
        except OSError:
            logging.exception(_('Internal Error'))


def check_autosaved(filename):
    """\
    Returns True iff there are some auto saved data for filename
    """
    if filename is not None and filename == app_tree.app.filename:
        # this happens when reloading, no autosave-restoring in this case...
        return False
    autosaved = get_name_for_autosave(filename)
    try:
        if filename:
            orig = os.stat(filename)
            auto = os.stat(autosaved)
            return orig.st_mtime < auto.st_mtime
        else:
            return os.path.exists(autosaved)
    except OSError, e:
        if e.errno != 2:
            logging.exception(_('Internel Error'))
        return False


def restore_from_autosaved(filename):
    autosaved = get_name_for_autosave(filename)
    # when restoring, make a backup copy (if user's preferences say so...)
    if os.access(autosaved, os.R_OK):
        try:
            save_file(filename, open(autosaved).read(), 'wxg')
        except OSError:
            logging.exception(_('Internel Error'))
            return False
        return True
    return False


def init_paths():
    """\
    Set all wxGlade related paths.

    The paths will be stored in L{config}.
    """
    # use directory of the exe in case of frozen packages e.g.
    # PyInstaller or py2exe
    if hasattr(sys, 'frozen'):
        wxglade_path = os.path.dirname(sys.argv[0])
    else:
        wxglade_path = __file__
        if os.path.islink(wxglade_path):
            wxglade_path = os.path.realpath(wxglade_path)
        wxglade_path = os.path.dirname(os.path.abspath(wxglade_path))

    # set the program's paths
    config.wxglade_path = wxglade_path

    # static paths
    config.docs_path      = os.path.join(config.wxglade_path, 'docs')
    config.icons_path     = os.path.join(config.wxglade_path, 'icons')
    config.widgets_path   = os.path.join(config.wxglade_path, 'widgets')
    config.templates_path = os.path.join(config.wxglade_path, 'templates')
    config.tutorial_file  = os.path.join(config.docs_path, 'html', 'index.html')

    # set home path
    home_dir = os.path.expanduser('~')
    if home_dir not in ('~', '%USERPROFILE%'):
        config.home_path = home_dir
    elif os.name == 'nt' and home_dir == '%USERPROFILE%':
        config.home_path = os.environ.get('USERPROFILE', config.wxglade_path)
    else:
        config.home_path = config.wxglade_path

    # set path of application data
    if 'WXGLADE_CONFIG_PATH' in os.environ:
        config.appdata_path = os.path.expandvars(
            os.environ['WXGLADE_CONFIG_PATH']
            )
    elif os.name == 'nt' and 'APPDATA' in os.environ:
        config.appdata_path = os.path.expandvars(os.environ['APPDATA'])
        old_name = '%s/.wxglade' % config.appdata_path
        new_name = '%s/wxglade' % config.appdata_path
        if os.path.isdir(new_name):
            config.appdata_path = new_name
        elif os.path.isdir(old_name):
            logging.info(
                _('Rename appdata path from "%s" to "%s"'), old_name, new_name
            )
            try:
                os.rename(old_name, new_name)
                config.appdata_path = new_name
            except (IOError, OSError), e:
                # ignore rename errors and just write an info message
                logging.info(_('Renaming failed: "%s"'), e)
                logging.info(_('Using the old path "%s" instead'), old_name)
                config.appdata_path = old_name
        else:
            config.appdata_path = new_name
    else:
        config.appdata_path = os.path.join(config.home_path, '.wxglade')

    # search files credits.txt and license.txt at different locations
    # - <wxglade_path>/docs   for linux packages
    # - <wxglade_path>   at Windows or started from source directory
    # - <wxglade_path>/./../../../share/doc/wxglade/   for local installations
    # BTW: <wxglade_path> is something like /.../lib/python2.7/site-packages/wxglade
    config.credits_file = None
    config.license_file = None
    for searchdir in [
        config.wxglade_path,
        config.docs_path,
        os.path.join(config.wxglade_path, '../../../../share/doc/wxglade'),
        ]:
        searchdir = os.path.normpath(searchdir)
        credits_file = os.path.join(searchdir, 'credits.txt')
        license_file = os.path.join(searchdir, 'license.txt')
        if os.path.exists(credits_file):
            config.credits_file = credits_file
        if os.path.exists(license_file):
            config.license_file = license_file
    if not config.credits_file:
        logging.error(_('Credits file "credits.txt" not found!'))
    if not config.license_file:
        logging.error(_('License file "license.txt" not found!'))

    # complete path to rc file
    if os.name == 'nt':
        config.rc_file = os.path.join(config.appdata_path, 'wxglade.ini')
    else:
        config.rc_file = os.path.join(config.appdata_path, 'wxgladerc')

    config.history_file = os.path.join(
        config.appdata_path, 'file_history.txt'
        )

    config.log_file = os.path.join(
        config.appdata_path, 'wxglade.log'
        )


def init_preferences():
    """\
    Load / initialise preferences
    """
    if config.preferences is None:
        config.preferences = Preferences()
        config.preferences.read(config.rc_file)
        if not config.preferences.has_section('wxglade'):
            config.preferences.add_section('wxglade')


def save_preferences():
    """\
    Save current settings as well as the file history

    @see: L{config.history_file}
    @see: L{config.use_file_history}
    """
    # let the exception be raised
    path = os.path.dirname(config.rc_file)
    if not os.path.isdir(path):
        os.makedirs(path)
        # always save the file history
    if config.use_file_history:
        fh = palette.file_history
        count = fh.GetCount()
        encoding = 'utf-8'
        filenames = [encode_to_xml(fh.GetHistoryFile(i), encoding)
                     for i in
                     range(min(config.preferences.number_history, count))]
        outfile = open(config.history_file, 'w')
        print >> outfile, "# -*- coding: %s -*-" % encoding
        for filename in filenames:
            print >> outfile, filename
        outfile.close()
    if config.preferences.changed:
        outfile = open(config.rc_file, 'w')
        # let the exception be raised to signal abnormal behaviour
        config.preferences.write(outfile)
        outfile.close()


def load_history():
    """\
    Loads the file history and returns a list of paths

    @see: L{config.history_file}
    @see: L{config.use_file_history}

    @rtype: list[str]
    """
    try:
        history = open(config.history_file)
        lines = history.readlines()
        if lines and lines[0].startswith('# -*- coding:'):
            try:
                encoding = 'utf-8'
                lines = [e.decode(encoding) for e in lines[1:]]
            except Exception:
                logging.exception(_("Internal Error"))
                lines = lines[1:]
        history.close()
        if config.use_gui:
            import misc
            lines = [misc.wxstr(e, 'utf-8') for e in lines]
        return lines
    except IOError:
        # don't consider this an error
        return []


class Preferences(ConfigParser.ConfigParser):
    _has_home = os.path.expanduser('~') != '~'
    _defaults = {
        'use_menu_icons': config.use_gui and config.platform != '__WXGTK__',
        'frame_tool_win': True,
        'open_save_path': '',
        'codegen_path': '',
        'use_dialog_units': False,
        'number_history': 4,
        'show_progress': True,
        'wxg_backup': True,
        'codegen_backup': True,
        'backup_suffix': sys.platform == 'win32' and '.bak' or '~',
        'buttons_per_row': 5,
        'remember_geometry': True,
        'local_widget_path': '',
        'default_border': False,
        'default_border_size': 3,
        'show_sizer_handle': True,
        'allow_duplicate_names': False,
        'autosave': True,
        'autosave_delay': 120,  # in seconds
        'use_kde_dialogs': False,
        'show_completion': True,
        'write_timestamp': True,
        'write_generated_from': False,
        'log_debug_info': False,
        }

    def __init__(self, defaults=None):
        # set defaults of 'codegen_path', 'local_widget_path', and
        # 'open_save_path' and 'codegen_path' if the class is
        # instantiated first time, because the home_path is set later
        if config.home_path and not self._defaults['open_save_path']:
            self._defaults['open_save_path'] = config.home_path
            self._defaults['codegen_path'] = config.home_path
        if config.appdata_path and not self._defaults['local_widget_path']:
            self._defaults['local_widget_path'] = os.path.join(
                config.appdata_path, 'widgets'
                )
        self.def_vals = defaults
        if self.def_vals is None:
            self.def_vals = Preferences._defaults
        self.changed = False
        ConfigParser.ConfigParser.__init__(self)

    def __getattr__(self, attr):
        val = self.def_vals.get(attr, "")
        # UGLY!!!
        cast = type(val)
        if cast is bool:
            cast = self._cast_to_bool
        # ...but I haven't found a better way: the problem is that
        # bool('0') == True, while int('0') == False, and we want the
        # latter behaviour
        try:
            return cast(self.get('wxglade', attr))
        except (ConfigParser.NoOptionError, ValueError):
            return val

    def __iter__(self):
        def do_iter():
            for key in self.def_vals:
                yield key, self[key]

        return do_iter()

    def _cast_to_bool(self, val):
        try:
            return int(val)
        except ValueError:
            val = val.lower().strip()
            if val in ('true', 'on'):
                return 1
            elif val in ('false', 'off'):
                return 0
            else:
                raise

    def __getitem__(self, attr):
        return self.__getattr__(attr)

    def __setitem__(self, attr, val):
        self.set('wxglade', attr, str(val))
        self.changed = True

    def set_geometry(self, name, geometry):
        if geometry is not None:
            section = 'geometry_%s' % name
            if not self.has_section(section):
                self.add_section(section)
            self.set(section, 'x', geometry[0])
            self.set(section, 'y', geometry[1])
            self.set(section, 'w', geometry[2])
            self.set(section, 'h', geometry[3])

    def get_geometry(self, name):
        section = 'geometry_%s' % name
        if self.has_section(section):
            x = self.get(section, 'x')
            y = self.get(section, 'y')
            w = self.get(section, 'w')
            h = self.get(section, 'h')
            return x, y, w, h
        else:
            return None

# end of class Preferences
