class MyStartApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        appframe = MyAppFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(appframe)
        appframe.Show()
        return 1

# end of class MyStartApp

if __name__ == "__main__":
    import gettext
    gettext.install("myapp") # replace with the appropriate catalog name

    myapp = MyStartApp(0)
    myapp.MainLoop()
