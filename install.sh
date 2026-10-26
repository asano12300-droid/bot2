#!/bin/bash

# 実行ユーザーの取得
user=$(whoami)

# 必要なディレクトリの作成
mkdir -p /home/$user/discord
pip install -r requirements.txt
sudo cp -r plugins/ /home/$user/discord/
sudo cp -r commands/ /home/$user/
sudo echo "export PATH:/home/$user/commands/" >> /home/$user/.bashrc
source ~/.bashrc

# 1から2までループ
for i in 1 2; do
    # botスクリプトの移動（ファイルが存在する場合のみなど、必要に応じて調整）
    if [ -f "bot/bot${i}.py" ]; then
        sudo mv bot/bot${i}.py /home/$user/discord/
    fi

    # systemdサービスファイルを /etc/systemd/system/ に作成
    sudo tee /etc/systemd/system/bot${i}.service > /dev/null << EOF
[Unit]
Description=Discord Bot Service ${i}
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/$user/discord
ExecStart=/home/$user/.local/bin/uv run /home/$user/discord/bot${i}.py
Restart=always
RestartSec=5
User=$user
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
done

# systemdの再読み込みとサービスの有効化・起動
sudo systemctl daemon-reload
sudo systemctl enable bot1.service bot2.service
sudo systemctl start bot1.service bot2.service

echo "インストールとサービスの登録が完了しました！"
