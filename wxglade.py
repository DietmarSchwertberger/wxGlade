#!/usr/bin/env python
# wxglade.py: entry point of wxGlade
#
# Copyright (c) 2002-2007 Alberto Griggio <agriggio@users.sourceforge.net>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

import os
import sys
import gettext
import getopt
import common

t = gettext.translation(domain="wxglade", localedir="locale", fallback=True)
t.install("wxglade")

def _fix_path(path):
    """\
    Returns an absolute version of path, accroding to the invoking dir of
    wxglade (which can be different from '.' if it is invoked from a shell
    script)
    """
    if not os.path.isabs(path):
        return os.path.join(os.getcwd(), path)
        #getenv('WXGLADE_INVOKING_DIR', '.'), path)
    return path


def parse_command_line():
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "g:o:",
            ['generate-code=', 'output=']
            )
    except getopt.GetoptError:
        #import traceback; traceback.print_exc()
        usage()
    return options, args


def command_line_code_generation(options, args):
    """\
    starts a code generator without starting the GUI.
    """
    if not options:
        usage()
    if not options[0]:
        usage() # a language for code generation must be provided
    if len(args) != 1:
        usage() # an input file name must be provided

    common.use_gui = False # don't import wxPython.wx
    # use_gui has to be set before importing config
    import config
    config.init_preferences()
    common.load_code_writers()
    common.load_widgets()
    common.load_sizers()
    try:
        from xml_parse import CodeWriter
        out_path = None
        language = ''
        for option, arg in options:
            if option == '-g' or option == '--generate-code':
                language = arg
            elif option == '-o' or option == '--output':
                out_path = _fix_path(arg)
        writer = common.code_writers[language]
        CodeWriter(writer, _fix_path(args[0]), out_path=out_path)
    except KeyError:
        print >> sys.stderr, \
              _('Error: no writer for language "%s" available') % language
        sys.exit(1)
    except Exception, e:
        print >> sys.stderr, _("Error: %s") % e
        import traceback; traceback.print_exc()
        sys.exit(1)
    sys.exit(0)


def usage():
    """\
    Prints a help message about the usage of wxGlade from the command line.
    """
    msg = _("""\
wxGlade usage:
- to start the GUI: python wxglade.py [WXG_FILE]
- to generate code from the command line: python wxglade.py OPTIONS... FILE
  OPTIONS are the following:
  -g, --generate-code=LANGUAGE  (required) give the output language
  -o, --output=PATH             (optional) name of the output file (in
                                single-file mode) or directory (in
                                multi-file mode)
    """)
    print msg
    print _('Valid LANGUAGE values:'),
    common.use_gui = False
    common.load_code_writers()
    for value in common.code_writers:
        print value,
    print '\n'
    sys.exit(1)


def determine_wxglade_path():
    """\
    @return: wxGlade application directory
    """
    # use directory of the exe in case of frozen packages e.g.
    # PyInstaller or py2exe
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.argv[0])

    root = __file__
    if os.path.islink(root):
        root = os.path.realpath(root)
    return os.path.dirname(os.path.abspath(root))


def run_main():
    """\
    This main procedure is started by calling either wxglade.py or
    wxglade.pyw on windows
    """
    # print versions first
    print _("Starting wxGlade version %s on Python %s") % (
        common.version,
        common.py_version,
        )

    # prepend the widgets dir to the
    wxglade_path = determine_wxglade_path()
    
    # set the program's paths
    common.wxglade_path   = wxglade_path

    # static paths
    common.docs_path      = os.path.join(wxglade_path, 'docs')
    common.icons_path     = os.path.join(wxglade_path, 'icons')
    common.widgets_path   = os.path.join(wxglade_path, 'widgets')
    common.templates_path = os.path.join(wxglade_path, 'templates')
    common.tutorial_file  = os.path.join(common.docs_path, 'html', 'index.html')

    # search credits file at two different locations
    # - <wxglade_path>/docs/credits.txt for linux packages
    # - <wxglade_path>/credits.txt at Windows or started from source directory
    if os.path.exists(os.path.join(common.wxglade_path, 'credits.txt')):
        common.credits_file = os.path.join(common.wxglade_path, 'credits.txt')
    elif os.path.exists(os.path.join(common.docs_path, 'credits.txt')):
        common.credits_file = os.path.join(common.docs_path, 'credits.txt')
    else:
        print _('ERROR: credits file "credits.txt" not found!')
        common.credits_file = None

    # search license file at two different locations
    # - <wxglade_path>/docs/license.txt for linux packages
    # - <wxglade_path>/license.txt at Windows or started from source directory
    if os.path.exists(os.path.join(common.wxglade_path, 'license.txt')):
        common.license_file = os.path.join(common.wxglade_path, 'license.txt')
    elif os.path.exists(os.path.join(common.docs_path, 'license.txt')):
        common.license_file = os.path.join(common.docs_path, 'license.txt')
    else:
        print _('ERROR: license file "license.txt" not found!')
        common.license_file = None

    # print used paths
    print _('Base directory:             %s') % common.wxglade_path
    print _('Documentation directory:    %s') % common.docs_path
    print _('Icons directory:            %s') % common.icons_path
    print _('Build-in widgets directory: %s') % common.widgets_path
    print _('Template directory:         %s') % common.templates_path
    print _('Credits file:               %s') % common.credits_file
    print _('License file:               %s') % common.license_file
    print _('Tutorial file:              %s') % common.tutorial_file

    # adapt application search path
    sys.path = [common.wxglade_path, common.widgets_path] + sys.path
    
    # before running the GUI, let's see if there are command line options for
    # code generation
    filename = None
    start_gui = False
    options, args = parse_command_line()
    if len(sys.argv) == 1:
        start_gui = True
    elif not options:
        filename = _fix_path(args[0])
        start_gui = True

    if start_gui:
        # print versions first
        import main
        # if there was no option, start the app in GUI mode
        main.main(filename)
    else:
        command_line_code_generation(options, args)

if __name__ == "__main__":
    run_main()
