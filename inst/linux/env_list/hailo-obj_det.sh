#!/bin/bash

echo ====================================================
echo $'\t'Install Hailo Object Detect Packages
echo ====================================================

if [ -f "$HOME/tappas/scripts/bash_completion.d/python-argcomplete" ]; then
    echo ======================================================
    echo $'\t'Hailo Object Detect  is already exist!
    echo ======================================================
    read -p "Do you want to delete and reinstall?(y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        rm -f "$HOME/tappas/scripts/bash_completion.d/python-argcomplete"
    else
        exit 0
    fi
fi

echo "Install Hailo tappas packages......"
#install require package
sudo apt-get install -y rsync ffmpeg x11-utils python3-dev python3-pip python3-setuptools python3-virtualenv python-gi-dev libgirepository1.0-dev gcc-12 g++-12 cmake git libzmq3-dev
#install cv
sudo apt-get install -y libopencv-dev python3-opencv
#install gstreamer
sudo apt-get install -y libcairo2-dev libgirepository1.0-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio gcc-12 g++-12 python-gi-dev
#install pygobject
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
#install tappas
git clone -b v3.30.0 --depth=1 https://github.com/hailo-ai/tappas.git $HOME/tappas
cd $HOME/tappas
./install.sh --skip-hailort

if [ -f "$HOME/tappas/scripts/bash_completion.d/_python-argcomplete" ];then
    mv $HOME/tappas/scripts/bash_completion.d/_python-argcomplete $HOME/tappas/scripts/bash_completion.d/python-argcomplete
fi

echo "Hailo Object detect Environment Installation Completed!"

