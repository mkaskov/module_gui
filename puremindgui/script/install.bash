#!/usr/bin/env bash
sudo apt install libappstream3 -y
sudo apt install git -y
sudo apt install python-pip -y
sudo pip2 install pyinstaller
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116
sudo apt-get update
sudo apt install ros-kinetic-desktop-full -y
sudo rosdep init
rosdep update
sudo apt install python-rosinstall python-rosinstall-generator python-wstool build-essential -y
echo "source /opt/ros/kinetic/setup.bash" >> ~/.bashrc
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
echo "ROS_IP=$(hostname -I | cut -d' ' -f1)" >> ~/.bashrc
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src/
git clone https://github.com/mkaskov/module_gui
cd ~/catkin_ws/
source /opt/ros/kinetic/setup.bash
catkin_make
source ~/.bashrc
cd ~/catkin_ws/src/module_gui/puremindgui/script/
bash build.bash
