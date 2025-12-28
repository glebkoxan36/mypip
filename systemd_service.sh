#!/bin/bash
# Systemd service setup script for Node Manager

SERVICE_NAME="node-manager"
USER_NAME="node-manager"
INSTALL_DIR="/opt/node-manager"
CONFIG_DIR="/etc/node-manager"

echo "🔧 Setting up Node Manager systemd service..."

# Создание пользователя
if ! id "$USER_NAME" &>/dev/null; then
    echo "👤 Creating user: $USER_NAME"
    sudo useradd -r -s /bin/false -m -d "$INSTALL_DIR" "$USER_NAME"
fi

# Создание директорий
echo "📁 Creating directories..."
sudo mkdir -p "$INSTALL_DIR" "$CONFIG_DIR"
sudo chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR" "$CONFIG_DIR"

# Копирование файлов
echo "📦 Copying files..."
sudo cp -r . "$INSTALL_DIR/"
sudo chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"

# Создание конфигурации
if [ ! -f "$CONFIG_DIR/.env" ]; then
    echo "⚙️ Creating configuration..."
    sudo cp .env.example "$CONFIG_DIR/.env"
    echo "📝 Please edit configuration: sudo nano $CONFIG_DIR/.env"
fi

# Создание systemd сервиса
echo "🔧 Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Node Manager - Cryptocurrency Node Manager with Web Panel
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
Environment="PYTHONPATH=$INSTALL_DIR"
EnvironmentFile=$CONFIG_DIR/.env
ExecStart=$INSTALL_DIR/venv/bin/node-manager-web \\
  --host \${WEB_HOST:-0.0.0.0} \\
  --port \${WEB_PORT:-8080} \\
  --username \${NODE_MANAGER_ADMIN_USERNAME:-admin} \\
  --password \${NODE_MANAGER_ADMIN_PASSWORD}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR/data $INSTALL_DIR/logs $CONFIG_DIR

[Install]
WantedBy=multi-user.target
EOF

# Создание виртуального окружения
echo "🐍 Creating Python virtual environment..."
cd "$INSTALL_DIR"
sudo -u "$USER_NAME" python3 -m venv venv
sudo -u "$USER_NAME" "$INSTALL_DIR/venv/bin/pip" install -e .

# Включение и запуск сервиса
echo "🚀 Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "✅ Node Manager service installed!"
echo ""
echo "📋 Commands:"
echo "  sudo systemctl status $SERVICE_NAME  # Check status"
echo "  sudo journalctl -u $SERVICE_NAME -f  # View logs"
echo "  sudo systemctl restart $SERVICE_NAME # Restart service"
echo "  sudo systemctl stop $SERVICE_NAME    # Stop service"
echo ""
echo "🌐 Web interface: http://$(hostname -I | awk '{print $1}'):8080"
echo "🔧 Configuration: $CONFIG_DIR/.env"
