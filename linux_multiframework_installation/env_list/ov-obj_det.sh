#!/bin/bash

echo =======================================================
echo $'\t'Install OpenVino Object Detect Packages
echo =======================================================

if [ -d "$PWD/env/obj_ov" ]; then
    echo OpenVino Object Detect  is already exist!
    read -p "Do you want to delete and reinstall?(y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        rm -r "$PWD/env/obj_ov"
    else
        exit 0
    fi
fi

python3 -m venv $PWD/env/obj_ov
source $PWD/env/obj_ov/bin/activate
python3 -m pip install --upgrade pip
pip install -r ../obj-detect/requirements.txt
if [ -f "../videos/obj_video.mp4" ]; then
    echo OpenVino demo video is already exist!
else 
    wget -P ../videos https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/video/people.mp4
    mv ../videos/people.mp4 ../videos/obj_video.mp4
fi
echo "OpenVino Object detect Environment Installation Completed!"