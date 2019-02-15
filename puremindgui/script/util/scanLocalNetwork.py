import socket
# import commands # for python2
import re
import subprocess

def getNetMask():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    iparr = s.getsockname()[0].split(".")
    netmask = iparr[0]+"."+iparr[1]+"."+iparr[2]+"."
    s.close()
    return netmask

def getLocalIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipaddr = s.getsockname()[0]
    s.close()
    return ipaddr

def pingit(hostip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

def pingLocalNetwork(netmask):
    # status, output = commands.getstatusoutput("nmap -sn -v "+netmask+"0/24")   # for python2
    # outarr = output.split("\n")                                                # for python2

    p = subprocess.Popen(["nmap -sn -v "+netmask+"0/24"], stdout=subprocess.PIPE,shell=True,  executable='/bin/bash')  # for python3
    output = str(p.stdout.read())                                                                                      # for python3
    # outarr = output.split("\\n")                                                                                       # for python3
    outarr = output.split("\n")      # ????                                                                                   # for python3

    outarrClean1 = [elem for elem in outarr if "scan report" in elem]
    outarrClean2 = [elem for elem in outarrClean1 if "host down" not in elem]

    return [re.findall(r'[0-9]+(?:\.[0-9]+){3}', elem)[0] for elem in outarrClean2]

def getRobotList():
    netmask = getNetMask()
    iplist = pingLocalNetwork(netmask)

    robotList = []

    for ip_ in iplist:
        if pingit(ip_):
            robotList.append(ip_)

    return robotList
