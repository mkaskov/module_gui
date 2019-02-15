#!/usr/bin/env python
"""
usage:
rosrun proteus_demo ImageView.py image:=/ATRV/CameraMain
"""
import roslib
roslib.load_manifest('rospy')
roslib.load_manifest('sensor_msgs')
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String as rosString
import wx.lib.masked as masked
import wx
import sys
from util import scanLocalNetwork
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess
import signal
import rospkg

# Option to remove maps from control panel?

rospack = rospkg.RosPack()
package_path = rospack.get_path('puremindgui')
bash_path = package_path + "/script/bash/"

localization = dict(
    new='new map',
    open='open map',
    edit='edit map',
    new_map_name='new map name',
    map_list="map_list",
    launch_map = "launch",
    app_name = "Puremind robot Control Panel",
    app_confirm_exit = "Confirm exit",
    app_exit_message = "Do you really want to close this application?"
)

isUpdated = False

pubcommand = rospy.Publisher("/slam/mapcommand", rosString,queue_size=10)
shutdownAll = rospy.Publisher("/remote_manager/shutdown", rosString,queue_size=10)


iSsave_map = 0
iSonly_odom = 0
iSdelet_map_on_start = 0
localizationType = 0
publish_pcl=0

# mods 1 -new, 2-open,3-edit  // # localization 1 - localization,2 - edit // # savemap  1 -save,2-not save
# pcl - 1 publish, 2 -notpublish
# delet_map_on_start 1 - delete, 2 - notdelete
# onlyodom 1 - odom,2- noodom

level1 = 10
# level2 = level1+200
level2 = 10
# level3 = level2+310
level3 = 10

sizepanel1 = (600,250)
sizepanel2 = (600,320)
sizepanel3 = (600,100)

class PureMindGui(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, title = localization['app_name'], size = (600, sizepanel1[1]+sizepanel2[1]+sizepanel3[1]),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.frame.Bind(wx.EVT_CLOSE, self.OnClose)
        self.frame.statusbar = self.frame.CreateStatusBar()






        self.ros_env = None

        self.hasPID = False
        self.iptext = ""

        self.lastMapName = ""

        self.slamCommand = []
        self.lastSlamCommand = -1

        self.process_list = []

        self.mapListArray = []

        self.process_rviz = None



        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")

        self.frame.Bind(wx.EVT_MENU, self.OnClose, m_exit)

        menuBar.Append(menu, "&File")
        self.frame.SetMenuBar(menuBar)

        self.makePanelConnect()
        self.makePanelSlam()
        self.makePanelTools()

        self.panel_slam.Disable()
        self.panel_tools.Disable()

        self.executor = ThreadPoolExecutor(max_workers=2)
        threadGetRobotList = self.executor.submit(scanLocalNetwork.getRobotList)
        threadGetRobotList.add_done_callback(self.callbackRobotList)

        self.frame.Show(True)
        return True

    def makePanelConnect(self):
        self.panel_connect = Panel(self.frame, size=sizepanel1)
        self.panel_connect.SetBackgroundColour((200, 200, 11)) # delete

        lbl1 = wx.StaticText(self.panel_connect, -1, style=wx.ALIGN_CENTER, pos=(10, level1 + 0))
        lbl1.SetFont(self.frame.GetFont())
        lbl1.SetLabel("ip address")

        control = ["ip address", "###.###.###.###", "", 'F^-', "^\d{3}.\d{3}.\d{3}.\d{3}", '', '', '']
        self.maskText = masked.TextCtrl(self.panel_connect,
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
                                        style=wx.TE_PROCESS_ENTER, pos=(10, level1 + 30))

        self.b_connect = wx.Button(self.panel_connect, wx.ID_CLOSE, "Connect", pos=(10, level1 + 65))
        self.b_connect.Bind(wx.EVT_BUTTON, self.OnConnect)

        m_shut = wx.Button(self.panel_connect, wx.ID_CLOSE, "Shutdown", pos=(10, level1 + 100))
        m_shut.Bind(wx.EVT_BUTTON, self.onShutdown)

        self.lbl2 = wx.StaticText(self.panel_connect, -1, style=wx.ALIGN_CENTER, pos=(200, level1 + 0))
        self.lbl2.SetFont(self.frame.GetFont())
        self.lbl2.SetLabel("scanning ...")

        self.btnReload = wx.Button(self.panel_connect, wx.ID_CLOSE, "Reload", pos=(315, level1 + 0))
        self.btnReload.Bind(wx.EVT_BUTTON, self.onReload)

        self.lst = wx.ListBox(self.panel_connect, pos=(200, level1 + 30), size=(200, 150), choices=[],
                              style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.selectRobotIp, self.lst)

        self.connect_status = wx.StaticText(self.panel_connect, -1, style=wx.ALIGN_CENTER, pos=(10, level1 + 200))
        self.connect_status.SetFont(self.frame.GetFont())
        self.connect_status.SetLabel("[CONNECT STATUS] ")

    def makePanelSlam(self):
        self.panel_slam = Panel(self.frame, size=sizepanel2, pos=(0, sizepanel1[1]))
        self.panel_slam.SetBackgroundColour((200, 0, 200)) # delete

        self.b_new = wx.Button(self.panel_slam, wx.ID_CLOSE, localization['new'], pos=(10, level2 + 0))
        self.b_new.Bind(wx.EVT_BUTTON, self.CreateNew)

        self.b_open = wx.Button(self.panel_slam, wx.ID_CLOSE, localization['open'], pos=(10, level2 + 40))
        self.b_open.Bind(wx.EVT_BUTTON, self.OpenMap)

        self.b_edit = wx.Button(self.panel_slam, wx.ID_CLOSE, localization['edit'], pos=(10, level2 + 80))
        self.b_edit.Bind(wx.EVT_BUTTON, self.EditMap)

        self.slamModeLbl = wx.StaticText(self.panel_slam, -1, style=wx.ALIGN_CENTER, pos=(120, level2 + 0))
        self.slamModeLbl.SetFont(self.frame.GetFont())
        self.slamModeLbl.SetLabel("map name")

        self.mapname = wx.TextCtrl(self.panel_slam, size=(250, -1), pos=(120, level2 + 30))
        self.maplst = wx.ListBox(self.panel_slam, size=(250, 200), pos=(120, level2 + 70), choices=[], style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX,self.selectMapName,self.maplst)

        self.b_runslam = wx.Button(self.panel_slam, wx.ID_CLOSE, "Run", pos=(380, level2 + 0))
        self.b_runslam.Bind(wx.EVT_BUTTON, self.runSlam)

        self.b_shutslam = wx.Button(self.panel_slam, wx.ID_CLOSE, "Shutdown", pos=(380, level2 + 100))
        self.b_shutslam.Bind(wx.EVT_BUTTON, self.shutSlam)

        # self.slamdelete = wx.CheckBox(self.panel_slam, label='delete map on start', pos=(380, level2 + 40))
        self.slamuseodom = wx.CheckBox(self.panel_slam, label='use odometry', pos=(380, level2 + 70))
        # self.slampubpcl = wx.CheckBox(self.panel_slam, label='publish pcl', pos=(380, level2 + 100))

        self.lbl_slamstatus = wx.StaticText(self.panel_slam, -1, style=wx.ALIGN_CENTER, pos=(10, level2 + 280))
        self.lbl_slamstatus.SetFont(self.frame.GetFont())
        self.lbl_slamstatus.SetLabel("[SLAM STATUS]")

        self.clearSlamPanel()

    def clearSlamPanel(self):
        self.mapname.Disable()
        self.maplst.Disable()
        self.slamuseodom.Disable()
        self.b_runslam.Disable()
        self.b_shutslam.Disable()
        self.slamModeLbl.SetLabelText("")
        self.lbl_slamstatus.SetLabelText("[SLAM STATUS]")
        self.b_edit.Enable()
        self.b_new.Enable()
        self.b_open.Enable()

    def makePanelTools(self):
        self.panel_tools = Panel(self.frame, size=sizepanel3, pos=(0, sizepanel1[1]+sizepanel2[1]))
        self.panel_tools.SetBackgroundColour((0, 200, 200)) # delete

        self.lbl_robotTools = wx.StaticText(self.panel_tools, -1, style=wx.ALIGN_CENTER, pos=(10, level3 + 0))
        self.lbl_robotTools.SetFont(self.frame.GetFont())
        self.lbl_robotTools.SetLabel("------------------ [ROBOT TOOLS] ------------------")

        self.b_toolsrviz = wx.Button(self.panel_tools, wx.ID_CLOSE, "Rviz", pos=(10, level3 + 30))
        self.b_toolsrviz.Bind(wx.EVT_BUTTON, self.runRviz)

        self.b_toolsrvizshut = wx.Button(self.panel_tools, wx.ID_CLOSE, "Stop Rviz", pos=(100, level3 + 30))
        self.b_toolsrvizshut.Bind(wx.EVT_BUTTON, self.shutDownRviz)

    def clearToolsPanel(self):
        self.b_toolsrviz.Enable()
        self.b_toolsrvizshut.Disable()

    def extendIP(self,ip_,merger):
        text_ = ip_.split(".")
        text_ = ["{:03d}".format(int(elem)) for elem in text_]
        return merger.join(text_)

    def callbackRobotList(self,value):
        if(len(value.result())>0):
            wx.CallAfter(self.lst.Set, value.result())
            wx.CallAfter(self.lbl2.SetLabel,  'robots list')
            wx.CallAfter(self.btnReload.Enable)
        else:
            wx.CallAfter(self.lbl2.SetLabel, 'robots not found')
            wx.CallAfter(self.btnReload.Enable)

    def subRosMapList(self):
        self.ros_maplist_sub = rospy.Subscriber("/slam/maplist", rosString, self.updMapList)

    def OnConnect(self, event):
        statusConnect,env_ros =self.makeConnect()

        if statusConnect:
            self.clearSlamPanel()
            self.clearToolsPanel()

            self.connect_status.SetLabel('connected to robot: ' + self.maskText.GetValue())
            self.panel_slam.Enable()
            self.panel_tools.Enable()
            self.maskText.Disable()
            self.b_connect.Disable()
            self.ros_env = env_ros
            self.subRosMapList()
        else:
            self.panel_slam.Disable()
            self.panel_tools.Disable()
            self.maskText.Enable()
            self.b_connect.Enable()
            self.ros_env = None
            self.connect_status.SetLabel('robot unavailable: ' + self.maskText.GetValue())

    def onShutdown(self,event):
        self.clearProcesses()

        self.panel_slam.Disable()
        self.panel_tools.Disable()
        self.maskText.Enable()
        self.b_connect.Enable()
        self.ros_env = None

        self.connect_status.SetLabel('disconnected from robot: ' + self.iptext)
        self.iptext = ""

        self.clearSlamPanel()

    def clearProcesses(self):
        rosstr = rosString()
        rosstr.data = ",".join("")
        shutdownAll.publish(rosstr)

        for proc in self.process_list:
            os.killpg(proc.pid, signal.SIGINT)

        self.process_list = []

    def onReload(self,event):
        self.lbl2.SetLabel("scanning ...")
        self.lst.Set([])
        threadGetRobotList = self.executor.submit(scanLocalNetwork.getRobotList)
        threadGetRobotList.add_done_callback(self.callbackRobotList)
        self.btnReload.Disable()

    def selectRobotIp(self,event):
        text_ = self.lst.GetString(self.lst.GetSelection())
        self.maskText.SetValue(self.extendIP(text_,""))

    def selectMapName(self,event):
        text__ = self.maplst.GetString(self.maplst.GetSelection())
        self.mapname.SetValue(text__)

    def makeConnect(self):
        topicsrospy_ = rospy.get_published_topics()
        topics_ = [x[0] for x in topicsrospy_]

        if "/slam/maplist" not in topics_:
            return False,None

        self.connect_status.SetLabel('')
        iptext = self.maskText.GetValue().replace(' ', '')

        if (self.extendIP(scanLocalNetwork.getLocalIp(), ".") == iptext or scanLocalNetwork.pingit(iptext)):
            self.hasPID = True

            if (self.extendIP(scanLocalNetwork.getLocalIp(), ".") != iptext):
                os.environ['ROS_MASTER_URI'] = "http://ipaddr:11311".replace("ipaddr", iptext)
                os.environ['ROS_IP'] = scanLocalNetwork.getLocalIp()
            self.iptext = iptext
            return True, os.environ.copy()
        else:
            if (iptext == "..."):
                iptext = ""
            self.iptext = ""
            return False,None

    def runRviz(self,event):
        if self.ros_env is not None:
            bashcommand = 'bash ' + bash_path + 'launchRviz.bash'
            self.process_rviz = subprocess.Popen(['gnome-terminal', '--disable-factory', "-e", bashcommand],preexec_fn=os.setpgrp, env=self.ros_env)
            self.process_list.append(self.process_rviz)
            self.b_toolsrviz.Disable()
            self.b_toolsrvizshut.Enable()
        else:
            print ('rviz: ros env not found')

    def shutDownRviz(self,event):
        if self.process_rviz is not None:
            os.killpg(self.process_rviz.pid, signal.SIGINT)
        self.clearToolsPanel()

    def shutSlam(self,event):
        rosstr = rosString()
        rosstr.data = "-1"
        pubcommand.publish(rosstr)
        self.clearSlamPanel()
        self.subRosMapList()

    def runSlam(self,event):
        self.lbl_slamstatus.SetLabelText("[SLAM STATUS]")

        if(len(self.slamCommand)==0):
            self.slamCommand = [str(self.lastSlamCommand)]

        if self.lastSlamCommand==1 and self.mapname.GetValue() in self.mapListArray:
            self.lbl_slamstatus.SetLabelText ("[SLAM STATUS] map exist: " + self.mapname.GetValue())
            return


        self.slamCommand.append(self.mapname.GetValue())
        self.slamCommand.append(str(int(self.slamuseodom.GetValue())))

        rosstr = rosString()
        rosstr.data = ",".join(self.slamCommand)

        pubcommand.publish(rosstr)

        slamStatusText_ = ""
        if self.slamCommand[0]=="1":
            slamStatusText_ = "New map: " +self.mapname.GetValue()
        elif self.slamCommand[0]=="2":
            slamStatusText_ = "Open map: " + self.mapname.GetValue()
        elif self.slamCommand[0] == "3":
            slamStatusText_ = "Edit map: " + self.mapname.GetValue()

        self.clearSlamPanel()

        self.lbl_slamstatus.SetLabelText("[SLAM STATUS] "+slamStatusText_)

        self.b_shutslam.Enable()
        self.b_runslam.Disable()
        self.b_edit.Disable()
        self.b_new.Disable()
        self.b_open.Disable()

        self.slamCommand = []

    def CreateNew(self,event):
        self.mapname.Enable()
        self.maplst.Disable()
        self.slamuseodom.Disable()
        self.b_runslam.Enable()
        self.b_shutslam.Disable()
        self.slamCommand = ["1"]
        self.lastSlamCommand = 1
        self.slamModeLbl.SetLabelText("New Map")

    def OpenMap(self,event):
        self.mapname.Disable()
        self.maplst.Enable()
        self.slamuseodom.Enable()
        self.b_runslam.Enable()
        self.b_shutslam.Disable()
        self.slamCommand = ["2"]
        self.lastSlamCommand = 2
        self.slamModeLbl.SetLabelText("Open Map")

    def EditMap(self,event):
        self.mapname.Disable()
        self.maplst.Enable()
        self.slamuseodom.Disable()
        self.b_runslam.Enable()
        self.b_shutslam.Disable()
        self.slamCommand = ["3"]
        self.lastSlamCommand = 3
        self.slamModeLbl.SetLabelText("Edit Map")

    def OnClose(self, event):
        dlg = wx.MessageDialog(self.frame,
                               localization['app_exit_message'],
                               localization['app_confirm_exit'], wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.clearProcesses()
            self.frame.Destroy()

    def updMapList(self,data):
        maps = data.data
        # print ("maplist ",maps)
        maplist = [x.strip() for x in maps.split(',')]
        self.lastMapName = maplist[:-1] # lastmap info
        self.mapListArray = maplist[:-1]
        wx.CallAfter(self.maplst.Set, maplist[:-1])
        self.ros_maplist_sub.unregister()

class Panel(wx.Panel):
    def updMapList(self,maps):
        return

def handle(data):
    global isUpdated
    if not isUpdated:
        wx.CallAfter(wx.GetApp().updMapList, data)
        isUpdated = True

def main(argv):
    app = PureMindGui()
    rospy.init_node('pureminggui_mapselector')
    # rospy.Subscriber("/slam/maplist", rosString, handle)
    print(__doc__)
    app.MainLoop()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))