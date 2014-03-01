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

#ifndef ALLWIDGETS_28_H
#define ALLWIDGETS_28_H

#include <wx/wx.h>
#include <wx/image.h>
#include "wx/intl.h"

#ifndef APP_CATALOG
#define APP_CATALOG "ComplexExampleApp"  // replace with the appropriate catalog name
#endif


// begin wxGlade: ::dependencies
#include <wx/calctrl.h>
#include <wx/notebook.h>
#include <wx/statline.h>
#include <wx/spinctrl.h>
#include <wx/datectrl.h>
#include <wx/listctrl.h>
#include <wx/spinbutt.h>
// end wxGlade

// begin wxGlade: ::extracode
// end wxGlade


class All_Widgets_Frame: public wxFrame {
public:
    // begin wxGlade: All_Widgets_Frame::ids
    // end wxGlade

    All_Widgets_Frame(wxWindow* parent, int id, const wxString& title, const wxPoint& pos=wxDefaultPosition, const wxSize& size=wxDefaultSize, long style=wxDEFAULT_FRAME_STYLE);

private:
    // begin wxGlade: All_Widgets_Frame::methods
    void set_properties();
    void do_layout();
    // end wxGlade

protected:
    // begin wxGlade: All_Widgets_Frame::attributes
    wxStaticBox* sizer_8_staticbox;
    wxBitmapButton* bitmap_button_1;
    wxPanel* notebook_1_wxBitmapButton;
    wxCalendarCtrl* calendar_ctrl_1;
    wxPanel* notebook_1_wxCalendarCtrl;
    wxChoice* choice_empty;
    wxChoice* choice_filled;
    wxPanel* notebook_1_wxChoice;
    wxComboBox* combo_box_empty;
    wxComboBox* combo_box_filled;
    wxPanel* notebook_1_wxComboBox;
    wxDatePickerCtrl* datepicker_ctrl_1;
    wxPanel* notebook_1_wxDatePickerCtrl;
    wxListBox* list_box_empty;
    wxListBox* list_box_filled;
    wxPanel* notebook_1_wxListBox;
    wxListCtrl* list_ctrl_1;
    wxPanel* notebook_1_wxListCtrl;
    wxRadioBox* radio_box_empty1;
    wxRadioBox* radio_box_filled1;
    wxRadioBox* radio_box_empty2;
    wxRadioBox* radio_box_filled2;
    wxPanel* notebook_1_wxRadioBox;
    wxRadioButton* radio_btn_1;
    wxTextCtrl* text_ctrl_1;
    wxRadioButton* radio_btn_2;
    wxTextCtrl* text_ctrl_2;
    wxRadioButton* radio_btn_3;
    wxTextCtrl* text_ctrl_3;
    wxPanel* notebook_1_wxRadioButton;
    wxGauge* gauge_1;
    wxPanel* notebook_1_wxSlider;
    wxSpinButton* spin_button_1;
    wxPanel* notebook_1_wxSpinButton;
    wxSpinCtrl* spin_ctrl_1;
    wxPanel* notebook_1_wxSpinCtrl;
    wxPanel* notebook_1_wxSplitterWindow;
    wxStaticBitmap* bitmap_code_nullbitmap;
    wxStaticBitmap* bitmap_file;
    wxStaticBitmap* bitmap_nofile;
    wxPanel* notebook_1_wxStaticBitmap;
    wxStaticLine* static_line_2;
    wxStaticLine* static_line_3;
    wxStaticLine* static_line_4;
    wxStaticLine* static_line_5;
    wxPanel* notebook_1_wxStaticLine;
    wxStaticText* label_3;
    wxStaticText* label_2;
    wxPanel* notebook_1_Spacer;
    wxTextCtrl* text_ctrl;
    wxPanel* notebook_1_wxTextCtrl;
    wxNotebook* notebook_1;
    wxStaticLine* static_line_1;
    wxButton* button_5;
    wxButton* button_1;
    // end wxGlade

    DECLARE_EVENT_TABLE();

public:
    virtual void startConverting(wxCommandEvent &event); // wxGlade: <event_handler>
}; // wxGlade: end class


#endif // ALLWIDGETS_28_H
