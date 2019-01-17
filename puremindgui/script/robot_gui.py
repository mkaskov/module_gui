#!/usr/bin/env python3
# by Sangheli a.savel.vic@gmail.com

import wx, wx.html,wx.lib
import wx.lib.masked as masked
import subprocess
import signal
import os
from util import scanLocalNetwork
from concurrent.futures import ThreadPoolExecutor

textLocal = [
"ip address",
"scanning ...",
"Connect",
"Shutdown",
"Reload",
'robots list',
'robots not found',
'connected to robot: ',
'robot unavailable: ' ,
'disconnected from robot: ',
"Do you really want to close this application?",
"Confirm Exit",
"Run rviz"
]

textLocalRus = [
"ip адрес",
"поиск ...",
"Подключиться",
"Выключить",
"Скан",
'роботы',
'роботы не обнаружены',
'подключен к роботу: ',
'робот недоступен: ' ,
'отключен от робота: ',
"Вы желаете закрыть приложение?",
"Подтвертить выход",
"Запуск rviz"
]

class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150, 150), size=(410, 205),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.statusbar = self.CreateStatusBar()

        self.hasPID = False

        self.iptext = ""

        self.path=os.path.expanduser("~/catkin_ws/src/module_gui/puremindgui/script/")
        self.bashcommand = 'bash ' + self.path + 'launch.bash'

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        lbl1 = wx.StaticText(self.panel, -1, style=wx.ALIGN_CENTER)
        lbl1.SetFont(self.GetFont())
        lbl1.SetLabel(textLocal[0])
        box.Add(lbl1, 0, wx.ALL, 5)

        self.lbl2 = wx.StaticText(self.panel, -1, style=wx.ALIGN_CENTER,pos=(200,5))
        self.lbl2.SetFont(self.GetFont())
        self.lbl2.SetLabel(textLocal[1])

        control = ["ip address", "###.###.###.###", "", 'F^-', "^\d{3}.\d{3}.\d{3}.\d{3}", '', '', '']
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

        self.lst = wx.ListBox(self.panel, pos=(200, 30), size = (200,150), choices=[], style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.selectRobotIp, self.lst)

        self.b_connect = wx.Button(self.panel, wx.ID_CLOSE, textLocal[2])
        self.b_connect.Bind(wx.EVT_BUTTON, self.OnConnect)
        box.Add(self.b_connect, 0, wx.ALL, 10)

        m_shut = wx.Button(self.panel, wx.ID_CLOSE, textLocal[3])
        m_shut.Bind(wx.EVT_BUTTON, self.onShutdown)
        box.Add(m_shut, 0, wx.ALL, 10)

        self.btnReload = wx.Button(self.panel, wx.ID_CLOSE, textLocal[4],pos=(315, 0))
        self.btnReload.Bind(wx.EVT_BUTTON, self.onReload)

        self.panel.SetSizer(box)
        self.panel.Layout()



        self.executor = ThreadPoolExecutor(max_workers=2)
        threadGetRobotList = self.executor.submit(scanLocalNetwork.getRobotList)
        threadGetRobotList.add_done_callback(self.callbackRobotList)

    def onReload(self,event):
        self.lbl2.SetLabel(textLocal[1])
        self.lst.Set([])
        threadGetRobotList = self.executor.submit(scanLocalNetwork.getRobotList)
        threadGetRobotList.add_done_callback(self.callbackRobotList)
        self.btnReload.Disable()

    def callbackRobotList(self,value):
        if(len(value.result())>0):
            wx.CallAfter(self.lst.Set, value.result())
            wx.CallAfter(self.lbl2.SetLabel,  textLocal[5])
            wx.CallAfter(self.btnReload.Enable)
        else:
            wx.CallAfter(self.lbl2.SetLabel, textLocal[6])
            wx.CallAfter(self.btnReload.Enable)

    def extendIP(self,ip_,merger):
        text_ = ip_.split(".")
        text_ = ["{:03d}".format(int(elem)) for elem in text_]
        return merger.join(text_)

    def selectRobotIp(self,event):
        text_ = self.lst.GetString(self.lst.GetSelection())
        self.maskText.SetValue(self.extendIP(text_,""))

    def makeConnect(self):
        self.statusbar.SetStatusText('')
        iptext = self.maskText.GetValue().replace(' ', '')

        if (self.extendIP(scanLocalNetwork.getLocalIp(),".") == iptext or scanLocalNetwork.pingit(iptext)):
            if (self.hasPID):
                os.killpg(self.process_rviz.pid, signal.SIGINT)

            self.hasPID = True

            if(self.extendIP(scanLocalNetwork.getLocalIp(),".")!=iptext):
                os.environ['ROS_MASTER_URI'] = "http://ipaddr:11311".replace("ipaddr", iptext)
                os.environ['ROS_IP'] = scanLocalNetwork.getLocalIp()
            self.iptext = iptext
            rviz_env = os.environ.copy()
            self.process_rviz = subprocess.Popen(['gnome-terminal', '--disable-factory', "-e",self.bashcommand],preexec_fn=os.setpgrp, env=rviz_env)
            self.statusbar.SetStatusText(textLocal[7] + self.iptext)
            self.b_connect.Disable()
        else:
            if(iptext=="..."):
                iptext=""
            self.statusbar.SetStatusText(textLocal[8]+ iptext)
            self.iptext = ""

    def killTerminal(self):
        if (self.hasPID):
            os.killpg(self.process_rviz.pid, signal.SIGINT)
        self.statusbar.SetStatusText(textLocal[9] + self.iptext)
        self.b_connect.Enable()


    def onTextKeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
            self.makeConnect()
            self.maskText.Navigate()
        event.Skip()

    def OnConnect(self, event):
        self.makeConnect()

    def onShutdown(self,event):
        self.killTerminal()

    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
                               textLocal[10],
                               textLocal[11], wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.killTerminal()
            self.Destroy()

def runApp():
    app = wx.App(redirect=True)  # Error messages go to popup window
    top = Frame(textLocal[12])
    top.Show()
    app.MainLoop()

runApp()