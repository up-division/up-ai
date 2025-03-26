#!/bin/bash

echo ===================================================
echo $'\t'Install Cuda Object Detect Packages
echo ===================================================

if [ -d "$PWD/inst/linux/env/obj_cuda" ]; then
    echo Cuda Object Detect is already exist!
    read -p "Do you want to delete and reinstall?(y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        rm -r "$PWD/inst/linux/env/obj_cuda"
    else
        exit 0
    fi
fi

python3 -m venv $PWD/inst/linux/env/obj_cuda
source $PWD/inst/linux/env/obj_cuda/bin/activate
python3 -m pip install --upgrade pip
pip install ultralytics
echo "Cuda Object detect Environment Installation Completed!"
