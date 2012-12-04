
import wx

class Rendezvous(object):

    def __init__(self, wxConnected, wxDisplay, wxLost):
        self.wxConnected = wxConnected
        self.wxDisplay = wxDisplay
        self.wxLost = wxLost

    def connected(self):
        "Notify the main tread that we are connected to the server"
        wx.CallAfter(self.wxConnected)

    def display(self, msg):
        "shuttle a message to be displayed in the chat read window"
        wx.CallAfter(self.wxDisplay, msg)

    def lost(self, msg):
        "Notify the main tread that the network connection dropped"
        wx.CallAfter(self.wxLost, msg)
