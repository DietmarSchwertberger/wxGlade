# py_codegen.py: python code generator
#
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY


"""\
How the code is generated: every time the end of an object is reached during
the parsing of the xml tree, either the function 'add_object' or the function
'add_class' is called: the latter when the object is a toplevel one, the former
when it is not. In the last case, 'add_object' calls the appropriate ``writer''
function for the specific object, found in the 'obj_builders' dict. Such
function accepts one argument, the CodeObject representing the object for
which the code has to be written, and returns 3 lists of strings, representing
the lines to add to the '__init__', '__set_properties' and '__do_layout'
methods of the parent object.
"""

import sys, os, os.path
import common
from xml_parse import XmlParsingError


# these two globals must be defined for every code generator module
language = 'python'
writer = sys.modules[__name__] # the writer is the module itself

# default extensions for generated files: a list of file extensions
default_extensions = ['py']

"""\
dictionary that maps the lines of code of a class to the name of such class:
the lines are divided in 3 categories: '__init__', '__set_properties' and
'__do_layout'
"""
classes = None

"""dictionary of ``writers'' for the various objects"""
obj_builders = {}

"""\
dictionary of ``property writer'' functions, used to set the properties of a
toplevel object
"""
obj_properties = {}

# random number used to be sure that the replaced tags in the sources are
# the right ones (see SourceFileContent and add_class)
nonce = None

# lines common to all the generated files (import of wxPython, ...)
header_lines = []

# if True, generate a file for each custom class
multiple_files = False

# if not None, it is the single source file to write into
output_file = None
# if not None, it is the directory inside which the output files are saved
out_dir = None


class ClassLines:
    """\
    Stores the lines of python code for a custom class
    """
    def __init__(self):
        self.init = [] # lines of code to insert in the __init__ method
                       # (for children widgets)
        self.parents_init = [] # lines of code to insert in the __init__ for
                               # container widgets (panels, splitters, ...)
        self.sizers_init = [] # lines related to sizer objects declarations
        self.props = [] # lines to insert in the __set_properties method
        self.layout = [] # lines to insert in the __do_layout method
        
        self.dependencies = {} #[] # names of the modules this class depends on
        self.done = False # if True, the code for this class has already
                          # been generated

# end of class ClassLines


class SourceFileContent:
    """\
    Keeps info about an existing file that has to be updated, to replace only
    the lines inside a wxGlade block, an to keep the rest of the file as it was
    """
    def __init__(self, name=None, content=None, classes=None):
        self.name = name # name of the file
        self.content = content # content of the source file, if it existed
                               # before this session of code generation
        self.classes = classes # classes declared in the file
        self.new_classes = [] # new classes to add to the file (they are
                              # inserted BEFORE the old ones)
        if classes is None: self.classes = {}
        self.spaces = {} # indentation level for each class
        if self.content is None:
            self.build_untouched_content()

    def build_untouched_content(self):
        """\
        Builds a string with the contents of the file that must be left as is,
        and replaces the wxGlade blocks with tags that in turn will be replaced
        by the new wxGlade blocks
        """
        import re
        class_name = None
        new_classes_inserted = False
        # regexp to match class declarations
        class_decl = re.compile(r'^\s*class\s+([a-zA-Z_]\w*)\s*'
                                '(\(\s*[a-zA-Z_]\w*\s*(,\s*[a-zA-Z_]\w*)*'
                                '\s*\))?:\s*$')
        # regexps to match wxGlade blocks
        block_start = re.compile(r'^(\s*)#\s*begin\s+wxGlade:\s*'
                                 '([A-Za-z_]+\w*)??[.]?(\w+)\s*$')
        block_end = re.compile(r'^\s*#\s*end\s+wxGlade\s*$')
        inside_block = False
        tmp_in = open(self.name)
        out_lines = []
        for line in tmp_in:
            result = class_decl.match(line)
            if result is not None:
                if class_name is None:
                    # this is the first class declared in the file: insert the
                    # new ones before this
                    out_lines.append('<%swxGlade insert new_classes>' %
                                     nonce)
                    new_classes_inserted = True
                class_name = result.group(1)
                self.classes[class_name] = 1 # add the found class to the list
                                             # of classes of this module
                out_lines.append(line)
            elif not inside_block:
                result = block_start.match(line)
                if result is not None:
                    # replace the lines inside a wxGlade block with a tag that
                    # will be used later by add_class
                    spaces = result.group(1)
                    which_class = result.group(2) #1)
                    which_block = result.group(3) #2)
                    if which_class is None: which_class = class_name
                    self.spaces[which_class] = spaces
                    inside_block = True
                    if class_name is None:
                        out_lines.append('<%swxGlade replace %s>' % \
                                         (nonce, which_block))
                        #result.group(1)))
                    else:
                        out_lines.append('<%swxGlade replace %s %s>' % \
                                         (nonce, which_class, which_block))
                        #class_name, result.group(1)))
                else:
                    out_lines.append(line)
                    if line.startswith('from wxPython.wx import *'):
                        # add a tag to allow extra modules
                        out_lines.append('<%swxGlade extra_modules>\n'
                                         % nonce)
            else:
                # ignore all the lines inside a wxGlade block
                if block_end.match(line) is not None:
                    inside_block = False
        if not new_classes_inserted:
            # if we are here, the previous ``version'' of the file did not
            # contain any class, so we must add the new_classes tag at the
            # end of the file
            out_lines.append('<%swxGlade insert new_classes>' % nonce)
        tmp_in.close()
        # set the ``persistent'' content of the file
        self.content = "".join(out_lines)
        
# end of class SourceFileContent

# if not None, it is an instance of SourceFileContent that keeps info about
# the previous version of the source to generate
previous_source = None 
                  
    
def tabs(number):
    return '    ' * number

def initialize(out_path, multi_files):
    """\
    Writer initialization function.
    - out_path: output path for the generated code (a file if multi_files is
      False, a dir otherwise)
    - multi_files: if True, generate a separate file for each custom class
    """
    global classes, header_lines, multiple_files, previous_source, nonce, \
           _current_extra_modules
    import time, random

    # this is to be more sure to replace the right tags
    nonce = '%s%s' % (str(time.time()).replace('.', ''),
                      random.randrange(10**6, 10**7))
    
    classes = {}
    _current_extra_modules = {}
    header_lines = ['# generated by wxGlade %s on %s\n\n' % (common.version,
                                                             time.asctime()),
                    'from wxPython.wx import *\n']
    multiple_files = multi_files
    if not multiple_files:
        global output_file, output_file_name
        if os.path.isfile(out_path):
            # the file exists, we must keep all the lines not inside a wxGlade
            # block. NOTE: this may cause troubles if out_path is not a valid
            # python file, so be careful!
            previous_source = SourceFileContent(out_path)
        else:
            # if the file doesn't exist, create it and write the ``intro''
            previous_source = None
##             try: output_file = open(out_path, 'w')
##             except: raise XmlParsingError("Error opening '%s' file" % out_path)
            import cStringIO
            output_file = cStringIO.StringIO()
            output_file_name = out_path
            output_file.write('#!/usr/bin/env python\n')
            for line in header_lines:
                output_file.write(line)
            output_file.write('<%swxGlade extra_modules>\n' % nonce)
            output_file.write('\n')
    else:
        previous_source = None
        global out_dir
        if not os.path.isdir(out_path):
            raise XmlParsingError("'path' must be a directory when generating"\
                                  " multiple output files")
        out_dir = out_path


def finalize():
    """\
    Writer ``finalization'' function: flushes buffers, closes open files, ...
    """
    if previous_source is not None:
        # insert all the new custom classes inside the old file
        tag = '<%swxGlade insert new_classes>' % nonce
        if previous_source.new_classes:
            code = "".join(previous_source.new_classes)
        else:
            code = ""
        previous_source.content = previous_source.content.replace(tag, code)
        tag = '<%swxGlade extra_modules>\n' % nonce
        code = "".join(_current_extra_modules.keys())
        previous_source.content = previous_source.content.replace(tag, code)
        # now remove all the remaining <123415wxGlade ...> tags from the
        # source: this may happen if we're not generating multiple files,
        # and one of the container class names is changed
        import re
        tags = re.findall('(<%swxGlade replace ([a-zA-Z_]\w*) +\w+>)' % nonce,
                          previous_source.content)
        for tag in tags:
            indent = previous_source.spaces.get(tag[1], tabs(2))
            comment = '%s# content of this block not found: ' \
                      'did you rename this class?\n%spass\n' % (indent, indent)
            previous_source.content = previous_source.content.replace(tag[0],
                                                                      comment)
        # write the new file contents to disk
        out = open(previous_source.name, 'w')
        out.write(previous_source.content)
        out.close()
        
    elif not multiple_files:
        global output_file
        em = "".join(_current_extra_modules.keys())
        content = output_file.getvalue().replace(
            '<%swxGlade extra_modules>\n' % nonce, em)
        output_file.close()
        try:
            output_file = open(output_file_name, 'w')
            output_file.write(content)
            output_file.close()
            # make the file executable
            os.chmod(output_file_name, 0755)
        except IOError, e:
            raise XmlParsingError(str(e))
        except OSError: pass # this isn't necessary a bad error
        del output_file


def add_object(top_obj, sub_obj):
    """\
    adds the code to build 'sub_obj' to the class body of 'top_obj'.
    """
    try: klass = classes[top_obj.klass]
    except KeyError: klass = classes[top_obj.klass] = ClassLines()
    try: builder = obj_builders[sub_obj.base]
    except KeyError:
        # no code generator found: write a comment about it
        klass.init.extend(['\n', '# code for %s (type %s) not generated: '
                           'no suitable writer found' % (sub_obj.name,
                                                         sub_obj.klass),'\n'])
    else:
        init, props, layout = builder(sub_obj)
        if sub_obj.in_windows: # the object is a wxWindow instance
            # --- patch 2002-08-26 ------------------------------------------
            #init.reverse()
            if sub_obj.is_container:
                init.reverse()
                klass.parents_init.extend(init)
            else: klass.init.extend(init)
            # ---------------------------------------------------------------
            #klass.init.extend(init)
        else: # the object is a sizer
            klass.sizers_init.extend(init)
        klass.props.extend(props)
        klass.layout.extend(layout)
        if sub_obj.is_toplevel and sub_obj.base != sub_obj.klass:
            key = 'from %s import %s\n' % (sub_obj.klass, sub_obj.klass)
            klass.dependencies[key] = 1
        for dep in _widget_extra_modules.get(sub_obj.base, []):
            klass.dependencies[dep] = 1


def add_sizeritem(toplevel, sizer, obj, option, flag, border):
    """\
    writes the code to add the object 'obj' to the sizer 'sizer'
    in the 'toplevel' object.
    """
    # an ugly hack to allow the addition of spacers: if obj_name can be parsed
    # as a couple of integers, it is the size of the spacer to add
    obj_name = obj.name
    try: w, h = [ int(s) for s in obj_name.split(',') ]
    except ValueError:
        if obj.base == 'wxNotebook' and not obj.is_toplevel:
            # this is a TEMPORARY HACK! we must find a better way
            obj_name += '_sizer'
        elif obj.in_windows:
            obj_name = 'self.' + obj_name # it's a real name
    else: pass # it was the dimension of a spacer
    try: klass = classes[toplevel.klass]
    except KeyError: klass = classes[toplevel.klass] = ClassLines()
    buffer = '%s.Add(%s, %s, %s, %s)\n' % \
             (sizer.name, obj_name, option, flag, border)
    klass.layout.append(buffer)


def add_class(code_obj):
    """\
    Generates the code for a custom class.
    """
    global _current_extra_modules
    if not multiple_files:
        # in this case, previous_source is the SourceFileContent instance
        # that keeps info about the single file to generate
        prev_src = previous_source
    else:
        # let's see if the file to generate exists, and in this case
        # create a SourceFileContent instance
        filename = os.path.join(out_dir, code_obj.klass + '.py')
        if not os.path.exists(filename): prev_src = None
        else: prev_src = SourceFileContent(filename)
        _current_extra_modules = {}
    
    if classes.has_key(code_obj.klass) and classes[code_obj.klass].done:
        return # the code has already been generated

    if prev_src is not None and prev_src.classes.has_key(code_obj.klass):
        is_new = False
        indentation = prev_src.spaces[code_obj.klass]
    else:
        # this class wasn't in the previous version of the source (if any)
        is_new = True
        indentation = tabs(2)
        mods = _widget_extra_modules.get(code_obj.base)
        if mods:
            for m in mods: _current_extra_modules[m] = 1

    buffer = []
    write = buffer.append

    if not classes.has_key(code_obj.klass):
        # if the class body was empty, create an empty ClassLines
        classes[code_obj.klass] = ClassLines()
    if is_new:
        write('class %s(%s):\n' % (code_obj.klass, code_obj.base))
        write(tabs(1) + 'def __init__(self, *args, **kwds):\n')
    # __init__ begin tag
    write(indentation + '# begin wxGlade: %s.__init__\n' % code_obj.klass)
    prop = code_obj.properties
    style = prop.get("style", None)
    if style: write(indentation + 'kwds["style"] = %s\n' % style)
    # __init__
    write(indentation + '%s.__init__(self, *args, **kwds)\n' % code_obj.base)
##     if not classes.has_key(code_obj.klass):
##         # if the class body was empty, create an empty ClassLines
##         classes[code_obj.klass] = ClassLines()
    tab = indentation #tabs(2)
    init_lines = classes[code_obj.klass].init
    # --- patch 2002-08-26 ---------------------------------------------------
    #init_lines.reverse()
    parents_init = classes[code_obj.klass].parents_init
    parents_init.reverse()
    for l in parents_init: write(tab+l)
    # ------------------------------------------------------------------------
    for l in init_lines: write(tab + l)
    write('\n' + tab + 'self.__set_properties()\n')
    write(tab + 'self.__do_layout()\n')
    # end tag
    write(tab + '# end wxGlade\n')
    if prev_src is not None and not is_new:
        # replace the lines inside the __init__ wxGlade block with the new ones
        tag = '<%swxGlade replace %s %s>' % (nonce, code_obj.klass,
                                             '__init__')
        if prev_src.content.find(tag) < 0:
            # no __init__ tag found, issue a warning and do nothing
            print >> sys.stderr, "WARNING: wxGlade __init__ block not found," \
                  " __init__ code NOT generated"
        else:
            prev_src.content = prev_src.content.replace(tag, "".join(buffer))
        buffer = []
        write = buffer.append

    # __set_properties
    props_builder = obj_properties.get(code_obj.base)
    write_body = len(classes[code_obj.klass].props)
    if props_builder:
        obj_p = obj_properties[code_obj.base](code_obj)
        if not write_body: write_body = len(obj_p)
    else: obj_p = []
    if is_new: write('\n%sdef __set_properties(self):\n' % tabs(1))
    # begin tag
    write(tab + '# begin wxGlade: %s.__set_properties\n' % code_obj.klass)
    if not write_body: write(tab + 'pass\n')
    else:
        for l in obj_p: write(tab + l)
        for l in classes[code_obj.klass].props: write(tab); write(l)
    # end tag
    write(tab + '# end wxGlade\n')
    if prev_src is not None and not is_new:
        # replace the lines inside the __set_properties wxGlade block
        # with the new ones
        tag = '<%swxGlade replace %s %s>' % (nonce, code_obj.klass,
                                             '__set_properties')
        if prev_src.content.find(tag) < 0:
            # no __set_properties tag found, issue a warning and do nothing
            print >> sys.stderr, "WARNING: wxGlade __set_properties block " \
                  "not found, __set_properties code NOT generated"
        else:
            prev_src.content = prev_src.content.replace(tag, "".join(buffer))
        buffer = []
        write = buffer.append

    # __do_layout
    if is_new: write('\n' + tabs(1) + 'def __do_layout(self):\n')
    layout_lines = classes[code_obj.klass].layout
    sizers_init_lines = classes[code_obj.klass].sizers_init
    # begin tag
    write(tab + '# begin wxGlade: %s.__do_layout\n' % code_obj.klass)
    if layout_lines or sizers_init_lines:
        sizers_init_lines.reverse()
        for l in sizers_init_lines: write(tab + l)
        for l in layout_lines: write(tab + l)
        write(tab + 'self.Layout()\n')
    else: write(tab + 'pass\n')
    # end tag
    write(tab + '# end wxGlade\n')
    if prev_src is not None and not is_new:
        # replace the lines inside the __do_layout wxGlade block
        # with the new ones
        tag = '<%swxGlade replace %s %s>' % (nonce, code_obj.klass,
                                             '__do_layout')
        if prev_src.content.find(tag) < 0:
            # no __do_layout tag found, issue a warning and do nothing
            print >> sys.stderr, "WARNING: wxGlade __do_layout block " \
                  "not found, __do_layout code NOT generated"
        else:
            prev_src.content = prev_src.content.replace(tag, "".join(buffer))

    # the code has been generated
    classes[code_obj.klass].done = True

    write('\n# end of class %s\n\n\n' % code_obj.klass)

    if not multiple_files and prev_src is not None:
        # if this is a new class, add its code to the new_classes list of the
        # SourceFileContent instance
        if is_new: prev_src.new_classes.append("".join(buffer))
        return

    if multiple_files:
        if prev_src is not None:
            tag = '<%swxGlade insert new_classes>' % nonce
            prev_src.content = prev_src.content.replace(tag, "") #code)

            # insert the extra modules
            tag = '<%swxGlade extra_modules>\n' % nonce
            code = "".join(_current_extra_modules.keys())
            prev_src.content = prev_src.content.replace(tag, code)
            
            # insert the module dependencies of this class
            extra_modules = classes[code_obj.klass].dependencies.keys()
            deps = ['# begin wxGlade: dependencies\n'] + extra_modules + \
                   ['# end wxGlade\n']
##             for module in extra_modules:
##                 deps.append('from %s import %s\n' % (module, module))
##             deps.append('# end wxGlade\n')
            tag = '<%swxGlade replace dependencies>' % nonce
            prev_src.content = prev_src.content.replace(tag, "".join(deps))
            
            # store the new file contents to disk
            try: out = open(filename, 'w')
            except:
                raise IOError("py_codegen.add_class: %s, %s, %s" % \
                              (out_dir, prev_src.name, code_obj.klass))
            out.write(prev_src.content)
            out.close()
            return

        # create the new source file
        filename = os.path.join(out_dir, code_obj.klass + '.py')
        try: out = open(filename, 'w')
        except:
            raise IOError("py_codegen.add_class: %s, %s, %s" % \
                          (out_dir, filename, code_obj.klass))
        write = out.write
        # write the common lines
        for line in header_lines: write(line)
        
        # write the module dependecies for this class
        #extra_modules = classes[code_obj.klass].dependencies
        write('\n# begin wxGlade: dependencies\n')
        for module in classes[code_obj.klass].dependencies:
            write(module)
## extra_modules: write(module)
##             write('from %s import %s\n' % (module, module))
        write('# end wxGlade\n')
        write('\n')
        
        # write the class body
        for line in buffer: write(line)
        out.close()

    else: # not multiple_files
        # write the class body onto the single source file
        for dep in classes[code_obj.klass].dependencies:
            _current_extra_modules[dep] = 1
        write = output_file.write
        for line in buffer: write(line)
        

def add_app(app_attrs, top_win_class):
    """\
    Generates the code for a wxApp instance.
    If the file to write into already exists, this function does nothing.
    """
    name = app_attrs.get('name')
    if not name: name = 'app'

    if not multiple_files: prev_src = previous_source
    else:
        filename = os.path.join(out_dir, name + '.py')
        if not os.path.exists(filename): prev_src = None
        else:
            # prev_src doesn't need to be a SourceFileContent instance in this
            # case, as we do nothing if it is not None
            prev_src = 1
        
    if prev_src is not None:
        return # do nothing if the file existed
    
    klass = app_attrs.get('class')
    top_win = app_attrs.get('top_window')
    if not top_win: return # do nothing if there is no top window
    lines = []
    append = lines.append
    if klass:
        tab = tabs(2)
        append('class %s(wxApp):\n' % klass)
        append(tabs(1) + 'def OnInit(self):\n')
    else:
        tab = tabs(1)
        append('if __name__ == "__main__":\n')
        append(tab + '%s = wxPySimpleApp()\n' % name)
    append(tab + 'wxInitAllImageHandlers()\n') # we add this to avoid troubles
    append(tab + '%s = %s(None, -1, "")\n' % (top_win, top_win_class))
    if klass:
        append(tab + 'self.SetTopWindow(%s)\n' % top_win)
        append(tab + '%s.Show(1)\n' % top_win)
        append(tab + 'return 1\n\n')
        append('# end of class %s\n\n' % klass)
        append('if __name__ == "__main__":\n')
        tab = tabs(1)
        append(tab + '%s = %s()\n' % (name, klass))
    else:
        append(tab + '%s.SetTopWindow(%s)\n' % (name, top_win))
        append(tab + '%s.Show(1)\n' % top_win)
    append(tab + '%s.MainLoop()\n' % name)

    if multiple_files:
        filename = os.path.join(out_dir, name + '.py')
        try: out = open(filename, 'w')
        except: raise IOError("py_codegen.add_app: %s, %s" % (out_dir, name))
        write = out.write
        write('#!/usr/bin/env python\n')
        # write the common lines
        for line in header_lines: write(line)
        # import the top window module
        write('from %s import %s\n\n' % (top_win_class, top_win_class))
        # write the wxApp code
        for line in lines: write(line)
        out.close()
        # make the file executable
        try: os.chmod(filename, 0755)
        except OSError: pass # this is not a bad error
    else:
        write = output_file.write
        for line in lines: write(line)


def generate_code_size(obj):
    """\
    returns the code fragment that sets the size of the given object.
    """
    if obj.is_toplevel: name = 'self'
    else: name = 'self.%s' % obj.name
    size = obj.properties.get('size', '').strip()
    use_dialog_units = (size[-1] == 'd')
    if use_dialog_units:
        return name + '.SetSize(wxDLG_SZE(%s, (%s)))\n' % (name, size[:-1])
    else:
        return name + '.SetSize((%s))\n' % size

def _string_to_colour(s):
    return '%d, %d, %d' % (int(s[1:3], 16), int(s[3:5], 16), int(s[5:], 16))

def generate_code_foreground(obj): 
    """\
    returns the code fragment that sets the foreground colour of
    the given object.
    """
    if obj.is_toplevel: self = 'self'
    else: self = 'self.%s' % obj.name
    try:
        color = 'wxColour(%s)' % \
                _string_to_colour(obj.properties['foreground'])
    except (IndexError, ValueError): # the color is from system settings
        color = 'wxSystemSettings_GetSystemColour(%s)' % \
                obj.properties['foreground']
    return self + '.SetForegroundColour(%s)\n' % color

def generate_code_background(obj):
    """\
    returns the code fragment that sets the background colour of
    the given object.
    """
    if obj.is_toplevel: self = 'self'
    else: self = 'self.%s' % obj.name
    try:
        color = 'wxColour(%s)' % \
                _string_to_colour(obj.properties['background'])
    except (IndexError, ValueError): # the color is from system settings
        color = 'wxSystemSettings_GetSystemColour(%s)' % \
                obj.properties['background']
    return self + '.SetBackgroundColour(%s)\n' % color

def generate_code_font(obj):
    """\
    returns the code fragment that sets the font of the given object.
    """
    font = obj.properties['font'] 
    size = font['size']; family = font['family']
    underlined = font['underlined']
    style = font['style']; weight = font['weight']
    face = '"%s"' % font['face'].replace('"', r'\"')
    if obj.is_toplevel: self = 'self'
    else: self = 'self.%s' % obj.name
    return self + '.SetFont(wxFont(%s, %s, %s, %s, %s, %s))\n' % \
            (size, family, style, weight, underlined, face)

def generate_code_id(obj):
    """\
    returns a 2-tuple of strings representing the LOC that sets the id of the
    given object: the first line is the declaration of the variable, and is
    empty if the object's id is a constant, and the second line is the value
    of the id
    """
    id = obj.properties.get('id')
    if id is None: return '', '-1'
    tokens = id.split('=')
    if len(tokens) > 1: name, val = tokens[:2]
    else: return '', tokens[0] # we assume name is declared elsewhere
    if not name: return '', val
    return ('%s = %s\n' % (name, val), name)

def generate_code_tooltip(obj):
    """\
    returns the code fragment that sets the tooltip of the given object.
    """
    if obj.is_toplevel: self = 'self'
    else: self = 'self.%s' % obj.name
    return self + '.SetToolTipString("%s")\n' % \
            obj.properties['tooltip'].replace('"', r'\"')

def generate_common_properties(widget):
    """\
    generates the code for various properties common to all widgets (background
    and foreground colors, font, ...)
    Returns a list of strings containing the generated code
    """
    prop = widget.properties
    out = []
    if prop.get('size', '').strip(): out.append(generate_code_size(widget))
    if prop.get('background'): out.append(generate_code_background(widget))
    if prop.get('foreground'): out.append(generate_code_foreground(widget))
    if prop.get('font'): out.append(generate_code_font(widget))
    # tooltip
    if prop.get('tooltip'): out.append(generate_code_tooltip(widget))
    return out


# custom property handlers
class FontPropertyHandler:
    """Handler for font properties"""
    font_families = { 'default': 'wxDEFAULT', 'decorative': 'wxDECORATIVE',
                      'roman': 'wxROMAN', 'swiss': 'wxSWISS',
                      'script': 'wxSCRIPT', 'modern': 'wxMODERN',
                      'teletype': 'wxTELETYPE' }
    font_styles = { 'normal': 'wxNORMAL', 'slant': 'wxSLANT',
                    'italic': 'wxITALIC' }
    font_weights = { 'normal': 'wxNORMAL', 'light': 'wxLIGHT',
                     'bold': 'wxBOLD' }
    def __init__(self):
        self.dicts = { 'family': self.font_families, 'style': self.font_styles,
                       'weight': self.font_weights }
        self.attrs = { 'size': '0', 'style': '0', 'weight': '0', 'family': '0',
                       'underlined': '0', 'face': '' }
        self.current = None 
        self.curr_data = []
        
    def start_elem(self, name, attrs):
        self.curr_data = []
        if name != 'font' and name in self.attrs:
            self.current = name
        else: self.current = None
            
    def end_elem(self, name, code_obj):
        if name == 'font':
            code_obj.properties['font'] = self.attrs
            return True
        elif self.current is not None:
            decode = self.dicts.get(self.current)
            if decode: val = decode.get("".join(self.curr_data), '0')
            else: val = "".join(self.curr_data)
            self.attrs[self.current] = val
        
    def char_data(self, data):
        self.curr_data.append(data)

# end of class FontPropertyHandler


class DummyPropertyHandler:
    """Empty handler for properties that do not need code"""
    def start_elem(self, name, attrs): pass
    def end_elem(self, name, code_obj): return True
    def char_data(self, data): pass

# end of class DummyPropertyHandler


# dictionary whose items are custom handlers for widget properties
_global_property_writers = { 'font': FontPropertyHandler }

# dictionary of dictionaries of property handlers specific for a widget
# the keys are the class names of the widgets
# Ex: _property_writers['wxRadioBox'] = {'choices', choices_handler}
_property_writers = {}


# map of widget class names to a list of extra modules needed for the
# widget. Example: 'wxGrid': 'from wxPython.grid import *\n'
_widget_extra_modules = {}

# set of lines of extra modules to add to the current file
_current_extra_modules = {} 

def get_property_handler(property_name, widget_name):
    try: cls = _property_writers[widget_name][property_name]
    except KeyError: cls = _global_property_writers.get(property_name, None)
    if cls: return cls()
    return None

def add_property_handler(property_name, handler, widget_name=None):
    """\
    sets a function to parse a portion of XML to get the value of the property
    property_name. If widget_name is not None, the function is called only if
    the property in inside a widget whose class is widget_name
    """
    if widget_name is None: _global_property_writers[property_name] = handler
    else:
        try: _property_writers[widget_name][property_name] = handler
        except KeyError:
            _property_writers[widget_name] = { property_name: handler }

def add_widget_handler(widget_name, handler,
                       properties_handler=generate_common_properties,
                       import_modules=None):
    """\
    sets the functions to generate the code for the widget whose base class
    is 'widget_name':
     - handler: function that writes the code
     - properties_handler: function that writes extra code to set the
                           properties of the widget if it is a toplevel class
     - import_modules: list of modules to import
                       (eg. ['from wxPython.grid import *\n'])
    """
    obj_builders[widget_name] = handler
    obj_properties[widget_name] = properties_handler
    if import_modules is not None:
        _widget_extra_modules[widget_name] = import_modules
