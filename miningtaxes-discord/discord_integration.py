"""
MiningTaxes Discord Integration Module
Adds Discord DM and Corp Summary functionality to MiningTaxes plugin

This module provides three types of Discord notifications:
1. Channel Webhooks - Public notifications via Discord webhooks
2. Individual DMs - Private messages to users via aadiscordbot
3. Corp Summaries - Formatted reports of all outstanding taxes

Requirements:
- allianceauth.services.modules.discord (for user Discord ID lookup)
- aadiscordbot (for DM and channel posting features)

Usage:
    from discord_integration import (
        send_discord_notification,
        send_discord_dm,
        send_corp_tax_summary,
        get_user_discord_id
    )
"""

import datetime as dt
import json
import requests
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

logger = LoggerAddTag(get_extension_logger(__name__), "MiningTaxes-Discord")


def send_discord_notification(webhook_url, title, message, color=0x3498db, username="MiningTaxes Bot"):
    """
    Send a notification to Discord via webhook.
    
    Args:
        webhook_url (str): Discord webhook URL
        title (str): Embed title
        message (str): Embed description/message
        color (int): Embed color in hex (default: blue 0x3498db)
        username (str): Bot username to display
    
    Returns:
        bool: True if successful, False otherwise
    
    Example:
        send_discord_notification(
            "https://discord.com/api/webhooks/...",
            "Taxes Due",
            "Please pay 1,234,567.89 ISK",
            color=0xf39c12  # Orange
        )
    """
    if not webhook_url:
        return False
    
    try:
        payload = {
            "username": username,
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": color,
                    "footer": {
                        "text": "MiningTaxes Notification System"
                    }
                }
            ]
        }
        
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            logger.debug(f"Successfully sent Discord notification: {title}")
            return True
        else:
            logger.warning(f"Failed to send Discord notification. Status: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending Discord notification: {e}")
        return False


def send_discord_dm(user_discord_id, title, message, color=0x3498db):
    """
    Send a private DM to a Discord user via aadiscordbot.
    
    Args:
        user_discord_id (str or int): Discord user ID
        title (str): Embed title
        message (str): Embed description/message
        color (int): Embed color in hex (default: blue 0x3498db)
    
    Returns:
        bool: True if successfully queued, False otherwise
    
    Example:
        discord_id = get_user_discord_id(user)
        if discord_id:
            send_discord_dm(
                discord_id,
                "Taxes Due!",
                "Please pay 1,234,567.89 ISK or you will be charged interest!",
                color=0xf39c12
            )
    
    Note:
        Requires aadiscordbot to be installed and configured.
        Falls back gracefully if aadiscordbot is not available.
    """
    if not user_discord_id:
        return False
    
    try:
        # Try to use aadiscordbot if available
        try:
            from discord import Embed
            from aadiscordbot.tasks import send_message
            
            # Create embed using discord.py Embed
            embed = Embed(
                title=title,
                description=message,
                color=color
            )
            embed.set_footer(text="MiningTaxes - Private Notification")
            
            # Queue the message via aadiscordbot
            send_message(
                message="",
                user_id=int(user_discord_id),
                embed=embed
            )
            
            logger.debug(f"Successfully queued DM to Discord user {user_discord_id}")
            return True
            
        except ImportError:
            logger.warning("aadiscordbot not available. Install it to enable Discord DMs.")
            logger.warning("pip install aa-discordbot")
            return False
            
    except Exception as e:
        logger.error(f"Error sending Discord DM: {e}")
        return False


def get_user_discord_id(user):
    """
    Get a user's Discord ID from Alliance Auth Discord service.
    
    Args:
        user: Django User object
    
    Returns:
        str: Discord user ID or None if not found
    
    Example:
        from django.contrib.auth.models import User
        user = User.objects.get(username='john_doe')
        discord_id = get_user_discord_id(user)
        if discord_id:
            send_discord_dm(discord_id, "Title", "Message")
    
    Note:
        Requires users to have linked their Discord account via
        Alliance Auth's Discord service.
    """
    try:
        # Try to import AA Discord service
        from allianceauth.services.modules.discord.models import DiscordUser
        
        try:
            discord_user = DiscordUser.objects.get(user=user)
            return discord_user.uid
        except DiscordUser.DoesNotExist:
            logger.debug(f"No Discord account linked for user {user.username}")
            return None
            
    except ImportError:
        logger.warning("Alliance Auth Discord service not installed or configured")
        return None
    except Exception as e:
        logger.error(f"Error getting Discord ID for user {user.username}: {e}")
        return None


def send_corp_tax_summary(webhook_url, tax_data, channel_id=None):
    """
    Send a formatted summary of all outstanding taxes to a corp channel.
    
    Args:
        webhook_url (str): Discord webhook URL (used if channel_id not provided)
        tax_data (list): List of dicts with keys:
            - username (str): User's username
            - main_character (str): Main character name
            - balance (float): Outstanding balance in millions
            - characters (list, optional): List of character names
        channel_id (int, optional): Discord channel ID to send via aadiscordbot
    
    Returns:
        bool: True if successful, False otherwise
    
    Example:
        tax_data = [
            {
                'username': 'john_doe',
                'main_character': 'John Doe',
                'balance': 125.5  # In millions
            },
            {
                'username': 'jane_smith',
                'main_character': 'Jane Smith',
                'balance': 89.23
            }
        ]
        
        # Option 1: Post to channel via aadiscordbot (recommended)
        send_corp_tax_summary(None, tax_data, channel_id=1234567890)
        
        # Option 2: Post via webhook
        send_corp_tax_summary("https://discord.com/api/webhooks/...", tax_data)
    
    Note:
        Priority: channel_id > webhook_url
        If channel_id is provided but aadiscordbot isn't available, falls back to webhook.
    """
    if (not webhook_url and not channel_id) or not tax_data:
        return False
    
    try:
        # Filter users with outstanding balance
        outstanding = [d for d in tax_data if d.get('balance', 0) > 0]
        
        if not outstanding:
            return True  # Nothing to report
        
        # Sort by balance descending
        outstanding.sort(key=lambda x: x.get('balance', 0), reverse=True)
        
        # Calculate totals
        total_outstanding = sum(d.get('balance', 0) for d in outstanding)
        total_users = len(outstanding)
        
        # Build table header
        description = "```\n"
        description += f"{'User':<20} {'Main Character':<25} {'Balance':>15}\n"
        description += "=" * 60 + "\n"
        
        # Add each user (limit to top 25 to avoid message size limits)
        for data in outstanding[:25]:
            username = data.get('username', 'Unknown')[:19]
            main_char = data.get('main_character', 'N/A')[:24]
            balance = data.get('balance', 0)
            
            description += f"{username:<20} {main_char:<25} {balance:>13,.2f}M\n"
        
        if len(outstanding) > 25:
            description += f"\n... and {len(outstanding) - 25} more users\n"
        
        description += "=" * 60 + "\n"
        description += f"{'TOTAL':<45} {total_outstanding:>13,.2f}M\n"
        description += "```"
        
        # Create embed fields for additional info
        fields = [
            {
                "name": "📊 Summary",
                "value": f"**{total_users}** users owe taxes\n**{total_outstanding:,.2f} M ISK** total outstanding",
                "inline": False
            }
        ]
        
        # Add top 3 debtors as a separate field
        if len(outstanding) >= 3:
            top_3 = "\n".join([
                f"{i+1}. **{d.get('username', 'Unknown')}** - {d.get('balance', 0):,.2f}M ISK"
                for i, d in enumerate(outstanding[:3])
            ])
            fields.append({
                "name": "🔥 Top Debtors",
                "value": top_3,
                "inline": False
            })
        
        # Try aadiscordbot first if channel_id provided
        if channel_id:
            try:
                from discord import Embed
                from aadiscordbot.tasks import send_message
                
                embed = Embed(
                    title="⚠️ Outstanding Mining Taxes Report",
                    description=description,
                    color=0xe74c3c  # Red
                )
                
                for field in fields:
                    embed.add_field(
                        name=field["name"],
                        value=field["value"],
                        inline=field.get("inline", False)
                    )
                
                embed.set_footer(text=f"MiningTaxes Corp Summary • {total_users} users with outstanding taxes")
                embed.timestamp = dt.datetime.utcnow()
                
                send_message(
                    message="",
                    channel_id=int(channel_id),
                    embed=embed
                )
                
                logger.info(f"Successfully queued corp tax summary via aadiscordbot: {total_users} users, {total_outstanding:,.2f}M ISK")
                return True
                
            except ImportError:
                logger.debug("aadiscordbot not available, falling back to webhook")
                if not webhook_url:
                    logger.error("No webhook URL provided for fallback")
                    return False
        
        # Fallback to webhook
        if webhook_url:
            payload = {
                "username": "MiningTaxes Corp Summary",
                "embeds": [
                    {
                        "title": "⚠️ Outstanding Mining Taxes Report",
                        "description": description,
                        "color": 0xe74c3c,  # Red
                        "fields": fields,
                        "footer": {
                            "text": f"MiningTaxes Corp Summary • {total_users} users with outstanding taxes"
                        },
                        "timestamp": dt.datetime.utcnow().isoformat()
                    }
                ]
            }
            
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"Successfully sent corp tax summary: {total_users} users, {total_outstanding:,.2f}M ISK")
                return True
            else:
                logger.warning(f"Failed to send corp tax summary. Status: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Error sending corp tax summary: {e}")
        return False
