#!/usr/bin/env python3
"""
Simple OpenAI connectivity test
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_connectivity():
    """Test basic network connectivity"""
    print("🌐 Testing network connectivity...")
    
    # Test basic internet
    try:
        response = requests.get("https://google.com", timeout=5)
        print("✅ Basic internet: OK")
    except Exception as e:
        print(f"❌ Basic internet: FAILED - {e}")
        return False
    
    # Test OpenAI API
    try:
        headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
        response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
        print(f"✅ OpenAI API: OK (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ OpenAI API: FAILED - {e}")
        return False
    
    # Test OpenAI blob storage (where tiktoken files are)
    try:
        response = requests.get("https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken", timeout=10)
        print(f"✅ OpenAI Blob Storage: OK (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ OpenAI Blob Storage: FAILED - {e}")
        print("   This is likely the source of your error!")
        return False
    
    return True

def test_openai_simple():
    """Test simple OpenAI API call"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        print("\n🤖 Testing simple OpenAI call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello World'"}],
            max_tokens=10
        )
        print(f"✅ OpenAI Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI Simple Call: FAILED - {e}")
        return False

if __name__ == "__main__":
    print("🔍 BACO Chatbot - Connectivity Diagnostics")
    print("=" * 45)
    
    connectivity_ok = test_connectivity()
    
    if connectivity_ok:
        print("\n🎯 All connectivity tests passed!")
        test_openai_simple()
    else:
        print("\n❌ Connectivity issues detected.")
        print("\n💡 Troubleshooting suggestions:")
        print("   1. Check your internet connection")
        print("   2. Try a different network/WiFi")
        print("   3. Disable VPN if using one")
        print("   4. Check firewall settings")
        print("   5. Try again in a few minutes")