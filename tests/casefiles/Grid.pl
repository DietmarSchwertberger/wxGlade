# generated by wxGlade
#
# To get wxPerl visit http://www.wxperl.it
#

use Wx qw[:allclasses];
use strict;

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

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
    $style = wxDEFAULT_FRAME_STYLE
        unless defined $style;

    $self = $self->SUPER::new( $parent, $id, $title, $pos, $size, $style, $name );
    $self->SetTitle("frame_1");
    
    $self->{sizer_1} = Wx::BoxSizer->new(wxVERTICAL);
    
    $self->{grid_1} = Wx::Grid->new($self, wxID_ANY);
    $self->{grid_1}->CreateGrid(2, 2);
    $self->{grid_1}->SetGridLineColour(Wx::Colour->new(255, 0, 0));
    $self->{grid_1}->SetLabelBackgroundColour(Wx::Colour->new(216, 191, 216));
    $self->{grid_1}->SetColLabelValue(0, "Column A");
    $self->{grid_1}->SetColLabelValue(1, "Column B");
    $self->{grid_1}->SetBackgroundColour(Wx::Colour->new(0, 255, 255));
    $self->{grid_1}->SetRowLabelValue(0, "Row 1");
    $self->{grid_1}->SetCellValue(0, 0, "1");
    $self->{sizer_1}->Add($self->{grid_1}, 1, wxEXPAND, 0);
    
    $self->SetSizer($self->{sizer_1});
    $self->{sizer_1}->Fit($self);
    
    $self->Layout();
    Wx::Event::EVT_GRID_CMD_CELL_LEFT_CLICK($self, $self->{grid_1}->GetId, $self->can('myEVT_GRID_CELL_LEFT_CLICK'));

    # end wxGlade
    return $self;

}


sub myEVT_GRID_CELL_LEFT_CLICK {
    my ($self, $event) = @_;
    # wxGlade: MyFrame::myEVT_GRID_CELL_LEFT_CLICK <event_handler>
    warn "Event handler (myEVT_GRID_CELL_LEFT_CLICK) not implemented";
    $event->Skip;
    # end wxGlade
}


# end of class MyFrame

1;

