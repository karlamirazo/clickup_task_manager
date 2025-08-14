#!/usr/bin/env python3
"""
Simple test script to verify ClickUp client step by step
"""

import asyncio
import aiohttp
from core.config import settings

async def test_simple():
    """Test ClickUp client step by step"""
    
    print("🔍 Testing ClickUp configuration step by step...")
    print("=" * 50)
    
    # 1. Check configuration
    print(f"1. API Token: {settings.CLICKUP_API_TOKEN[:15]}...")
    print(f"2. Base URL: {settings.CLICKUP_API_BASE_URL}")
    
    # 2. Test direct API call
    print(f"\n3. Testing direct API call...")
    token = settings.CLICKUP_API_TOKEN
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    print(f"   Headers: {headers}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "https://api.clickup.com/api/v2/team",
                headers=headers
            ) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Success! Found {len(data.get('teams', []))} teams")
                else:
                    text = await response.text()
                    print(f"   ❌ Error: {text}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # 3. Test with ClickUp client
    print(f"\n4. Testing with ClickUp client...")
    try:
        from core.clickup_client import ClickUpClient
        client = ClickUpClient()
        print(f"   Client headers: {client.headers}")
        
        # Test a simple method
        workspaces = await client.get_workspaces()
        print(f"   ✅ Client works! Found {len(workspaces)} workspaces")
        
    except Exception as e:
        print(f"   ❌ Client error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple())
