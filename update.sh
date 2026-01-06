#!/bin/bash

# MiningTaxes Update Script
# Updates the MiningTaxes plugin to the latest version

set -e

echo "========================================"
echo "MiningTaxes Plugin Update"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please do not run as root. Run as your allianceauth user."
   exit 1
fi

# Detect Alliance Auth installation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Virtual environment not activated!"
    echo "Please activate your Alliance Auth virtual environment first:"
    echo "  source /home/allianceauth/venv/bin/activate"
    exit 1
fi

echo "Virtual environment detected: $VIRTUAL_ENV"
echo ""

# Update repository
INSTALL_DIR="$HOME/aa-miningtaxes-discord"
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Error: Installation directory not found at $INSTALL_DIR"
    echo "Please run install.sh first"
    exit 1
fi

echo "Pulling latest changes..."
cd "$INSTALL_DIR"
git pull
echo "✓ Repository updated"
echo ""

# Update plugin
echo "Installing/updating MiningTaxes plugin..."
pip install -e "$INSTALL_DIR" --upgrade
echo "✓ Plugin updated"
echo ""

# Detect Alliance Auth path
if [ -n "$AA_PATH" ]; then
    AUTH_PATH="$AA_PATH"
elif [ -d "$HOME/myauth" ]; then
    AUTH_PATH="$HOME/myauth"
else
    echo "Warning: Could not auto-detect Alliance Auth path."
    echo "Set AA_PATH environment variable or ensure it's at ~/myauth"
    AUTH_PATH="$HOME/myauth"
fi

# Run migrations
echo "Running migrations..."
cd "$AUTH_PATH"
python manage.py migrate
echo "✓ Migrations complete"
echo ""

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"
echo ""

# Restart services
echo "========================================"
echo "RESTART SERVICES"
echo "========================================"
echo ""
echo "Restart your Alliance Auth services:"
echo ""
echo "sudo systemctl restart myauth-gunicorn"
echo "sudo systemctl restart myauth-worker"
echo "sudo systemctl restart myauth-beat"
echo ""
echo "Or if using supervisor:"
echo ""
echo "sudo supervisorctl restart myauth:"
echo ""

echo "========================================"
echo "Update Complete!"
echo "========================================"
