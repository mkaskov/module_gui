#!/usr/bin/env python3
# by Sangheli a.savel.vic@gmail.com

import wx, wx.html,wx.lib
import wx.lib.masked as masked
import subprocess
import signal
from socket import *
import os

def pingit(hostip):
    s = socket(AF_INET, SOCK_STREAM)
    host = hostip
    port = 11311

    try:
        s.connect((host, port))
    except: # if failed to connect
        s.close()
        return False

    while True:
        s.close()
        return True

class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150, 150), size=(200, 200),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.hasPID = False

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.statusbar = self.CreateStatusBar()

        self.panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        control = ["Phone No", "###.###.###.###", "", 'F^-', "^\(\d{3}\) \d{3}-\d{4}", '', '', '']
        self.maskText = masked.TextCtrl(self.panel,
                                   mask=control[1],
                                   excludeChars=control[2],
                                   formatcodes=control[3],
                                   includeChars="",
                                   validRegex=control[4],
                                   validRange=control[5],
                                   choices=control[6],
                                   choiceRequired=True,
                                   defaultValue=control[7],
                                   demo=True,
                                   name=control[0],
                                   style=wx.TE_PROCESS_ENTER)
        self.maskText.Bind(wx.EVT_KEY_DOWN, self.onTextKeyEvent)
        box.Add(self.maskText, 0, wx.ALL, 10)

        m_close = wx.Button(self.panel, wx.ID_CLOSE, "Connect")
        m_close.Bind(wx.EVT_BUTTON, self.OnConnect)
        box.Add(m_close, 0, wx.ALL, 10)

        m_shut = wx.Button(self.panel, wx.ID_CLOSE, "Shutdown")
        m_shut.Bind(wx.EVT_BUTTON, self.onShutdown)
        box.Add(m_shut, 0, wx.ALL, 10)

        self.panel.SetSizer(box)
        self.panel.Layout()

    def makeConnect(self):
        self.statusbar.SetStatusText('')
        iptext = self.maskText.GetValue().replace(' ', '')

        if (pingit(iptext)):
            self.hasPID = True
            os.environ['ROS_MASTER_URI'] = "http://ipaddr:11311".replace("ipaddr", iptext)
            rviz_env = os.environ.copy()
            # self.process_rviz = subprocess.Popen(['gnome-terminal', '--disable-factory', '-e', 'bash launch.bash'],preexec_fn=os.setpgrp,env=rviz_env)
            self.process_rviz = subprocess.Popen(['gnome-terminal', '--disable-factory', "-e",
                                                  'bash /home/user/catkin_ws/src/moudle_gui/puremindgui/script/launch.bash'],
                                                 preexec_fn=os.setpgrp, env=rviz_env)
        else:
            self.statusbar.SetStatusText('robot unavailable')

    def kellTerminal(self):
        if (self.hasPID):
            os.killpg(self.process_rviz.pid, signal.SIGINT)






    def onTextKeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
            self.makeConnect()
            # self.panel.SetCursor(wx.Cursor(wx.CURSOR_BLANK))
            # self.maskText.SetCursor(wx.Cursor(wx.CURSOR_CHAR))
            self.maskText.Navigate()
        event.Skip()

    def OnConnect(self, event):
        self.makeConnect()

    def onShutdown(self,event):
        self.kellTerminal()

    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
                               "Do you really want to close this application?",
                               "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.kellTerminal()
            self.Destroy()

app = wx.App(redirect=True)  # Error messages go to popup window
top = Frame("Run rviz")
top.Show()
app.MainLoop()