# perl_codegen.py : perl generator functions for wxBitmapButton objects
# $Id: perl_codegen.py,v 1.5 2003/08/07 12:22:01 agriggio Exp $
#
# Copyright (c) 2002-2003 D.H. aka crazyinsomniac on sourceforge
# License: MIT (see license.txt)
# THIS PROGRAM COMES WITH NO WARRANTY

import common, os

#this should be in common 
_bmp_str_types = {
    '.bmp' : 'wxBITMAP_TYPE_BMP',
    '.gif' : 'wxBITMAP_TYPE_GIF',
    '.xpm' : 'wxBITMAP_TYPE_XPM',
    '.jpg' : 'wxBITMAP_TYPE_JPEG',
    '.jpeg': 'wxBITMAP_TYPE_JPEG',
    '.png' : 'wxBITMAP_TYPE_PNG',
    '.pcx' : 'wxBITMAP_TYPE_PCX'
    }

class PerlCodeGenerator:
    def get_code(self, obj):
        plgen = common.code_writers['perl']
        prop = obj.properties
        id_name, id = plgen.generate_code_id(obj) 
        bmp_file = prop.get('bitmap', '')

        if not obj.parent.is_toplevel:
            parent = '$self->{%s}' % obj.parent.name
        else:
            parent = '$self'

        if not bmp_file:
            bmp = 'wxNullBitmap'
        elif bmp_file.startswith('var:'): # this is a variable holding XPM data
            bmp = 'Wx::Bitmap->newFromXPM(%s)' % bmp_file[4:].strip()
        else:
            bmp = 'Wx::Bitmap->new(%s, wxBITMAP_TYPE_ANY)' % \
                  plgen.quote_path(bmp_file)
        init = []
        if id_name: init.append(id_name)
        init.append('$self->{%s} = %s->new(%s, %s, %s);\n' % 
                    ( obj.name, obj.klass.replace('wx','Wx::',1),
                      parent, id, bmp) )

        props_buf = plgen.generate_common_properties(obj)

        disabled_bmp = prop.get('disabled_bitmap')
        if disabled_bmp:
            if disabled_bmp.startswith('var:'):
                var = disabled_bmp[4:].strip()
                props_buf.append(
                    '$self->{%s}->SetBitmapDisabled('
                    'Wx::Bitmap->newFromXPM(%s));\n' % (obj.name, var))
            else:
                props_buf.append(
                    '$self->{%s}->SetBitmapDisabled('
                    'Wx::Bitmap->new(%s, wxBITMAP_TYPE_ANY));\n' % \
                    (obj.name, plgen.quote_path(disabled_bmp)))
                
        if not prop.has_key('size'):
            props_buf.append(
                '$self->{%s}->SetSize($self->{%s}->GetBestSize());\n' %
                (obj.name, obj.name)
                )

        if prop.get('default', False):
            props_buf.append('$self->{%s}->SetDefault();\n' % obj.name)
        return init, props_buf, []

# end of class PerlCodeGenerator



def initialize():
    common.class_names['EditBitmapButton'] = 'wxBitmapButton'
    plgen = common.code_writers.get('perl')

    if plgen:
        plgen.add_widget_handler('wxBitmapButton', PerlCodeGenerator())
