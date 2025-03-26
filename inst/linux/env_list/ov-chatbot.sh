#!/bin/bash

echo =================================================
echo         Install OpenVino Chatbot Packages
echo =================================================

if [ -d "$PWD/inst/linux/env/chatbot" ]; then
    echo OpenVino Chatbot is already exist!
    read -p "Do you want to delete and reinstall?(y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        rm -r "$PWD/inst/linux/env/chatbot"
    else
        exit 0
    fi
fi

python3 -m venv $PWD/inst/linux/env/chatbot
source $PWD/inst/linux/env/chatbot/bin/activate
python3 -m pip install --upgrade pip
pip install -r demos/chatbot/requirements.txt
if [ -f "demos/chatbot/tiny-llama-1b-chat" ]; then
    :
else
    wget -O chat.zip "https://aaeon365-my.sharepoint.com/:u:/g/personal/junyinglai_aaeon_com_tw/ERzwCuBCBbZNh0-08aTXsj4BpZyy0o0X2NoZBUbrxGtbCQ?e=8ANs3B&download=1"
    unzip chat.zip -d demos/chatbot/tiny-llama-1b-chat
    rm -rf chat.zip
fi
echo "Chatbot Environment Installation Completed!"
