# application.py: Application class to store properties of the application
#                 being created
# $Id: application.py,v 1.21 2003/05/13 10:13:51 agriggio Exp $
# 
# Copyright (c) 2002-2003 Alberto Griggio <albgrig@tiscalinet.it>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

from wxPython.wx import *
from widget_properties import *
from tree import Tree, WidgetTree
import common, math, misc, os, config
import traceback

class FileDirDialog:
    """\
    Custom class which displays a FileDialog or a DirDialog, according to the
    value of the codegen_opt of its parent (instance of Application)
    """
    def __init__(self, owner, parent, wildcard="All Files|*",
                 file_message="Choose a file", dir_message=None, style=0):
        self.owner = owner
        self.prev_dir = config.preferences.codegen_path
        self.file_dialog = wxFileDialog(parent, file_message, self.prev_dir,
                                        wildcard=wildcard, style=style)
        if dir_message is None: dir_message = file_message
        log_null = wxLogNull() # to prevent popup messages about lack of
                               # permissions to view the contents of
                               # some directories
        style = 0
        if misc.check_wx_version(2, 3, 3):
            style = wxDD_DEFAULT_STYLE|wxDD_NEW_DIR_BUTTON
        self.dir_dialog = wxDirDialog(parent, dir_message, style=style)
        del log_null
        self.parent = parent
        self.file_message = file_message
        self.style = style

    def ShowModal(self):
        if self.owner.codegen_opt == 0:
            if self.prev_dir is not None:
                self.file_dialog.SetDirectory(self.prev_dir)
            dialog = self.file_dialog
        else:
            if self.prev_dir is not None:
                self.dir_dialog.SetPath(self.prev_dir)
            dialog = self.dir_dialog
        ok = dialog.ShowModal()
        if ok == wxID_OK:
            self.prev_dir = dialog.GetPath()
            if not os.path.isdir(self.prev_dir):
                self.prev_dir = os.path.dirname(self.prev_dir)
        return ok

    def get_value(self):
        if self.owner.codegen_opt == 0: return self.file_dialog.GetPath()
        else: return self.dir_dialog.GetPath()

    def set_wildcard(self, wildcard):
        if wxPlatform == '__WXMSW__': self.file_dialog.SetWildcard(wildcard)
        else:
            # on GTK SetWildcard has no effect, so we recreate the dialog
            self.file_dialog = wxFileDialog(self.parent, self.file_message,
                                            wildcard=wildcard,
                                            style=self.style)
# end of class FileDirDialog


class Application(object):
    """\
    properties of the application being created
    """
    def __init__(self, property_window):
        self.property_window = property_window
        self.notebook = wxNotebook(self.property_window, -1)
        nb_sizer = wxNotebookSizer(self.notebook)
        self.notebook.SetAutoLayout(True)
        self.notebook.sizer = nb_sizer
        self.notebook.Hide()
        #panel = wxPanel(self.notebook, -1)
        panel = wxScrolledWindow(self.notebook, -1, style=wxTAB_TRAVERSAL)
        self.name = "app" # name of the wxApp instance to generate
        self.__saved = True # if True, there are no changes to save
        self.__filename = None # name of the output xml file
        def set_name(value): self.name = str(value)
        self.klass = "MyApp"
        def set_klass(value): self.klass = str(value)
        self.codegen_opt = 0 # if != 0, generates a separate file
                             # for each class 
        def set_codegen_opt(value):
            try: opt = int(value)
            except ValueError: pass
            else: self.codegen_opt = opt
        self.output_path = ""
        self.language = 'python' # output language
        def set_output_path(value): self.output_path = value
        self.use_gettext = False
        def set_use_gettext(value): self.use_gettext = bool(int(value))
        self.access_functions = {
            'name': (lambda : self.name, set_name),
            'class': (lambda : self.klass, set_klass), 
            'code_generation': (lambda : self.codegen_opt, set_codegen_opt),
            'output_path': (lambda : self.output_path, set_output_path),
            'language': (self.get_language, self.set_language),
            'encoding': (self.get_encoding, self.set_encoding),
            'use_gettext': (lambda : self.use_gettext, set_use_gettext)
            }
        self.use_gettext_prop = CheckBoxProperty(self, "use_gettext", panel,
                                                 "Enable gettext support")
        TOP_WIN_ID = wxNewId()
        self.top_win_prop = wxChoice(panel, TOP_WIN_ID, choices=[],
                                     size=(1, -1))
        self.top_window = '' # name of the top window of the generated app

        self.name_prop = TextProperty(self, "name", panel, True)
        self.klass_prop = TextProperty(self, "class", panel, True)

        self.encoding = self._get_default_encoding()
        self.encoding_prop = TextProperty(self, 'encoding', panel)
        
        self.codegen_prop = RadioProperty(self, "code_generation", panel,
                                          ["Single file", "Separate file for" \
                                           " each class"])
        ext = getattr(common.code_writers.get('python'),
                      'default_extensions', [])
        wildcard = []
        for e in ext:
            wildcard.append('%s files (*.%s)|*.%s' % ('Python', e, e))
        wildcard.append('All files|*')
        dialog = FileDirDialog(self, panel, '|'.join(wildcard),
                               "Select output file", "Select output directory",
                               wxSAVE|wxOVERWRITE_PROMPT)
        
        self.codewriters_prop = RadioProperty(self, "language", panel,
                                              common.code_writers.keys(),
                                              columns=3)

        self.codewriters_prop.set_str_value('python')
        
        self.outpath_prop = DialogProperty(self, "output_path", panel,
                                           dialog)
        BTN_ID = wxNewId()
        btn = wxButton(panel, BTN_ID, "Generate code")

        # layout of self.notebook
        sizer = wxBoxSizer(wxVERTICAL)
        sizer.Add(self.name_prop.panel, 0, wxEXPAND)
        sizer.Add(self.klass_prop.panel, 0, wxEXPAND)
        sizer.Add(self.encoding_prop.panel, 0, wxEXPAND)
        sizer.Add(self.use_gettext_prop.panel, 0, wxEXPAND)
        szr = wxBoxSizer(wxHORIZONTAL)
        from widget_properties import _label_initial_width as _w
        label = wxGenStaticText(panel, -1, "Top window", size=(_w, -1))
        label.SetToolTip(wxToolTip("Top window"))
        szr.Add(label, 2, wxALL|wxALIGN_CENTER, 3)
        szr.Add(self.top_win_prop, 5, wxALL|wxALIGN_CENTER, 3)
        sizer.Add(szr, 0, wxEXPAND)
        sizer.Add(self.codegen_prop.panel, 0, wxALL|wxEXPAND, 4)
        sizer.Add(self.codewriters_prop.panel, 0, wxALL|wxEXPAND, 4)
        sizer.Add(self.outpath_prop.panel, 0, wxEXPAND)
        sizer.Add(btn, 0, wxALL|wxEXPAND, 5)
        
        panel.SetAutoLayout(True)
        panel.SetSizer(sizer)
        sizer.Layout()
        sizer.Fit(panel)
        h = panel.GetSize()[1]
        self.notebook.AddPage(panel, "Application")
        import math
        panel.SetScrollbars(1, 5, 1, math.ceil(h/5.0))

        EVT_BUTTON(btn, BTN_ID, self.generate_code)
        EVT_CHOICE(self.top_win_prop, TOP_WIN_ID, self.set_top_window)

        # this is here to keep the interface similar to the various widgets
        # (to simplify Tree)
        self.widget = None # this is always None


    def _get_default_encoding(self):
        """\
        Returns the name of the default character encoding of this machine
        """
        import locale
        locale.setlocale(locale.LC_ALL)
        try: return locale.nl_langinfo(locale.CODESET)
        except AttributeError: return 'latin-1' # this is what I use, so... :-)

    def get_encoding(self):
        return self.encoding

    def set_encoding(self, value):
        try: unicode('a', value)
        except LookupError, e:
            wxMessageBox(str(e), "Error", wxOK|wxCENTRE|wxICON_ERROR)
            self.encoding_prop.set_value(self.encoding)
        else:
            self.encoding = value

    def set_language(self, value):
        language = self.language = self.codewriters_prop.get_str_value()
        ext = getattr(common.code_writers[language], 'default_extensions', [])
        wildcard = []
        for e in ext:
            wildcard.append('%s files (*.%s)|*.%s' % (language.capitalize(),
                                                      e, e))
        wildcard.append('All files|*')
        self.outpath_prop.dialog.set_wildcard('|'.join(wildcard))

    def get_language(self):
        return self.language #codewriters_prop.get_str_value()

    def _get_saved(self): return self.__saved
    def _set_saved(self, value):
        if self.__saved != value:
            self.__saved = value
            t = common.app_tree.get_title()
            if not value: common.app_tree.set_title('* ' + t)
            else:
                if t[0] == '*': common.app_tree.set_title(t[1:])
    saved = property(_get_saved, _set_saved)

    def _get_filename(self): return self.__filename
    def _set_filename(self, value):
        if self.__filename != value:
            self.__filename = value
            if self.__saved: flag = ' '
            else: flag = '* '
            common.app_tree.set_title('%s(%s)' % (flag, self.__filename))
    filename = property(_get_filename, _set_filename)
       
    def get_top_window(self): return self.top_window

    def set_top_window(self, *args):
        self.top_window = self.top_win_prop.GetStringSelection()

    def add_top_window(self, name):
        self.top_win_prop.Append(str(name))

    def remove_top_window(self, name):
        index = self.top_win_prop.FindString(str(name))
        if index != -1:
            if wxPlatform == '__WXGTK__':
                choices = [ self.top_win_prop.GetString(i) for i in \
                            range(self.top_win_prop.Number()) if i != index ]
                self.top_win_prop.Clear()
                for c in choices:
                    self.top_win_prop.Append(c)
            else:
                self.top_win_prop.Delete(index)

    def update_top_window_name(self, oldname, newname):
        index = self.top_win_prop.FindString(oldname)
        if index != -1:
            if self.top_window == oldname:
                self.top_window = newname
            if wxPlatform == '__WXGTK__':
                sel_index = self.top_win_prop.GetSelection()
                choices = [ self.top_win_prop.GetString(i) for i in \
                            range(self.top_win_prop.Number()) ]
                choices[index] = newname
                self.top_win_prop.Clear()
                for c in choices:
                    self.top_win_prop.Append(c)
                self.top_win_prop.SetSelection(sel_index)
            else:
                self.top_win_prop.SetString(index, newname)
        
    def reset(self):
        """\
        resets the default values of the attributes of the app
        """
        self.klass = "MyApp"; self.klass_prop.set_value("MyApp")
        self.klass_prop.toggle_active(False)
        self.name = "app"; self.name_prop.set_value("app")
        self.name_prop.toggle_active(False)
        self.codegen_opt = 0; self.codegen_prop.set_value(0)
        self.output_path = ""; self.outpath_prop.set_value("")
        # do not reset language, but call set_language anyway to update the
        # wildcard of the file dialog
        self.set_language(self.get_language())
        self.top_window = ''
        self.top_win_prop.Clear()
        
    def show_properties(self, *args):
        sizer_tmp = self.property_window.GetSizer()
        sizer_tmp = wxPyTypeCast(sizer_tmp, "wxBoxSizer")
        child = wxPyTypeCast(sizer_tmp.GetChildren()[0], "wxSizerItem")
        w = wxPyTypeCast(child.GetWindow(), "wxWindow")
        if w is self.notebook: return
        w.Hide()
        child.SetWindow(self.notebook)
        self.notebook.Show(True)
        self.property_window.Layout()
        self.property_window.SetTitle('Properties - <%s>' % self.name)
        try: common.app_tree.select_item(self.node)
        except AttributeError: pass

    def __getitem__(self, name):
        return self.access_functions[name]

    def generate_code(self, *args, **kwds):
        preview = kwds.get('preview', False)
        if not self.output_path:
            return wxMessageBox("You must specify an output file\n"
                                "before generating any code", "Error",
                                wxOK|wxCENTRE|wxICON_EXCLAMATION,
                                self.notebook)
        if not preview and \
               ((self.name_prop.is_active() or self.klass_prop.is_active()) \
                and self.top_win_prop.GetSelection() < 0):
            return wxMessageBox("Please select a top window "
                                "for the application", "Error", wxOK |
                                wxCENTRE | wxICON_EXCLAMATION, self.notebook)
                
        from cStringIO import StringIO
        out = StringIO()
        common.app_tree.write(out) # write the xml onto a temporary buffer
        from xml_parse import CodeWriter
        try:
            # generate the code from the xml buffer
            cw = self.get_language() #self.codewriters_prop.get_str_value()
            CodeWriter(common.code_writers[cw], out.getvalue(), True,
                       preview=preview)
        except (IOError, OSError), msg:
            wxMessageBox("Error generating code:\n%s" % msg, "Error",
                         wxOK|wxCENTRE|wxICON_ERROR)
        except Exception, msg:
            import traceback; traceback.print_exc()
            wxMessageBox("An exception occurred while generating the code "
                         "for the application.\n"
                         "This is the error message associated with it:\n"
                         "        %s\n"
                         "For more details, look at the full traceback "
                         "on the console.\nIf you think this is a wxGlade bug,"
                         " please report it." % msg, "Error",
                         wxOK|wxCENTRE|wxICON_ERROR)
        else:
            if not preview:
                wxMessageBox("Code generation completed successfully",
                             "Information", wxOK|wxCENTRE|wxICON_INFORMATION)

    def get_name(self):
        if self.name_prop.is_active(): return self.name
        return ''

    def get_class(self):
        if self.klass_prop.is_active(): return self.klass
        return ''

    def update_view(self, *args): pass

    def is_visible(self): return True

    def preview(self, widget, out_name=[None]):
        if out_name[0] is None:
            import warnings
            warnings.filterwarnings("ignore", "tempnam", RuntimeWarning,
                                    "application")
            out_name[0] = os.tempnam(None, 'wxg') + '.py'
            #print 'Temporary name:', out_name[0]
        widget_class_name = widget.klass
        real_path = self.output_path
        self.output_path = out_name[0]
        real_codegen_opt = self.codegen_opt
        real_language = self.language
        real_use_gettext = self.use_gettext
        self.use_gettext = False
        self.language = 'python'
        self.codegen_opt = 0
        frame = None
        try:
            self.generate_code(preview=True)
            # dynamically import the generated module
            FrameClass = misc.import_name(self.output_path, widget_class_name)
            if not (issubclass(FrameClass, wxFrame) or
                    issubclass(FrameClass, wxDialog)):
                # the toplevel class isn't really toplevel, add a frame...
                frame = wxFrame(None, -1, widget_class_name)
                if issubclass(FrameClass, wxMenuBar):
                    menubar = FrameClass()
                    frame.SetMenuBar(menubar)
                elif issubclass(FrameClass, wxToolBar):
                    toolbar = FrameClass(frame, -1)
                    frame.SetToolBar(toolbar)
                else:
                    panel = FrameClass(frame, -1)
                frame.Fit()
            else:
                frame = FrameClass(None, -1, '')
            def on_close(event):
                frame.Destroy()
                widget.preview_widget = None
                widget.preview_button.SetLabel('Preview')
            EVT_CLOSE(frame, on_close)
            frame.SetTitle('<Preview> %s' % frame.GetTitle())
            # raise the frame
            frame.Center()
            frame.Show()
            # remove the temporary file (and the .pyc one too)
            if os.path.isfile(self.output_path):
                os.unlink(self.output_path)
            for ext in 'c', 'o': # remove eventual .pyc and .pyo files
                name = self.output_path + ext
                if os.path.isfile(name):
                    os.unlink(name)
        except:
            traceback.print_exc()
            wxMessageBox("Problem previewing gui", "Error",
                         wxOK|wxCENTRE|wxICON_EXCLAMATION, self.notebook)
        # restore app state
        self.output_path = real_path
        self.codegen_opt = real_codegen_opt
        self.language = real_language
        self.use_gettext = real_use_gettext
        return frame

# end of class Application
