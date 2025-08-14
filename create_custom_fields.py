#!/usr/bin/env python3
"""
Create custom fields "Celular" and "Email" in ClickUp list
"""

import asyncio
import aiohttp
from core.config import settings

async def create_custom_fields():
    """Create custom fields in ClickUp list"""
    
    print("🏷️ Creating custom fields in ClickUp...")
    print("=" * 50)
    
    token = settings.CLICKUP_API_TOKEN
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    # List ID from our created list
    list_id = "901412119767"
    
    # Custom fields to create
    custom_fields = [
        {
            "name": "Celular",
            "type": "phone",
            "type_config": {},
            "width": 100
        },
        {
            "name": "Email",
            "type": "email",
            "type_config": {},
            "width": 100
        }
    ]
    
    print(f"Creating custom fields in list ID: {list_id}")
    
    for field in custom_fields:
        field_name = field['name']
        field_type = field['type']
        
        print(f"\n🔧 Creating field: {field_name} (Type: {field_type})")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Create the custom field
                url = f"https://api.clickup.com/api/v2/list/{list_id}/field"
                
                async with session.post(url, headers=headers, json=field) as response:
                    print(f"   Response status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        field_id = data.get('id')
                        print(f"   ✅ Field '{field_name}' created successfully!")
                        print(f"      Field ID: {field_id}")
                        
                    else:
                        text = await response.text()
                        print(f"   ❌ Error creating field '{field_name}': {text}")
                        
        except Exception as e:
            print(f"   ❌ Exception creating field '{field_name}': {e}")
    
    # Verify all fields were created
    print(f"\n🔍 Verifying custom fields creation...")
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.clickup.com/api/v2/list/{list_id}/field"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    fields_data = await response.json()
                    fields = fields_data.get("fields", [])
                    print(f"   ✅ Found {len(fields)} custom fields in list")
                    
                    for field in fields:
                        field_name = field.get('name', 'Unknown')
                        field_type = field.get('type', 'Unknown')
                        field_id = field.get('id', 'Unknown')
                        print(f"      🏷️  {field_name} (Type: {field_type}, ID: {field_id})")
                        
                        # Check if this is one of our target fields
                        if field_name.lower() in ['celular', 'email']:
                            print(f"         🎯 TARGET FIELD CONFIRMED: {field_name}")
                else:
                    text = await response.text()
                    print(f"   ❌ Error getting fields: {text}")
                    
    except Exception as e:
        print(f"   ❌ Exception verifying fields: {e}")

if __name__ == "__main__":
    asyncio.run(create_custom_fields())
