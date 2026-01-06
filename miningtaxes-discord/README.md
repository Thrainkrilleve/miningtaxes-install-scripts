# MiningTaxes Discord Integration

Discord integration components for the MiningTaxes Alliance Auth plugin.

## 📁 What's Included

- **discord_integration.py** - Standalone Python module with all Discord functions
- Complete integration with aa-discordbot and Alliance Auth Discord service
- Three types of notifications: Webhooks, Individual DMs, Corp Summaries

## 🔧 Requirements

### Core Dependencies
```bash
pip install aa-discordbot
```

### Required Alliance Auth Services
- `allianceauth.services.modules.discord` - For Discord user ID lookup
- `aa-discordbot` - For DM delivery and channel posting

## 📦 Installation

### Option 1: Copy into existing MiningTaxes installation

1. Copy `discord_integration.py` to your MiningTaxes plugin directory:
```bash
cp miningtaxes-discord/discord_integration.py /path/to/miningtaxes/
```

2. Import the functions in your tasks or helpers:
```python
from .discord_integration import (
    send_discord_notification,
    send_discord_dm,
    get_user_discord_id,
    send_corp_tax_summary
)
```

### Option 2: Use as reference module

Use this file as documentation to see exactly what functions to add to your MiningTaxes plugin.

## 🎯 Functions

### 1. `send_discord_notification(webhook_url, title, message, color, username)`
Sends public notifications to Discord channels via webhook.

**Use case**: General announcements, tax reminders
**Dependencies**: `requests` (standard)

### 2. `send_discord_dm(user_discord_id, title, message, color)`
Sends private DMs to individual users.

**Use case**: Personal tax notifications
**Dependencies**: 
- `aadiscordbot.tasks.send_message`
- `discord.Embed`

### 3. `get_user_discord_id(user)`
Retrieves Discord user ID from Alliance Auth.

**Use case**: Getting user's Discord ID for DMs
**Dependencies**:
- `allianceauth.services.modules.discord.models.DiscordUser`

### 4. `send_corp_tax_summary(webhook_url, tax_data, channel_id)`
Sends formatted tax reports to corp channel.

**Use case**: Corp-wide tax summaries
**Dependencies**:
- Primary: `aadiscordbot.tasks.send_message` + `discord.Embed`
- Fallback: `requests` (webhook)

## 💡 Usage Examples

### Send a DM
```python
from discord_integration import send_discord_dm, get_user_discord_id
from django.contrib.auth.models import User

user = User.objects.get(username='john_doe')
discord_id = get_user_discord_id(user)

if discord_id:
    send_discord_dm(
        discord_id,
        "Taxes Due!",
        "Please pay 1,234,567.89 ISK",
        color=0xf39c12  # Orange
    )
```

### Send Corp Summary
```python
from discord_integration import send_corp_tax_summary

tax_data = [
    {
        'username': 'user1',
        'main_character': 'Character Name 1',
        'balance': 125.5  # millions ISK
    },
    {
        'username': 'user2',
        'main_character': 'Character Name 2',
        'balance': 89.23
    }
]

# Option 1: Via aadiscordbot (recommended)
send_corp_tax_summary(None, tax_data, channel_id=YOUR_CHANNEL_ID)

# Option 2: Via webhook
send_corp_tax_summary("https://discord.com/api/webhooks/...", tax_data)
```

### Integration in MiningTaxes Tasks
```python
@shared_task
def notify_taxes_due():
    from .discord_integration import (
        send_discord_dm, 
        get_user_discord_id, 
        send_corp_tax_summary
    )
    from .models import Settings
    
    settings = Settings.load()
    user2taxes = calculate_taxes()  # Your tax calculation function
    
    corp_summary_data = []
    
    # Send individual DMs
    for user, (balance, details) in user2taxes.items():
        if balance > THRESHOLD and settings.discord_send_individual_dms:
            discord_id = get_user_discord_id(user)
            if discord_id:
                send_discord_dm(
                    discord_id,
                    "Mining Taxes Due!",
                    f"Please pay {balance:,.2f} ISK",
                    color=0xf39c12
                )
            
            # Collect data for corp summary
            corp_summary_data.append({
                'username': user.username,
                'main_character': user.profile.main_character.character_name,
                'balance': balance / 1000000  # Convert to millions
            })
    
    # Send corp summary
    if corp_summary_data and settings.discord_send_corp_summary:
        channel_id = settings.discord_corp_channel_id or None
        webhook = settings.discord_corp_webhook_url or settings.discord_webhook_url
        send_corp_tax_summary(webhook, corp_summary_data, channel_id=channel_id)
```

## ⚙️ Configuration

### Required Settings Model Fields

Add these to your Settings model:

```python
# In models/settings.py
class Settings(models.Model):
    discord_webhook_url = models.CharField(
        max_length=500,
        default="",
        blank=True,
        help_text="Discord webhook URL for notifications"
    )
    
    discord_send_individual_dms = models.BooleanField(
        default=False,
        help_text="Send private DMs to users"
    )
    
    discord_corp_webhook_url = models.CharField(
        max_length=500,
        default="",
        blank=True,
        help_text="Webhook for corp summaries"
    )
    
    discord_corp_channel_id = models.BigIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Channel ID for corp summaries (via aadiscordbot)"
    )
    
    discord_send_corp_summary = models.BooleanField(
        default=True,
        help_text="Send corp tax summaries"
    )
```

## 🔍 Verification

### Check aa-discordbot is installed
```python
try:
    from aadiscordbot.tasks import send_message
    print("✅ aa-discordbot available")
except ImportError:
    print("❌ aa-discordbot not installed")
```

### Check Alliance Auth Discord service
```python
try:
    from allianceauth.services.modules.discord.models import DiscordUser
    print("✅ AA Discord service available")
except ImportError:
    print("❌ AA Discord service not configured")
```

### Test user has Discord linked
```python
from django.contrib.auth.models import User
from discord_integration import get_user_discord_id

user = User.objects.get(username='test_user')
discord_id = get_user_discord_id(user)

if discord_id:
    print(f"✅ User Discord ID: {discord_id}")
else:
    print("❌ User has no Discord account linked")
```

## 📚 Documentation

For complete documentation on how this integrates with MiningTaxes:
- See the full plugin repository for implementation examples
- Check DISCORD_INTEGRATION.md and DISCORD_DM_GUIDE.md in the main repo

## 🔗 Dependencies Summary

| Function | aa-discordbot | AA Discord | requests |
|----------|---------------|------------|----------|
| send_discord_notification | ❌ | ❌ | ✅ |
| send_discord_dm | ✅ Required | ❌ | ❌ |
| get_user_discord_id | ❌ | ✅ Required | ❌ |
| send_corp_tax_summary | ✅ Recommended | ❌ | ✅ Fallback |

## 📝 License

See LICENSE file in repository root.
