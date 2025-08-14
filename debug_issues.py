#!/usr/bin/env python3
"""
Debug script to identify issues with:
1. Custom fields not populating in ClickUp
2. Dashboard counters showing zeros
3. Dashboard visualization being too narrow
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db, engine
from models.notification_log import NotificationLog
from models.task import Task
from core.clickup_client import ClickUpClient
from utils.notifications import log_notification
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_

async def debug_custom_fields():
    """Debug custom fields not populating in ClickUp"""
    print("\n🔍 DEBUGGING CUSTOM FIELDS ISSUE")
    print("=" * 50)
    
    try:
        # Test ClickUp client
        client = ClickUpClient()
        print("✅ ClickUp client initialized")
        
        # Test workspace access
        workspaces = await client.get_workspaces()
        if workspaces:
            print(f"✅ Found {len(workspaces)} workspaces")
            workspace = workspaces[0]
            print(f"   Using workspace: {workspace['id']}")
            
            # Get spaces in the workspace
            try:
                spaces = await client.get_spaces(workspace['id'])
                if spaces:
                    print(f"✅ Found {len(spaces)} spaces in workspace")
                    space = spaces[0]  # Use first space
                    space_id = space['id']
                    print(f"   Using space: {space['name']} (ID: {space_id})")
                    
                    # Test lists access in the specific space
                    try:
                        lists = await client.get_lists(space_id)
                        if lists:
                            print(f"✅ Found {len(lists)} lists in space")
                            # Test tasks access
                            if lists:
                                list_id = lists[0]['id']
                                try:
                                    tasks = await client.get_tasks(list_id)
                                    print(f"✅ Found {len(tasks)} tasks in first list")
                                except Exception as e:
                                    print(f"❌ Error getting tasks: {e}")
                        else:
                            print("❌ No lists found in space")
                    except Exception as e:
                        print(f"Error obteniendo listas del espacio: {e}")
                        
                    # Test folders access in the specific space
                    try:
                        folders = await client.get_folders(space_id)
                        if folders:
                            print(f"✅ Found {len(folders)} folders in space")
                        else:
                            print("❌ No folders found in space")
                    except Exception as e:
                        print(f"Error obteniendo folders del espacio: {e}")
                else:
                    print("❌ No spaces found in workspace")
            except Exception as e:
                print(f"Error obteniendo espacios: {e}")
        else:
            print("❌ No workspaces found")
            
    except Exception as e:
        print(f"❌ Error initializing ClickUp client: {e}")

async def debug_dashboard_counters():
    """Debug dashboard counters showing zeros"""
    print("\n🔍 DEBUGGING DASHBOARD COUNTERS ISSUE")
    print("=" * 50)
    
    try:
        # Check NotificationLog table
        print("📊 Checking NotificationLog table...")
        db = next(get_db())
        
        # Count total logs
        total_logs = db.query(NotificationLog).count()
        print(f"   Total notification logs: {total_logs}")
        
        if total_logs > 0:
            print(f"   Found {total_logs} logs, showing recent ones...")
            recent_logs = db.query(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(5).all()
            for log in recent_logs:
                print(f"   - {log.notification_type} to {log.recipient}: {log.status} at {log.created_at}")
        else:
            print("   ⚠️ No notification logs found")
        
        # Check notification stats for last 24h
        print("\n📊 Checking notification stats for last 24h...")
        yesterday = datetime.now() - timedelta(days=1)
        recent_logs = db.query(NotificationLog).filter(
            NotificationLog.created_at >= yesterday
        ).all()
        
        print(f"   Notifications in last 24h: {len(recent_logs)}")
        
        if recent_logs:
            # Count by status
            status_counts = {}
            type_counts = {}
            for log in recent_logs:
                status_counts[log.status] = status_counts.get(log.status, 0) + 1
                type_counts[log.notification_type] = type_counts.get(log.notification_type, 0) + 1
            
            print("   By status:")
            for status, count in status_counts.items():
                print(f"     {status}: {count}")
            
            print("   By type:")
            for type_, count in type_counts.items():
                print(f"     {type_}: {count}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error checking dashboard counters: {e}")

async def debug_dashboard_width():
    """Debug dashboard visualization being too narrow"""
    print("\n🔍 DEBUGGING DASHBOARD WIDTH ISSUE")
    print("=" * 50)
    
    # Check dashboard HTML
    dashboard_file = "static/dashboard.html"
    if os.path.exists(dashboard_file):
        print(f"✅ Dashboard file exists: {dashboard_file}")
        
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for correct CSS
        if 'max-width: 95%' in content:
            print("✅ Found correct max-width: 95%")
        else:
            print("❌ max-width: 95% not found")
            
        if 'min-width: 1200px' in content:
            print("✅ Found correct min-width: 1200px")
        else:
            print("❌ min-width: 1200px not found")
            
        if 'width: 100%' in content:
            print("✅ Found correct width: 100%")
        else:
            print("❌ width: 100% not found")
    else:
        print(f"❌ Dashboard file not found: {dashboard_file}")
    
    # Check CSS file for conflicts
    css_file = "static/styles.css"
    print(f"\n📁 Checking CSS file: {css_file}")
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        if '.dashboard-container' in css_content:
            print("   ✅ Found .dashboard-container in CSS")
        else:
            print("   ⚠️ No .dashboard-container found in static/styles.css")
    else:
        print(f"   ❌ CSS file not found: {css_file}")

async def test_notification_logging():
    """Test notification logging functionality"""
    print("\n🔍 TESTING NOTIFICATION LOGGING")
    print("=" * 40)
    
    try:
        print("📝 Testing notification logging...")
        # Test with correct parameters
        log_notification(
            notification_type="test",
            recipient="test@example.com", 
            status="sent",
            task_id="test_task_123",
            task_name="Test Task"
        )
        print("✅ Notification logging test successful")
        
    except Exception as e:
        print(f"❌ Error testing notification logging: {e}")

async def main():
    """Main debug function"""
    print("🚀 STARTING COMPREHENSIVE DEBUG")
    print("=" * 60)
    
    # Run all debug functions
    await debug_custom_fields()
    await debug_dashboard_counters()
    await debug_dashboard_width()
    await test_notification_logging()
    
    print("\n" + "=" * 60)
    print("🏁 DEBUG COMPLETE")
    print("\n📋 SUMMARY OF FINDINGS:")
    print("1. Check the output above for specific issues")
    print("2. If custom fields are failing, check ClickUp API responses")
    print("3. If dashboard counters are zero, check notification logging")
    print("4. If dashboard is narrow, check CSS conflicts")

if __name__ == "__main__":
    asyncio.run(main())
