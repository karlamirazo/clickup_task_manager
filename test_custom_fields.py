#!/usr/bin/env python3
"""
Test script to verify that custom fields "Celular" and "Email" 
are accessible and the ClickUp integration is working
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.clickup_client import ClickUpClient
from core.config import settings
from utils.notifications import log_notification
from core.database import get_db
from models.notification_log import NotificationLog

async def test_clickup_integration():
    """Test ClickUp API integration and custom fields access"""
    print("🧪 TESTING CLICKUP INTEGRATION")
    print("=" * 60)
    
    # Initialize ClickUp client
    client = ClickUpClient()
    print(f"✅ ClickUp client initialized with token: {client.api_token[:20]}...")
    
    try:
        # Test API connection
        print("\n🔗 Testing ClickUp API connection...")
        
        # Get workspaces directly
        workspaces = await client.get_workspaces()
        if workspaces:
            print(f"✅ API connection successful! Found {len(workspaces)} workspaces")
            
            # Get the first workspace
            workspace = workspaces[0]
            print(f"🏢 Using workspace: {workspace['name']} (ID: {workspace['id']})")
            
            # Get spaces in this workspace
            spaces = await client.get_spaces(workspace['id'])
            if spaces:
                space = spaces[0]
                print(f"🚀 Using space: {space['name']} (ID: {space['id']})")
                
                # Get lists in this space
                lists = await client.get_lists(space['id'])
                if lists:
                    print(f"📝 Found {len(lists)} lists in the space:")
                    for lst in lists:
                        print(f"   - {lst['name']} (ID: {lst['id']})")
                    
                    # Find our "Tareas del Proyecto" list
                    target_list = None
                    for lst in lists:
                        if lst['name'] == 'Tareas del Proyecto':
                            target_list = lst
                            break
                    
                    if target_list:
                        print(f"\n🎯 Target list found: {target_list['name']} (ID: {target_list['id']})")
                        
                        # Get custom fields for this list
                        custom_fields = await client.get_list_custom_fields(target_list['id'])
                        if custom_fields:
                            print(f"🎯 Found {len(custom_fields)} custom fields:")
                            for field in custom_fields:
                                print(f"   - {field['name']} ({field['type']}) - ID: {field['id']}")
                            
                            # Test creating a simple task
                            print("\n📝 Testing task creation...")
                            
                            # Create a test task
                            task_data = {
                                "name": f"Test Task - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                "content": "This is a test task to verify the integration is working"
                            }
                            
                            new_task = await client.create_task(target_list['id'], task_data)
                            if new_task:
                                print(f"✅ Task created successfully! ID: {new_task['id']}")
                                print(f"   Name: {new_task.get('name', 'N/A')}")
                                print(f"   Content: {new_task.get('content', 'N/A')}")
                                print(f"   Status: {new_task.get('status', 'N/A')}")
                                
                                # Clean up - delete the test task
                                print("\n🧹 Cleaning up test task...")
                                delete_result = await client.delete_task(new_task['id'])
                                if delete_result:
                                    print("✅ Test task deleted successfully!")
                                else:
                                    print("⚠️ Could not delete test task (may need manual cleanup)")
                                
                            else:
                                print("❌ Failed to create test task")
                        else:
                            print("❌ No custom fields found in the list")
                    else:
                        print("❌ Target list 'Tareas del Proyecto' not found")
                        print("Available lists:")
                        for lst in lists:
                            print(f"   - {lst['name']}")
                else:
                    print("❌ No lists found in the space")
            else:
                print("❌ No spaces found in the workspace")
        else:
            print("❌ No workspaces found or API connection failed")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_notification_logging():
    """Test notification logging functionality"""
    print("\n\n📊 TESTING NOTIFICATION LOGGING")
    print("=" * 60)
    
    try:
        # Test logging a notification
        print("📝 Testing notification logging...")
        
        # Log a test notification
        await log_notification(
            notification_type="test",
            recipient="test@example.com",
            status="success",
            task_id="test_task_123",
            task_name="Test Task for Custom Fields"
        )
        
        print("✅ Notification logged successfully!")
        
        # Verify it was logged in the database
        print("🔍 Verifying notification in database...")
        db = next(get_db())
        try:
            notifications = db.query(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(5).all()
            if notifications:
                print(f"✅ Found {len(notifications)} recent notifications:")
                for notif in notifications:
                    print(f"   - {notif.notification_type} | {notif.recipient} | {notif.status} | {notif.created_at}")
            else:
                print("❌ No notifications found in database")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error during notification testing: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("🚀 STARTING CLICKUP INTEGRATION TEST")
    print("=" * 60)
    
    # Test ClickUp integration
    await test_clickup_integration()
    
    # Test notification logging
    await test_notification_logging()
    
    print("\n\n🎯 TEST COMPLETED!")
    print("=" * 60)
    print("\n📋 SUMMARY:")
    print("✅ If you see 'Task created successfully' above, the ClickUp integration is working")
    print("✅ If you see custom fields listed above, they are accessible")
    print("✅ The next step is to test the actual automatic population logic")

if __name__ == "__main__":
    asyncio.run(main())
