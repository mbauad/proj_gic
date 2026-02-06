#!/bin/bash

# Configuration
APP_DIR="/var/www/proj_gic"

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Reconfiguring Nginx...${NC}"

# Re-copy Nginx config
cp "$APP_DIR/deployment/nginx.conf" /etc/nginx/sites-available/proj_gic
ln -sf /etc/nginx/sites-available/proj_gic /etc/nginx/sites-enabled/

# Disable default if it exists (Easypanel might use its own structure though)
rm -f /etc/nginx/sites-enabled/default

# Reload
nginx -t && systemctl restart nginx

echo -e "${GREEN}Configuration updated.${NC}"
