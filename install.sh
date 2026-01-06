#!/bin/bash

# MiningTaxes Installation Script with Discord Integration
# This script installs and configures the MiningTaxes plugin for Alliance Auth

set -e

echo "========================================"
echo "MiningTaxes Plugin Installation"
echo "with Discord DM & Corp Summary Support"
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

# Clone or update repository
INSTALL_DIR="$HOME/aa-miningtaxes-discord"
if [ -d "$INSTALL_DIR" ]; then
    echo "Updating existing installation at $INSTALL_DIR..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "Cloning MiningTaxes with Discord integration..."
    git clone https://github.com/Thrainkrilleve/miningtaxdiscordupdate.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi
echo "✓ Repository ready at $INSTALL_DIR"
echo ""

# Install plugin from repository
echo "Installing MiningTaxes plugin..."
pip install -e "$INSTALL_DIR"
echo "✓ Plugin installed"
echo ""

# Install required dependencies
echo "Installing dependencies..."
pip install django-celery-results
echo "✓ Dependencies installed"
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

# Backup settings
echo "Backing up local settings..."
SETTINGS_FILE="$AUTH_PATH/myauth/settings/local.py"
if [ -f "$SETTINGS_FILE" ]; then
    cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✓ Backup created at $SETTINGS_FILE.backup.*"
else
    echo "Warning: Settings file not found at $SETTINGS_FILE"
    echo "You will need to manually add configuration."
fi
echo ""

# Add to installed apps (show instructions)
echo "========================================"
echo "MANUAL CONFIGURATION REQUIRED"
echo "========================================"
echo ""
echo "1. Add to INSTALLED_APPS in your local.py:"
echo ""
echo "INSTALLED_APPS += ["
echo "    'miningtaxes',"
echo "    'django_celery_results',"
echo "]"
echo ""

echo "2. Add Celery configuration:"
echo ""
echo "CELERY_RESULT_BACKEND = 'django-db'"
echo "CELERY_CACHE_BACKEND = 'django-cache'"
echo ""

echo "3. Add scheduled tasks to CELERYBEAT_SCHEDULE:"
echo ""
echo "CELERYBEAT_SCHEDULE['miningtaxes_update_daily'] = {"
echo "    'task': 'miningtaxes.tasks.update_daily',"
echo "    'schedule': crontab(minute=0, hour='1'),"
echo "}"
echo ""
echo "CELERYBEAT_SCHEDULE['miningtaxes_notifications'] = {"
echo "    'task': 'miningtaxes.tasks.notify_taxes_due',"
echo "    'schedule': crontab(0, 0, day_of_month='2'),"
echo "}"
echo ""
echo "CELERYBEAT_SCHEDULE['miningtaxes_apply_interest'] = {"
echo "    'task': 'miningtaxes.tasks.apply_interest',"
echo "    'schedule': crontab(0, 0, day_of_month='15'),"
echo "}"
echo ""

echo "4. (Optional) Configure price source:"
echo ""
echo "# For Fuzzworks (default, no API key needed):"
echo "MININGTAXES_PRICE_METHOD = 'Fuzzwork'"
echo ""
echo "# OR for Janice (requires API key from https://janice.e-351.com/):"
echo "MININGTAXES_PRICE_METHOD = 'Janice'"
echo "MININGTAXES_PRICE_JANICE_API_KEY = 'your_api_key_here'"
echo ""

echo "5. (Optional) Configure Discord notifications:"
echo ""
echo "MININGTAXES_DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/...'"
echo "MININGTAXES_DISCORD_CORP_WEBHOOK_URL = 'https://discord.com/api/webhooks/...'"
echo "MININGTAXES_DISCORD_CORP_CHANNEL_ID = 1234567890"
echo ""

echo "========================================"
echo "Press Enter when you have updated your local.py..."
read -p ""

# Run migrations
echo ""
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

# Preload prices
echo "Preloading ore prices (this may take a minute)..."
python manage.py miningtaxes_preload_prices
echo "✓ Prices preloaded"
echo ""

# Restart services
echo "========================================"
echo "RESTART SERVICES"
echo "========================================"
echo ""
echo "You must restart your Alliance Auth services:"
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
echo "NEXT STEPS"
echo "========================================"
echo ""
echo "1. Restart your Alliance Auth services (see above)"
echo "2. Log in to your Alliance Auth admin panel"
echo "3. Navigate to MiningTaxes → Settings"
echo "4. Configure tax rates and interest rate"
echo "5. Add corp accountant characters in MiningTaxes → Admin Characters"
echo "6. (Optional) Configure Discord settings in admin panel"
echo ""
echo "For Discord DM functionality:"
echo "  - Install: pip install aa-discordbot"
echo "  - See: $INSTALL_DIR/DISCORD_DM_GUIDE.md for setup instructions"
echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Plugin source: $INSTALL_DIR"
echo ""
echo "Documentation:"
echo "  - README: $INSTALL_DIR/README.md"
echo "  - Discord Webhook Setup: $INSTALL_DIR/DISCORD_INTEGRATION.md"
echo "  - Discord DM & Corp Summary: $INSTALL_DIR/DISCORD_DM_GUIDE.md"
echo "  - Quick Discord Setup: $INSTALL_DIR/DISCORD_QUICKSTART.md"
echo ""
