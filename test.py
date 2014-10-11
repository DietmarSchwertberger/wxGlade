#!/usr/bin/env  python2
"""
Create a test suites and run all tests

@see: L{wxglade.tests}

@copyright: 2012-2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

# import general python modules
import gettext
import logging
import imp
import os
import sys
import unittest
from optparse import OptionParser

t = gettext.translation(domain="wxglade", localedir="locale", fallback=True)
t.install("wxglade")

import wxglade


def run_tests(gui_tests=False):
    """\
    Create test suites and run all tests

    @param gui_tests: Test GUI components or test internal functionality
    @type gui_tests:  bool
    """
    suites = []

    # disable logging first because the initialisation logs path details and
    # other details
    logging.disable(999)
    wxglade.init_stage1()
    wxglade.init_stage2(gui_tests)

    # get a list of all test modules
    modules = os.listdir('./tests')
    if '__init__.py' in modules:
        modules.remove('__init__.py')

    # select proper wxversion
    if gui_tests:
        # import proper wx-module using wxversion
        if not hasattr(sys, "frozen") and 'wx' not in sys.modules:
            try:
                import wxversion
                # Currently we use wxPython 2.8 only
                wxversion.select('2.8')
                #wxversion.ensureMinimal('2.8')
            except ImportError:
                print _('Please install missing python module "wxversion".')
                sys.exit(1)
            except wxversion.VersionError, e:
                print _('The requested wxPython version is not found. '
                        'Disable GUI tests.')
                gui_tests = False

    # try to import all files as modules
    for module_name in modules:
        if (not module_name.endswith('.py')) or \
           (gui_tests and not module_name.endswith('_gui.py')) or \
           (not gui_tests and module_name.endswith('_gui.py')):
            continue
        module_name = os.path.splitext(module_name)[0]
        fp, path, info = imp.find_module(module_name, ['./tests'])
        try:
            module = imp.load_module(module_name, fp, path, info)
        finally:
            # Make sure fp is closed properly
            if fp:
                fp.close()

        # search all test cases in the loaded module
        suites.append(unittest.findTestCases(module))

    # summarise all suites and run tests
    all_tests = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(all_tests)


if __name__ == '__main__':
    # evaluate command line options first
    parser = OptionParser(
        usage="%prog [options]  Test wxGlade components",
        )
    parser.add_option(
        '-g',
        '--gui',
        dest='gui_tests',
        default=False,
        action='store_true',
        help=_('Test GUI components instead of non-GUI components'),
        )

    (options, args) = parser.parse_args()

    run_tests(options.gui_tests)
