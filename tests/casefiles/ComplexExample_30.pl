#!/usr/bin/perl -w -- 
#
# generated by wxGlade "faked test version"
#
# To get wxPerl visit http://www.wxperl.it
#

use Wx qw[:allclasses];
use strict;

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

package PyOgg2_MyFrame;

use Wx qw[:everything];
use base qw(Wx::Frame);
use strict;

use Wx::Locale gettext => '_T';
sub new {
    my( $self, $parent, $id, $title, $pos, $size, $style, $name ) = @_;
    $parent = undef              unless defined $parent;
    $id     = -1                 unless defined $id;
    $title  = ""                 unless defined $title;
    $pos    = wxDefaultPosition  unless defined $pos;
    $size   = wxDefaultSize      unless defined $size;
    $name   = ""                 unless defined $name;

    # begin wxGlade: PyOgg2_MyFrame::new
    $style = wxDEFAULT_FRAME_STYLE
        unless defined $style;

    $self = $self->SUPER::new( $parent, $id, $title, $pos, $size, $style, $name );
    

    # Menu Bar

    $self->{Mp3_To_Ogg_menubar} = Wx::MenuBar->new();
    my $wxglade_tmp_menu;
    $wxglade_tmp_menu = Wx::Menu->new();
    $wxglade_tmp_menu->Append(wxID_OPEN, _T("&Open"), "");
    $wxglade_tmp_menu->Append(wxID_EXIT, _T("&Quit"), "");
    $self->{Mp3_To_Ogg_menubar}->Append($wxglade_tmp_menu, _T("&File"));
    $wxglade_tmp_menu = Wx::Menu->new();
    $wxglade_tmp_menu->Append(wxID_ABOUT, _T("&About"), _T("About dialog"));
    $self->{Mp3_To_Ogg_menubar}->Append($wxglade_tmp_menu, _T("&Help"));
    $self->SetMenuBar($self->{Mp3_To_Ogg_menubar});
    
    # Menu Bar end

    $self->{Mp3_To_Ogg_statusbar} = $self->CreateStatusBar(2);
    
    # Tool Bar
    $self->{Mp3_To_Ogg_toolbar} = Wx::ToolBar->new($self, -1, wxDefaultPosition, wxDefaultSize, wxTB_HORIZONTAL|wxTB_TEXT);
    $self->SetToolBar($self->{Mp3_To_Ogg_toolbar});
    $self->{Mp3_To_Ogg_toolbar}->AddTool(wxID_OPEN, _T("&Open"), wxNullBitmap, wxNullBitmap, wxITEM_NORMAL, _T("Open a file"), _T("Open a MP3 file to convert into OGG format"));
    # Tool Bar end
    $self->{notebook_1} = Wx::Notebook->new($self, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxNB_BOTTOM);
    $self->{notebook_1_pane_1} = Wx::Panel->new($self->{notebook_1}, wxID_ANY);
    $self->{text_ctrl_1} = Wx::TextCtrl->new($self->{notebook_1_pane_1}, wxID_ANY, "");
    $self->{button_3} = Wx::Button->new($self->{notebook_1_pane_1}, wxID_OPEN, "");
    $self->{notebook_1_pane_2} = Wx::Panel->new($self->{notebook_1}, wxID_ANY);
    $self->{rbx_sampling_rate} = Wx::RadioBox->new($self->{notebook_1_pane_2}, wxID_ANY, _T("Sampling Rate"), wxDefaultPosition, wxDefaultSize, [_T("44 kbit"), _T("128 kbit")], 0, wxRA_SPECIFY_ROWS);
    $self->{cbx_love} = Wx::CheckBox->new($self->{notebook_1_pane_2}, wxID_ANY, _T("\N{U+2665} Love this song"));
    $self->{notebook_1_pane_3} = Wx::Panel->new($self->{notebook_1}, wxID_ANY);
    $self->{text_ctrl_2} = Wx::TextCtrl->new($self->{notebook_1_pane_3}, wxID_ANY, "", wxDefaultPosition, wxDefaultSize, wxTE_MULTILINE);
    $self->{notebook_1_pane_4} = Wx::Panel->new($self->{notebook_1}, wxID_ANY);
    $self->{_lbl_output_filename} = Wx::StaticText->new($self->{notebook_1_pane_4}, wxID_ANY, _T("File name:"));
    $self->{text_ctrl_3} = Wx::TextCtrl->new($self->{notebook_1_pane_4}, wxID_ANY, "");
    $self->{button_4} = Wx::Button->new($self->{notebook_1_pane_4}, wxID_OPEN, "");
    $self->{checkbox_1} = Wx::CheckBox->new($self->{notebook_1_pane_4}, wxID_ANY, _T("Overwrite existing file"));
    $self->{notebook_1_pane_5} = Wx::Panel->new($self->{notebook_1}, wxID_ANY);
    $self->{label_1} = Wx::StaticText->new($self->{notebook_1_pane_5}, wxID_ANY, _T("Please check the format of those lines manually:\n\nSingle line without any special characters.\n\na line break between new and line: new\nline\na tab character between new and line: new\tline\na backslash and a t \\t\ntwo backslash characters: \\\\ \nthree backslash characters: \\\\\\ \na double quote: \"\nan escaped new line sequence: \\n"));
    $self->{static_line_1} = Wx::StaticLine->new($self, wxID_ANY);
    $self->{button_5} = Wx::Button->new($self, wxID_CLOSE, "");
    $self->{button_2} = Wx::Button->new($self, wxID_CANCEL, "", wxDefaultPosition, wxDefaultSize, wxBU_TOP);
    $self->{button_1} = Wx::Button->new($self, wxID_OK, "", wxDefaultPosition, wxDefaultSize, wxBU_TOP);

    $self->__set_properties();
    $self->__do_layout();

    Wx::Event::EVT_MENU($self, wxID_OPEN, $self->can('OnOpen'));
    Wx::Event::EVT_MENU($self, wxID_EXIT, $self->can('OnClose'));
    Wx::Event::EVT_MENU($self, wxID_ABOUT, $self->can('OnAboutDialog'));
    Wx::Event::EVT_BUTTON($self, $self->{button_1}->GetId, $self->can('startConverting'));

    # end wxGlade
    return $self;

}


sub __set_properties {
    my $self = shift;
    # begin wxGlade: PyOgg2_MyFrame::__set_properties
    $self->SetTitle(_T("mp3 2 ogg"));
    $self->{Mp3_To_Ogg_statusbar}->SetStatusWidths(-2, -1);

    # statusbar fields
    my( @Mp3_To_Ogg_statusbar_fields ) = (
        _T("Mp3_To_Ogg_statusbar"),
        "",
    );

    if( @Mp3_To_Ogg_statusbar_fields ) {
        $self->{Mp3_To_Ogg_statusbar}->SetStatusText($Mp3_To_Ogg_statusbar_fields[$_], $_)
        for 0 .. $#Mp3_To_Ogg_statusbar_fields ;
    }
    $self->{Mp3_To_Ogg_toolbar}->Realize();
    $self->{rbx_sampling_rate}->SetSelection(0);
    $self->{cbx_love}->SetToolTip(_T("Yes!\nWe \N{U+2665} it!"));
    $self->{cbx_love}->SetValue(1);
    $self->{text_ctrl_3}->SetToolTip(_T("File name of the output file\nAn existing file will be overwritten without futher information!"));
    $self->{checkbox_1}->SetToolTip(_T("Overwrite an existing file"));
    $self->{checkbox_1}->SetValue(1);
    # end wxGlade
}

sub __do_layout {
    my $self = shift;
    # begin wxGlade: PyOgg2_MyFrame::__do_layout
    $self->{sizer_1} = Wx::FlexGridSizer->new(3, 1, 0, 0);
    $self->{sizer_2} = Wx::FlexGridSizer->new(1, 3, 0, 0);
    $self->{sizer_5} = Wx::BoxSizer->new(wxHORIZONTAL);
    $self->{_gszr_pane4} = Wx::FlexGridSizer->new(2, 3, 0, 0);
    $self->{_szr_pane3} = Wx::BoxSizer->new(wxHORIZONTAL);
    $self->{sizer_4} = Wx::BoxSizer->new(wxHORIZONTAL);
    $self->{sizer_3} = Wx::StaticBoxSizer->new(Wx::StaticBox->new($self->{notebook_1_pane_2}, wxID_ANY, _T("Misc")), wxHORIZONTAL);
    $self->{_gszr_pane1} = Wx::FlexGridSizer->new(1, 3, 0, 0);
    my $_lbl_input_filename = Wx::StaticText->new($self->{notebook_1_pane_1}, wxID_ANY, _T("File name:"));
    $self->{_gszr_pane1}->Add($_lbl_input_filename, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5);
    $self->{_gszr_pane1}->Add($self->{text_ctrl_1}, 1, wxALIGN_CENTER_VERTICAL|wxALL|wxEXPAND, 5);
    $self->{_gszr_pane1}->Add($self->{button_3}, 0, wxALL, 5);
    $self->{notebook_1_pane_1}->SetSizer($self->{_gszr_pane1});
    $self->{_gszr_pane1}->AddGrowableCol(1);
    $self->{sizer_4}->Add($self->{rbx_sampling_rate}, 1, wxALL|wxEXPAND, 5);
    $self->{sizer_3}->Add($self->{cbx_love}, 0, wxALL|wxSHAPED, 5);
    $self->{sizer_4}->Add($self->{sizer_3}, 1, wxALL|wxEXPAND, 5);
    $self->{notebook_1_pane_2}->SetSizer($self->{sizer_4});
    $self->{_szr_pane3}->Add($self->{text_ctrl_2}, 1, wxALL|wxEXPAND, 5);
    $self->{notebook_1_pane_3}->SetSizer($self->{_szr_pane3});
    $self->{_gszr_pane4}->Add($self->{_lbl_output_filename}, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5);
    $self->{_gszr_pane4}->Add($self->{text_ctrl_3}, 0, wxALL|wxEXPAND, 5);
    $self->{_gszr_pane4}->Add($self->{button_4}, 0, wxALL, 5);
    $self->{_gszr_pane4}->Add(20, 20, 0, 0, 0);
    $self->{_gszr_pane4}->Add($self->{checkbox_1}, 0, wxALL|wxEXPAND, 5);
    $self->{_gszr_pane4}->Add(20, 20, 0, 0, 0);
    $self->{notebook_1_pane_4}->SetSizer($self->{_gszr_pane4});
    $self->{_gszr_pane4}->AddGrowableCol(1);
    $self->{sizer_5}->Add($self->{label_1}, 1, wxALL|wxEXPAND, 5);
    $self->{notebook_1_pane_5}->SetSizer($self->{sizer_5});
    $self->{notebook_1}->AddPage($self->{notebook_1_pane_1}, _T("Input File"));
    $self->{notebook_1}->AddPage($self->{notebook_1_pane_2}, _T("Converting Options"));
    $self->{notebook_1}->AddPage($self->{notebook_1_pane_3}, _T("Converting Progress"));
    $self->{notebook_1}->AddPage($self->{notebook_1_pane_4}, _T("Output File"));
    $self->{notebook_1}->AddPage($self->{notebook_1_pane_5}, _T("Some Text"));
    $self->{sizer_1}->Add($self->{notebook_1}, 1, wxEXPAND, 0);
    $self->{sizer_1}->Add($self->{static_line_1}, 0, wxALL|wxEXPAND, 5);
    $self->{sizer_2}->Add($self->{button_5}, 0, wxALIGN_RIGHT|wxALL, 5);
    $self->{sizer_2}->Add($self->{button_2}, 0, wxALIGN_RIGHT|wxALL, 5);
    $self->{sizer_2}->Add($self->{button_1}, 0, wxALIGN_RIGHT|wxALL, 5);
    $self->{sizer_1}->Add($self->{sizer_2}, 0, wxALIGN_RIGHT, 0);
    $self->SetSizer($self->{sizer_1});
    $self->{sizer_1}->SetSizeHints($self);
    $self->{sizer_1}->AddGrowableRow(0);
    $self->{sizer_1}->AddGrowableCol(0);
    $self->Layout();
    $self->Centre();
    # end wxGlade
}

sub OnOpen {
    my ($self, $event) = @_;
    # wxGlade: PyOgg2_MyFrame::OnOpen <event_handler>
    warn "Event handler (OnOpen) not implemented";
    $event->Skip;
    # end wxGlade
}


sub OnClose {
    my ($self, $event) = @_;
    # wxGlade: PyOgg2_MyFrame::OnClose <event_handler>
    warn "Event handler (OnClose) not implemented";
    $event->Skip;
    # end wxGlade
}


sub OnAboutDialog {
    my ($self, $event) = @_;
    # wxGlade: PyOgg2_MyFrame::OnAboutDialog <event_handler>
    warn "Event handler (OnAboutDialog) not implemented";
    $event->Skip;
    # end wxGlade
}


sub startConverting {
    my ($self, $event) = @_;
    # wxGlade: PyOgg2_MyFrame::startConverting <event_handler>
    warn "Event handler (startConverting) not implemented";
    $event->Skip;
    # end wxGlade
}


# end of class PyOgg2_MyFrame

1;

package MyFrameGrid;

use Wx qw[:everything];
use base qw(Wx::Frame);
use strict;

use Wx::Locale gettext => '_T';
sub new {
    my( $self, $parent, $id, $title, $pos, $size, $style, $name ) = @_;
    $parent = undef              unless defined $parent;
    $id     = -1                 unless defined $id;
    $title  = ""                 unless defined $title;
    $pos    = wxDefaultPosition  unless defined $pos;
    $size   = wxDefaultSize      unless defined $size;
    $name   = ""                 unless defined $name;

    # begin wxGlade: MyFrameGrid::new
    $style = wxDEFAULT_FRAME_STYLE
        unless defined $style;

    $self = $self->SUPER::new( $parent, $id, $title, $pos, $size, $style, $name );
    $self->{grid} = Wx::Grid->new($self, wxID_ANY);
    $self->{static_line} = Wx::StaticLine->new($self, wxID_ANY);
    $self->{button} = Wx::Button->new($self, wxID_CLOSE, "");

    $self->__set_properties();
    $self->__do_layout();

    # end wxGlade
    return $self;

}


sub __set_properties {
    my $self = shift;
    # begin wxGlade: MyFrameGrid::__set_properties
    $self->SetTitle(_T("FrameOggCompressionDetails"));
    $self->{grid}->CreateGrid(8, 3);
    $self->{button}->SetFocus();
    $self->{button}->SetDefault();
    # end wxGlade
}

sub __do_layout {
    my $self = shift;
    # begin wxGlade: MyFrameGrid::__do_layout
    $self->{_szr_frame} = Wx::BoxSizer->new(wxVERTICAL);
    $self->{grid_sizer} = Wx::FlexGridSizer->new(3, 1, 0, 0);
    $self->{grid_sizer}->Add($self->{grid}, 1, wxEXPAND, 0);
    $self->{grid_sizer}->Add($self->{static_line}, 0, wxALL|wxEXPAND, 5);
    $self->{grid_sizer}->Add($self->{button}, 0, wxALIGN_RIGHT|wxALL, 5);
    $self->{grid_sizer}->AddGrowableRow(0);
    $self->{grid_sizer}->AddGrowableCol(0);
    $self->{_szr_frame}->Add($self->{grid_sizer}, 1, wxEXPAND, 0);
    $self->SetSizer($self->{_szr_frame});
    $self->{_szr_frame}->SetSizeHints($self);
    $self->Layout();
    # end wxGlade
}

# end of class MyFrameGrid

1;

1;

package main;

unless(caller){
    my $local = Wx::Locale->new("English", "en", "en"); # replace with ??
    $local->AddCatalog("ComplexExampleApp"); # replace with the appropriate catalog name

    local *Wx::App::OnInit = sub{1};
    my $ComplexExampleApp = Wx::App->new();
    Wx::InitAllImageHandlers();

    my $Mp3_To_Ogg = PyOgg2_MyFrame->new();

    $ComplexExampleApp->SetTopWindow($Mp3_To_Ogg);
    $Mp3_To_Ogg->Show(1);
    $ComplexExampleApp->MainLoop();
}
