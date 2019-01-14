import os
import subprocess
import sys
import signal

from subprocess import Popen

os.environ['ROS_MASTER_URI'] = "http://192.168.1.213:11311"
# subprocess.Popen("source /opt/ros/kinetic/setup.bash", shell=True, executable='/bin/bash')
# subprocess.Popen("source /opt/ros/kinetic/setup.bash && roslaunch puremindgui rviz.launch", shell=True, executable='/bin/bash')
# subprocess.call('source /opt/ros/kinetic/setup.bash && roslaunch puremindgui rviz.launch', shell=True)
# subprocess.Popen(['/bin/bash', '-c', "source /opt/ros/kinetic/setup.bash"])
# subprocess.Popen(['/bin/bash', '-c', "roslaunch puremindgui rviz.launch"])
# subprocess.call("source /opt/ros/kinetic/setup.bash", shell=True)
# subprocess.call('roslaunch puremindgui rviz.launch', shell=True)


# Popen("source /opt/ros/kinetic/setup.bash && roslaunch puremindgui rviz.launch", shell=True,  executable='/bin/bash',preexec_fn=os.setsid,creationflags=subprocess.CREATE_NEW_CONSOLE)
# Popen("source /opt/ros/kinetic/setup.bash",executable='/bin/bash' ,shell=True,stdout=subprocess.PIPE)
# Popen("sh launch.sh")
# subprocess.call(["gnome-terminal","-e","bash sh launch.sh"])
# Popen("roslaunch puremindgui rviz.launch", shell=True,  executable='/bin/bash',preexec_fn=os.setsid)

# os.system("gnome-terminal -e 'bash -c \"sudo apt-get update; exec bash\"'")
# os.system("gnome-terminal -e 'bash -c \"bash launch.bash; exec bash\"'")

process_rviz = subprocess.Popen("gnome-terminal -e 'bash -c \"bash launch.bash; exec bash\"'", shell=True, executable='/bin/bash')

os.killpg(os.getpgid(process_rviz.pid), signal.SIGTERM)