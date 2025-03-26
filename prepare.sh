#! /bin/bash

export PATH="/usr/local/bin:$PATH"
ori_dir=$(pwd)

python3 $ori_dir/inst/linux/app/board_check.py

if [ $? -eq 0 ]; then
    :
else
    echo "Sorry ! This board is not supported !"
    exit 0
fi

# check network connect
ping -c 4 8.8.8.8 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Network connection successful!"
else
    echo "Network connection failed!"
    echo "Please check your network connection!"
    exit 0
fi

sudo apt update
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev liblzma-dev libbz2-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget python3-venv

install_git() {
    echo "Install git now......"
    if ! command -v git &> /dev/null
    then
	sudo apt install -y git git-lfs
    else
	echo "Git is already installed !"
    fi
}

install_driver() {
    echo "Running driver installation script..."
    python3 $ori_dir/inst/linux/app/scanf_driver.py --install_driver
    echo "Driver is already installed !"
}

install_min() {
    clear
    echo ===========================================
    echo $'\t'Select Enviroment Installation
	echo ===========================================
	echo 1. Object Detection
	echo 2. Chatbot
	echo 0. Return to menu
	echo ===========================================
	read -p "Please input: " app
	
	case $app in
    	0) 
			main_menu;;
        1) 
            # source $PWD/env_list/ov-obj_det.sh
            python3 $ori_dir/inst/linux/app/scanf_driver.py -env -at 1
            ;;
        2) 
            # source $PWD/env_list/ov-chatbot.sh
            python3 $ori_dir/inst/linux/app/scanf_driver.py -env -at 2
            ;;
        *) 
            echo "Unknown option, please choose again!"
            read -p "Press any key to continue..."  # Wait for user to continue
            install_env
            ;;
    esac
}

install_git
install_driver
install_min

echo "Enviroment Installation is Complete! Please Reboot!"
