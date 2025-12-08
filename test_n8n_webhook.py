#!/usr/bin/env python3
"""
Test script for n8n webhook integration
Usage: python test_n8n_webhook.py
"""

import requests
import json
from datetime import datetime

# Your n8n webhook URL
N8N_WEBHOOK_URL = "https://vmi2955047.contaboserver.net/webhook/863ccad9-ebba-4970-aaa5-c042aeea478c"

def test_webhook_direct():
    """Test the webhook directly (without going through the backend)"""
    print("🧪 Testing n8n Webhook (Direct Method)")
    print(f"URL: {N8N_WEBHOOK_URL}\n")
    
    # Prepare test payload matching the expected format
    # NOTE: Replace '123456789' with your actual Telegram chat ID
    payload = {
        "chatId": "123456789",  # Your Telegram chat ID
        "message": "🚨 ULINZI TEST ALERT: Suspected Raid Activity Detected",
        "data": {
            "region": "Marsabit County",
            "threat_level": "HIGH",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_mode": True
        }
    }
    
    try:
        print("📤 Sending payload:")
        print(json.dumps(payload, indent=2))
        print("\n⏳ Waiting for response...\n")
        
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📥 Response: {response.text}\n")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Check your Telegram bot for the alert message.")
        elif response.status_code == 404:
            print("⚠️  WEBHOOK NOT ACTIVE")
            print("📌 Action Required:")
            print("   1. Open your n8n workflow")
            print("   2. Click 'Execute Workflow' or 'Listen for Test Event'")
            print("   3. Make sure the workflow is ACTIVATED (toggle switch)")
            print("   4. Run this script again\n")
        else:
            print(f"❌ ERROR: Unexpected status code {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")

def test_webhook_via_backend():
    """Test the webhook through the Ulinzi backend API"""
    print("\n" + "="*60)
    print("🧪 Testing n8n Webhook (Via Ulinzi Backend)")
    print("="*60 + "\n")
    
    backend_url = "http://localhost:8000/alerts/n8n"
    
    payload = {
        "webhook_url": N8N_WEBHOOK_URL,
        "message": "🚨 ULINZI BACKEND TEST: System Integration Check",
        "data": {
            "region": "West Pokot",
            "threat_level": "MEDIUM",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Backend API Test"
        }
    }
    
    try:
        print("📤 Sending via Backend API:")
        print(json.dumps(payload, indent=2))
        print("\n⏳ Waiting for response...\n")
        
        response = requests.post(backend_url, json=payload, timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📥 Response: {response.json()}\n")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Backend API working correctly.")
            print("   Check your Telegram bot for the alert message.")
        else:
            print(f"❌ ERROR: {response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend")
        print("📌 Make sure your backend is running:")
        print("   cd backend && uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🛡️  ULINZI n8n WEBHOOK TESTER")
    print("="*60 + "\n")
    
    # Test 1: Direct webhook call
    test_webhook_direct()
    
    # Test 2: Via backend (optional, comment out if backend is not running)
    # test_webhook_via_backend()
    
    print("\n" + "="*60)
    print("✅ Test Complete")
    print("="*60)
