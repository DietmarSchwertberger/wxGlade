if __name__ == "__main__":
    gettext.install("myapp") # replace with the appropriate catalog name

    myapp = wx.PySimpleApp(0)
    appframe = MyAppFrame(None, wx.ID_ANY, "")
    myapp.SetTopWindow(appframe)
    appframe.Show()
    myapp.MainLoop()
