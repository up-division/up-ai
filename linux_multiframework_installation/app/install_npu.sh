#!/bin/bash

ori_dir=$(pwd)

# Install NPU driver
echo "Install npu driver......"
USER_NAME=$(whoami)
sudo dpkg --purge --force-remove-reinstreq intel-driver-compiler-npu intel-fw-npu intel-level-zero-npu
mkdir -p $ori_dir/app/driver/npu
cd $ori_dir/app/driver/npu

if [ ! -f "intel-driver-compiler-npu_1.10.0.20241107-11729849322_ubuntu22.04_amd64.deb" ]; then
	wget https://github.com/intel/linux-npu-driver/releases/download/v1.10.0/intel-driver-compiler-npu_1.10.0.20241107-11729849322_ubuntu22.04_amd64.deb
else
	echo This .deb is already exist!
fi

if [ ! -f "intel-fw-npu_1.10.0.20241107-11729849322_ubuntu22.04_amd64.deb" ]; then
	
	wget https://github.com/intel/linux-npu-driver/releases/download/v1.10.0/intel-fw-npu_1.10.0.20241107-11729849322_ubuntu22.04_amd64.deb
else
	echo This .deb is already exist!
fi

if [ ! -f "intel-level-zero-npu_1.10.0.20241107-11729849322_ubuntu22.04_amd64.deb" ]; then
	wget https://github.com/intel/linux-npu-driver/releases/download/v1.10.0/intel-level-zero-npu_1.10.0.20241107-11729849322_ubuntu22.04_amd64.deb
else
	echo This .deb is already exist!
fi

sudo apt update
sudo apt install -y libtbb12
sudo dpkg -i *.deb
sudo dpkg -l level-zero > /dev/null 2>&1

if [ ! -f "level-zero_1.17.44+u22.04_amd64.deb" ]; then
	wget https://github.com/oneapi-src/level-zero/releases/download/v1.17.44/level-zero_1.17.44+u22.04_amd64.deb
else
	echo This .deb is already exist!
fi

sudo dpkg -i level-zero*.deb
sudo chown $USER_NAME:$USER_NAME /dev/accel/accel0
echo "NPU Installation Completed!"

# Install kernel
version=$(grep "^VERSION_ID=" /etc/*-release | cut -d '=' -f2 | tr -d '"')
if [ "$version" == "22.04" ]; then
	sudo apt update
	sudo apt-get install linux-image-6.5.0-1009-oem
fi
