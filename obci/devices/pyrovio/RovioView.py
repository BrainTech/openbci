import Rovio
import wx

class RovioView(wx.Frame):
    "View and control a Rovio"
    def __init__(self, rovio):
        
        self.rovio = rovio
        
wximg = wx.ImageFromStream(jpeg_stream, wx.BITMAP_TYPE_JPEG)
wxbmp = wximg.ConvertToBitmap()
f = wx.Frame(None, -1, "Show JPEG demo")
f.SetSize( wxbmp.GetSize() )
wx.StaticBitmap(f,-1,wxbmp,(0,0))
f.Show(True)
def callback(evt,a=a,f=f):
    # Closes the window upon any keypress
    f.Close()
    a.ExitMainLoop()
wx.EVT_CHAR(f,callback)
