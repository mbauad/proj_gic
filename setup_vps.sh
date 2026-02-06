#!/bin/bash

# Configuration
APP_DIR="/var/www/proj_gic"
USER="root" # Change if deploying as a non-root user, but typically setup needs root

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Starting Deployment Setup...${NC}"

# 1. Update System
echo -e "${GREEN}Updating system...${NC}"
apt-get update && apt-get upgrade -y
apt-get install -y python3-pip python3-venv nginx

# 2. Setup Directory Structure
echo -e "${GREEN}Setting up directories...${NC}"
mkdir -p "$APP_DIR"

# Determine where this script is running from
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
echo "Script located at: $SCRIPT_DIR"

# Copy Application Files
if [ -d "$SCRIPT_DIR/flask_app" ]; then
    echo "Found flask_app in $SCRIPT_DIR, syncing to $APP_DIR..."
    rsync -av --exclude 'venv' --exclude '__pycache__' "$SCRIPT_DIR/" "$APP_DIR/"
else
    echo -e "${GREEN}Error: flask_app directory not found in $SCRIPT_DIR${NC}"
    echo "Files in $SCRIPT_DIR:"
    ls -la "$SCRIPT_DIR"
    exit 1
fi

# 3. Setup Python Virtual Environment
echo -e "${GREEN}Setting up Python Environment...${NC}"
cd "$APP_DIR/flask_app"
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 4. Configure Gunicorn
echo -e "${GREEN}Configuring Gunicorn...${NC}"
cp "$APP_DIR/deployment/gunicorn.service" /etc/systemd/system/gunicorn_gic.service
systemctl daemon-reload
systemctl enable gunicorn_gic
systemctl restart gunicorn_gic

# 5. Configure Nginx
echo -e "${GREEN}Configuring Nginx...${NC}"
cp "$APP_DIR/deployment/nginx.conf" /etc/nginx/sites-available/proj_gic
ln -sf /etc/nginx/sites-available/proj_gic /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 6. Permissions (Optional but good)
chown -R www-data:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"

echo -e "${GREEN}Deployment Complete! App should be running on http://<YOUR_VPS_IP>${NC}"
