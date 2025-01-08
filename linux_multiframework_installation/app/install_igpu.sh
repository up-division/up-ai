#!/bin/bash

ori_dir=$(pwd)

# Install iGPU driver
echo "Install igpu driver......"
cd $ori_dir
wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | \
sudo gpg --yes --dearmor --output /usr/share/keyrings/intel-graphics.gpg

echo "deb [arch=amd64,i386 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu jammy client" | \
sudo tee /etc/apt/sources.list.d/intel-gpu-jammy.list
sudo apt update
sudo apt install -y \
	intel-opencl-icd intel-level-zero-gpu level-zero \
	intel-media-va-driver-non-free libmfx1 libmfxgen1 libvpl2 \
	libegl-mesa0 libegl1-mesa libegl1-mesa-dev libgbm1 libgl1-mesa-dev libgl1-mesa-dri \
	libglapi-mesa libgles2-mesa-dev libglx-mesa0 libigdgmm12 libxatracker2 mesa-va-drivers \
	mesa-vdpau-drivers mesa-vulkan-drivers va-driver-all vainfo hwinfo clinfo
sudo apt-get install -y linux-firmware
echo "GRUB_CMDLINE_LINUX='i915.force_probe=7d55'" | sudo tee -a /etc/default/grub > /dev/null
sudo update-grub
echo "iGPU Installation Completed!"
