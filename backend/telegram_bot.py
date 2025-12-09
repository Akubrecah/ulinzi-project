"""
Direct Telegram Bot Integration for Ulinzi Alert System
Replaces n8n webhook with direct Telegram API calls
Supports multi-user verification with consensus voting
"""

import asyncio
import ssl
import certifi
import httpx
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from datetime import datetime

# Create SSL context with certifi certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())



async def send_telegram_alert_async(bot_token: str, chat_id: str, message: str, 
                                    region: str = "", threat_level: str = "", 
                                    timestamp: str = "", incident_id: str = ""):
    """
    Send alert message directly to Telegram bot with interactive buttons.
    Uses async to avoid blocking.
    """
    try:
        # Create httpx client with SSL context
        httpx_client = httpx.AsyncClient(verify=ssl_context)
        bot = Bot(token=bot_token, request=httpx_client)
        
        # Format message with Markdown
        formatted_message = f"""
🚨 *ULINZI ALERT SYSTEM* 🚨

*Message:* {message}

📍 *Region:* {region}
⚠️ *Threat Level:* {threat_level}
🕒 *Time:* {timestamp}

_Click a button below to verify:_
"""
        
        # Create interactive buttons
        keyboard = [[
            InlineKeyboardButton("✅ SAFE", callback_data=f"vote_safe_{incident_id}_{chat_id}"),
            InlineKeyboardButton("🚨 THREAT", callback_data=f"vote_threat_{incident_id}_{chat_id}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_message(
            chat_id=chat_id,
            text=formatted_message.strip(),
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        return True, "Telegram alert sent successfully"
        
    except TelegramError as e:
        return False, f"Telegram error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


async def send_telegram_to_multiple_async(bot_token: str, chat_ids: list, message: str,
                                         region: str = "", threat_level: str = "",
                                         timestamp: str = "", incident_id: str = ""):
    """
    Send alert to multiple Telegram users with interactive buttons.
    Returns success count and any errors.
    """
    httpx_client = httpx.AsyncClient(verify=ssl_context)
    bot = Bot(token=bot_token, request=httpx_client)
    results = {"success": 0, "failed": 0, "errors": []}
    
    formatted_message = f"""
🚨 *ULINZI ALERT SYSTEM* 🚨

*Message:* {message}

📍 *Region:* {region}
⚠️ *Threat Level:* {threat_level}
🕒 *Time:* {timestamp}

_Click a button below to verify:_
"""
    
    # Create interactive buttons - same for all users
    keyboard = [[
        InlineKeyboardButton("✅ SAFE", callback_data=f"vote_safe_{incident_id}"),
        InlineKeyboardButton("🚨 THREAT", callback_data=f"vote_threat_{incident_id}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    for chat_id in chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id.strip(),
                text=formatted_message.strip(),
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            results["success"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Chat {chat_id}: {str(e)}")
    
    return results


async def check_telegram_responses_async(bot_token: str, chat_ids: list, min_timestamp=None):
    """
    Check for responses from Telegram users.
    Similar to SMS checking - looks for keywords in recent messages.
    """
    bot = Bot(token=bot_token)
    responses = []
    
    try:
        for chat_id in chat_ids:
            try:
                # Get recent updates for this chat
                updates = await bot.get_updates(allowed_updates=["message"])
                
                for update in updates:
                    if update.message and str(update.message.chat.id) == str(chat_id).strip():
                        msg_text = update.message.text.upper() if update.message.text else ""
                        msg_time = update.message.date
                        
                        # Check timestamp
                        if min_timestamp and msg_time <= min_timestamp:
                            continue
                        
                        # Check for keywords
                        if any(keyword in msg_text for keyword in ["SAFE", "THREAT", "YES", "CONFIRM", "OK", "RAID"]):
                            responses.append({
                                "chat_id": chat_id,
                                "message": update.message.text,
                                "timestamp": msg_time,
                                "vote": "THREAT" if any(k in msg_text for k in ["THREAT", "YES", "CONFIRM", "RAID"]) else "SAFE"
                            })
                            break  # One vote per user
                            
            except Exception as e:
                continue
                
        return True, responses
        
    except Exception as e:
        return False, f"Error checking responses: {str(e)}"


def send_telegram_alert(bot_token: str, chat_id: str, message: str,
                       region: str = "", threat_level: str = "", 
                       timestamp: str = ""):
    """
    Synchronous wrapper for sending Telegram alerts.
    Creates new event loop to run async function.
    """
    if not bot_token or not chat_id:
        return False, "Missing bot token or chat ID"
    
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run async function
        success, msg = loop.run_until_complete(
            send_telegram_alert_async(bot_token, chat_id, message, region, threat_level, timestamp)
        )
        
        loop.close()
        return success, msg
        
    except Exception as e:
        return False, f"Failed to send Telegram alert: {str(e)}"


def send_telegram_to_multiple(bot_token: str, chat_ids: list, message: str,
                              region: str = "", threat_level: str = "",
                              timestamp: str = ""):
    """
    Synchronous wrapper for sending to multiple users.
    """
    if not bot_token or not chat_ids:
        return False, "Missing bot token or chat IDs"
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        results = loop.run_until_complete(
            send_telegram_to_multiple_async(bot_token, chat_ids, message, region, threat_level, timestamp)
        )
        
        loop.close()
        
        if results["success"] > 0:
            return True, f"Sent to {results['success']}/{len(chat_ids)} users"
        else:
            return False, f"Failed to send: {results['errors']}"
        
    except Exception as e:
        return False, f"Failed: {str(e)}"


def check_telegram_responses(bot_token: str, chat_ids: list, min_timestamp=None):
    """
    Synchronous wrapper for checking Telegram responses.
    """
    if not bot_token or not chat_ids:
        return False, "Missing bot token or chat IDs", []
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success, responses = loop.run_until_complete(
            check_telegram_responses_async(bot_token, chat_ids, min_timestamp)
        )
        
        loop.close()
        
        if success:
            return True, responses
        else:
            return False, responses
        
    except Exception as e:
        return False, f"Error: {str(e)}"

