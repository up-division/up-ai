#!/bin/bash

ori_dir=$(pwd)
sudo apt install -y dkms linux-headers-$(uname -r)

echo "Install Hailo pcie driver now......"
if dpkg -l | grep hailort-pcie-driver;then
    echo "Hailort-pcie-driver is already installed."
else
    sudo dpkg --install $ori_dir/app/driver/hailo/hailort-pcie-driver_4.19.0_all.deb
fi

echo "Install HailoRT now......"
if dpkg -l | grep hailort | grep -v hailort-pcie-driver;then
    echo "HailoRT is already installed."
else
    sudo dpkg --install $ori_dir/app/driver/hailo/hailort_4.19.0_amd64.deb
fi
