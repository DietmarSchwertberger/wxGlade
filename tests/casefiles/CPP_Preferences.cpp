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

#include "CPP_Preferences.h"

// begin wxGlade: ::extracode
// end wxGlade



wxGladePreferencesUI::wxGladePreferencesUI(wxWindow* parent, int id, const wxString& title, const wxPoint& pos, const wxSize& size, long style):
    wxDialog(parent, id, title, pos, size, wxDEFAULT_DIALOG_STYLE)
{
    // begin wxGlade: wxGladePreferencesUI::wxGladePreferencesUI
    notebook_1 = new wxNotebook(this, wxID_ANY, wxDefaultPosition, wxDefaultSize, 0);
    notebook_1_pane_2 = new wxPanel(notebook_1, wxID_ANY);
    sizer_6_staticbox = new wxStaticBox(notebook_1_pane_2, wxID_ANY, _("Local widget path"));
    notebook_1_pane_1 = new wxPanel(notebook_1, wxID_ANY);
    use_menu_icons = new wxCheckBox(notebook_1_pane_1, wxID_ANY, _("Use icons in menu items"));
    frame_tool_win = new wxCheckBox(notebook_1_pane_1, wxID_ANY, _("Show properties and tree windows as small frames"));
    show_progress = new wxCheckBox(notebook_1_pane_1, wxID_ANY, _("Show progress dialog when loading wxg files"));
    remember_geometry = new wxCheckBox(notebook_1_pane_1, wxID_ANY, _("Remember position and size of wxGlade windows"));
    show_sizer_handle = new wxCheckBox(notebook_1_pane_1, wxID_ANY, _("Show \"handles\" of sizers"));
    use_kde_dialogs = new wxCheckBox(notebook_1_pane_1, wxID_ANY, _("Use native file dialogs on KDE"));
    open_save_path = new wxTextCtrl(notebook_1_pane_1, wxID_ANY, wxEmptyString);
    codegen_path = new wxTextCtrl(notebook_1_pane_1, wxID_ANY, wxEmptyString);
    number_history = new wxSpinCtrl(notebook_1_pane_1, wxID_ANY, wxT("4"), wxDefaultPosition, wxDefaultSize, wxSP_ARROW_KEYS, 0, 100);
    buttons_per_row = new wxSpinCtrl(notebook_1_pane_1, wxID_ANY, wxT("5"), wxDefaultPosition, wxDefaultSize, wxSP_ARROW_KEYS, 1, 100);
    use_dialog_units = new wxCheckBox(notebook_1_pane_2, wxID_ANY, _("Use dialog units by default for size properties"));
    wxg_backup = new wxCheckBox(notebook_1_pane_2, wxID_ANY, _("Create backup wxg files"));
    codegen_backup = new wxCheckBox(notebook_1_pane_2, wxID_ANY, _("Create backup files for generated source"));
    allow_duplicate_names = new wxCheckBox(notebook_1_pane_2, wxID_ANY, _("Allow duplicate widget names"));
    default_border = new wxCheckBox(notebook_1_pane_2, wxID_ANY, _("Default border width for widgets"));
    default_border_size = new wxSpinCtrl(notebook_1_pane_2, wxID_ANY, wxT(""), wxDefaultPosition, wxDefaultSize, wxSP_ARROW_KEYS, 0, 20);
    autosave = new wxCheckBox(notebook_1_pane_2, wxID_ANY, _("Auto save wxg files every "));
    autosave_delay = new wxSpinCtrl(notebook_1_pane_2, wxID_ANY, wxT("120"), wxDefaultPosition, wxDefaultSize, wxSP_ARROW_KEYS, 30, 300);
    write_timestamp = new wxCheckBox(notebook_1_pane_2, wxID_ANY, _("Insert timestamp on generated source files"));
    write_generated_from = new wxCheckBox(notebook_1_pane_2, wxID_ANY, _("Insert .wxg file name on generated source files"));
    const wxString backup_suffix_choices[] = {
        _("append ~ to filename"),
        _("append .bak to filename")
    };
    backup_suffix = new wxRadioBox(notebook_1_pane_2, wxID_ANY, _("Backup options"), wxDefaultPosition, wxDefaultSize, 2, backup_suffix_choices, 2, wxRA_SPECIFY_COLS);
    local_widget_path = new wxTextCtrl(notebook_1_pane_2, wxID_ANY, wxEmptyString);
    choose_widget_path = new wxButton(notebook_1_pane_2, wxID_ANY, _("..."), wxDefaultPosition, wxDefaultSize, wxBU_EXACTFIT);
    ok = new wxButton(this, wxID_OK, wxEmptyString);
    cancel = new wxButton(this, wxID_CANCEL, wxEmptyString);

    set_properties();
    do_layout();
    // end wxGlade
}


void wxGladePreferencesUI::set_properties()
{
    // begin wxGlade: wxGladePreferencesUI::set_properties
    SetTitle(_("wxGlade: preferences"));
    wxIcon _icon;
    _icon.CopyFromBitmap(wxBitmap(_icon_path, wxBITMAP_TYPE_ANY));
    SetIcon(_icon);
    use_menu_icons->SetValue(1);
    frame_tool_win->SetValue(1);
    show_progress->SetValue(1);
    remember_geometry->SetValue(1);
    show_sizer_handle->SetValue(1);
    use_kde_dialogs->SetValue(1);
    open_save_path->SetMinSize(wxSize(196, -1));
    codegen_path->SetMinSize(wxSize(196, -1));
    number_history->SetMinSize(wxSize(196, -1));
    buttons_per_row->SetMinSize(wxSize(196, -1));
    wxg_backup->SetValue(1);
    codegen_backup->SetValue(1);
    allow_duplicate_names->Hide();
    default_border_size->SetMinSize(wxSize(45, 22));
    autosave_delay->SetMinSize(wxSize(45, 22));
    write_timestamp->SetValue(1);
    backup_suffix->SetSelection(0);
    ok->SetDefault();
    // end wxGlade
}


void wxGladePreferencesUI::do_layout()
{
    // begin wxGlade: wxGladePreferencesUI::do_layout
    wxBoxSizer* sizer_1 = new wxBoxSizer(wxVERTICAL);
    wxBoxSizer* sizer_2 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_5 = new wxBoxSizer(wxVERTICAL);
    wxStaticBoxSizer* sizer_6 = new wxStaticBoxSizer(sizer_6_staticbox, wxHORIZONTAL);
    wxBoxSizer* sizer_7_copy = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_7 = new wxBoxSizer(wxHORIZONTAL);
    wxBoxSizer* sizer_3 = new wxBoxSizer(wxVERTICAL);
    wxFlexGridSizer* sizer_4 = new wxFlexGridSizer(4, 2, 0, 0);
    sizer_3->Add(use_menu_icons, 0, wxALL|wxEXPAND, 5);
    sizer_3->Add(frame_tool_win, 0, wxALL|wxEXPAND, 5);
    sizer_3->Add(show_progress, 0, wxALL|wxEXPAND, 5);
    sizer_3->Add(remember_geometry, 0, wxALL|wxEXPAND, 5);
    sizer_3->Add(show_sizer_handle, 0, wxALL|wxEXPAND, 5);
    sizer_3->Add(use_kde_dialogs, 0, wxALL|wxEXPAND, 5);
    wxStaticText* label_1 = new wxStaticText(notebook_1_pane_1, wxID_ANY, _("Initial path for \nfile opening/saving dialogs:"));
    sizer_4->Add(label_1, 0, wxALL|wxALIGN_CENTER_VERTICAL, 5);
    sizer_4->Add(open_save_path, 1, wxALL|wxALIGN_CENTER_VERTICAL, 5);
    wxStaticText* label_2_copy = new wxStaticText(notebook_1_pane_1, wxID_ANY, _("Initial path for \ncode generation file dialogs:"));
    sizer_4->Add(label_2_copy, 0, wxALL|wxALIGN_CENTER_VERTICAL, 5);
    sizer_4->Add(codegen_path, 1, wxALL|wxALIGN_CENTER_VERTICAL, 5);
    wxStaticText* label_2 = new wxStaticText(notebook_1_pane_1, wxID_ANY, _("Number of items in file history"));
    sizer_4->Add(label_2, 0, wxALL|wxALIGN_CENTER_VERTICAL, 5);
    sizer_4->Add(number_history, 1, wxALL|wxALIGN_CENTER_VERTICAL, 5);
    wxStaticText* label_2_copy_1 = new wxStaticText(notebook_1_pane_1, wxID_ANY, _("Number of buttons per row\nin the main palette"));
    sizer_4->Add(label_2_copy_1, 0, wxALL|wxALIGN_CENTER_VERTICAL, 5);
    sizer_4->Add(buttons_per_row, 1, wxALL|wxALIGN_CENTER_VERTICAL, 5);
    sizer_4->AddGrowableCol(1);
    sizer_3->Add(sizer_4, 0, wxEXPAND, 3);
    notebook_1_pane_1->SetSizer(sizer_3);
    sizer_5->Add(use_dialog_units, 0, wxALL|wxEXPAND, 5);
    sizer_5->Add(wxg_backup, 0, wxALL|wxEXPAND, 5);
    sizer_5->Add(codegen_backup, 0, wxALL|wxEXPAND, 5);
    sizer_5->Add(allow_duplicate_names, 0, wxALL|wxEXPAND, 5);
    sizer_7->Add(default_border, 0, wxALL|wxALIGN_CENTER_VERTICAL, 5);
    sizer_7->Add(default_border_size, 0, wxALL, 5);
    sizer_5->Add(sizer_7, 0, wxEXPAND, 0);
    sizer_7_copy->Add(autosave, 0, wxLEFT|wxTOP|wxBOTTOM|wxALIGN_CENTER_VERTICAL, 5);
    sizer_7_copy->Add(autosave_delay, 0, wxTOP|wxBOTTOM, 5);
    wxStaticText* label_3 = new wxStaticText(notebook_1_pane_2, wxID_ANY, _(" seconds"));
    sizer_7_copy->Add(label_3, 0, wxTOP|wxBOTTOM|wxALIGN_CENTER_VERTICAL|wxFIXED_MINSIZE, 5);
    sizer_5->Add(sizer_7_copy, 0, wxEXPAND, 0);
    sizer_5->Add(write_timestamp, 0, wxALL|wxEXPAND, 5);
    sizer_5->Add(write_generated_from, 0, wxALL|wxEXPAND, 5);
    sizer_5->Add(backup_suffix, 0, wxALL|wxEXPAND, 5);
    sizer_6->Add(local_widget_path, 1, wxALL, 3);
    sizer_6->Add(choose_widget_path, 0, wxALL|wxALIGN_CENTER_VERTICAL, 3);
    sizer_5->Add(sizer_6, 0, wxALL|wxEXPAND, 5);
    notebook_1_pane_2->SetSizer(sizer_5);
    notebook_1->AddPage(notebook_1_pane_1, _("Interface"));
    notebook_1->AddPage(notebook_1_pane_2, _("Other"));
    sizer_1->Add(notebook_1, 1, wxALL|wxEXPAND, 5);
    sizer_2->Add(ok, 0, 0, 0);
    sizer_2->Add(cancel, 0, wxLEFT, 10);
    sizer_1->Add(sizer_2, 0, wxALL|wxALIGN_RIGHT, 10);
    SetSizer(sizer_1);
    sizer_1->Fit(this);
    Layout();
    Centre();
    // end wxGlade
}

#include "wx/intl.h"

#ifndef APP_CATALOG
#define APP_CATALOG "app"  // replace with the appropriate catalog name
#endif

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
    wxGladePreferencesUI* dialog_1 = new wxGladePreferencesUI(NULL, wxID_ANY, wxEmptyString);
    SetTopWindow(dialog_1);
    dialog_1->Show();
    return true;
}
