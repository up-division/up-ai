#!/bin/bash

ori_dir=$(pwd)
sudo apt --fix-broken install

# Function to display the main menu
main_menu() {
    clear
    echo =============================
    echo $'\t'Function Menu
    echo =============================
    echo 1. Object detect -- Video
    echo 2. Object detect -- Camera
    echo 3. Chatbot
    echo 0. Exit
    echo =============================
    read -p "Please input : " demo

    case $demo in
        0) exit 0 ;;
        1)
            python3 $ori_dir/inst/linux/app/scanf_driver.py -env -at 1
            objv_menu;;
        2) 
            python3 $ori_dir/inst/linux/app/scanf_driver.py -env -at 1
            objc_menu ;;
        3) 
            python3 $ori_dir/inst/linux/app/scanf_driver.py -env -at 2
            chatbot_menu ;;
        *) 
            echo "Unknown option, please choose again!"
            read -n 1 -s -p "Press any key to continue..."  # Wait for user to continue
            clear
            main_menu
            ;;
    esac
}

objv_menu() {
    echo ============================================================
    echo $'\t'Select Hardware "("Object Detection -- Video")"
    echo ============================================================

    dev_option=()
    index=1

    if lspci | grep -iq "Intel"; then
        dev_option+=("$index. Intel Device")
        intel_opt=$index
        ((index++))
    fi

    if lspci | grep -iq "Hailo"; then
        dev_option+=("$index. Hailo")
        hailo_opt=$index
        ((index++))
    fi

    if lspci | grep -iq "NVIDIA"; then
        dev_option+=("$index. Nvidia Device")
        nvidia_opt=$index
        ((index++))
    fi

    if [ ${#dev_option[@]} -gt 0 ]; then
        index=1
        for device in "${dev_option[@]}"; do
            echo "$device"
            ((index++))
        done
        echo 0. Return to main menu
        echo ============================================================
        read -p "Please input : " dev_option
    else
        echo No Compatible Hardware Detected!
        read -n 1 -s -p "Press any key to return to main menu......"
        main_menu
    fi

    case $dev_option in
        0) 
            main_menu;;
        $intel_opt) 
            if [ -f "$PWD/inst/linux/env/obj_ov/bin/activate" ];then
                source inst/linux/env/obj_ov/bin/activate
                echo Start Object Detect......
                cd demos/obj-detect/intel
                python3 demo.py
                cd $ori_dir
            else
                echo This demo environment not install! Please choose again!
                read -n 1 -s -p "Press any key to continue..."
                clear
                objv_menu
            fi
            ;;
        $hailo_opt)
            if [ -f "$HOME/.hailo/tappas/tappas_env" ];then
                source $HOME/.hailo/tappas/tappas_env
                echo Start Object Detect......
                cd $HOME/tappas
                ./apps/h8/gstreamer/general/multistream_detection/multi_stream_detection.sh --show-fps
            else
                echo This demo environment not install! Please choose again!
                read -n 1 -s -p "Press any key to continue..."
                clear
                objv_menu
            fi
            ;;
        $nvidia_opt)
            if [ -f "$PWD/inst/linux/env/obj_cuda/bin/activate" ];then
                source inst/linux/env/obj_cuda/bin/activate
                echo Start Object Detect......
                python3 $PWD/inst/linux/app/pytorch/yolov11_predict.py ../videos/obj_video.mp4
                cd $ori_dir
            else
                echo This demo environment not install! Please choose again!
                read -n 1 -s -p "Press any key to continue..."
                clear
                objv_menu
            fi
            #main_menu
            ;;
        *)
            echo "Unknown option, please choose again!"
            read -n 1 -s -p "Press any key to continue..."
            clear
            objv_menu
            ;;
    esac
}

objc_menu() {
    clear
    echo =============================================================
    echo $'\t'Select Hardware "("Object Detection -- Camera")"
    echo =============================================================

    dev_option=()
    index=1

    if lspci | grep -iq "Intel"; then
        dev_option+=("$index. Intel Device")
        intel_opt=$index
        ((index++))
    fi

    if lspci | grep -iq "NVIDIA"; then
        dev_option+=("$index. Nvidia Device")
        nvidia_opt=$index
        ((index++))
    fi

    if [ ${#dev_option[@]} -gt 0 ]; then
        index=1
        for device in "${dev_option[@]}"; do
            echo "$device"
            ((index++))
        done
        echo 0. Return to main menu
        echo ============================================================
        read -p "Please input : " dev_option
    else
        echo No Compatible Hardware Detected!
        read -n 1 -s -p "Press any key to return to main menu......"
        main_menu
    fi

    case $dev_option in
        0) 
            main_menu;;
        $intel_opt) 
            if [ -f "$PWD/inst/linux/env/obj_ov/bin/activate" ];then
                source inst/linux/env/obj_ov/bin/activate
                echo Start Object Detect......
                cd demos/obj-detect/intel
                python3 demo.py 0
                cd $ori_dir
            else
                echo This demo environment not install! Please choose again!
                read -n 1 -s -p "Press any key to continue..."
                clear
                objc_menu
            fi
            ;;
        $nvidia_opt)
            if [ -f "$PWDcenv/obj_cuda/bin/activate" ];then
                source inst/linux/env/obj_cuda/bin/activate
                echo Start Object Detect......
                python3 $PWD/inst/linux/app/pytorch/yolov11_predict.py 0
                cd $ori_dir
            else
                echo This demo environment not install! Please choose again!
                read -n 1 -s -p "Press any key to continue..."
                clear
                objc_menu
            fi
            main_menu
            ;;
        *)
            echo "Unknown option, please choose again!"
            read -n 1 -s -p "Press any key to continue..."
            clear
            objc_menu
            ;;
    esac
}

chatbot_menu() {
    echo ==========================================
    echo        $'\t'Select Hardware "("Chatbot")"
    echo ==========================================

    dev_option=()
    index=1

    if lspci | grep -iq "Intel"; then
        dev_option+=("$index. Intel Device")
        intel_opt=$index
        ((index++))
    fi

    if [ ${#dev_option[@]} -gt 0 ]; then
        index=1
        for device in "${dev_option[@]}"; do
            echo "$device"
            ((index++))
        done
        echo 0. Return to main menu
        echo ============================================================
        read -p "Please input : " dev_option
    else
        echo No Compatible Hardware Detected!
        read -n 1 -s -p "Press any key to return to main menu......"
        main_menu
    fi

    case $dev_option in
        0) 
            main_menu;;
        $intel_opt) 
            if [ -f "$PWD/inst/linux/env/chatbot/bin/activate" ]; then
                source inst/linux/env/chatbot/bin/activate
                echo Start Chatbot......
                cd demos/chatbot
                python3 chatbot.py
                cd $ori_dir
                chatbot_menu
            else
                echo This demo environment not install! Please choose again!
                read -n 1 -s -p "Press any key to continue..."
                clear
                chatbot_menu
            fi
            ;;
        *)
            echo "Unknown option, please choose again!"
            read -n 1 -s -p "Press any key to continue..."
            clear
            objc_menu
            ;;
    esac
}

# Start the script by calling the main menu
if [ $# -lt 1 ] ; then
cd $ori_dir/demos/edge-ai-sizing-tool
./start.sh
firefox "http://localhost:8080/"
else
main_menu
fi
