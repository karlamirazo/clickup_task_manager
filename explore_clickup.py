#!/usr/bin/env python3
"""
Explore ClickUp workspace structure to find lists and custom fields
"""

import asyncio
import aiohttp
from core.config import settings

async def explore_clickup():
    """Explore ClickUp workspace structure"""
    
    print("🔍 Exploring ClickUp workspace structure...")
    print("=" * 60)
    
    token = settings.CLICKUP_API_TOKEN
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    print(f"Using token: {token[:15]}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # 1. Get all teams
            print("\n📋 Step 1: Getting all teams...")
            async with session.get("https://api.clickup.com/api/v2/team", headers=headers) as response:
                if response.status == 200:
                    teams_data = await response.json()
                    teams = teams_data.get("teams", [])
                    print(f"   ✅ Found {len(teams)} teams")
                    
                    for team in teams:
                        team_id = team.get('id')
                        team_name = team.get('name')
                        print(f"   📁 Team: {team_name} (ID: {team_id})")
                        
                        # 2. Get all spaces in this team
                        print(f"\n   🔍 Getting spaces for team: {team_name}")
                        async with session.get(f"https://api.clickup.com/api/v2/team/{team_id}/space", headers=headers) as space_response:
                            if space_response.status == 200:
                                spaces_data = await space_response.json()
                                spaces = spaces_data.get("spaces", [])
                                print(f"      ✅ Found {len(spaces)} spaces")
                                
                                for space in spaces:
                                    space_id = space.get('id')
                                    space_name = space.get('name')
                                    space_type = space.get('type', 'Unknown')
                                    print(f"      📂 Space: {space_name} (ID: {space_id}, Type: {space_type})")
                                    
                                    # 3. Get all lists in this space
                                    print(f"         🔍 Getting lists for space: {space_name}")
                                    async with session.get(f"https://api.clickup.com/api/v2/space/{space_id}/list", headers=headers) as list_response:
                                        if list_response.status == 200:
                                            lists_data = await list_response.json()
                                            lists = lists_data.get("lists", [])
                                            print(f"            ✅ Found {len(lists)} lists")
                                            
                                            for lst in lists:
                                                list_id = lst.get('id')
                                                list_name = lst.get('name')
                                                list_type = lst.get('type', 'Unknown')
                                                print(f"            📝 List: {list_name} (ID: {list_id}, Type: {list_type})")
                                                
                                                # 4. Get custom fields for this list
                                                print(f"               🔍 Getting custom fields for list: {list_name}")
                                                async with session.get(f"https://api.clickup.com/api/v2/list/{list_id}/field", headers=headers) as field_response:
                                                    if field_response.status == 200:
                                                        fields_data = await field_response.json()
                                                        fields = fields_data.get("fields", [])
                                                        print(f"                  ✅ Found {len(fields)} fields")
                                                        
                                                        for field in fields:
                                                            field_name = field.get('name', 'Unknown')
                                                            field_type = field.get('type', 'Unknown')
                                                            field_id = field.get('id', 'Unknown')
                                                            print(f"                     🏷️  Field: {field_name} (Type: {field_type}, ID: {field_id})")
                                                            
                                                            # Check if this is one of our target fields
                                                            if field_name.lower() in ['celular', 'email', 'phone', 'correo']:
                                                                print(f"                        🎯 TARGET FIELD FOUND: {field_name}")
                                                    else:
                                                        text = await field_response.text()
                                                        print(f"                  ❌ Custom fields error: {text}")
                                        else:
                                            text = await list_response.text()
                                            print(f"            ❌ Lists error: {text}")
                            else:
                                text = await space_response.text()
                                print(f"      ❌ Spaces error: {text}")
                else:
                    text = await response.text()
                    print(f"   ❌ Teams error: {text}")
                    
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(explore_clickup())
