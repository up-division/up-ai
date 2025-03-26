#!/bin/bash

echo =======================================================
echo $'\t'Install OpenVino Object Detect Packages
echo =======================================================

if [ -d "$PWD/inst/linux/env/obj_ov" ]; then
    echo OpenVino Object Detect  is already exist!
    read -p "Do you want to delete and reinstall?(y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        rm -r "$PWD/inst/linux/env/obj_ov"
    else
        exit 0
    fi
fi

python3 -m venv $PWD/inst/linux/env/obj_ov
source $PWD/inst/linux/env/obj_ov/bin/activate
python3 -m pip install --upgrade pip
pip install -r demos/obj-detect/intel/requirements.txt
if [ -f "demos/obj-detect/videos/obj_video.mp4" ]; then
    echo OpenVino demo video is already exist!
else 
    wget -P demos/obj-detect/videos https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/video/people.mp4
    mv demos/obj-detect/videos/people.mp4 demos/obj-detect/videos/obj_video.mp4
fi
echo "OpenVino Object detect Environment Installation Completed!"
