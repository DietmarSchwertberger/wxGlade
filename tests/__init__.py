"""
@copyright: 2012 Carsten Grohmann

@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

# import general python modules
import cStringIO
import difflib
import glob
import os.path
import unittest

# import project modules
import common
import wxglade
from xml_parse import CodeWriter


class WXGladeBaseTest(unittest.TestCase):
    """\
    Provide basic functions for all tests

    All test cases uses an own implementation to L{common.save_file()} to
    catch the results. This behaviour is limitied to single file
    creation.
    """

    vFiles = {}
    """\
    Dictionary to store the content of the files generated by the code
    generators.

    The filename is the key and the content is a StringIO instance.
    """

    origSaveFile = None
    """\
    Reference to the original I{save_file()} implementation
    """

    caseDirectory = 'casefiles'
    """\
    Directory with input files and result files
    """

    init_stage1 = False
    """\
    Initialise the first stage of wxGlade e.g. path settings
    """

    init_use_gui = False
    """\
    Initialise the GUI part of wxGlade
    """

    def setUp(self):
        """\
        Initialise parts of wxGlade only
        """
        # initialise path settings
        if self.init_stage1:
            wxglade.init_stage1()

        # initialise sizers, widgets, codewriter
        wxglade.init_stage2(use_gui=self.init_use_gui)

        # initialise wxGlade configuration
        import config
        config.init_preferences()

        # set some useful preferences
        config.preferences.autosave = False
        config.preferences.write_timestamp = False
        config.preferences.show_progress = False

        # initiate empty structure to store files and there content
        self.vFiles = {}

        # replace original save_file() by test specific implementation
        self.origSaveFile = common.save_file
        common.save_file = self._save_file

        # set own version string to prevent diff mismatches
        common.version = '"faked test version"'

        # Determinate case directory
        self.caseDirectory = os.path.join(
            os.path.dirname(__file__),
            self.caseDirectory,
            )

    def tearDown(self):
        """\
        Cleanup
        """
        # cleanup virtual files
        for filename in self.vFiles:
            self.vFiles[filename].close()
        self.vFiles = {}

        # restore original save_file() implementation
        common.save_file = self.origSaveFile

    def _generate_code(self, language, document, filename):
        """\
        Generate code for the given language.

        @param language: Language to generate code for
        @param document: XML document to generate code for
        @type document:  String
        @param filename: Name of the virtual output file
        @type filename:  String
        """
        self.failUnless(
            language in common.code_writers,
            "No codewriter loaded for %s" % language
            )

        # generate code
        CodeWriter(
            writer=common.code_writers[language],
            input=document,
            from_string=True,
            out_path=filename,
            )

        return

    def _load_file(self, filename):
        """\
        Load a file need by a test case.

        @param filename:  Name of the file to load
        @type filename:   String
        @param extension: File extension e.g. I{.wxg} or I{.py}
        @type extension:  String
        @return:          File content
        @rtype:           String
        """
        casename, extension = os.path.splitext(filename)
        if extension == '.wxg':
            filetype = 'input'
        else:
            filetype = 'result'

        file_list = glob.glob(
            os.path.join(self.caseDirectory, "%s*%s" % (casename, extension))
            )
        self.failIf(
           len(file_list) == 0,
           'No %s file for case "%s" found!' % (filetype, casename)
           )
        self.failIf(
           len(file_list) > 1,
           'More than one %s file for case "%s" found!' % (filetype, casename)
           )

        fh = open(file_list[0])
        content = fh.read()
        fh.close()

        # replacing path entries
        content = content % {
            'wxglade_path':   common.wxglade_path,
            'docs_path':      common.docs_path,
            'icons_path':     common.icons_path,
            'widgets_path':   common.widgets_path,
            'templates_path': common.templates_path,
            'tutorial_file':  common.tutorial_file,
            }

        return content

    def _save_file(self, filename, content, which='wxg'):
        """\
        Test specific implementation of L{common.save_file()} to get the
        result of the code generation without file creation.

        The file content is stored in a StringIO instance. It's
        accessible at L{self.vFiles} using the filename as key.

        @note: The signature is as same as L{wxglade.common.save_file()} but
               the functionality differs.

        @param filename: Name of the file to create
        @param content:  String to store into 'filename'
        @param which:    Kind of backup: 'wxg' or 'codegen'
        """
        self.failIf(
            filename in self.vFiles,
            "Virtual file %s already exists" % filename
            )
        self.failUnless(
            filename,
            "No filename given",
            )
        outfile = cStringIO.StringIO()
        outfile.write(content)
        self.vFiles[filename] = outfile

    def _diff(self, text1, text2):
        """\
        Compare two lists, tailing spaces will be removed

        @param text1: Expected text
        @type text1:  String
        @param text2: Generated text
        @type text2:  String

        @return: Changes formatted as unified diff
        @rtype:  String
        """
        self.assertEqual(type(text1), type(""))
        self.assertEqual(type(text2), type(""))

        # split into lists, because difflib needs lists and remove
        # tailing spaces
        list1 = [x.rstrip() for x in text1.splitlines()]
        list2 = [x.rstrip() for x in text2.splitlines()]

        # compare source files
        diff_gen = difflib.unified_diff(
            list1,
            list2,
            fromfile='expected source',
            tofile='created source',
            lineterm=''
            )
        return '\n'.join(diff_gen)

    def _generate_and_compare(self, lang, inname, outname):
        """\
        Generate code and compare generated and expected code

        @param lang:    Language to generate code for
        @type lang:     String
        @param inname:  Name of the XML input file
        @type inname:   String
        @param outname: Name of the output file
        @type outname:  String
        """
        # load XML input file
        source = self._load_file(inname)
        expected = self._load_file(outname)

        # generate code
        self._generate_code(lang, source, outname)
        generated = self.vFiles[outname].getvalue()
        self._compare(expected, generated)

    def _compare(self, expected, generated, filetype=None):
        """\
        Compare expected and generated content using a diff algorithm

        @param expected:  Expected content
        @type expected:   Multiline String
        @param generated: Generated content
        @type generated:  Multiline String
        @param filetype:  Short description of the content
        @type filetype:   String
        """
        # compare files
        delta = self._diff(expected, generated)

        if filetype:
            self.failIf(
                delta,
                "Generated %s file and expected result differs:\n%s" % (
                    filetype.capitalize(),
                    delta,
                    )
                )
        else:
            self.failIf(
                delta,
                "Generated file and expected result differs:\n%s"
                )
