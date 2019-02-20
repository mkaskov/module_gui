import os
import subprocess

path = map_save_path = os.path.expanduser("~/catkin_ws/src/module_gui/puremindgui/script/")
command = path + "launchgui.bash"

def main():
    subprocess.call("bash "+command, shell=True)

if __name__ == '__main__':
    try:
        main()
    except:
        pass
