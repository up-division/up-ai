#!/bin/bash

ori_dir=$(pwd)

echo "Donload code from GitHub"

git clone -b v2.3.3 --recurse-submodules https://github.com/DEEPX-AI/dx-all-suite.git $ori_dir/demos/dx-all-suite

# Install runtime package
echo "Install runtime package......"
cd $ori_dir/demos/dx-all-suite/dx-runtime/
./install.sh --all

cd $ori_dir/demos/dx-all-suite/dx-runtime/

./dx_app/setup.sh --all

chown -R $USER:$USER ./dx_app/

#pip install $ori_dir/demos/dx_engine-3.3.2-cp312-cp312-linux_x86_64.whl --break-system-packages

cd $ori_dir
