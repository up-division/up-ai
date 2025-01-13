#!/bin/bash

echo =================================================
echo         Install OpenVino Chatbot Packages
echo =================================================

if [ -d "$PWD/env/chatbot" ]; then
    echo OpenVino Chatbot is already exist!
    read -p "Do you want to delete and reinstall?(y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        rm -r "$PWD/env/chatbot"
    else
        exit 0
    fi
fi

python3 -m venv $PWD/env/chatbot
source $PWD/env/chatbot/bin/activate
python3 -m pip install --upgrade pip
pip install -r ../chatbot/requirements.txt
echo "Chatbot Environment Installation Completed!"
