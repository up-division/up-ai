#!/bin/bash

echo ====================================================
echo $'\t'Install Hailo Object Detect Packages
echo ====================================================

# Hailo 8/8L
if [ -d "$PWD/inst/linux/app/hailo-apps-infra/venv_hailo_apps" ]; then
    echo ======================================================
    echo $'\t'Hailo8 Object Detect  is already exist!
    echo ======================================================
    read -p "Do you want to delete and reinstall?(y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        sudo rm -rf "$PWD/inst/linux/app/hailo-apps-infra/venv_hailo_apps"
    else
        exit 0
    fi
fi

# Hailo 10
if [ -d "$PWD/inst/linux/app/hailo-apps/venv_hailo10_apps" ];then
    echo ======================================================
    echo $'\t'Hailo10 Object Detect  is already exist!
    echo ======================================================
    read -p "Do you want to delete and reinstall?(y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        sudo rm -rf "$PWD/inst/linux/app/hailo-apps-infra/venv_hailo_apps"
    else
        exit 0
    fi
fi

# Hailo Chip ID: 2864 -> Hailo 8 ; 45c4 -> Hailo 10
HAS_HAILO10=false
HAS_HAILO8=false
if lspci -nn | grep -q '\[1e60:45c4\]'; then
    HAS_HAILO10=true
fi

if lspci -nn | grep -q '\[1e60:2864\]'; then
    HAS_HAILO8=true
fi

UBUNTU_VER=$(lsb_release -rs)

case "$UBUNTU_VER" in
        24.04)
            if $HAS_HAILO10; then
                echo Hailo 10 detected!
                sudo dpkg -i $PWD/inst/linux/app/driver/hailo/hailo10_5.3.0_patched.deb
                sudo dpkg -i $PWD/inst/linux/app/driver/hailo/hailort_5.3.0_amd64.deb
                sudo dpkg -i $PWD/inst/linux/app/driver/hailo/hailo-tappas-core_5.3.0_amd64.deb

                if [ ! -d "$PWD/inst/linux/app/hailo-apps/.git" ]; then
                    git clone https://github.com/hailo-ai/hailo-apps.git "$PWD/inst/linux/app/hailo-apps"
                fi

                python3 -m venv --system-site-packages $PWD/inst/linux/app/hailo-apps/venv_hailo10_apps
                source $PWD/inst/linux/app/hailo-apps/venv_hailo10_apps/bin/activate 
                pip install $PWD/inst/linux/app/driver/hailo/hailort-5.3.0-cp312-cp312-linux_x86_64.whl
                pip install $PWD/inst/linux/app/driver/hailo/hailo_tappas_core_python_binding-5.3.0-py3-none-any.whl
                pip install --upgrade pip
                cd $PWD/inst/linux/app/hailo-apps
                pip install -e .
                sudo $(which hailo-post-install)
            elif $HAS_HAILO8; then
                echo Hailo 8 detected!
                git clone -b v25.10.0 --depth=1 https://github.com/hailo-ai/hailo-apps-infra.git $PWD/inst/linux/app/hailo-apps-infra
                cd $PWD/inst/linux/app/hailo-apps-infra
                yes | sudo ./scripts/hailo_installer.sh --hw-arch=hailo8
                sudo ./install.sh
            else
                echo "No supported Hailo device found."
                exit 1
            fi
            ;;
        22.04)
            git clone -b 25.7.0 --depth=1 https://github.com/hailo-ai/hailo-apps-infra.git $PWD/inst/linux/app/hailo-apps-infra
            cd $PWD/inst/linux/app/hailo-apps-infra
            yes | sudo ./scripts/hailo_installer.sh
            sudo ./install.sh
            ;;
        *)
            echo "Unsupported Ubuntu version: $UBUNTU_VER. Exiting."
            exit 1
            ;;
esac
