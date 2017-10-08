#!/usr/bin/env python
# -*- coding: ISO-8859-15 -*-
#
# generated by wxGlade "faked test version"
#

import wx

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, _("Some Input"), style=wx.TE_READONLY)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle(_("frame_1"))
        self.text_ctrl_1.SetBackgroundColour(wx.Colour(0, 255, 127))
        self.text_ctrl_1.SetForegroundColour(wx.Colour(255, 0, 0))
        self.text_ctrl_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.text_ctrl_1.SetFocus()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.text_ctrl_1, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

# end of class MyFrame
class MyApp(wx.App):
    def OnInit(self):
        self.frame_1 = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame_1)
        self.frame_1.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    gettext.install("app") # replace with the appropriate catalog name

    app = MyApp(0)
    app.MainLoop()
