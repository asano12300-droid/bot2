#!/bin/bash

user=$(whoami)
cp -r /home/$user/bot2/commands/ /home/$user/
sudo chmod +x /home/$user/commands/cmd

echo "user=$(whoami)" >> /home/$user/.bashrc
echo "export PATH:$PAHT:/home/$user/" >> /home/$user/.bashrc
source /home/$user/.bashrc
