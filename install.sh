#!/bin/bash

user=`whoami`

for i in {1..2}
do
[Unit]
Description=Discord Bot Service
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/$user/discord
ExecStart=/home/$user/discord/sh/bot$i.sh

Restart=always
RestartSec=5

User=$user

Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
done
