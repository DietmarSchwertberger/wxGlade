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

package MyMenuBar;

use Wx qw[:everything];
use base qw(Wx::MenuBar);
use strict;

sub new {
    my( $self,  ) = @_;
    # begin wxGlade: MyMenuBar::new
    $self = $self->SUPER::new( @_[1 .. $#_] );
    my $wxglade_tmp_menu;
    $wxglade_tmp_menu = Wx::Menu->new();
    $self->Append($wxglade_tmp_menu, "File");

    $self->__set_properties();
    $self->__do_layout();

    # end wxGlade
    return $self;

}


sub __set_properties {
    my $self = shift;
    # begin wxGlade: MyMenuBar::__set_properties
    return;
    # end wxGlade
}

sub __do_layout {
    my $self = shift;
    # begin wxGlade: MyMenuBar::__do_layout
    return;
    # end wxGlade
}

# end of class MyMenuBar

1;

package MyToolBar;

use Wx qw[:everything];
use base qw(Wx::ToolBar);
use strict;

sub new {
    my( $self,  ) = @_;
    # begin wxGlade: MyToolBar::new
    $self = $self->SUPER::new( @_[1 .. $#_] );

    $self->__set_properties();
    $self->__do_layout();

    # end wxGlade
    return $self;

}


sub __set_properties {
    my $self = shift;
    # begin wxGlade: MyToolBar::__set_properties
    $self->Realize();
    # end wxGlade
}

sub __do_layout {
    my $self = shift;
    # begin wxGlade: MyToolBar::__do_layout
    return;
    # end wxGlade
}

# end of class MyToolBar

1;

package MyFrame;

use Wx qw[:everything];
use base qw(Wx::Frame);
use strict;

sub new {
    my( $self, $parent, $id, $title, $pos, $size, $style, $name ) = @_;
    $parent = undef              unless defined $parent;
    $id     = -1                 unless defined $id;
    $title  = ""                 unless defined $title;
    $pos    = wxDefaultPosition  unless defined $pos;
    $size   = wxDefaultSize      unless defined $size;
    $name   = ""                 unless defined $name;

    # begin wxGlade: MyFrame::new
    $self = $self->SUPER::new( $parent, $id, $title, $pos, $size, $style, $name );
    $self->SetSize(Wx::Size->new(200, 200));
    $self->{label_1} = Wx::StaticText->new($self, wxID_ANY, "placeholder - every design\nneeds a toplevel window", wxDefaultPosition, wxDefaultSize, wxALIGN_CENTER);

    $self->__set_properties();
    $self->__do_layout();

    # end wxGlade
    return $self;

}


sub __set_properties {
    my $self = shift;
    # begin wxGlade: MyFrame::__set_properties
    $self->SetTitle("frame_1");
    # end wxGlade
}

sub __do_layout {
    my $self = shift;
    # begin wxGlade: MyFrame::__do_layout
    $self->{sizer_1} = Wx::BoxSizer->new(wxVERTICAL);
    $self->{sizer_1}->Add($self->{label_1}, 1, wxALIGN_CENTER|wxALL|wxEXPAND, 0);
    $self->SetSizer($self->{sizer_1});
    $self->Layout();
    # end wxGlade
}

# end of class MyFrame

1;

package MyApp;

use base qw(Wx::App);
use strict;

sub OnInit {
    my( $self ) = shift;

    Wx::InitAllImageHandlers();

    my $frame_1 = MyFrame->new();

    $self->SetTopWindow($frame_1);
    $frame_1->Show(1);

    return 1;
}
# end of class MyApp

package main;

unless(caller){
    my $app = MyApp->new();
    $app->MainLoop();
}
