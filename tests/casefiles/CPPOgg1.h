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

#ifndef CPPOGG1_H
#define CPPOGG1_H

#include <wx/wx.h>
#include <wx/image.h>
#include <wx/intl.h>

#ifndef APP_CATALOG
#define APP_CATALOG "myapp"  // replace with the appropriate catalog name
#endif


// begin wxGlade: ::dependencies
#include <wx/notebook.h>
#include <wx/statline.h>
// end wxGlade

// begin wxGlade: ::extracode
// extra code added using wxGlade
#include <wx/utils.h>
// end wxGlade


class CPPOgg1_MyDialog: public wxDialog {
public:
    // begin wxGlade: CPPOgg1_MyDialog::ids
    // end wxGlade

    CPPOgg1_MyDialog(wxWindow* parent, int id, const wxString& title, const wxPoint& pos=wxDefaultPosition, const wxSize& size=wxDefaultSize, long style=wxDEFAULT_DIALOG_STYLE);

private:
    // begin wxGlade: CPPOgg1_MyDialog::methods
    void set_properties();
    void do_layout();
    // end wxGlade

protected:
    // begin wxGlade: CPPOgg1_MyDialog::attributes
    wxTextCtrl* text_ctrl_1;
    wxButton* button_3;
    wxPanel* notebook_1_pane_1;
    wxRadioBox* radio_box_1;
    wxPanel* notebook_1_pane_2;
    wxTextCtrl* text_ctrl_2;
    wxPanel* notebook_1_pane_3;
    wxStaticText* label_2;
    wxTextCtrl* text_ctrl_3;
    wxButton* button_4;
    wxCheckBox* checkbox_1;
    wxPanel* notebook_1_pane_4;
    wxNotebook* notebook_1;
    wxStaticLine* static_line_1;
    wxButton* button_5;
    wxButton* button_2;
    wxButton* button_1;
    // end wxGlade

    DECLARE_EVENT_TABLE();

public:
    void startConverting(wxCommandEvent &event); // wxGlade: <event_handler>
}; // wxGlade: end class


#endif // CPPOGG1_H
