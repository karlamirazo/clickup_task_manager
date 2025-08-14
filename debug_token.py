#!/usr/bin/env python3
"""
Comprehensive debug script for ClickUp API token issues
"""

import aiohttp
import asyncio
import json

async def debug_clickup_token():
    """Debug ClickUp API token issues comprehensively"""
    
    # Test multiple tokens to compare
    tokens = [
        "pk_156221125_XB0BCWQCZ1ML1W7S88M0RCHX6WIZFY7O",  # New token
        "pk_156221125_VE0TJ0IMP8ZQ5U5QBCYGUQC2K94I8B48"   # Old token
    ]
    
    # Test different endpoints
    endpoints = [
        "https://api.clickup.com/api/v2/team",
        "https://api.clickup.com/api/v2/user",
        "https://api.clickup.com/api/v2/oauth/token"  # Check if token is valid
    ]
    
    for token in tokens:
        print(f"\n🔑 Testing token: {token[:15]}...")
        print("=" * 50)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        for endpoint in endpoints:
            print(f"\n📡 Testing endpoint: {endpoint}")
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, headers=headers) as response:
                        print(f"   Status: {response.status}")
                        print(f"   Response Headers: {dict(response.headers)}")
                        
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"   ✅ Success! Response: {json.dumps(data, indent=2)[:200]}...")
                            except:
                                text = await response.text()
                                print(f"   ✅ Success! Text response: {text[:200]}...")
                        else:
                            try:
                                error_data = await response.json()
                                print(f"   ❌ Error: {json.dumps(error_data, indent=2)}")
                            except:
                                text = await response.text()
                                print(f"   ❌ Error: {text}")
                                
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        
        # Test without Bearer prefix
        print(f"\n🔍 Testing without 'Bearer' prefix...")
        headers_no_bearer = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.clickup.com/api/v2/team", headers=headers_no_bearer) as response:
                    print(f"   Status: {response.status}")
                    if response.status == 200:
                        print("   ✅ Success without Bearer prefix!")
                    else:
                        text = await response.text()
                        print(f"   ❌ Error: {text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_clickup_token())
