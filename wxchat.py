#!/bin/env python
# -*- coding: utf-8 -*-
import string
import threading
import wx
import os
import sys

from chatnetworking import ChatConnect, defaulthost
import rendezvous


xmax = 500
ymax = 500
MAIN_WINDOW_DEFAULT_SIZE = (xmax,ymax)

class ChatFrame(wx.Frame):
    def __init__(self, parent, id, title):
        style=wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, parent, id, title=title,
                          size=MAIN_WINDOW_DEFAULT_SIZE, style=style)
        self.Center() 
        wx.BeginBusyCursor()
        
        
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('white')
        self.host = host  # host is global variable
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        #create a StatusBar and give it 2 columns
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount(2)
        # A menu to set the server's host name...
        self._createMenuBar()
        banner = wx.StaticText(self.panel, -1,
                    "Chat Client for Linux",
                    style = wx.ALIGN_CENTER)
        banner.SetFont(wx.Font(16, wx.ROMAN, wx.SLANT, wx.NORMAL))
        # The window for reading chat messages
        self.readWin = wx.TextCtrl(self.panel, -1,
             style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        self.readWin.SetBackgroundColour('white')
        # The windows for writing chat messages
        self.writeWin = wx.TextCtrl(self.panel, -1,
             size = (xmax*.95, ymax*0.15),
             style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP )
        self.writeWin.SetBackgroundColour('white')
        self.inputWin = wx.TextCtrl(self.panel, -1,
             size = (xmax*.95, ymax*0.1),
             style = wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.TE_WORDWRAP)
        self.inputWin.SetBackgroundColour('white')
        self.Bind(wx.EVT_TEXT_ENTER, self.send)

   
        # Create a BoxSizer which grows in the vertical direction
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(banner, 0,
                wx.ALIGN_TOP | wx.ALL | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer.Add(self.readWin, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.writeWin, 0,
                wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_BOTTOM, 5)
        sizer.Add(self.inputWin, 0,
                wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.ALIGN_TOP, 5)
      
        # Tell our panel to use this new Sizer
        self.panel.SetSizer(sizer)
        # Tell our panel to calculate the size of its items.
        self.panel.Layout()
        
       
        
        self._CreatToolBar()
        

        #-- Graphics now set-up, set-up Chat client
        self.rendezvous = rendezvous.Rendezvous(
                                    self.connected,
                                    self.chatDisplay,
                                    self.lostConnection)
        self.readPos = []
        self.writePos = []
        self.here = True
        self.blank_line_len = len(os.linesep)
        self._not_connected()
        wx.EndBusyCursor()
    #-- end of __init__
    
    def _CreatToolBar(self):
        
        ToolBar = self.CreateToolBar()
        #connection
        connbtn = ToolBar.AddLabelTool(wx.ID_EDIT,'Connect', wx.Bitmap('images/conn.jpg'))
                
        self.ToolBar.AddSeparator()
        #quit
        qbtn = ToolBar.AddLabelTool(wx.ID_ANY,'Exit',wx.Bitmap('images/exit.jpg'))
        
        self.ToolBar.AddSeparator()
        #info
        infobtn = ToolBar.AddLabelTool(wx.ID_ABOUT,'Info', wx.Bitmap('images/info.jpg'))
        
        
        self.Bind(wx.EVT_MENU, self.connect,connbtn)
        self.Bind(wx.EVT_MENU, self.OnExit,qbtn)
        self.Bind(wx.EVT_MENU, self.OnInfomation,infobtn)

        ToolBar.Realize()
        
        
        
    def _createMenuBar(self):
        self.menuServ = wx.Menu()
        
        menuBar = wx.MenuBar()
        menuBar.Append(self.menuServ, '&Menu')
        self.SetMenuBar(menuBar)
        
        self.menuServ.Append(-1, '&Connect', 'Connect to Server')
        self.Bind(wx.EVT_MENU, self.connect)
        
        self.menuServ.AppendSeparator()
        
        self.menuServ.Append(-1, '&Exit',
                'Exit the chat application')
        self.Bind(wx.EVT_MENU, self.OnExit)
           

    def _not_connected(self):
        self.connected = False
        self.statusBar.SetStatusText('Not connected to a chat server', 1)
        self.statusBar.SetStatusText(
                "The 'Connect' button lets you chat", 0)
        
        self.clear_readWin()
        self.add_readWin(
            "this window msg from server\n")
        self.clear_writeWin()
        self.add_writeWin(
            "this window msg from user\n")

    # Next several functions implement auto-scrolling in the read and write
    # windows.
    def clear_readWin(self):
       
        self.readWin.Clear()
        self.readPos = []

    def add_readWin(self, msg):
       
        self.readWin.AppendText(msg)
        self.readPos.append(self.readWin.GetInsertionPoint())
        if len(self.readPos) > 10:
            clear = self.readPos.pop(0)
            self.readWin.Remove(0, clear)
            for i in range(len(self.readPos)):
                self.readPos[i] -= clear
        if self.readWin.GetNumberOfLines() > 15:
            self.readWin.ScrollLines(10)

    def clear_writeWin(self):
       
        self.writeWin.Clear()
        self.writePos = []

    def add_writeWin(self, msg):
        
        if len(msg):
            self.writeWin.AppendText(msg)
            self.writePos.append(self.writeWin.GetInsertionPoint())
        while len(self.writePos) > 10 or \
              (len(self.writePos) and self.writePos[0] <= self.blank_line_len):
            clear = self.writePos.pop(0)
            self.writeWin.Remove(0, clear)
            for i in range(len(self.writePos)):
                self.writePos[i] -= clear
        if self.writeWin.GetNumberOfLines() > 5:
            self.writeWin.ScrollLines(5)

    def getText(self):
       
        message = string.strip(self.inputWin.GetValue())
        self.inputWin.Clear()
        self.inputWin.SetInsertionPoint(0)
        if len(message):
            self.add_writeWin(message + '\n')
            return message
        else:
            return ''

    def connect(self, event):
        wx.BeginBusyCursor()
        if self.connected:
            # a disconnect request
            name = self.getText()
            self.net.send("/quit " + name)
            self.add_writeWin('\n')
            self.net.join()
            # Note: finish this up in lostConnection
        else:
            # a connect request
            self.add_readWin('\n')
            # A thread to listen to the network and 
            # display messages from server
            self.net = ChatConnect(self.host,
                            self.rendezvous.connected,
                            self.rendezvous.display,
                            self.rendezvous.lost,
                            )
            self.net.start()
            # Note: finish this up in connected
        #--
        wx.EndBusyCursor()

    def send(self, event):
        if self.connected:
            sendData = self.getText()
            if len(sendData):
                self.net.send(sendData)
            else:
                self.add_writeWin('\n')
        self.inputWin.SetFocus()



    def connected(self):
        
        self.connected = True
        self.statusBar.SetStatusText(
            'Connected to a chat server', 1)
        self.statusBar.SetStatusText(
            "return to send message", 0)
        self.add_readWin('\n\nConnected to a chat server\n\n')
        self.clear_writeWin()
        self.inputWin.SetFocus()

    def chatDisplay(self, msg):
        
        self.add_readWin(msg)

    def lostConnection(self, msg):
        
        
        self._not_connected()
        self.add_readWin('\n\n'+ msg)
        self.net.join()

 

    def OnExit(self, event):
       
        if self.connected:
            #self.net.send("/quit")
            self.net.join()
        self.Destroy()
  
    def OnInfomation(self, e):
        info = wx.MessageDialog(None,'Shock & Awe Losers! \n\t Thanks to KJM  ','Infomation',wx.ICON_INFORMATION)
        info.ShowModal()
class App(wx.App):

    def OnInit(self):
        self.frame = ChatFrame(parent=None, id=-1,
                title='ingsun Chat Client')
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = defaulthost
   
    app = App(redirect=False)
    app.MainLoop()
