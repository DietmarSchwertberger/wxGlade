"""
@copyright: 2014-2017 Carsten Grohmann

@license: MIT (see LICENSE.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import common

# import test base class
from tests import WXGladeBaseTest


class TestBugs(WXGladeBaseTest):
    """\
    Test for different reported bugs
    """

    def test_bug163(self):
        """Test SF bug #163 - Don't convert first char of a XRC extraproperty to upper case."""
        self._test_all('bug163')

    def test_bug165(self):
        """Test SF bug #165 - Can't rename notebook widget class - internal error on Preview """
        self._test_all('bug165')

    def test_bug166(self):
        """Test SF bug #166 - UnicodeDecodeError when saving project using non ASCII characters in menu items."""
        self._test_all('bug166')

    def test_bug167(self):
        """\
        Test bug #167 - ascii codec error - UnicodeDecodeError will be raised
        if existing files will be changed (and not overwritten) and those files
        contains non-ASCII characters.

        That's the test case for SF bug #167.
        """
        self._test_all('bug167')
        self._test_all('bug167_utf8')

    def test_bug179(self):
        """Test SF bug #179 - Main file is generated without custom extensions"""
        codegen = common.code_writers['C++']
        source = self._load_file('bug179.wxg')
        source = self._modify_attrs(source, overwrite='0')
        result_app        = self._load_file('Bug179_main.cpp')
        result_frame_cpp  = self._load_file('Bug179_Frame.c++')
        result_frame_h    = self._load_file('Bug179_Frame.hpp')

        self._generate_code('C++', source, self.curr_dir)

        main_cpp = self._with_curr_dir('Bug179_main.cpp')
        generated_app = self.get_content(main_cpp)
        generated_frame_cpp = self.get_content(self._with_curr_dir('Bug179_Frame.c++'))
        generated_frame_h = self.get_content(self._with_curr_dir('Bug179_Frame.hpp'))
        self._compare(result_app, generated_app, 'Bug179_main.cpp')
        self._compare(result_frame_cpp,  generated_frame_cpp, 'Bug179_Frame.c++')
        self._compare(result_frame_h,    generated_frame_h,   'Bug179_Frame.hpp')

    def test_bug183(self):
        """Test SF bug #183 - Preview failure for class names with Perl scope separator."""
        self._test_all('bug183')
        return

    def test_bug184(self):
        """Test SF bug #184 - Perl code generation: System colour constants named incorrectly."""
        self._test_all('bug184')

    def test_bug186(self):
        """Test SF bug #186 - Fix C++ code issue with Ids assigned to variables."""
        self._test_all('bug186')

    def test_bug188_toolbar_depencencies(self):
        """Test bug #188 - Missing dependencies with wxToolBox widgets."""
        self._test_all('bug188_included_toolbar')
        self._test_all('bug188_standalone_toolbar')

    def test_bars_wo_parent(self):
        """Test AttributeError during code generation of toplevel menubars."""
        self._test_all('bars_wo_parent')

    def test_bug189_XMLParsingError(self):
        """Test SF bug #189 - XmlParsingError : An internal error occurred while Generate Code."""
        # Lisp code has to raise an exception
        source = self._load_file('bug183.wxg')
        source = self._modify_attrs(source, path='/tmp/existing_but_no_access.pl')

        self.failUnlessRaises(
            IOError,
            self._generate_code,
            'perl',
            source,
            '/tmp/existing_but_no_access.pl',
        )

    def test_bug192(self):
        """Test SF bug #192 - 'Store as attribute' does not work for sizers in C++"""
        self._test_all('bug192')

    def test_bug194(self):
        """Test SF bug #194 - LB_EXTENDED for ListBox they never show up in generated code"""
        self._test_all('bug194')