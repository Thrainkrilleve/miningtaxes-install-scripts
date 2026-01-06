# MiningTaxes Discord Integration

**What it does:** Makes MiningTaxes send Discord messages to your players!

## 📁 What You Get

One file called `discord_integration.py` that can:
- 💬 Send private messages to players
- 📢 Post announcements in channels  
- 📊 Show who owes taxes in a nice table

## ⚙️ What You Need First

**Step 1:** Install aa-discordbot
```bash
pip install aa-discordbot
```

**Step 2:** Make sure your Alliance Auth has Discord turned on

That's it! 

## 🚀 How to Use It

### Super Simple Way

1. **Download the file**
   - Grab `discord_integration.py` from this folder

2. **Put it in your MiningTaxes folder**
   - Drop it where your other MiningTaxes files are

3. **Tell MiningTaxes to use it**
   - Add this to the top of your tasks.py file:
   ```python
   from .discord_integration import send_discord_dm, get_user_discord_id
   ```

4. **Done!** Now you can send Discord messages!

## 🎯 Functions

### 1. `send_discord_notification(webhook_url, title, message, color, username)`
Sends public notifications to Discord channels via webhook.
What Each Thing Does

### 1. Send Channel Messages
`send_discord_notification()` - Posts to a Discord channel everyone can see

**Example:** "Taxes are due on the 15th!"

### 2. Send Private Messages  
`send_discord_dm()` - Sends a secret message to one person

**Example:** "Hey John, you owe 500,000 ISK"

### 3. Find Someone's Discord
`get_user_discord_id()` - Looks up a player's Discord username

**Example:** Finds that "john_doe" is Discord user #12345

### 4. Make a Tax Report
`send_corp_tax_summary()` - Creates a pretty table showing who owes what

**Example:** Shows top 25 people who owe taxes with a leaderboard
```python
from discord_integration import send_discord_dm, get_user_discord_id
from django.contrib.auth.models import User

user = User.objects.get(username='john_doe')
discord_id = get_user_discord_id(user)
Copy & Paste Examples

### Example 1: Send Someone a Private Message
```python
# Get their Discord ID
discord_id = get_user_discord_id(user)

# Send them a message
send_discord_dm(
    discord_id,
    "Taxes Due!",
    "Please pay 1,234,567 ISK",
    color=0xf39c12  # Makes it orange
)
```

### Example 2: Post a Tax Report  
```python
# Make a list of who owes what
tax_data = [
    {
        'username': 'john_doe',
        'main_character': 'John Doe',
        'balance': 125.5  # in millions
    }
]

# Send it to Discord
send_corp_tax_summary(None, tax_data, channel_id=YOUR_CHANNEL_ID)
```

### Example 3: Full Setup in MiningTaxes
```python
# In your tasks.py file, add this:

@shared_task
def notify_taxes_due():
    # Load the Discord tools
    from .discord_integration import send_discord_dm, get_user_discord_id
    
    # For each person who owes taxes...
    for user in users_who_owe_money:
        discord_id = get_user_discord_id(user)
        
        if discord_id:
            send_discord_dm(
                discord_id,
                "Taxes Due!",
                f"You owe {amount} ISK",
                color=0xf39c12
            
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
   🔧 Settings You Need to Add

If you want buttons in your admin panel, add these to your Settings model:

```python
discord_send_individual_dms = True/False  # Turn DMs on or off
discord_corp_channel_id = 123456789       # Your Discord channel number
discord_send_corp_summary = True/False    # Turn reports on or off
```

## ✅ How to Test If It's Working

### Test 1: Is aa-discordbot installed?
```python
try:
    from aadiscordbot.tasks import send_message
    print("✅ Yes it's installed!")
except:
    print("❌ Nope, you need to install it")
```

### Test 2: Can you find Discord users?
```python
from discord_integration import get_user_discord_id

discord_id = get_user_discord_id(some_user)

if discord_id:
    print(f"✅ Found them! Their ID is {discord_id}")
else:
    print("❌ They haven't linked their Discord yet")
```

## ❓ Common Questions

**Q: Do players need to do anything?**  
A: Yes! They need to link their Discord account in Alliance Auth first.

**Q: What if someone doesn't have Discord linked?**  
A: The code skips them automatically - no error!

**Q: Can I change the message colors?**  
A: Yes! Use these color codes:
- `0xe74c3c` = Red
- `0xf39c12` = Orange  
- `0x2ecc71` = Green
- `0x3498db` = Blue

**Q: Where do I get a channel ID?**  
A: In Discord, right-click a channel → Copy ID (you need Developer Mode on)

## 📝 That's It!

Copy the file, drop it in, use the examples above. Done! 🎉