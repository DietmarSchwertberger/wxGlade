// -*- C++ -*-
//
// generated by wxGlade "faked test version"
//
// Example for compiling a single file project under Linux using g++:
//  g++ MyApp.cpp $(wx-config --libs) $(wx-config --cxxflags) -o MyApp
//
// Example for compiling a multi file project under Linux using g++:
//  g++ main.cpp $(wx-config --libs) $(wx-config --cxxflags) -o MyApp Dialog1.cpp Frame1.cpp
//

#include "AllWidgets_28.h"

// begin wxGlade: ::extracode
// end wxGlade



All_Widgets_Frame::All_Widgets_Frame(wxWindow* parent, int id, const wxString& title, const wxPoint& pos, const wxSize& size, long style):
    wxFrame(parent, id, title, pos, size, wxDEFAULT_FRAME_STYLE)
{
    // begin wxGlade: All_Widgets_Frame::All_Widgets_Frame
    notebook_1 = new wxNotebook(this, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxNB_BOTTOM);
    notebook_1_wxTextCtrl = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_Spacer = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxStaticLine = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxStaticBitmap = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxSpinCtrl = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxSpinButton = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxSlider = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxRadioButton = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxRadioBox = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxListCtrl = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxListBox = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxDatePickerCtrl = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxComboBox = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxChoice = new wxPanel(notebook_1, wxID_ANY);
    notebook_1_wxCalendarCtrl = new wxPanel(notebook_1, wxID_ANY);
    sizer_8_staticbox = new wxStaticBox(notebook_1_wxRadioButton, wxID_ANY, _("My RadioButton Group"));
    notebook_1_wxBitmapButton = new wxPanel(notebook_1, wxID_ANY);
    bitmap_button_1 = new wxBitmapButton(notebook_1_wxBitmapButton, wxID_ANY, wxBitmap("icon.xpm", wxBITMAP_TYPE_ANY));
    calendar_ctrl_1 = new wxCalendarCtrl(notebook_1_wxCalendarCtrl, wxID_ANY);
    const wxString *choice_empty_choices = NULL;
    choice_empty = new wxChoice(notebook_1_wxChoice, wxID_ANY, wxDefaultPosition, wxDefaultSize, 0, choice_empty_choices);
    const wxString choice_filled_choices[] = {
        _("Item 1"),
        _("Item 2 (pre-selected)"),
    };
    choice_filled = new wxChoice(notebook_1_wxChoice, wxID_ANY, wxDefaultPosition, wxDefaultSize, 2, choice_filled_choices);
    const wxString *combo_box_empty_choices = NULL;
    combo_box_empty = new wxComboBox(notebook_1_wxComboBox, wxID_ANY, wxT(""), wxDefaultPosition, wxDefaultSize, 0, combo_box_empty_choices, wxCB_DROPDOWN);
    const wxString combo_box_filled_choices[] = {
        _("Item 1 (pre-selected)"),
        _("Item 2"),
    };
    combo_box_filled = new wxComboBox(notebook_1_wxComboBox, wxID_ANY, wxT(""), wxDefaultPosition, wxDefaultSize, 2, combo_box_filled_choices, wxCB_DROPDOWN);
    datepicker_ctrl_1 = new wxDatePickerCtrl(notebook_1_wxDatePickerCtrl, wxID_ANY);
    const wxString *list_box_empty_choices = NULL;
    list_box_empty = new wxListBox(notebook_1_wxListBox, wxID_ANY, wxDefaultPosition, wxDefaultSize, 0, list_box_empty_choices);
    const wxString list_box_filled_choices[] = {
        _("Item 1"),
        _("Item 2 (pre-selected)"),
    };
    list_box_filled = new wxListBox(notebook_1_wxListBox, wxID_ANY, wxDefaultPosition, wxDefaultSize, 2, list_box_filled_choices);
    list_ctrl_1 = new wxListCtrl(notebook_1_wxListCtrl, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxLC_REPORT|wxSUNKEN_BORDER);
    const wxString *radio_box_empty1_choices = NULL;
    radio_box_empty1 = new wxRadioBox(notebook_1_wxRadioBox, wxID_ANY, _("radio_box_empty1"), wxDefaultPosition, wxDefaultSize, 0, radio_box_empty1_choices, 0, wxRA_SPECIFY_ROWS);
    const wxString radio_box_filled1_choices[] = {
        _("choice 1"),
        _("choice 2 (pre-selected)"),
        _("choice 3"),
    };
    radio_box_filled1 = new wxRadioBox(notebook_1_wxRadioBox, wxID_ANY, _("radio_box_filled1"), wxDefaultPosition, wxDefaultSize, 3, radio_box_filled1_choices, 0, wxRA_SPECIFY_ROWS);
    const wxString *radio_box_empty2_choices = NULL;
    radio_box_empty2 = new wxRadioBox(notebook_1_wxRadioBox, wxID_ANY, _("radio_box_empty2"), wxDefaultPosition, wxDefaultSize, 0, radio_box_empty2_choices, 0, wxRA_SPECIFY_COLS);
    const wxString radio_box_filled2_choices[] = {
        _("choice 1"),
        _("choice 2 (pre-selected)"),
    };
    radio_box_filled2 = new wxRadioBox(notebook_1_wxRadioBox, wxID_ANY, _("radio_box_filled2"), wxDefaultPosition, wxDefaultSize, 2, radio_box_filled2_choices, 0, wxRA_SPECIFY_COLS);
    radio_btn_1 = new wxRadioButton(notebook_1_wxRadioButton, wxID_ANY, _("Alice"), wxDefaultPosition, wxDefaultSize, wxRB_GROUP);
    text_ctrl_1 = new wxTextCtrl(notebook_1_wxRadioButton, wxID_ANY, wxEmptyString);
    radio_btn_2 = new wxRadioButton(notebook_1_wxRadioButton, wxID_ANY, _("Bob"));
    text_ctrl_2 = new wxTextCtrl(notebook_1_wxRadioButton, wxID_ANY, wxEmptyString);
    radio_btn_3 = new wxRadioButton(notebook_1_wxRadioButton, wxID_ANY, _("Malroy"));
    text_ctrl_3 = new wxTextCtrl(notebook_1_wxRadioButton, wxID_ANY, wxEmptyString);
    gauge_1 = new wxGauge(notebook_1_wxSlider, wxID_ANY, 20);
    spin_button_1 = new wxSpinButton(notebook_1_wxSpinButton, wxID_ANY);
    spin_ctrl_1 = new wxSpinCtrl(notebook_1_wxSpinCtrl, wxID_ANY, wxT("4"), wxDefaultPosition, wxDefaultSize, wxSP_ARROW_KEYS|wxTE_AUTO_URL, 0, 100);
    notebook_1_wxSplitterWindow = new wxPanel(notebook_1, wxID_ANY);
    bitmap_code_nullbitmap = new wxStaticBitmap(notebook_1_wxStaticBitmap, wxID_ANY, (wxNullBitmap));
    bitmap_file = new wxStaticBitmap(notebook_1_wxStaticBitmap, wxID_ANY, wxBitmap("icon.xpm", wxBITMAP_TYPE_ANY));
    bitmap_nofile = new wxStaticBitmap(notebook_1_wxStaticBitmap, wxID_ANY, wxBitmap("non-existing.bmp", wxBITMAP_TYPE_ANY));
    static_line_2 = new wxStaticLine(notebook_1_wxStaticLine, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxLI_VERTICAL);
    static_line_3 = new wxStaticLine(notebook_1_wxStaticLine, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxLI_VERTICAL);
    static_line_4 = new wxStaticLine(notebook_1_wxStaticLine, wxID_ANY);
    static_line_5 = new wxStaticLine(notebook_1_wxStaticLine, wxID_ANY);
    label_3 = new wxStaticText(notebook_1_Spacer, wxID_ANY, _("Two labels with a"));
    label_2 = new wxStaticText(notebook_1_Spacer, wxID_ANY, _("spacer between"));
    text_ctrl = new wxTextCtrl(notebook_1_wxTextCtrl, wxID_ANY, _("This\nis\na\nmultiline\nwxTextCtrl"), wxDefaultPosition, wxDefaultSize, wxTE_LINEWRAP|wxTE_MULTILINE|wxTE_WORDWRAP);
    static_line_1 = new wxStaticLine(this, wxID_ANY);
    button_5 = new wxButton(this, wxID_CLOSE, wxEmptyString);
    button_1 = new wxButton(this, wxID_OK, wxEmptyString, wxDefaultPosition, wxDefaultSize, wxBU_TOP);

    set_properties();
    do_layout();
    // end wxGlade
}


void All_Widgets_Frame::set_properties()
{
    // begin wxGlade: All_Widgets_Frame::set_properties
    SetTitle(_("All Widgets"));
    bitmap_button_1->SetSize(bitmap_button_1->GetBestSize());
    bitmap_button_1->SetDefault();
    choice_filled->SetSelection(1);
    combo_box_filled->SetSelection(0);
    list_box_filled->SetSelection(1);
    radio_box_filled1->SetSelection(1);
    radio_box_filled2->SetSelection(1);
    // end wxGlade
}


void All_Widgets_Frame::do_layout()
{
    // begin wxGlade: All_Widgets_Frame::do_layout
    wxFlexGridSizer* sizer_1 = new wxFlexGridSizer(3, 1, 0, 0);
    wxFlexGridSizer* sizer_2 = new wxFlexGridSizer(1, 2, 0, 0);
    wxBoxSizer* sizer_18 = new wxBoxSizer(wxHORIZONTAL);
    wxFlexGridSizer* grid_sizer_3 = new wxFlexGridSizer(1, 3, 0, 0);
    wxBoxSizer* sizer_9 = new wxBoxSizer(wxVERTICAL);
    wxBoxSizer* sizer_10 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_11 = new wxBoxSizer(wxVERTICAL);
    wxBoxSizer* sizer_14 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_16 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_15 = new wxBoxSizer(wxHORIZONTAL);
    sizer_8_staticbox->Lower();
    wxStaticBoxSizer* sizer_8 = new wxStaticBoxSizer(sizer_8_staticbox, wxHORIZONTAL);
    wxFlexGridSizer* grid_sizer_2 = new wxFlexGridSizer(3, 2, 0, 0);
    wxGridSizer* grid_sizer_1 = new wxGridSizer(2, 2, 0, 0);
    wxBoxSizer* sizer_3 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_4 = new wxBoxSizer(wxVERTICAL);
    wxBoxSizer* sizer_17 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_6 = new wxBoxSizer(wxVERTICAL);
    wxBoxSizer* sizer_7 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_5 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_12 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_13 = new wxBoxSizer(wxHORIZONTAL);
    sizer_13->Add(bitmap_button_1, 1, wxALL|wxEXPAND, 5);
    notebook_1_wxBitmapButton->SetSizer(sizer_13);
    sizer_12->Add(calendar_ctrl_1, 1, wxALL|wxEXPAND, 5);
    notebook_1_wxCalendarCtrl->SetSizer(sizer_12);
    sizer_5->Add(choice_empty, 1, wxALL, 5);
    sizer_5->Add(choice_filled, 1, wxALL, 5);
    notebook_1_wxChoice->SetSizer(sizer_5);
    sizer_7->Add(combo_box_empty, 1, wxALL, 5);
    sizer_7->Add(combo_box_filled, 1, wxALL, 5);
    sizer_6->Add(sizer_7, 1, wxEXPAND, 0);
    notebook_1_wxComboBox->SetSizer(sizer_6);
    sizer_17->Add(datepicker_ctrl_1, 1, wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL|wxALL, 5);
    notebook_1_wxDatePickerCtrl->SetSizer(sizer_17);
    sizer_4->Add(list_box_empty, 1, wxALL|wxEXPAND, 5);
    sizer_4->Add(list_box_filled, 1, wxALL|wxEXPAND, 5);
    notebook_1_wxListBox->SetSizer(sizer_4);
    sizer_3->Add(list_ctrl_1, 1, wxALL|wxEXPAND, 5);
    notebook_1_wxListCtrl->SetSizer(sizer_3);
    grid_sizer_1->Add(radio_box_empty1, 1, wxALL|wxEXPAND, 5);
    grid_sizer_1->Add(radio_box_filled1, 1, wxALL|wxEXPAND, 5);
    grid_sizer_1->Add(radio_box_empty2, 1, wxALL|wxEXPAND, 5);
    grid_sizer_1->Add(radio_box_filled2, 1, wxALL|wxEXPAND, 5);
    notebook_1_wxRadioBox->SetSizer(grid_sizer_1);
    grid_sizer_2->Add(radio_btn_1, 1, wxALL|wxEXPAND, 5);
    grid_sizer_2->Add(text_ctrl_1, 1, wxALL|wxEXPAND, 5);
    grid_sizer_2->Add(radio_btn_2, 1, wxALL|wxEXPAND, 5);
    grid_sizer_2->Add(text_ctrl_2, 1, wxALL|wxEXPAND, 5);
    grid_sizer_2->Add(radio_btn_3, 1, wxALL|wxEXPAND, 5);
    grid_sizer_2->Add(text_ctrl_3, 1, wxALL|wxEXPAND, 5);
    sizer_8->Add(grid_sizer_2, 1, wxEXPAND, 0);
    notebook_1_wxRadioButton->SetSizer(sizer_8);
    sizer_15->Add(gauge_1, 1, wxALL, 5);
    notebook_1_wxSlider->SetSizer(sizer_15);
    sizer_16->Add(spin_button_1, 1, wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL|wxALL|wxEXPAND, 5);
    notebook_1_wxSpinButton->SetSizer(sizer_16);
    sizer_14->Add(spin_ctrl_1, 1, wxALL, 5);
    notebook_1_wxSpinCtrl->SetSizer(sizer_14);
    sizer_11->Add(bitmap_code_nullbitmap, 1, wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL|wxALL|wxEXPAND, 5);
    sizer_11->Add(bitmap_file, 1, wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL|wxALL|wxEXPAND, 5);
    sizer_11->Add(bitmap_nofile, 1, wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL|wxALL|wxEXPAND, 5);
    notebook_1_wxStaticBitmap->SetSizer(sizer_11);
    sizer_10->Add(static_line_2, 1, wxALL|wxEXPAND, 5);
    sizer_10->Add(static_line_3, 1, wxALL|wxEXPAND, 5);
    sizer_9->Add(sizer_10, 1, wxEXPAND, 0);
    sizer_9->Add(static_line_4, 1, wxALL|wxEXPAND, 5);
    sizer_9->Add(static_line_5, 1, wxALL|wxEXPAND, 5);
    notebook_1_wxStaticLine->SetSizer(sizer_9);
    grid_sizer_3->Add(label_3, 1, wxALL|wxEXPAND, 5);
    grid_sizer_3->Add(60, 20, 1, wxALL|wxEXPAND, 5);
    grid_sizer_3->Add(label_2, 1, wxALL|wxEXPAND, 5);
    notebook_1_Spacer->SetSizer(grid_sizer_3);
    sizer_18->Add(text_ctrl, 1, wxALL|wxEXPAND, 5);
    notebook_1_wxTextCtrl->SetSizer(sizer_18);
    notebook_1->AddPage(notebook_1_wxBitmapButton, _("wxBitmapButton"));
    notebook_1->AddPage(notebook_1_wxCalendarCtrl, _("wxCalendarCtrl"));
    notebook_1->AddPage(notebook_1_wxChoice, _("wxChoice"));
    notebook_1->AddPage(notebook_1_wxComboBox, _("wxComboBox"));
    notebook_1->AddPage(notebook_1_wxDatePickerCtrl, _("wxDatePickerCtrl"));
    notebook_1->AddPage(notebook_1_wxListBox, _("wxListBox"));
    notebook_1->AddPage(notebook_1_wxListCtrl, _("wxListCtrl"));
    notebook_1->AddPage(notebook_1_wxRadioBox, _("wxRadioBox"));
    notebook_1->AddPage(notebook_1_wxRadioButton, _("wxRadioButton"));
    notebook_1->AddPage(notebook_1_wxSlider, _("wxSlider"));
    notebook_1->AddPage(notebook_1_wxSpinButton, _("wxSpinButton"));
    notebook_1->AddPage(notebook_1_wxSpinCtrl, _("wxSpinCtrl"));
    notebook_1->AddPage(notebook_1_wxSplitterWindow, _("wxSplitterWindow"));
    notebook_1->AddPage(notebook_1_wxStaticBitmap, _("wxStaticBitmap"));
    notebook_1->AddPage(notebook_1_wxStaticLine, _("wxStaticLine"));
    notebook_1->AddPage(notebook_1_Spacer, _("wxStaticText (with Spacer)"));
    notebook_1->AddPage(notebook_1_wxTextCtrl, _("wxTextCtrl"));
    sizer_1->Add(notebook_1, 1, wxEXPAND, 0);
    sizer_1->Add(static_line_1, 0, wxALL|wxEXPAND, 5);
    sizer_2->Add(button_5, 0, wxALIGN_RIGHT|wxALL, 5);
    sizer_2->Add(button_1, 0, wxALIGN_RIGHT|wxALL, 5);
    sizer_1->Add(sizer_2, 0, wxALIGN_RIGHT, 0);
    SetSizer(sizer_1);
    sizer_1->Fit(this);
    sizer_1->SetSizeHints(this);
    sizer_1->AddGrowableRow(0);
    sizer_1->AddGrowableCol(0);
    Layout();
    Centre();
    // end wxGlade
}


BEGIN_EVENT_TABLE(All_Widgets_Frame, wxFrame)
    // begin wxGlade: All_Widgets_Frame::event_table
    EVT_BUTTON(wxID_ANY, All_Widgets_Frame::startConverting)
    // end wxGlade
END_EVENT_TABLE();


void All_Widgets_Frame::startConverting(wxCommandEvent &event)
{
    event.Skip();
    // notify the user that he hasn't implemented the event handler yet
    wxLogDebug(wxT("Event handler (All_Widgets_Frame::startConverting) not implemented yet"));
}


// wxGlade: add All_Widgets_Frame event handlers


class MyApp: public wxApp {
public:
    bool OnInit();
protected:
    wxLocale m_locale;  // locale we'll be using
};

IMPLEMENT_APP(MyApp)

bool MyApp::OnInit()
{
    m_locale.Init();
#ifdef APP_LOCALE_DIR
    m_locale.AddCatalogLookupPathPrefix(wxT(APP_LOCALE_DIR));
#endif
    m_locale.AddCatalog(wxT(APP_CATALOG));

    wxInitAllImageHandlers();
    All_Widgets_Frame* All_Widgets = new All_Widgets_Frame(NULL, wxID_ANY, wxEmptyString);
    SetTopWindow(All_Widgets);
    All_Widgets->Show();
    return true;
}