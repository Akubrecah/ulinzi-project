# 🛡️ Ulinzi n8n + Telegram Integration Guide

## Overview
This guide will help you set up the complete n8n + Telegram integration for the Ulinzi threat alert system.

## Quick Setup (3 Steps)

### Step 1: Get Your Telegram Chat ID

1. **Start a chat with @userinfobot** on Telegram
2. The bot will reply with your user information
3. Copy your **Chat ID** (it's a number like `123456789`)
4. Save this number - you'll need it in Step 3

### Step 2: Import & Activate the n8n Workflow

1. **Open your n8n instance** (https://vmi2955047.contaboserver.net/ or your n8n URL)

2. **Import the workflow**:
   - Click "Workflows" → "Import from File"
   - Select `n8n_workflow.json` from the ulinzi-project folder
   - Click "Import"

3. **Configure the Telegram node**:
   - Click on the "Telegram" node in the workflow
   - Click on "Credential to connect with"
   - Select or create new "Telegram API" credentials
   - Enter your **Bot Token** (get from @BotFather if you don't have one)
   - Save the credentials

4. **Activate the workflow**:
   - Toggle the **"Active"** switch in the top-right to ON
   - The workflow is now live and listening for webhooks!

### Step 3: Configure the Streamlit App

1. **Run the Ulinzi application**:
   ```bash
   streamlit run frontend/app.py
   ```

2. **Navigate to GrazingGuard** in the sidebar

3. **Enter your settings** in the sidebar:
   ## Your n8n Webhook URL
   ```
   https://vmi2955047.contaboserver.net/webhook/863ccad9-ebba-4970-aaa5-c042aeea478c
   ```
   - **Telegram Chat ID**: Enter the Chat ID from Step 1

4. **Test the integration**:
   - Select "Active Raid Simulation"
   - Click "Send SMS Alert to Chief"
   - Check your Telegram - you should receive an alert! 🎉

## Testing the Integration

### Method 1: Using the Test Script

```bash
python test_n8n_webhook.py
```

**Before running**: Edit `test_n8n_webhook.py` and replace `123456789` with your actual Chat ID.

**Expected output**:
```
✅ Status Code: 200
✅ SUCCESS! Check your Telegram bot for the alert message.
```

### Method 2: Manual curl Test

```bash
curl -X POST https://vmi2955047.contaboserver.net/webhook-test/ulinzi-alert \
  -H "Content-Type: application/json" \
  -d '{
    "chatId": "YOUR_CHAT_ID",
    "message": "Test from Ulinzi",
    "data": {
      "region": "Marsabit County",
      "threat_level": "HIGH",
      "timestamp": "2025-12-08 12:00:00"
    }
  }'
```

## Troubleshooting

### ❌ Error: "The requested webhook is not registered"

**Solution**:
- Make sure the n8n workflow is **ACTIVATED** (toggle switch ON)
- The workflow must be running 24/7 to receive webhooks
- If in test mode, click "Execute Workflow" before sending requests

### ❌ No Telegram Message Received

**Possible causes**:

1. **Wrong Chat ID**: 
   - Verify your Chat ID with @userinfobot
   - Make sure you entered it correctly in the Streamlit sidebar

2. **Bot Credentials Not Set**:
   - Open the Telegram node in n8n
   - Make sure credentials are configured
   - Test the credentials

3. **Bot Can't Send Messages**:
   - Start a conversation with your bot first
   - Send it `/start` message
   - Make sure the bot isn't blocked

### ❌ Workflow Validation Errors in n8n

**Solution**:
The workflow has been fixed to remove all validation errors:
- ✅ All required fields have values
- ✅ Expressions use correct n8n syntax
- ✅ No empty credential requirements
- Re-import the latest `n8n_workflow.json` file

## How It Works

```
┌─────────────────┐
│ Ulinzi App      │
│ Detects Threat  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send SMS Alert  │
│ to Elders       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Trigger n8n     │
│ Webhook         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ n8n Workflow    │
│ Receives Data   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Telegram Node   │
│ Sends Message   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 📱 You receive  │
│ alert on        │
│ Telegram!       │
└─────────────────┘
```

## Message Format

When a threat is detected, you'll receive a Telegram message like this:

```
🚨 *ULINZI ALERT SYSTEM* 🚨

*Message:* ULINZI ALERT: Suspected Raid in West Pokot. Please CONFIRM status immediately.

📍 *Region:* West Pokot
⚠️ *Threat Level:* HIGH
🕒 *Time:* 2025-12-08 12:00:00
```

## Getting a Telegram Bot Token

If you don't have a Telegram bot yet:

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts to name your bot
4. Copy the **Bot Token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Use this token in the n8n Telegram credentials

## Production Deployment

For production use:

1. ✅ Keep the n8n workflow **ACTIVATED** at all times
2. ✅ Use environment variables for sensitive data (Chat ID, Bot Token)
3. ✅ Set up n8n monitoring/alerts
4. ✅ Add webhook authentication for security
5. ✅ Consider using Telegram groups for team alerts

## Support

If you encounter issues:
1. Check n8n execution logs for errors
2. Verify all credentials are set correctly
3. Test with the test script first
4. Check backend logs: `uvicorn main:app --reload`

---

**🎉 Once set up, your Ulinzi system will send real-time threat alerts to both SMS and Telegram!**
