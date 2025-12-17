#!/bin/bash

echo ====================================================
echo $'\t'Install Hailo Object Detect Packages
echo ====================================================

if [ -d "$PWD/inst/linux/app/hailo-apps-infra/venv_hailo_apps" ]; then
    echo ======================================================
    echo $'\t'Hailo Object Detect  is already exist!
    echo ======================================================
    read -p "Do you want to delete and reinstall?(y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        sudo rm -rf "$PWD/inst/linux/app/hailo-apps-infra/venv_hailo_apps"
    else
        exit 0
    fi
fi

ubuntu_version=$(lsb_release -rs)

case "$ubuntu_version" in
        24.04)
            git clone -b v25.10.0 --depth=1 https://github.com/hailo-ai/hailo-apps-infra.git $PWD/inst/linux/app/hailo-apps-infra
            cd $PWD/inst/linux/app/hailo-apps-infra
            yes | sudo ./scripts/hailo_installer.sh --hw-arch=hailo8
            sudo ./install.sh
            ;;
        22.04)
            git clone -b 25.7.0 --depth=1 https://github.com/hailo-ai/hailo-apps-infra.git $PWD/inst/linux/app/hailo-apps-infra
            cd $PWD/inst/linux/app/hailo-apps-infra
            yes | sudo ./scripts/hailo_installer.sh
            sudo ./install.sh
            ;;
        *)
            echo "Unsupported Ubuntu version: $ubuntu_version. Exiting."
            exit 1
            ;;
esac
