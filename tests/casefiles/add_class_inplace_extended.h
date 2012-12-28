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

#ifndef ADD_CLASS_INPLACE_ORIG_H
#define ADD_CLASS_INPLACE_ORIG_H

#include <wx/wx.h>
#include <wx/image.h>
#include "wx/intl.h"

#ifndef APP_CATALOG
#define APP_CATALOG "app"  // replace with the appropriate catalog name
#endif


// begin wxGlade: ::dependencies
#include <wx/statline.h>
#include <wx/hyperlink.h>
// end wxGlade

// begin wxGlade: ::extracode
// end wxGlade



class MyDialog1: public wxDialog {
public:
    // begin wxGlade: MyDialog1::ids
    // end wxGlade

    MyDialog1(wxWindow* parent, int id, const wxString& title, const wxPoint& pos=wxDefaultPosition, const wxSize& size=wxDefaultSize, long style=wxDEFAULT_DIALOG_STYLE);

private:
    // begin wxGlade: MyDialog1::methods
    void set_properties();
    void do_layout();
    // end wxGlade

protected:
    // begin wxGlade: MyDialog1::attributes
    wxHyperlinkCtrl* hyperlink_1;
    // end wxGlade
}; // wxGlade: end class

class MyDialog: public wxDialog {
public:
    // begin wxGlade: MyDialog::ids
    // end wxGlade

    MyDialog(wxWindow* parent, int id, const wxString& title, const wxPoint& pos=wxDefaultPosition, const wxSize& size=wxDefaultSize, long style=wxDEFAULT_DIALOG_STYLE);

private:
    // begin wxGlade: MyDialog::methods
    void set_properties();
    void do_layout();
    // end wxGlade

protected:
    // begin wxGlade: MyDialog::attributes
    wxTextCtrl* text_ctrl_1;
    wxStaticLine* static_line_1;
    wxButton* button_2;
    wxButton* button_1;
    // end wxGlade
}; // wxGlade: end class


#endif // ADD_CLASS_INPLACE_ORIG_H
