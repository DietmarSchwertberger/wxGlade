# generated by wxGlade 0.2 on Sat Nov 30 15:30:36 2002
# $Id: font_dialog.py,v 1.3 2003/05/13 10:13:51 agriggio Exp $

from wxPython.wx import *
import misc

_reverse_dict = misc._reverse_dict

class wxGladeFontDialog(wxDialog):
    font_families_to = { 'default': wxDEFAULT, 'decorative': wxDECORATIVE,
                         'roman': wxROMAN, 'swiss': wxSWISS,
                         'script':wxSCRIPT, 'modern': wxMODERN }
    font_families_from = _reverse_dict(font_families_to)
    font_styles_to = { 'normal': wxNORMAL, 'slant': wxSLANT,
                       'italic': wxITALIC }
    font_styles_from = _reverse_dict(font_styles_to)
    font_weights_to = { 'normal': wxNORMAL, 'light': wxLIGHT, 'bold': wxBOLD }
    font_weights_from = _reverse_dict(font_weights_to)

    import misc
    if misc.check_wx_version(2, 3, 3):
        font_families_to['teletype'] = wxTELETYPE 
        font_families_from[wxTELETYPE] = 'teletype'
        
    def __init__(self, *args, **kwds):
        # begin wxGlade: wxGladeFontDialog.__init__
        kwds["style"] = wxDEFAULT_DIALOG_STYLE
        wxDialog.__init__(self, *args, **kwds)
        self.label_2_copy = wxStaticText(self, -1, "Family:")
        self.label_3_copy = wxStaticText(self, -1, "Style:")
        self.label_4_copy = wxStaticText(self, -1, "Weight:")
        self.family = wxChoice(self, -1, choices=[
            "Default", "Decorative", "Roman", "Script", "Swiss", "Modern"])
        self.style = wxChoice(self, -1, choices=["Normal", "Slant", "Italic"])
        self.weight = wxChoice(self, -1, choices=["Normal", "Light", "Bold"])
        self.label_1 = wxStaticText(self, -1, "Size in points:")
        self.point_size = wxSpinCtrl(self, -1, "", min=0, max=100)
        self.underline = wxCheckBox(self, -1, "Underlined")
        self.font_btn = wxButton(self, -1, "Specific font...")
        self.static_line_1 = wxStaticLine(self, -1)
        self.ok_btn = wxButton(self, wxID_OK, "OK")
        self.cancel_btn = wxButton(self, wxID_CANCEL, "Cancel")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        self.value = None
        EVT_BUTTON(self, self.font_btn.GetId(), self.choose_specific_font)
        EVT_BUTTON(self, self.ok_btn.GetId(), self.on_ok)

    def choose_specific_font(self, event):
        dialog = wxFontDialog(self, wxFontData())
        if dialog.ShowModal() == wxID_OK:
            font = dialog.GetFontData().GetChosenFont()
            family = font.GetFamily()
            if misc.check_wx_version(2, 3, 3):
                for f in (wxVARIABLE, wxFIXED):
                    if family & f: family = family ^ f
            self.value = "['%s', '%s', '%s', '%s', '%s', '%s']" % \
                         (font.GetPointSize(),
                          self.font_families_from[family],
                          self.font_styles_from[font.GetStyle()],
                          self.font_weights_from[font.GetWeight()],
                          font.GetUnderlined(), font.GetFaceName())
            self.EndModal(wxID_OK)

    def on_ok(self, event):
        self.value = "['%s', '%s', '%s', '%s', '%s', '']" % \
                     (self.point_size.GetValue(),
                      self.family.GetStringSelection().lower(),
                      self.style.GetStringSelection().lower(),
                      self.weight.GetStringSelection().lower(),
                      self.underline.GetValue())
        self.EndModal(wxID_OK)
        
    def get_value(self):
        return self.value

    def set_value(self, props):
        self.family.SetStringSelection(props[1].capitalize())
        self.style.SetStringSelection(props[2].capitalize())
        self.weight.SetStringSelection(props[3].capitalize())
        try:
            self.underline.SetValue(int(props[4]))
            self.point_size.SetValue(int(props[0]))            
        except ValueError:
            import traceback; traceback.print_exc()
    
    def __set_properties(self):
        # begin wxGlade: wxGladeFontDialog.__set_properties
        self.SetTitle("Select font attributes")
        self.family.SetSelection(0)
        self.style.SetSelection(0)
        self.weight.SetSelection(0)
        self.ok_btn.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: wxGladeFontDialog.__do_layout
        sizer_1 = wxBoxSizer(wxVERTICAL)
        sizer_2 = wxBoxSizer(wxVERTICAL)
        sizer_4 = wxBoxSizer(wxHORIZONTAL)
        sizer_5 = wxBoxSizer(wxVERTICAL)
        grid_sizer_1_copy = wxFlexGridSizer(2, 3, 2, 10)
        grid_sizer_2_copy = wxFlexGridSizer(2, 3, 2, 5)
        grid_sizer_2_copy.Add(self.label_2_copy, 0, wxALIGN_BOTTOM, 3)
        grid_sizer_2_copy.Add(self.label_3_copy, 0, wxALIGN_BOTTOM, 3)
        grid_sizer_2_copy.Add(self.label_4_copy, 0, wxALIGN_BOTTOM, 3)
        grid_sizer_2_copy.Add(self.family, 0, wxEXPAND, 0)
        grid_sizer_2_copy.Add(self.style, 0, wxEXPAND, 0)
        grid_sizer_2_copy.Add(self.weight, 0, wxEXPAND, 0)
        grid_sizer_2_copy.AddGrowableCol(0)
        grid_sizer_2_copy.AddGrowableCol(1)
        grid_sizer_2_copy.AddGrowableCol(2)
        sizer_5.Add(grid_sizer_2_copy, 0, wxEXPAND, 0)
        grid_sizer_1_copy.Add(self.label_1, 0, wxALIGN_BOTTOM, 0)
        grid_sizer_1_copy.Add(20, 5, 0, wxALIGN_BOTTOM, 0)
        grid_sizer_1_copy.Add(20, 5, 0, wxALIGN_BOTTOM, 0)
        grid_sizer_1_copy.Add(self.point_size, 0, 0, 0)
        grid_sizer_1_copy.Add(self.underline, 0, wxEXPAND, 0)
        grid_sizer_1_copy.Add(self.font_btn, 0, 0, 0)
        grid_sizer_1_copy.AddGrowableCol(1)
        sizer_5.Add(grid_sizer_1_copy, 0, wxTOP|wxEXPAND, 3)
        sizer_5.Add(self.static_line_1, 0, wxTOP|wxEXPAND, 8)
        sizer_2.Add(sizer_5, 0, wxEXPAND, 0)
        sizer_4.Add(self.ok_btn, 0, wxRIGHT, 12)
        sizer_4.Add(self.cancel_btn, 0, 0, 0)
        sizer_2.Add(sizer_4, 0, wxTOP|wxALIGN_RIGHT, 9)
        sizer_1.Add(sizer_2, 1, wxALL|wxEXPAND, 10)
        self.SetAutoLayout(1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()
        # end wxGlade

# end of class wxGladeFontDialog
