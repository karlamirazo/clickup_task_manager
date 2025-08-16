#!/usr/bin/env python3
"""
Test script to verify ClickUp API token
"""

import aiohttp
import asyncio

async def test_clickup_token():
    """Test ClickUp API token directly"""
    token = "pk_156221125_VE0TJ0IMP8ZQ5U5QBCYGUQC2K94I8B48"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Testing token: {token[:10]}...")
    print(f"Headers: {headers}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "https://api.clickup.com/api/v2/team", 
                headers=headers
            ) as response:
                print(f"Status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success! Found {len(data.get('teams', []))} teams")
                    for team in data.get('teams', []):
                        print(f"   - {team.get('name', 'Unknown')} (ID: {team.get('id', 'Unknown')})")
                else:
                    text = await response.text()
                    print(f"❌ Error: {text}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_clickup_token())
