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



class MyDialog1(wx.Dialog):
    def __init__(self, *args, **kwds):
        # Content of this block not found. Did you rename this class?
        pass

    def __set_properties(self):
        # Content of this block not found. Did you rename this class?
        pass

    def __do_layout(self):
        # Content of this block not found. Did you rename this class?
        pass

# end of class MyDialog1
class MyDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        self.button_2 = wx.Button(self, wx.ID_OK, "")
        self.button_1 = wx.Button(self, wx.ID_CANCEL, "")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle(_("dialog_1"))
        self.button_1.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        grid_sizer_1 = wx.FlexGridSizer(3, 1, 0, 0)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(self.text_ctrl_1, 1, wx.ALL | wx.EXPAND, 5)
        grid_sizer_1.Add(self.static_line_1, 0, wx.ALL | wx.EXPAND, 5)
        sizer_1.Add(self.button_2, 0, wx.ALL, 5)
        sizer_1.Add(self.button_1, 0, wx.ALL, 5)
        grid_sizer_1.Add(sizer_1, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_1)
        grid_sizer_1.Fit(self)
        grid_sizer_1.AddGrowableRow(0)
        self.Layout()
        # end wxGlade

# end of class MyDialog
class MyApp(wx.App):
    def OnInit(self):
        dialog_1 = MyDialog(None, wx.ID_ANY, "")
        self.SetTopWindow(dialog_1)
        dialog_1.Show()
        return 1

# end of class MyApp

if __name__ == "__main__":
    gettext.install("app") # replace with the appropriate catalog name

    app = MyApp(0)
    app.MainLoop()
