# MiningTaxes Installation Scripts

Installation scripts for the MiningTaxes plugin with Discord DM and Corp Summary integration.

## Features

This fork adds Discord integration to the original MiningTaxes plugin:
- **Individual Discord DMs** - Private tax notifications sent directly to users
- **Corp Tax Summaries** - Formatted reports showing all outstanding taxes
- **Channel Webhooks** - Public notifications to Discord channels

## Quick Install

```bash
# Download and run the installer
wget https://raw.githubusercontent.com/Thrainkrilleve/miningtaxes-install-scripts/main/install.sh
source /home/allianceauth/venv/bin/activate
bash install.sh
```

The script will:
1. Clone the plugin repository to `~/aa-miningtaxes-discord`
2. Install the plugin and dependencies
3. Backup your settings
4. Guide you through configuration
5. Run migrations and collect static files
6. Preload ore prices

## Updating

```bash
# Download and run the updater
wget https://raw.githubusercontent.com/Thrainkrilleve/miningtaxes-install-scripts/main/update.sh
source /home/allianceauth/venv/bin/activate
bash update.sh
```

## Manual Installation

If you prefer manual installation:

```bash
# Clone the repository
git clone https://github.com/Thrainkrilleve/miningtaxdiscordupdate.git ~/aa-miningtaxes-discord
cd ~/aa-miningtaxes-discord

# Activate venv and install
source /home/allianceauth/venv/bin/activate
pip install -e ~/aa-miningtaxes-discord

# Add to settings
nano ~/myauth/myauth/settings/local.py
```

Add to your `local.py`:
```python
INSTALLED_APPS += [
    'miningtaxes',
    'django_celery_results',
]

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'

# Scheduled tasks
from celery.schedules import crontab

CELERYBEAT_SCHEDULE['miningtaxes_update_daily'] = {
    'task': 'miningtaxes.tasks.update_daily',
    'schedule': crontab(minute=0, hour='1'),
}

CELERYBEAT_SCHEDULE['miningtaxes_notifications'] = {
    'task': 'miningtaxes.tasks.notify_taxes_due',
    'schedule': crontab(0, 0, day_of_month='2'),
}

CELERYBEAT_SCHEDULE['miningtaxes_apply_interest'] = {
    'task': 'miningtaxes.tasks.apply_interest',
    'schedule': crontab(0, 0, day_of_month='15'),
}
```

Then run:
```bash
cd ~/myauth
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py miningtaxes_preload_prices

# Restart services
sudo systemctl restart myauth-gunicorn myauth-worker myauth-beat
```

## Discord Setup

### Basic Webhooks (Public Notifications)

1. In Discord, go to Channel Settings → Integrations → Webhooks
2. Create a webhook and copy the URL
3. In Alliance Auth admin, go to MiningTaxes → Settings
4. Paste webhook URL in "Discord Webhook URL"
5. Enable desired notification types

### Discord DMs (Private Notifications)

Requires [aa-discordbot](https://github.com/pvyParts/allianceauth-discordbot):

```bash
pip install aa-discordbot
```

Add to settings:
```python
INSTALLED_APPS += [
    'aadiscordbot',
    'allianceauth.services.modules.discord',
]
```

Then in MiningTaxes admin:
- Enable "Send individual DMs to Discord users"
- Users must link Discord accounts via Alliance Auth Services

### Corp Summaries

Two options:

**Option A: Channel ID (Recommended)**
- Get channel ID from Discord (enable Developer Mode, right-click channel, Copy ID)
- Enter in "Discord Corp Summary Channel ID" field

**Option B: Webhook**
- Create webhook in leadership channel
- Enter in "Discord Corp Summary Webhook URL" field

## Documentation

Full documentation available in the repository:
- [Discord Integration Guide](https://github.com/Thrainkrilleve/miningtaxdiscordupdate/blob/main/DISCORD_INTEGRATION.md)
- [Discord DM Setup Guide](https://github.com/Thrainkrilleve/miningtaxdiscordupdate/blob/main/DISCORD_DM_GUIDE.md)
- [Quick Start Guide](https://github.com/Thrainkrilleve/miningtaxdiscordupdate/blob/main/DISCORD_QUICKSTART.md)
- [Main README](https://github.com/Thrainkrilleve/miningtaxdiscordupdate/blob/main/README.md)

## Source Repository

Plugin source code: https://github.com/Thrainkrilleve/miningtaxdiscordupdate

## Support

- GitHub Issues: https://github.com/Thrainkrilleve/miningtaxdiscordupdate/issues
- Alliance Auth Discord: https://discord.gg/4SEyDZKB

## Credits

Based on the original [aa-miningtaxes](https://gitlab.com/arctiru/aa-miningtaxes) plugin.
