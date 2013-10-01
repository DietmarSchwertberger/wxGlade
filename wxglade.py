#!/usr/bin/env python
"""
Entry point of wxGlade

@copyright: 2002-2007 Alberto Griggio <agriggio@users.sourceforge.net>
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import atexit
import codecs
import locale
import logging
import os
import sys
import gettext
import optparse

import common
import config
import log

t = gettext.translation(domain="wxglade", localedir="locale", fallback=True)
t.install("wxglade")

import errors


def _fix_path(path):
    """\
    Returns an absolute version of path.

    According to the invoking dir of wxGlade (which can be different from '.'
    if it is invoked from a shell script).
    """
    if not os.path.isabs(path):
        return os.path.join(os.getcwd(), path)
    return path

def parse_command_line():
    """\
    Parse command line
    """
    # list of all available languages
    # don't load code generators at this point!!
    languages = ['C++', 'XRC', 'lisp', 'perl', 'python']

    # inject 
    optparse.OptionParser.format_description = lambda self, formatter: self.description

    parser = optparse.OptionParser(
        add_help_option=False,
        usage=_("""\
Usage: wxglade <WXG File>             start the wxGlade GUI
 or:   wxglade <Options> <WXG File>   generate code from command line
 or:   wxglade --version              show programs version number and exit
 or:   wxglade -h|--help              show this help message and exit"""),
        version=_("""\
wxGlade version %s
Copyright (C) 2007-2012 Alberto Griggio
License MIT: The MIT License
             <http://www.opensource.org/licenses/mit-license.php>""") % config.version
        )
    parser.add_option(
        '-h',
        '--help',
        dest='help',
        action='store_true',
        help=_('show this help message and exit'),
        )
    parser.add_option(
        "-g",
        "--generate-code",
        type="choice",
        choices=languages,
        metavar="LANG",
        dest="language",
        help=_("(required) output language, valid languages are: %s") % ", ".join(languages)
        )
    parser.add_option(
        "-o",
        "--output",
        metavar="PATH",
        dest="output",
        help=_("(optional) output file in single-file mode or output directory in multi-file mode"),
        )

    (options, args) = parser.parse_args()

    # print epilog because OptionParser.epilog isn't available to Python 2.3
    if options.help:
        parser.print_help()
        print _("""
Example: Generate Python code out of myapp.wxg

   wxglade -o temp -g python myapp.wxg

Report bugs to:    <wxglade-general@lists.sourceforge.net> or at
                   <http://sourceforge.net/projects/wxglade/>
wxGlade home page: <http://wxglade.sourceforge.net/>""")
        sys.exit()

    # make absolute path
    if len(args) == 1:
        options.filename = _fix_path(args[0])
    else:
        options.filename = None

    # check parameters
    #  - language
    #     - one file            -> cmdline code generation
    #     - no / > one files    -> usage
    #  - no language            -> start gui
    if options.language:
        if len(args) == 1:
            options.start_gui = False
        elif len(args) == 0:
            logging.error(_("No wxg file given!\n"))
            parser.print_help()
            sys.exit(1)
        else:
            logging.error(_("Too many wxg files given!\n"))
            parser.print_help()
            sys.exit(1)
    else:
        options.start_gui = True

    return options


def command_line_code_generation(filename, language, out_path=None):
    """\
    Starts a code generator without starting the GUI.

    @param filename: Name of wxg file to generate code from
    @type filename:  String
    @param language: Code generator language
    @type language:  String
    @param out_path: output file / output directory
    @type out_path:  String
    """
    from xml_parse import CodeWriter
    if not common.code_writers.has_key(language):
        logging.error(_('No writer for language "%s" available'), language)

    writer = common.code_writers[language]
    try:
        CodeWriter(
            writer=writer,
            input=filename,
            out_path=out_path,
            )
    except (errors.WxgOutputDirectoryNotExist,
            errors.WxgOutputDirectoryNotWritable,
            errors.WxgOutputPathIsDirectory,
            ), inst:
        logging.error(inst)
        sys.exit(1)
    except Exception:
        logging.error(
            _("An exception occurred while generating the code for the application.\n"
              "If you think this is a wxGlade bug, please report it.")
             )
        logging.exception(_('Internal Error'))
        sys.exit(1)
    sys.exit(0)


def init_stage1():
    """\
    Initialise paths for wxGlade (first stage)

    Initialisation is split because the test suite doesn't work with proper
    initialised paths.
    
    Initialise locale settings too. The determined system locale will be
    stored in L{config.encoding}.
    """
    config.version = common.set_version()
    common.init_paths()

    # initialise own logging extensions
    log.init(
        filename=config.log_file,
        encoding='utf-8',
        level='INFO',
        )
    atexit.register(log.deinit)
    
    # initialise localization
    encoding = None
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        # ignore problems by fallback to ascii
        logging.warning(
            _('Setting locale failed. Use "ascii" instead')
            )
        encoding = 'ascii'

    # try to query character encoding used in the selected locale
    if not encoding and hasattr(locale, 'nl_langinfo'):
        try:
            encoding = locale.nl_langinfo(locale.CODESET)
        except AttributeError, e:
            logging.warning(
                _('locale.nl_langinfo(locale.CODESET) failed: %s') ,
                str(e)
                )

    # try getdefaultlocale, it used environment variables
    if not encoding:
        try:
            encoding = locale.getdefaultlocale()[1]
        except ValueError:
            encoding = config.default_encoding
            
    # On Mac OS X encoding may None or '' somehow
    if not encoding:
        encoding = config.default_encoding
        logging.warning(
            _('Empty encoding. Use "%s" instead'), encoding
            )

    # check if a codec for the encoding exists
    try:
        codecs.lookup(encoding)
    except LookupError:
        logging.warning(
            _('No codec for encoding "%s" found. Use "ascii" instead'),
            encoding
            )
        encoding = 'ascii'

    # print versions 
    logging.info(
        _("Starting wxGlade version %s on Python %s"),
        config.version,
        config.py_version,
        )

    # show current locale
    loc_langcode, loc_encoding = locale.getlocale()
    logging.info(_('Current locale settings are:'))
    logging.info(_('  Language code: %s'), loc_langcode)
    logging.info(_('  Encoding: %s'), loc_encoding)
    logging.info(_('  Filesystem encoding: %s'), sys.getfilesystemencoding())

    # store determined encoding
    config.encoding = encoding.upper()

    # print used paths
    logging.info(_('Base directory:             %s'), config.wxglade_path)
    logging.info(_('Documentation directory:    %s'), config.docs_path)
    logging.info(_('Icons directory:            %s'), config.icons_path)
    logging.info(_('Build-in widgets directory: %s'), config.widgets_path)
    logging.info(_('Template directory:         %s'), config.templates_path)
    logging.info(_('Credits file:               %s'), config.credits_file)
    logging.info(_('License file:               %s'), config.license_file)
    logging.info(_('Tutorial file:              %s'), config.tutorial_file)
    logging.info(_('Home directory:             %s'), config.home_path)
    logging.info(_('Application data directory: %s'), config.appdata_path)
    logging.info(_('Configuration file:         %s'), config.rc_file)
    logging.info(_('History file:               %s'), config.history_file)

    # adapt application search path
    sys.path = [config.wxglade_path, config.widgets_path] + sys.path


def init_stage2(use_gui):
    """\
    Initialise the remaining (non-path) parts of wxGlade (second stage)

    @param use_gui: Starting wxGlade GUI
    @type use_gui:  Boolean
    """
    config.use_gui = use_gui
    if use_gui:
        # import proper wx-module using wxversion
        if not hasattr(sys, "frozen") and 'wx' not in sys.modules:
            try:
                import wxversion
                wxversion.ensureMinimal('2.6')
            except ImportError:
                logging.error(
                    _('Please install missing python module "wxversion".'))
                sys.exit(1)

        try:
            import wx
        except ImportError:
            logging.error(
                _('Please install missing python module "wxPython".')
                )
            sys.exit(1)

        # store current platform (None is default)
        config.platform = wx.Platform

        # codewrites, widgets and sizers are loaded in class main.wxGladeFrame
    else:
        # use_gui has to be set before importing config
        common.init_preferences()
        if config.preferences.log_debug_info:
            log.setDebugLevel()
        common.load_code_writers()
        common.load_widgets()
        common.load_sizers()


def run_main():
    """\
    This main procedure is started by calling either wxglade.py or
    wxglade.pyw on windows.
    """
    # check command line parameters first
    options = parse_command_line()

    # initialise wxGlade (first stage)
    init_stage1()

    # print versions 
    logging.info(_("Starting wxGlade version %s on Python %s"),
        config.version,
        config.py_version,
        )

    # initialise wxGlade (second stage)
    init_stage2(options.start_gui)

    if options.start_gui:
        # late import of main (imported wx) for using wxversion  in
        # init_stage2()
        import main
        main.main(options.filename)
    else:
        command_line_code_generation(
            filename=options.filename,
            language=options.language,
            out_path=options.output,
            )

if __name__ == "__main__":
    run_main()
