#!/bin/bash

INSTALL_DIR=/var/lib/ai-discord-bot
NAME=ai-discord-bot
SERVICE=$NAME.service

systemctl disable --now $SERVICE
rm -rf $INSTALL_DIR
rm -f /etc/systemd/system/$SERVICE
userdel $NAME
