#!/bin/bash

ori_dir=$(pwd)
sudo apt install -y dkms linux-headers-$(uname -r)

hailort_pcie_driver=$(dpkg -l | grep hailort-pcie-driver | awk '{print $3}')
hailort=$(dpkg -l | grep hailort | grep -v hailort-pcie-driver | awk '{print $3}')

echo "Install Hailo pcie driver now......"
if [ -z "$hailort_pcie_driver" ]; then
    yes | sudo dpkg --install $ori_dir/inst/linux/app/driver/hailo/hailort-pcie-driver_4.23.0_all.deb
elif [ "$hailort_pcie_driver" == "4.19.0" ]; then
    sudo dpkg -P hailort-pcie-driver
    yes | sudo dpkg --install $ori_dir/inst/linux/app/driver/hailo/hailort-pcie-driver_4.23.0_all.deb
else
    echo "Hailort-pcie-driver is already installed."
fi

echo "Install HailoRT now......"
if [ -z "$hailort" ]; then
    yes | sudo dpkg --install $ori_dir/inst/linux/app/driver/hailo/hailort_4.23.0_amd64.deb
elif [ "$hailort" == "4.19.0" ]; then
    sudo dpkg -P hailort
    yes | sudo dpkg --install $ori_dir/inst/linux/app/driver/hailo/hailort_4.23.0_amd64.deb
else
    echo "HailoRT is already installed."
fi
