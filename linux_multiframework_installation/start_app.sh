#!/bin/bash

ori_dir=$(pwd)
sudo apt --fix-broken install

# Function to display the main menu
main_menu() {
    clear
    echo ===========================
    echo        $'\t'Function Menu
    echo ===========================
    echo 1. Object detect -- Video
    echo 2. Object detect -- Camera
    echo 3. Chatbot
    echo 0. Exit
    echo ===========================
    read -p "Please input : " demo

    case $demo in
        0) exit 0 ;;
        1) objv_menu;;
        2) objc_menu ;;
        3) chatbot_menu ;;
        *) 
            echo "Unknown option, please rechoose!"
            read -p "Press any key to continue..."  # Wait for user to continue
            clear
            main_menu
            ;;
    esac
}

objv_menu() {
    echo ============================================================
    echo        $'\t'Select Hardware "("Object Detection -- Video")"
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
        read -p "Press any key to return to main menu......"
        main_menu
    fi

    case $dev_option in
        0) 
            main_menu;;
        $intel_opt) 
            if [ -f "$PWD/env/obj_ov/bin/activate" ];then
                source env/obj_ov/bin/activate
                echo Start Object Detect......
                cd $PWD/../obj-detect
                python3 demo.py
                cd $ori_dir
            else
                echo This demo environment not install! Please rechoose!
                read -p "Press any key to continue..."
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
                echo This demo environment not install! Please rechoose!
                read -p "Press any key to continue..."
                clear
                objv_menu
            fi
            ;;
        $nvidia_opt)
            if [ -f "$PWD/env/obj_cuda/bin/activate" ];then
                source env/obj_cuda/bin/activate
                echo Start Object Detect......
                mkdir -p $PWD/up-ai/obj-cuda
                cd $PWD/../obj-cuda
                yolo predict model=yolo11n.pt source="https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/video/people.mp4" show=True save=False device=0
                cd $ori_dir
            else
                echo This demo environment not install! Please rechoose!
                read -p "Press any key to continue..."
                clear
                objv_menu
            fi
            main_menu
            ;;
        *)
            echo "Unknown option, please rechoose!"
            read -p "Press any key to continue..."
            clear
            objv_menu
            ;;
    esac
}

objc_menu() {
    clear
    echo =============================================================
    echo        $'\t'Select Hardware "("Object Detection -- Camera")"
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
        read -p "Press any key to return to main menu......"
        main_menu
    fi

    case $dev_option in
        0) 
            main_menu;;
        $intel_opt) 
            if [ -f "$PWD/env/obj_ov/bin/activate" ];then
                source env/obj_ov/bin/activate
                echo Start Object Detect......
                cd $PWD/../obj-detect
                python3 demo.py 0
                cd $ori_dir
            else
                echo This demo environment not install! Please rechoose!
                read -p "Press any key to continue..."
                clear
                objc_menu
            fi
            ;;
        $nvidia_opt)
            if [ -f "$PWD/env/obj_cuda/bin/activate" ];then
                source env/obj_cuda/bin/activate
                echo Start Object Detect......
                mkdir $PWD/up-ai/obj-cuda
                cd $PWD/../obj-cuda
                yolo predict model=yolo11n.pt source=0 show=True save=False device=0
                cd $ori_dir
            else
                echo This demo environment not install! Please rechoose!
                read -p "Press any key to continue..."
                clear
                objc_menu
            fi
            main_menu
            ;;
        *)
            echo "Unknown option, please rechoose!"
            read -p "Press any key to continue..."
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
        read -p "Press any key to return to main menu......"
        main_menu
    fi

    case $dev_option in
        0) 
            main_menu;;
        $intel_opt) 
            if [ -f "$PWD/env/chatbot/bin/activate" ]; then
                source env/chatbot/bin/activate
                echo Start Chatbot......
                cd $PWD/../chatbot
                python3 chatbot.py
                cd $ori_dir
                chatbot_menu
            else
                echo This demo environment not install! Please rechoose!
                read -p "Press any key to continue..."
                clear
                chatbot_menu
            fi
            ;;
        *)
            echo "Unknown option, please rechoose!"
            read -p "Press any key to continue..."
            clear
            objc_menu
            ;;
    esac
}

# Start the script by calling the main menu
main_menu
