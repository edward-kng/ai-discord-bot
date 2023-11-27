#!/bin/bash

INSTALL_DIR=/var/lib/ai-discord-bot
NAME=ai-discord-bot
SERVICE=$NAME.service

read -p "Enter Discord bot token: " env

rm -rf $INSTALL_DIR
rm -f /etc/systemd/system/$SERVICE
git clone https://github.com/edward-kng/ai-discord-bot.git $INSTALL_DIR
echo DISCORD_BOT_TOKEN=$env > $INSTALL_DIR/.env
useradd $NAME
chown -R $NAME:$NAME $INSTALL_DIR
chmod +x $INSTALL_DIR/run.sh
ln -s $INSTALL_DIR/systemd/$SERVICE /etc/systemd/system/$SERVICE
su $NAME -c "\
    python3 -m venv $INSTALL_DIR/.venv \
    && source $INSTALL_DIR/.venv/bin/activate \
    && pip3 install -r $INSTALL_DIR/requirements.txt"
systemctl enable --now $SERVICE
