# about.py: about box with general info
# 
# Copyright (c) 2002 Alberto Griggio <albgrig@tiscalinet.it>
# License: GPL (see license.txt)

from wxPython.wx import *
from wxPython.html import *
import wxPython.lib.wxpTag
import common, misc

class wxGladeAboutBox(wxDialog):
    text = '''
    <html>
    <body bgcolor="%s"><center>
    <font size="-1">
    <table bgcolor="#458154" width="100%%" cellspacing="0"
    cellpadding="2" border="2">
    <tr>
        <td align="center">
        <h3>wxGlade %s: a GUI builder for<br>wxPython</h3>
        Running on Python %s and wxPython %s<br>
        </td>
    </tr>
    </table>
    </font>
    </center>
    <table border="0">
    <tr><td width="50">&nbsp;</td><td>
    <font size="-1"><b>&nbsp;<br>
    Copyright (c) 2002 Alberto Griggio<br>
    License: GPL (see license.txt)</b></font>
    </td></tr>
    <tr><td width="50">&nbsp;</td><td>
    <font size="-1">
    <br>Authors:<br>
    &nbsp;&nbsp;&nbsp;Alberto Griggio &lt;albgrig@tiscalinet.it&gt;<br>
    &nbsp;&nbsp;&nbsp;Marco Barisione &lt;marco.bari@vene.ws&gt;<br><br>
    For credits, see credits.txt
    </font>
    </td></tr></table>
    <center>
    <hr><div align="right">
    <wxp class="wxButton">
        <param name="label" value="OK">
        <param name="id" value="wxID_OK">
    </wxp>&nbsp;&nbsp;&nbsp;</div>
    </center>
    </body>
    </html>
    '''
    def __init__(self, parent=None):
        wxDialog.__init__(self, parent, -1, 'About wxGlade')
        html = wxHtmlWindow(self, -1, size=(430, -1))
        py_version = sys.version.split()[0]
        bgcolor = misc.color_to_string(self.GetBackgroundColour())
        html.SetPage(self.text % (bgcolor, common.version, py_version,
                                  wx.__version__))
        ir = html.GetInternalRepresentation()
        html.SetSize((ir.GetWidth()+5, ir.GetHeight()+10))
        w, h = html.GetSize()
        self.SetClientSize((w, h))
        if parent: self.CenterOnParent()
        else: self.CenterOnScreen()

# end of class wxGladeAboutBox


if __name__ == '__main__':
    app = wxPySimpleApp()
    d = wxGladeAboutBox()
    app.SetTopWindow(d)
    d.ShowModal()
    
