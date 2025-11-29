#!/bin/bash
# Deployment script for MC RCON Manager
# Copyright © 2025 MoYuK1ng

echo "🚀 Starting deployment..."

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Compile translation files
echo "🌐 Compiling translation files..."
python manage.py compilemessages

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Restart service
echo "🔄 Restarting service..."
sudo systemctl restart mc_rcon

# Check status
echo "✅ Checking service status..."
sudo systemctl status mc_rcon --no-pager

echo "🎉 Deployment complete!"
