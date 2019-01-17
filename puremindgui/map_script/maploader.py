#!/usr/bin/env python
# by Sangheli a.savel.vic@gmail.com
from __future__ import print_function
import rospy
import os
import yaml
import sys
import re
import rospkg
import configparser
import shutil
from std_msgs.msg import String as rosString
import wx, wx.html,wx.lib
import wx.lib.masked as masked
import subprocess
import signal

localization = dict(
    new='new map',
    open='open map',
    edit='edit map',
    new_map_name='new map name',
    map_list="map_list",
    launch_map = "launch",
    app_name = "Slam map loader",
    app_confirm_exit = "Confirm exit",
    app_exit_message = "Do you really want to close this application?"
)

class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150, 150), size=(800, 400),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.statusbar = self.CreateStatusBar()

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)



        lbl_mapname = wx.StaticText(self.panel, -1, style=wx.ALIGN_CENTER, pos=(10, 10))
        lbl_mapname.SetFont(self.GetFont())
        lbl_mapname.SetLabel("map name")

        self.mapname = wx.TextCtrl(self.panel, size=(200, -1),pos=(10, 40))
        self.b_new = wx.Button(self.panel, wx.ID_CLOSE, localization['new'], pos=(10, 80))





        self.b_open = wx.Button(self.panel, wx.ID_CLOSE, localization['open'], pos=(250, 10))
        self.b_edit = wx.Button(self.panel, wx.ID_CLOSE, localization['edit'], pos=(350, 10))

        lbl_maplist = wx.StaticText(self.panel, -1, style=wx.ALIGN_CENTER, pos=(250, 50))
        lbl_maplist.SetFont(self.GetFont())
        lbl_maplist.SetLabel("map list")

        self.maplst = wx.ListBox(self.panel, pos=(250, 80), size=(250, 200), choices=[], style=wx.LB_SINGLE)

    def updMapList(self,maps):
        print(maps)

    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
                               localization['app_exit_message'],
                               localization['app_confirm_exit'], wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

top = None
app = None

def runApp():
    global top,app
    app = wx.App(redirect=True)  # Error messages go to popup window
    top = Frame(localization['app_name'])
    top.Show()
    app.MainLoop()
    # app.MainLoop()

def readml(data):
    print(data)


def handle(data):
    # print(data)
    wx.CallAfter(app.updMapList, data)

def main():
    global top, app
    rospy.init_node('maploader_remote_slam')
    app = wx.App(redirect=True)  # Error messages go to popup window
    top = Frame(localization['app_name'])
    top.Show()

    # rospy.Subscriber("/slam/maplist", rosString, top.updMapList)
    rospy.Subscriber("/slam/maplist", rosString, handle)
    # runApp()
    # rospy.spin()
    app.MainLoop()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass