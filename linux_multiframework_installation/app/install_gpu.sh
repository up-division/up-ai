#!/bin/bash

ori_dir=$(pwd)

# Install GPU driver
echo "Install gpu driver......"

if [ ! -d "$PWD/app/driver/cuda" ]; then
	mkdir -p $PWD/app/driver/cuda
fi
cd $ori_dir/app/driver/cuda

if [ ! -f "intel-level-zero-npu_1.10.0.20241107-11729849322_ubuntu22.04_amd64.deb" ]; then
	wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
else
	echo This .deb is already exist!
fi

sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-drivers-550
sudo apt-get -y install cuda-toolkit-12-4
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
echo "GPU Installation Completed!"
