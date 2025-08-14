#!/usr/bin/env python3
"""
Test script to verify the new ClickUp API token
"""

import aiohttp
import asyncio

async def test_new_clickup_token():
    """Test the new ClickUp API token directly"""
    token = "pk_156221125_XB0BCWQCZ1ML1W7S88M0RCHX6WIZFY7O"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"Testing new token: {token[:10]}...")
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
                    
                    # Test getting workspaces for the first team
                    if data.get('teams'):
                        team_id = data['teams'][0]['id']
                        print(f"\n🔍 Testing workspace access for team {team_id}...")
                        
                        async with session.get(
                            f"https://api.clickup.com/api/v2/team/{team_id}/space",
                            headers=headers
                        ) as space_response:
                            if space_response.status == 200:
                                space_data = await space_response.json()
                                print(f"✅ Workspace access successful! Found {len(space_data.get('spaces', []))} spaces")
                                for space in space_data.get('spaces', [])[:3]:  # Show first 3
                                    print(f"   - {space.get('name', 'Unknown')} (ID: {space.get('id', 'Unknown')})")
                            else:
                                print(f"❌ Workspace access failed: {space_response.status}")
                                
                else:
                    text = await response.text()
                    print(f"❌ Error: {text}")

        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_clickup_token())
