#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Example: Basic CRUD Application
Task Management System
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from datetime import datetime, timedelta
from bson import ObjectId
import json

class TaskManager:
    """Task Manager - Integrated CRUD System"""
    
    def __init__(self, connection_string="mongodb://localhost:27017/"):
        """Initialize connection and setup database"""
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client.task_management
            self.tasks = self.db.tasks
            self.users = self.db.users
            
            # Setup indexes
            self.setup_indexes()
            
            print("✅ Connected to MongoDB successfully")
            
        except ConnectionFailure as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    def setup_indexes(self):
        """Setup indexes for performance optimization"""
        
        # Task indexes
        self.tasks.create_index("task_id", unique=True)
        self.tasks.create_index([("status", ASCENDING), ("priority", DESCENDING)])
        self.tasks.create_index("user_id")
        self.tasks.create_index("due_date")
        
        # User indexes
        self.users.create_index("email", unique=True)
        self.users.create_index("username", unique=True)
        
        print("📊 Indexes have been set up")
    
    # === User Management ===
    
    def create_user(self, username, email, full_name):
        """Create new user"""
        
        user_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "created_at": datetime.utcnow(),
            "task_count": 0,
            "active": True
        }
        
        try:
            result = self.users.insert_one(user_data)
            print(f"✅ User created: {username} (ID: {result.inserted_id})")
            return result.inserted_id
            
        except DuplicateKeyError:
            print(f"❌ User already exists: {username} or {email}")
            return None
    
    def get_user(self, identifier):
        """Get user (by username, email, or ID)"""
        
        # Try searching in different ways
        query = {}
        if ObjectId.is_valid(identifier):
            query = {"_id": ObjectId(identifier)}
        elif "@" in identifier:
            query = {"email": identifier}
        else:
            query = {"username": identifier}
        
        user = self.users.find_one(query)
        return user
    
    # === Task Management ===
    
    def create_task(self, title, description, user_id, priority="medium", due_date=None):
        """Create new task"""
        
        # Create unique task_id
        task_count = self.tasks.count_documents({}) + 1
        task_id = f"TASK-{task_count:04d}"
        
        # Prepare task data
        task_data = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "user_id": user_id,
            "status": "todo",  # todo, in_progress, completed, cancelled
            "priority": priority,  # low, medium, high, urgent
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "due_date": due_date,
            "completed_at": None,
            "tags": [],
            "comments": []
        }
        
        try:
            result = self.tasks.insert_one(task_data)
            
            # Update user's task count
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": {"task_count": 1}}
            )
            
            print(f"✅ Task created: {task_id}")
            return result.inserted_id
            
        except Exception as e:
            print(f"❌ Error creating task: {e}")
            return None
    
    def get_tasks(self, filters=None, sort_by="created_at", limit=50):
        """Get task list with filters"""
        
        query = filters or {}
        
        # Sort results
        sort_order = DESCENDING if sort_by in ["created_at", "updated_at", "due_date"] else ASCENDING
        
        tasks = list(self.tasks.find(query)
                    .sort(sort_by, sort_order)
                    .limit(limit))
        
        return tasks
    
    def get_task(self, task_identifier):
        """Get specific task"""
        
        query = {}
        if ObjectId.is_valid(task_identifier):
            query = {"_id": ObjectId(task_identifier)}
        else:
            query = {"task_id": task_identifier}
        
        return self.tasks.find_one(query)
    
    def update_task(self, task_identifier, updates):
        """Update task"""
        
        # Add update time
        updates["updated_at"] = datetime.utcnow()
        
        # If status changed to completed
        if updates.get("status") == "completed" and "completed_at" not in updates:
            updates["completed_at"] = datetime.utcnow()
        
        query = {}
        if ObjectId.is_valid(task_identifier):
            query = {"_id": ObjectId(task_identifier)}
        else:
            query = {"task_id": task_identifier}
        
        result = self.tasks.update_one(query, {"$set": updates})
        
        if result.modified_count > 0:
            print(f"✅ Task updated: {task_identifier}")
            return True
        else:
            print(f"❌ Task not found: {task_identifier}")
            return False
    
    def delete_task(self, task_identifier):
        """Delete task"""
        
        # Get task first to know user_id
        task = self.get_task(task_identifier)
        if not task:
            print(f"❌ Task not found: {task_identifier}")
            return False
        
        query = {}
        if ObjectId.is_valid(task_identifier):
            query = {"_id": ObjectId(task_identifier)}
        else:
            query = {"task_id": task_identifier}
        
        result = self.tasks.delete_one(query)
        
        if result.deleted_count > 0:
            # Decrease user's task count
            self.users.update_one(
                {"_id": ObjectId(task["user_id"])},
                {"$inc": {"task_count": -1}}
            )
            
            print(f"✅ Task deleted: {task_identifier}")
            return True
        else:
            print(f"❌ Failed to delete task: {task_identifier}")
            return False
    
    # === Advanced Operations ===
    
    def add_comment_to_task(self, task_identifier, comment_text, author):
        """Add comment to task"""
        
        comment = {
            "text": comment_text,
            "author": author,
            "created_at": datetime.utcnow()
        }
        
        query = {}
        if ObjectId.is_valid(task_identifier):
            query = {"_id": ObjectId(task_identifier)}
        else:
            query = {"task_id": task_identifier}
        
        result = self.tasks.update_one(
            query,
            {
                "$push": {"comments": comment},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count > 0:
            print("✅ Comment added")
            return True
        return False
    
    def add_tags_to_task(self, task_identifier, tags):
        """Add tags to a task"""
        
        query = {}
        if ObjectId.is_valid(task_identifier):
            query = {"_id": ObjectId(task_identifier)}
        else:
            query = {"task_id": task_identifier}
        
        result = self.tasks.update_one(
            query,
            {
                "$addToSet": {"tags": {"$each": tags}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Tags added: {tags}")
            return True
        return False
    
    # === Reports and Statistics ===
    
    def get_user_statistics(self, user_id):
        """User task statistics"""
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "tasks": {"$push": {
                    "task_id": "$task_id",
                    "title": "$title",
                    "priority": "$priority"
                }}
            }}
        ]
        
        stats = list(self.tasks.aggregate(pipeline))
        
        # Prepare statistics
        user_stats = {
            "total_tasks": 0,
            "by_status": {},
            "by_priority": {}
        }
        
        for stat in stats:
            status = stat["_id"]
            count = stat["count"]
            user_stats["by_status"][status] = count
            user_stats["total_tasks"] += count
        
        # Priority statistics
        priority_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
        ]
        
        priority_stats = list(self.tasks.aggregate(priority_pipeline))
        for stat in priority_stats:
            user_stats["by_priority"][stat["_id"]] = stat["count"]
        
        return user_stats
    
    def get_overdue_tasks(self):
        """Overdue tasks"""
        
        current_time = datetime.utcnow()
        
        overdue_tasks = list(self.tasks.find({
            "due_date": {"$lt": current_time},
            "status": {"$nin": ["completed", "cancelled"]}
        }))
        
        return overdue_tasks
    
    def get_productivity_report(self, days=7):
        """Productivity report for the past N days"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "completed_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$completed_at"
                        }
                    },
                    "completed_tasks": {"$sum": 1},
                    "tasks": {"$push": {
                        "task_id": "$task_id",
                        "title": "$title",
                        "user_id": "$user_id"
                    }}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        report = list(self.tasks.aggregate(pipeline))
        return report
    
    # === Display Data ===
    
    def display_task(self, task):
        """Display task details"""
        
        if not task:
            print("❌ Task not found")
            return
        
        print(f"\n📋 {task['title']} ({task['task_id']})")
        print(f"   Description: {task['description']}")
        print(f"   Status: {task['status']}")
        print(f"   Priority: {task['priority']}")
        print(f"   Created at: {task['created_at'].strftime('%Y-%m-%d %H:%M')}")
        
        if task.get('due_date'):
            print(f"   Due date: {task['due_date'].strftime('%Y-%m-%d %H:%M')}")
        
        if task.get('tags'):
            print(f"   Tags: {', '.join(task['tags'])}")
        
        if task.get('comments'):
            print(f"   Comments: {len(task['comments'])}")
            for comment in task['comments'][-3:]:  # Last 3 comments
                print(f"     - {comment['author']}: {comment['text']}")
    
    def display_user_tasks(self, user_identifier):
        """Display user's tasks"""
        
        user = self.get_user(user_identifier)
        if not user:
            print(f"❌ User not found: {user_identifier}")
            return
        
        tasks = self.get_tasks({"user_id": str(user["_id"])})
        
        print(f"\n👤 Tasks for {user['full_name']} ({len(tasks)} tasks)")
        print("-" * 50)
        
        for task in tasks:
            status_icon = {
                "todo": "⏳",
                "in_progress": "🔄", 
                "completed": "✅",
                "cancelled": "❌"
            }.get(task["status"], "❓")
            
            priority_icon = {
                "urgent": "🔥",
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task["priority"], "⚪")
            
            print(f"{status_icon} {priority_icon} {task['task_id']}: {task['title']}")
    
    def close(self):
        """Close connection"""
        self.client.close()
        print("🔌 Connection closed")

# === Usage and Testing ===

def main():
    """Main function for testing"""
    
    # Create task manager
    tm = TaskManager()
    
    try:
        print("🚀 Starting Task Management system test")
        print("=" * 50)
        
        # Create users
        user1_id = tm.create_user("ahmed_dev", "ahmed@example.com", "Ahmed Mohamed")
        user2_id = tm.create_user("sara_pm", "sara@example.com", "Sara Ahmed")
        
        if user1_id and user2_id:
            
            # Create tasks
            task1_id = tm.create_task(
                "Develop UI",
                "Create UI for the new app",
                str(user1_id),
                priority="high",
                due_date=datetime.utcnow() + timedelta(days=7)
            )
            
            task2_id = tm.create_task(
                "Review requirements",
                "Review and update project requirements",
                str(user2_id),
                priority="medium",
                due_date=datetime.utcnow() + timedelta(days=3)
            )
            
            task3_id = tm.create_task(
                "Unit testing",
                "Write unit tests for new features",
                str(user1_id),
                priority="urgent"
            )
            
            # Add comments and tags
            if task1_id:
                tm.add_comment_to_task(task1_id, "Started the initial design", "Ahmed")
                tm.add_tags_to_task(task1_id, ["frontend", "ui", "react"])
            
            if task2_id:
                tm.add_tags_to_task(task2_id, ["requirements", "documentation"])
            
            # Update a task status
            if task3_id:
                tm.update_task(task3_id, {"status": "in_progress"})
            
            # Display users' tasks
            tm.display_user_tasks("ahmed_dev")
            tm.display_user_tasks("sara_pm")
            
            # Show statistics
            print(f"\n📊 Ahmed's statistics:")
            stats = tm.get_user_statistics(str(user1_id))
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            
            # Overdue tasks
            overdue = tm.get_overdue_tasks()
            print(f"\n⏰ Overdue tasks: {len(overdue)}")
            
            # Productivity report
            productivity = tm.get_productivity_report(7)
            print(f"\n📈 Productivity report (7 days): {len(productivity)} days")
            
            print("\n✅ System test completed successfully!")
        
    except Exception as e:
        print(f"❌ Execution error: {e}")
    
    finally:
        tm.close()

if __name__ == "__main__":
    main()
