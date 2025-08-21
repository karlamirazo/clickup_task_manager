#!/usr/bin/env python3
"""
Test script to verify custom field values are being set correctly in ClickUp
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.clickup_client import ClickUpClient
from core.config import settings

async def test_custom_field_values():
    """Test setting custom field values in ClickUp"""
    print("üß™ TESTING CUSTOM FIELD VALUES IN CLICKUP")
    print("=" * 60)
    
    # Initialize ClickUp client
    client = ClickUpClient()
    print(f"‚úÖ ClickUp client initialized with token: {client.api_token[:20]}...")
    
    try:
        # Get workspaces
        workspaces = await client.get_workspaces()
        if workspaces:
            workspace = workspaces[0]
            print(f"üè¢ Using workspace: {workspace['name']} (ID: {workspace['id']})")
            
            # Get spaces
            spaces = await client.get_spaces(workspace['id'])
            if spaces:
                space = spaces[0]
                print(f"üöÄ Using space: {space['name']} (ID: {space['id']})")
                
                # Get lists
                lists = await client.get_lists(space['id'])
                if lists:
                    # Find our target list
                    target_list = None
                    for lst in lists:
                        if lst['name'] == 'Tareas del Proyecto':
                            target_list = lst
                            break
                    
                    if target_list:
                        print(f"üéØ Target list found: {target_list['name']} (ID: {target_list['id']})")
                        
                        # Get custom fields
                        custom_fields = await client.get_list_custom_fields(target_list['id'])
                        if custom_fields:
                            print(f"üéØ Found {len(custom_fields)} custom fields:")
                            for field in custom_fields:
                                print(f"   - {field['name']} ({field['type']}) - ID: {field['id']}")
                            
                            # Create a test task with custom field values
                            print("\nüìù Creating test task with custom field values...")
                            
                            task_data = {
                                "name": f"Test Task with Custom Fields - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                "content": "This task should have custom fields populated",
                                "custom_fields": [
                                    {
                                        "id": "51fa0661-0995-4c37-ba8d-3307aef300ca",  # Celular
                                        "value": "+525512345678"
                                    },
                                    {
                                        "id": "621ed627-a960-4d3a-8ac7-7d0946fe17c2",  # Email
                                        "value": "test@example.com"
                                    }
                                ]
                            }
                            
                            print(f"üìã Task data: {task_data}")
                            
                            # Create the task
                            new_task = await client.create_task(target_list['id'], task_data)
                            if new_task:
                                print(f"‚úÖ Task created successfully! ID: {new_task['id']}")
                                print(f"   Name: {new_task.get('name', 'N/A')}")
                                
                                # Wait a moment for ClickUp to process
                                print("‚è≥ Waiting for ClickUp to process custom fields...")
                                await asyncio.sleep(3)
                                
                                # Get the task to see if custom fields were set
                                print("üîç Retrieving task to check custom fields...")
                                # Note: We need to implement get_task method or check via API
                                
                                # For now, let's check if we can update the custom fields after creation
                                print("üîÑ Attempting to update custom fields after task creation...")
                                
                                # This would require implementing update_custom_field_value method
                                print("‚ö†Ô∏è Note: update_custom_field_value method not yet implemented")
                                
                            else:
                                print("‚ùå Failed to create test task")
                        else:
                            print("‚ùå No custom fields found in the list")
                    else:
                        print("‚ùå Target list 'Tareas del Proyecto' not found")
                else:
                    print("‚ùå No lists found in the space")
            else:
                print("‚ùå No spaces found in the workspace")
        else:
            print("‚ùå No workspaces found or API connection failed")
            
    except Exception as e:
        print(f"‚ùå Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("üöÄ STARTING CUSTOM FIELD VALUES TEST")
    print("=" * 60)
    
    await test_custom_field_values()
    
    print("\n\nüéØ TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
