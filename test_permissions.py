#!/usr/bin/env python3
"""
Test ClickUp API permissions at different levels
"""

import asyncio
import aiohttp
from core.config import settings

async def test_permissions():
    """Test different levels of ClickUp API access"""
    
    print("🔍 Testing ClickUp API permissions...")
    print("=" * 50)
    
    token = settings.CLICKUP_API_TOKEN
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    print(f"Using token: {token[:15]}...")
    
    # Test different endpoints
    endpoints = [
        ("Team level", "https://api.clickup.com/api/v2/team"),
        ("User level", "https://api.clickup.com/api/v2/user"),
        ("Workspace level", "https://api.clickup.com/api/v2/team/9014943317"),
    ]
    
    for level, endpoint in endpoints:
        print(f"\n📡 Testing {level}: {endpoint}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers) as response:
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        if level == "Team level":
                            teams = data.get("teams", [])
                            print(f"   ✅ Success! Found {len(teams)} teams")
                            for team in teams:
                                print(f"      - {team.get('name', 'Unknown')} (ID: {team.get('id', 'Unknown')})")
                        elif level == "User level":
                            user = data.get("user", {})
                            print(f"   ✅ Success! User: {user.get('username', 'Unknown')}")
                        elif level == "Workspace level":
                            workspace = data.get("team", {})
                            print(f"   ✅ Success! Workspace: {workspace.get('name', 'Unknown')}")
                    else:
                        text = await response.text()
                        print(f"   ❌ Error: {text}")
                        
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test specific space access
    print(f"\n🔍 Testing specific space access...")
    try:
        async with aiohttp.ClientSession() as session:
            # First get the workspace details
            async with session.get("https://api.clickup.com/api/v2/team/9014943317", headers=headers) as response:
                if response.status == 200:
                    workspace_data = await response.json()
                    workspace = workspace_data.get("team", {})
                    print(f"   Workspace: {workspace.get('name', 'Unknown')}")
                    
                    # Try to get spaces
                    async with session.get("https://api.clickup.com/api/v2/team/9014943317/space", headers=headers) as space_response:
                        print(f"   Spaces endpoint status: {space_response.status}")
                        if space_response.status == 200:
                            spaces_data = await space_response.json()
                            spaces = spaces_data.get("spaces", [])
                            print(f"   ✅ Found {len(spaces)} spaces")
                            for space in spaces[:3]:  # Show first 3
                                print(f"      - {space.get('name', 'Unknown')} (ID: {space.get('id', 'Unknown')})")
                            
                            # Test list access for the first space
                            if spaces:
                                first_space = spaces[0]
                                space_id = first_space.get('id')
                                print(f"\n🔍 Testing list access for space: {first_space.get('name')} (ID: {space_id})")
                                
                                async with session.get(f"https://api.clickup.com/api/v2/space/{space_id}/list", headers=headers) as list_response:
                                    print(f"   Lists endpoint status: {list_response.status}")
                                    if list_response.status == 200:
                                        lists_data = await list_response.json()
                                        lists = lists_data.get("lists", [])
                                        print(f"   ✅ Found {len(lists)} lists")
                                        for lst in lists[:3]:  # Show first 3
                                            print(f"      - {lst.get('name', 'Unknown')} (ID: {lst.get('id', 'Unknown')})")
                                        
                                        # Test custom fields access for the first list
                                        if lists:
                                            first_list = lists[0]
                                            list_id = first_list.get('id')
                                            print(f"\n🔍 Testing custom fields access for list: {first_list.get('name')} (ID: {list_id})")
                                            
                                            async with session.get(f"https://api.clickup.com/api/v2/list/{list_id}/field", headers=headers) as field_response:
                                                print(f"   Custom fields endpoint status: {field_response.status}")
                                                if field_response.status == 200:
                                                    fields_data = await field_response.json()
                                                    fields = fields_data.get("fields", [])
                                                    print(f"   ✅ Found {len(fields)} fields")
                                                    for field in fields[:5]:  # Show first 5
                                                        field_type = field.get('type', 'Unknown')
                                                        field_name = field.get('name', 'Unknown')
                                                        print(f"      - {field_name} (Type: {field_type})")
                                                else:
                                                    text = await field_response.text()
                                                    print(f"   ❌ Custom fields error: {text}")
                                    else:
                                        text = await list_response.text()
                                        print(f"   ❌ Lists error: {text}")
                        else:
                            text = await space_response.text()
                            print(f"   ❌ Spaces error: {text}")
                else:
                    print(f"   ❌ Workspace access failed: {response.status}")
                    
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_permissions())
