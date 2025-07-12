# VPSデプロイ手順

## 1. 環境変数の設定

VPSで以下の環境変数を設定してください：

```bash
# .envファイルを作成
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=production
FLASK_DEBUG=False
EOF
```

または、システム環境変数として設定：

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export FLASK_SECRET_KEY="your_secret_key_here"
export FLASK_ENV="production"
export FLASK_DEBUG="False"
```

## 2. 依存関係のインストール

```bash
pip install -r requirement.txt
```

## 3. アプリケーションの起動

### 開発環境
```bash
python app.py
```

### 本番環境（推奨）
```bash
gunicorn -c gunicorn.conf.py app:app
```

## 4. systemdサービスファイル（オプション）

`/etc/systemd/system/history-game.service`を作成：

```ini
[Unit]
Description=History Game Flask App
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/history_game
Environment="PATH=/path/to/venv/bin"
Environment="OPENAI_API_KEY=your_api_key"
Environment="FLASK_SECRET_KEY=your_secret_key"
Environment="FLASK_ENV=production"
Environment="FLASK_DEBUG=False"
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

サービスを有効化：
```bash
sudo systemctl enable history-game
sudo systemctl start history-game
sudo systemctl status history-game
```

## 5. Nginx設定（オプション）

`/etc/nginx/sites-available/history-game`を作成：

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

有効化：
```bash
sudo ln -s /etc/nginx/sites-available/history-game /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## トラブルシューティング

### エラーログの確認
```bash
# systemdログ
sudo journalctl -u history-game -f

# gunicornログ
tail -f /var/log/gunicorn/error.log
```

### 環境変数の確認
```bash
echo $OPENAI_API_KEY
echo $FLASK_SECRET_KEY
```

### ポートの確認
```bash
netstat -tlnp | grep :5000
``` 