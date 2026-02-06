#!/bin/bash

# Usage: ./deploy_to_vps.sh user@ip_address

TARGET=$1

if [ -z "$TARGET" ]; then
    echo "Usage: ./deploy_to_vps.sh user@vps_ip_address"
    exit 1
fi

echo "Deploying to $TARGET..."

# 1. Zip the project (excluding venv and other garbage)
echo "zipping files..."
# Go up one level to zip the 'proj_gic' folder structure or zip content relative to current dir
# We are in proj_gic? Let's check.
# The user's metadata says /home/marcelo-auad/Antigravit/Controle de tarefas Diarias/proj_gic/
# So we are at the root of the project ideally.
cd "/home/marcelo-auad/Antigravit/Controle de tarefas Diarias/proj_gic"

tar -czf deployment_package.tar.gz \
    --exclude='flask_app/venv' \
    --exclude='flask_app/__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='.env' \
    .

# 2. Copy package and setup script to VPS
echo "Transferring files..."
scp deployment_package.tar.gz "$TARGET:/tmp/"

# 3. Execute setup on VPS
echo "Running setup on remote server..."
ssh "$TARGET" 'bash -s' << 'ENDSSH'
    # Commands to run on the VPS
    
    # Create temp dir
    mkdir -p /tmp/gic_deploy
    tar -xzf /tmp/deployment_package.tar.gz -C /tmp/gic_deploy
    
    # Run the setup script (Assuming it needs root, we might need sudo here if the user is not root)
    # Trying to prompt for sudo if not root
    if [ "$EUID" -ne 0 ]; then 
        echo "Elevation to root required for installation steps..."
        sudo bash /tmp/gic_deploy/setup_vps.sh
    else
        bash /tmp/gic_deploy/setup_vps.sh
    fi
    
    # Cleanup
    rm -rf /tmp/gic_deploy
    rm /tmp/deployment_package.tar.gz
ENDSSH

echo "Done!"
