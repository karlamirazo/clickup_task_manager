#!/usr/bin/env python3
"""
Create a new list in ClickUp space to enable custom fields
"""

import asyncio
import aiohttp
from core.config import settings

async def create_list():
    """Create a new list in ClickUp space"""
    
    print("🚀 Creating new list in ClickUp...")
    print("=" * 50)
    
    token = settings.CLICKUP_API_TOKEN
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    # Space ID from our exploration
    space_id = "90143983983"
    
    # List data - only required fields
    list_data = {
        "name": "Tareas del Proyecto",
        "content": "Lista para gestionar tareas del proyecto con campos personalizados"
    }
    
    print(f"Creating list in space ID: {space_id}")
    print(f"List name: {list_data['name']}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Create the list
            url = f"https://api.clickup.com/api/v2/space/{space_id}/list"
            
            async with session.post(url, headers=headers, json=list_data) as response:
                print(f"Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    list_id = data.get('id')
                    list_name = data.get('name')
                    print(f"✅ List created successfully!")
                    print(f"   List ID: {list_id}")
                    print(f"   List Name: {list_name}")
                    
                    # Now let's try to get the list details to confirm
                    print(f"\n🔍 Verifying list creation...")
                    async with session.get(f"https://api.clickup.com/api/v2/list/{list_id}", headers=headers) as get_response:
                        if get_response.status == 200:
                            list_details = await get_response.json()
                            print(f"   ✅ List verified successfully")
                            print(f"   List Type: {list_details.get('type', 'Unknown')}")
                            print(f"   Space ID: {list_details.get('space', {}).get('id', 'Unknown')}")
                        else:
                            text = await get_response.text()
                            print(f"   ❌ Error verifying list: {text}")
                    
                else:
                    text = await response.text()
                    print(f"❌ Error creating list: {text}")
                    
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(create_list())
