# PyMongo CRUD Operations

This comprehensive guide covers all Create, Read, Update, and Delete operations using PyMongo, including advanced techniques, error handling, and best practices.

## Table of Contents

1. [CRUD Overview](#crud-overview)
2. [Create Operations](#create-operations)
3. [Read Operations](#read-operations)
4. [Update Operations](#update-operations)
5. [Delete Operations](#delete-operations)
6. [Bulk Operations](#bulk-operations)
7. [Advanced Patterns](#advanced-patterns)
8. [Error Handling](#error-handling)
9. [Performance Optimization](#performance-optimization)
10. [Best Practices](#best-practices)

## CRUD Overview

PyMongo provides intuitive methods for all CRUD operations that map closely to MongoDB's native operations.

### Basic CRUD Methods

```python
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.myapp
collection = db.users

# Create (Insert)
result = collection.insert_one({"name": "John", "age": 30})
results = collection.insert_many([{"name": "Jane"}, {"name": "Bob"}])

# Read (Find)
user = collection.find_one({"name": "John"})
users = collection.find({"age": {"$gte": 18}})

# Update
result = collection.update_one({"name": "John"}, {"$set": {"age": 31}})
result = collection.update_many({"age": {"$lt": 18}}, {"$set": {"minor": True}})

# Delete
result = collection.delete_one({"name": "John"})
result = collection.delete_many({"age": {"$lt": 18}})
```

### Return Objects and Acknowledgments

```python
# All write operations return result objects
insert_result = collection.insert_one({"name": "Alice"})
print(f"Inserted ID: {insert_result.inserted_id}")
print(f"Acknowledged: {insert_result.acknowledged}")

update_result = collection.update_one({"name": "Alice"}, {"$set": {"age": 25}})
print(f"Matched: {update_result.matched_count}")
print(f"Modified: {update_result.modified_count}")
print(f"Upserted ID: {update_result.upserted_id}")

delete_result = collection.delete_many({"age": {"$lt": 18}})
print(f"Deleted: {delete_result.deleted_count}")
```

## Create Operations

### insert_one() - Single Document Insertion

```python
from bson import ObjectId
from datetime import datetime

def create_user_document():
    """Create a comprehensive user document"""
    user = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "active": True,
        "profile": {
            "bio": "Software developer with 5 years experience",
            "location": "San Francisco, CA",
            "skills": ["Python", "JavaScript", "MongoDB"]
        },
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "language": "en"
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        result = collection.insert_one(user)
        print(f"✅ User created with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        raise

# Usage
user_id = create_user_document()
```

### insert_many() - Multiple Document Insertion

```python
def create_multiple_users():
    """Create multiple users efficiently"""
    users = [
        {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "department": "Engineering",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "department": "Marketing",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "department": "Sales",
            "created_at": datetime.utcnow()
        }
    ]

    try:
        # Insert all documents
        result = collection.insert_many(users)
        print(f"✅ Inserted {len(result.inserted_ids)} users")
        print(f"IDs: {result.inserted_ids}")
        return result.inserted_ids

    except Exception as e:
        print(f"❌ Error inserting users: {e}")
        raise

# Insert with options
def create_users_with_options():
    """Insert users with specific options"""
    users = [{"name": f"User {i}"} for i in range(5)]

    result = collection.insert_many(
        users,
        ordered=False,  # Continue on error
        bypass_document_validation=False  # Respect schema validation
    )

    return result.inserted_ids

# Usage
user_ids = create_multiple_users()
```

### Custom \_id and Document Validation

```python
def create_user_with_custom_id():
    """Create user with custom _id"""
    user = {
        "_id": "user_12345",  # Custom string ID
        "name": "Custom User",
        "email": "custom@example.com",
        "created_at": datetime.utcnow()
    }

    try:
        result = collection.insert_one(user)
        print(f"✅ User created with custom ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def create_user_with_validation():
    """Create user with client-side validation"""
    def validate_user(user_data):
        """Validate user data before insertion"""
        errors = []

        # Required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if not user_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Email validation
        if 'email' in user_data and '@' not in user_data['email']:
            errors.append("Invalid email format")

        # Age validation
        if 'age' in user_data and (user_data['age'] < 0 or user_data['age'] > 120):
            errors.append("Age must be between 0 and 120")

        return errors

    user_data = {
        "name": "Validated User",
        "email": "valid@example.com",
        "age": 25
    }

    # Validate before inserting
    validation_errors = validate_user(user_data)
    if validation_errors:
        raise ValueError(f"Validation failed: {', '.join(validation_errors)}")

    # Add timestamps
    user_data.update({
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    result = collection.insert_one(user_data)
    return result.inserted_id

# Usage
validated_user_id = create_user_with_validation()
```

## Read Operations

### find_one() - Single Document Retrieval

```python
def find_user_examples():
    """Examples of finding single documents"""

    # Find by ID
    user_id = ObjectId("507f1f77bcf86cd799439011")
    user = collection.find_one({"_id": user_id})

    # Find by email
    user = collection.find_one({"email": "john@example.com"})

    # Find with projection (specific fields only)
    user = collection.find_one(
        {"email": "john@example.com"},
        {"name": 1, "email": 1, "profile.location": 1, "_id": 0}
    )

    # Find with nested field
    user = collection.find_one({"profile.location": "San Francisco, CA"})

    if user:
        print(f"Found user: {user}")
    else:
        print("User not found")

    return user

# Advanced find_one with options
def find_user_advanced():
    """Advanced find_one operations"""

    # Find with sorting (get latest user)
    latest_user = collection.find_one(
        {"active": True},
        sort=[("created_at", -1)]  # Sort by created_at descending
    )

    # Find with maximum time
    import time
    user = collection.find_one(
        {"email": "john@example.com"},
        max_time_ms=1000  # Timeout after 1 second
    )

    return latest_user
```

### find() - Multiple Document Retrieval

```python
def find_users_examples():
    """Examples of finding multiple documents"""

    # Find all users
    all_users = list(collection.find())

    # Find with filter
    active_users = list(collection.find({"active": True}))

    # Find with age range
    adult_users = list(collection.find({
        "age": {"$gte": 18, "$lt": 65}
    }))

    # Find with multiple conditions
    engineers = list(collection.find({
        "department": "Engineering",
        "active": True,
        "age": {"$gte": 25}
    }))

    # Find with projection
    user_names = list(collection.find(
        {},
        {"name": 1, "email": 1, "_id": 0}
    ))

    # Find with sorting
    sorted_users = list(collection.find().sort([
        ("department", 1),  # Sort by department ascending
        ("created_at", -1)  # Then by created_at descending
    ]))

    # Find with limit and skip (pagination)
    page_size = 10
    page_number = 2
    users_page = list(collection.find()
                     .skip((page_number - 1) * page_size)
                     .limit(page_size))

    return {
        "all_users": len(all_users),
        "active_users": len(active_users),
        "adult_users": len(adult_users),
        "engineers": len(engineers)
    }

def find_with_cursor():
    """Working with cursors efficiently"""

    # Method 1: Iterate through cursor
    for user in collection.find({"active": True}):
        print(f"Processing user: {user['name']}")

    # Method 2: Use cursor with batch size
    cursor = collection.find({"active": True}).batch_size(100)
    for user in cursor:
        # Process each user
        pass

    # Method 3: Manual cursor handling
    cursor = collection.find({"active": True})
    try:
        while True:
            try:
                user = next(cursor)
                # Process user
                print(f"User: {user['name']}")
            except StopIteration:
                break
    finally:
        cursor.close()
```

### Query Operators and Filters

```python
def advanced_query_examples():
    """Examples of advanced queries with operators"""

    # Comparison operators
    young_users = collection.find({"age": {"$lt": 30}})
    adult_users = collection.find({"age": {"$gte": 18, "$lte": 65}})
    specific_ages = collection.find({"age": {"$in": [25, 30, 35]}})
    not_these_ages = collection.find({"age": {"$nin": [25, 30, 35]}})

    # Logical operators
    active_adults = collection.find({
        "$and": [
            {"active": True},
            {"age": {"$gte": 18}}
        ]
    })

    engineers_or_managers = collection.find({
        "$or": [
            {"department": "Engineering"},
            {"department": "Management"}
        ]
    })

    not_inactive = collection.find({
        "$not": {"active": False}
    })

    # Element operators
    users_with_phone = collection.find({"phone": {"$exists": True}})
    string_ages = collection.find({"age": {"$type": "string"}})

    # Array operators
    python_developers = collection.find({"profile.skills": "Python"})
    full_stack_devs = collection.find({
        "profile.skills": {"$all": ["Python", "JavaScript", "MongoDB"]}
    })
    skilled_devs = collection.find({"profile.skills": {"$size": 3}})

    # Text search (requires text index)
    # collection.create_index([("name", "text"), ("profile.bio", "text")])
    # text_results = collection.find({"$text": {"$search": "developer python"}})

    # Regex searches
    gmail_users = collection.find({"email": {"$regex": r".*@gmail\.com$"}})
    john_users = collection.find({"name": {"$regex": "^John", "$options": "i"}})

    return {
        "young_users": young_users.count(),
        "adult_users": adult_users.count(),
        "active_adults": active_adults.count()
    }

def nested_field_queries():
    """Query nested fields and arrays"""

    # Nested field queries
    sf_users = collection.find({"profile.location": "San Francisco, CA"})
    python_devs = collection.find({"profile.skills": "Python"})

    # Array element matching
    experienced_devs = collection.find({
        "profile.skills": {
            "$elemMatch": {
                "$in": ["Python", "JavaScript", "Java"]
            }
        }
    })

    # Nested array queries
    senior_python_devs = collection.find({
        "profile.skills": "Python",
        "experience_years": {"$gte": 5}
    })

    return list(sf_users)
```

## Update Operations

### update_one() - Single Document Update

```python
def update_user_examples():
    """Examples of updating single documents"""

    # Simple field update
    result = collection.update_one(
        {"email": "john@example.com"},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

    # Multiple field update
    result = collection.update_one(
        {"_id": ObjectId("507f1f77bcf86cd799439011")},
        {
            "$set": {
                "name": "John Smith",
                "age": 31,
                "updated_at": datetime.utcnow()
            }
        }
    )

    # Nested field update
    result = collection.update_one(
        {"email": "john@example.com"},
        {
            "$set": {
                "profile.location": "New York, NY",
                "profile.bio": "Updated bio",
                "preferences.theme": "light"
            }
        }
    )

    # Increment numeric field
    result = collection.update_one(
        {"email": "john@example.com"},
        {
            "$inc": {"login_count": 1},
            "$set": {"last_login": datetime.utcnow()}
        }
    )

    return result

def update_with_operators():
    """Update operations using various operators"""

    # $set - Set field values
    collection.update_one(
        {"email": "john@example.com"},
        {"$set": {"verified": True, "verification_date": datetime.utcnow()}}
    )

    # $unset - Remove fields
    collection.update_one(
        {"email": "john@example.com"},
        {"$unset": {"temporary_field": "", "old_data": ""}}
    )

    # $inc - Increment/decrement numeric values
    collection.update_one(
        {"email": "john@example.com"},
        {"$inc": {"login_count": 1, "points": 10}}
    )

    # $mul - Multiply numeric values
    collection.update_one(
        {"email": "john@example.com"},
        {"$mul": {"points": 1.1}}  # 10% bonus
    )

    # $min/$max - Set to minimum/maximum value
    collection.update_one(
        {"email": "john@example.com"},
        {
            "$min": {"lowest_score": 100},
            "$max": {"highest_score": 95}
        }
    )

    # $currentDate - Set current date
    collection.update_one(
        {"email": "john@example.com"},
        {
            "$currentDate": {
                "last_modified": True,
                "last_login": {"$type": "timestamp"}
            }
        }
    )
```

### Array Update Operations

```python
def array_update_examples():
    """Examples of updating arrays in documents"""

    # $push - Add element to array
    collection.update_one(
        {"email": "john@example.com"},
        {"$push": {"profile.skills": "Docker"}}
    )

    # $push with $each - Add multiple elements
    collection.update_one(
        {"email": "john@example.com"},
        {
            "$push": {
                "profile.skills": {
                    "$each": ["Kubernetes", "AWS", "Redis"]
                }
            }
        }
    )

    # $push with modifiers
    collection.update_one(
        {"email": "john@example.com"},
        {
            "$push": {
                "recent_scores": {
                    "$each": [85, 92, 78],
                    "$slice": -5,  # Keep only last 5 scores
                    "$sort": -1    # Sort descending
                }
            }
        }
    )

    # $addToSet - Add unique elements
    collection.update_one(
        {"email": "john@example.com"},
        {"$addToSet": {"profile.skills": {"$each": ["Python", "Java", "Go"]}}}
    )

    # $pull - Remove matching elements
    collection.update_one(
        {"email": "john@example.com"},
        {"$pull": {"profile.skills": "Java"}}
    )

    # $pullAll - Remove multiple elements
    collection.update_one(
        {"email": "john@example.com"},
        {"$pullAll": {"profile.skills": ["Java", "PHP", "Ruby"]}}
    )

    # $pop - Remove first or last element
    collection.update_one(
        {"email": "john@example.com"},
        {"$pop": {"recent_scores": 1}}  # Remove last element (-1 for first)
    )

def positional_array_updates():
    """Update specific array elements using positional operators"""

    # Update first matching array element ($)
    collection.update_one(
        {"email": "john@example.com", "profile.skills": "Python"},
        {"$set": {"profile.skills.$": "Python 3.9"}}
    )

    # Update all matching array elements ($[])
    collection.update_one(
        {"email": "john@example.com"},
        {"$set": {"profile.skills.$[]": "Updated"}}
    )

    # Update array elements matching filter ($[identifier])
    collection.update_one(
        {"email": "john@example.com"},
        {"$set": {"scores.$[elem]": 100}},
        array_filters=[{"elem": {"$gte": 95}}]
    )

    # Complex array update with multiple conditions
    collection.update_one(
        {"_id": ObjectId("507f1f77bcf86cd799439011")},
        {"$set": {"projects.$[project].status": "completed"}},
        array_filters=[
            {"project.name": "Website Redesign"},
            {"project.deadline": {"$lt": datetime.utcnow()}}
        ]
    )
```

### update_many() - Multiple Document Updates

```python
def update_multiple_documents():
    """Examples of updating multiple documents"""

    # Update all users in a department
    result = collection.update_many(
        {"department": "Engineering"},
        {
            "$set": {"bonus_eligible": True},
            "$inc": {"salary": 5000}
        }
    )
    print(f"Updated {result.modified_count} engineers")

    # Update users based on date condition
    cutoff_date = datetime(2023, 1, 1)
    result = collection.update_many(
        {"created_at": {"$lt": cutoff_date}},
        {"$set": {"legacy_user": True}}
    )

    # Bulk update with different conditions
    result = collection.update_many(
        {"age": {"$gte": 65}},
        {"$set": {"retirement_eligible": True, "status": "senior"}}
    )

    # Update with upsert (create if not exists)
    result = collection.update_many(
        {"department": "HR"},
        {
            "$set": {"department_head": "Jane Smith"},
            "$setOnInsert": {"created_at": datetime.utcnow()}
        },
        upsert=True
    )

    return result
```

### replace_one() - Document Replacement

```python
def replace_document_example():
    """Replace entire document while keeping _id"""

    # Find current document
    current_user = collection.find_one({"email": "john@example.com"})
    if not current_user:
        print("User not found")
        return

    # Create new document (keeping _id)
    new_user_data = {
        "_id": current_user["_id"],  # Keep original _id
        "name": "John Smith Jr.",
        "email": "john.smith@example.com",
        "age": 32,
        "department": "Senior Engineering",
        "profile": {
            "bio": "Senior software engineer with 7 years experience",
            "location": "Seattle, WA",
            "skills": ["Python", "Go", "Kubernetes", "AWS"]
        },
        "updated_at": datetime.utcnow(),
        "migrated": True
    }

    # Replace document
    result = collection.replace_one(
        {"_id": current_user["_id"]},
        new_user_data
    )

    print(f"Replaced: {result.modified_count} document")
    return result
```

### Upsert Operations

```python
def upsert_examples():
    """Examples of upsert operations (update or insert)"""

    # Basic upsert
    result = collection.update_one(
        {"email": "new.user@example.com"},
        {
            "$set": {
                "name": "New User",
                "active": True,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "created_at": datetime.utcnow(),
                "login_count": 0
            }
        },
        upsert=True
    )

    if result.upserted_id:
        print(f"Created new user with ID: {result.upserted_id}")
    else:
        print(f"Updated existing user")

    # Upsert with increment
    result = collection.update_one(
        {"email": "metrics@example.com"},
        {
            "$inc": {"page_views": 1},
            "$set": {"last_access": datetime.utcnow()},
            "$setOnInsert": {
                "created_at": datetime.utcnow(),
                "type": "metrics"
            }
        },
        upsert=True
    )

    return result
```

## Delete Operations

### delete_one() and delete_many()

```python
def delete_examples():
    """Examples of delete operations"""

    # Delete single document
    result = collection.delete_one({"email": "user.to.delete@example.com"})
    print(f"Deleted {result.deleted_count} document")

    # Delete multiple documents
    result = collection.delete_many({"active": False})
    print(f"Deleted {result.deleted_count} inactive users")

    # Delete with complex filter
    cutoff_date = datetime.utcnow() - timedelta(days=365)
    result = collection.delete_many({
        "last_login": {"$lt": cutoff_date},
        "active": False
    })
    print(f"Deleted {result.deleted_count} old inactive users")

    # Delete all documents (be careful!)
    # result = collection.delete_many({})

    return result

def safe_delete_patterns():
    """Safe deletion patterns with verification"""

    def safe_delete_user(email):
        """Safely delete user with verification"""

        # First, find the user to verify it exists
        user = collection.find_one({"email": email})
        if not user:
            print(f"User with email {email} not found")
            return False

        print(f"Found user: {user['name']} ({user['email']})")

        # Confirm deletion (in real app, this might be a UI confirmation)
        confirm = input("Are you sure you want to delete this user? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Deletion cancelled")
            return False

        # Perform deletion
        result = collection.delete_one({"_id": user["_id"]})

        if result.deleted_count > 0:
            print(f"✅ User {email} deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete user {email}")
            return False

    # Usage
    # safe_delete_user("user@example.com")
```

### Soft Delete Pattern

```python
def soft_delete_implementation():
    """Implement soft delete instead of hard delete"""

    def soft_delete_user(email):
        """Mark user as deleted instead of removing"""
        result = collection.update_one(
            {"email": email, "deleted": {"$ne": True}},
            {
                "$set": {
                    "deleted": True,
                    "deleted_at": datetime.utcnow(),
                    "active": False
                }
            }
        )

        if result.modified_count > 0:
            print(f"✅ User {email} soft deleted")
            return True
        else:
            print(f"❌ User {email} not found or already deleted")
            return False

    def restore_user(email):
        """Restore soft-deleted user"""
        result = collection.update_one(
            {"email": email, "deleted": True},
            {
                "$unset": {"deleted": "", "deleted_at": ""},
                "$set": {"active": True, "restored_at": datetime.utcnow()}
            }
        )

        return result.modified_count > 0

    def find_active_users():
        """Find only non-deleted users"""
        return collection.find({"deleted": {"$ne": True}})

    def permanent_delete_old():
        """Permanently delete old soft-deleted records"""
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        result = collection.delete_many({
            "deleted": True,
            "deleted_at": {"$lt": cutoff_date}
        })
        print(f"Permanently deleted {result.deleted_count} old records")
        return result

    # Usage examples
    soft_delete_user("user@example.com")
    active_users = list(find_active_users())
    # restore_user("user@example.com")
    # permanent_delete_old()
```

## Bulk Operations

### Bulk Write Operations

```python
from pymongo import UpdateOne, InsertOne, DeleteOne, ReplaceOne

def bulk_operations_example():
    """Perform multiple operations in a single bulk write"""

    operations = [
        # Insert new users
        InsertOne({
            "name": "Alice Johnson",
            "email": "alice.j@example.com",
            "department": "Marketing"
        }),
        InsertOne({
            "name": "Bob Wilson",
            "email": "bob.w@example.com",
            "department": "Sales"
        }),

        # Update existing users
        UpdateOne(
            {"email": "john@example.com"},
            {"$set": {"last_login": datetime.utcnow()}}
        ),
        UpdateOne(
            {"department": "Engineering"},
            {"$inc": {"project_count": 1}},
        ),

        # Replace a document
        ReplaceOne(
            {"email": "old.user@example.com"},
            {
                "name": "Updated User",
                "email": "old.user@example.com",
                "status": "migrated",
                "updated_at": datetime.utcnow()
            }
        ),

        # Delete inactive users
        DeleteOne({"active": False, "last_login": {"$lt": datetime(2022, 1, 1)}})
    ]

    try:
        result = collection.bulk_write(operations, ordered=False)

        print("Bulk operation results:")
        print(f"  Inserted: {result.inserted_count}")
        print(f"  Matched: {result.matched_count}")
        print(f"  Modified: {result.modified_count}")
        print(f"  Deleted: {result.deleted_count}")
        print(f"  Upserted: {result.upserted_count}")

        return result

    except Exception as e:
        print(f"Bulk operation error: {e}")
        raise

def batch_upsert_users(user_data_list):
    """Efficiently upsert multiple users"""
    operations = []

    for user_data in user_data_list:
        operation = UpdateOne(
            {"email": user_data["email"]},  # Filter
            {
                "$set": {
                    **user_data,
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow(),
                    "login_count": 0
                }
            },
            upsert=True
        )
        operations.append(operation)

    if operations:
        result = collection.bulk_write(operations, ordered=False)
        print(f"Upserted {result.upserted_count + result.modified_count} users")
        return result

# Usage
users_to_upsert = [
    {"name": "User 1", "email": "user1@example.com", "department": "IT"},
    {"name": "User 2", "email": "user2@example.com", "department": "HR"},
    {"name": "User 3", "email": "user3@example.com", "department": "Finance"}
]

batch_upsert_users(users_to_upsert)
```

### Ordered vs Unordered Operations

```python
def ordered_vs_unordered_example():
    """Compare ordered and unordered bulk operations"""

    # Sample operations with one that will fail
    operations = [
        InsertOne({"_id": 1, "name": "User 1"}),
        InsertOne({"_id": 2, "name": "User 2"}),
        InsertOne({"_id": 1, "name": "Duplicate"}),  # This will fail
        InsertOne({"_id": 3, "name": "User 3"}),
        InsertOne({"_id": 4, "name": "User 4"})
    ]

    print("Testing ordered operations:")
    try:
        result = collection.bulk_write(operations, ordered=True)
        print(f"Ordered - Inserted: {result.inserted_count}")
    except Exception as e:
        print(f"Ordered operation stopped at error: {e}")

    # Clear collection
    collection.delete_many({})

    print("\nTesting unordered operations:")
    try:
        result = collection.bulk_write(operations, ordered=False)
        print(f"Unordered - Inserted: {result.inserted_count}")
    except Exception as e:
        print(f"Unordered operation completed with errors: {e}")

    # Check what was actually inserted
    inserted_docs = list(collection.find({}, {"_id": 1, "name": 1}))
    print(f"Actually inserted: {inserted_docs}")
```

## Advanced Patterns

### find_one_and_update() - Atomic Operations

```python
def atomic_operations_example():
    """Examples of atomic find and modify operations"""

    # Get and update user's login count atomically
    updated_user = collection.find_one_and_update(
        {"email": "john@example.com"},
        {
            "$inc": {"login_count": 1},
            "$set": {"last_login": datetime.utcnow()}
        },
        return_document=True  # Return updated document
    )

    if updated_user:
        print(f"User {updated_user['name']} login count: {updated_user['login_count']}")

    # Get original document before update
    original_user = collection.find_one_and_update(
        {"email": "john@example.com"},
        {"$set": {"status": "inactive"}},
        return_document=False  # Return original document
    )

    # Find and update with upsert
    user = collection.find_one_and_update(
        {"email": "new.atomic@example.com"},
        {
            "$set": {"name": "Atomic User", "active": True},
            "$setOnInsert": {"created_at": datetime.utcnow()}
        },
        upsert=True,
        return_document=True
    )

    return updated_user

def find_one_and_delete_example():
    """Atomic find and delete operations"""

    # Remove and return the deleted document
    deleted_user = collection.find_one_and_delete(
        {"email": "user.to.remove@example.com"}
    )

    if deleted_user:
        print(f"Deleted user: {deleted_user['name']}")
        # Could log the deleted user for audit purposes
        audit_collection = db.audit_log
        audit_collection.insert_one({
            "action": "user_deleted",
            "deleted_user": deleted_user,
            "timestamp": datetime.utcnow()
        })

    return deleted_user

def counter_pattern():
    """Implement atomic counter using find_one_and_update"""

    def get_next_sequence_number(sequence_name):
        """Get next sequence number atomically"""
        counter = collection.find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"sequence": 1}},
            upsert=True,
            return_document=True
        )
        return counter["sequence"]

    # Usage
    next_user_id = get_next_sequence_number("user_id")
    next_order_id = get_next_sequence_number("order_id")

    print(f"Next user ID: {next_user_id}")
    print(f"Next order ID: {next_order_id}")
```

### Optimistic Locking Pattern

```python
def optimistic_locking_example():
    """Implement optimistic locking using version numbers"""

    def update_user_with_version(email, updates):
        """Update user with optimistic locking"""

        # Get current document with version
        current_user = collection.find_one({"email": email})
        if not current_user:
            raise ValueError("User not found")

        current_version = current_user.get("version", 0)

        # Attempt update with version check
        result = collection.update_one(
            {
                "email": email,
                "version": current_version  # Only update if version matches
            },
            {
                "$set": {
                    **updates,
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"version": 1}  # Increment version
            }
        )

        if result.modified_count == 0:
            # Version mismatch - document was modified by another process
            raise ValueError("Document was modified by another process. Please retry.")

        return result

    # Usage
    try:
        update_user_with_version(
            "john@example.com",
            {"name": "John Updated", "age": 31}
        )
        print("✅ User updated successfully")
    except ValueError as e:
        print(f"❌ Update failed: {e}")
```

## Error Handling

### Comprehensive Error Handling

```python
from pymongo.errors import (
    DuplicateKeyError,
    WriteError,
    WriteConcernError,
    BulkWriteError,
    ConnectionFailure,
    ServerSelectionTimeoutError
)

def robust_crud_operations():
    """CRUD operations with comprehensive error handling"""

    def safe_insert_user(user_data):
        """Insert user with error handling"""
        try:
            result = collection.insert_one(user_data)
            print(f"✅ User inserted with ID: {result.inserted_id}")
            return result.inserted_id

        except DuplicateKeyError as e:
            print(f"❌ Duplicate key error: {e.details}")
            return None

        except WriteError as e:
            print(f"❌ Write error: {e.details}")
            return None

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

    def safe_update_user(filter_dict, update_dict):
        """Update user with error handling"""
        try:
            result = collection.update_one(filter_dict, update_dict)

            if result.matched_count == 0:
                print("⚠ No documents matched the filter")
            elif result.modified_count == 0:
                print("⚠ Document found but no changes made")
            else:
                print(f"✅ Updated {result.modified_count} document(s)")

            return result

        except WriteError as e:
            print(f"❌ Update error: {e.details}")
            return None

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

    def safe_bulk_operations(operations):
        """Bulk operations with error handling"""
        try:
            result = collection.bulk_write(operations, ordered=False)
            print("✅ Bulk operation completed successfully")
            return result

        except BulkWriteError as e:
            print(f"⚠ Bulk operation completed with errors:")
            for error in e.details['writeErrors']:
                print(f"  Error: {error['errmsg']}")

            # Still return successful operations count
            return e.details

        except Exception as e:
            print(f"❌ Bulk operation failed: {e}")
            raise

# Usage examples
safe_insert_user({"name": "Safe User", "email": "safe@example.com"})
safe_update_user({"email": "safe@example.com"}, {"$set": {"updated": True}})
```

### Retry Logic for Transient Errors

```python
import time
import random
from functools import wraps

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """Decorator to retry operations on transient failures"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)

                except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                    retries += 1
                    if retries >= max_retries:
                        print(f"❌ Max retries ({max_retries}) reached. Giving up.")
                        raise

                    wait_time = delay * (backoff ** (retries - 1)) + random.uniform(0, 1)
                    print(f"⚠ Attempt {retries} failed: {e}. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)

                except Exception as e:
                    # Don't retry on non-transient errors
                    print(f"❌ Non-retryable error: {e}")
                    raise

            return None
        return wrapper
    return decorator

# Usage
@retry_on_failure(max_retries=3, delay=1, backoff=2)
def resilient_find_user(email):
    """Find user with automatic retry on connection failures"""
    return collection.find_one({"email": email})

@retry_on_failure(max_retries=5, delay=0.5, backoff=1.5)
def resilient_insert_user(user_data):
    """Insert user with automatic retry"""
    return collection.insert_one(user_data)

# Usage
user = resilient_find_user("john@example.com")
```

## Performance Optimization

### Efficient Query Patterns

```python
def performance_optimized_operations():
    """Examples of performance-optimized CRUD operations"""

    # Use projection to reduce network transfer
    def get_user_summary():
        """Get user summary with minimal data transfer"""
        return list(collection.find(
            {"active": True},
            {"name": 1, "email": 1, "last_login": 1, "_id": 0}
        ))

    # Use limit to prevent large result sets
    def get_recent_users(limit=100):
        """Get recent users with limit"""
        return list(collection.find()
                   .sort("created_at", -1)
                   .limit(limit))

    # Use hint to force specific index usage
    def find_users_with_hint():
        """Find users using specific index"""
        return list(collection.find({"department": "Engineering"})
                   .hint([("department", 1), ("created_at", -1)]))

    # Batch processing for large datasets
    def process_all_users_batched(batch_size=1000):
        """Process all users in batches"""
        cursor = collection.find({}).batch_size(batch_size)

        processed_count = 0
        for user in cursor:
            # Process each user
            processed_count += 1

            if processed_count % batch_size == 0:
                print(f"Processed {processed_count} users...")

        print(f"Total processed: {processed_count} users")

    # Use explain to analyze query performance
    def analyze_query_performance():
        """Analyze query performance"""
        explain_result = collection.find({"department": "Engineering"}).explain()

        execution_stats = explain_result.get('executionStats', {})
        print(f"Execution time: {execution_stats.get('executionTimeMillis', 0)}ms")
        print(f"Documents examined: {execution_stats.get('totalDocsExamined', 0)}")
        print(f"Documents returned: {execution_stats.get('totalDocsReturned', 0)}")

        return explain_result

# Usage
user_summaries = performance_optimized_operations()
```

### Bulk Operations for Better Performance

```python
def performance_bulk_patterns():
    """Performance-optimized bulk operation patterns"""

    def batch_insert_users(users, batch_size=1000):
        """Insert users in batches for better performance"""
        total_inserted = 0

        for i in range(0, len(users), batch_size):
            batch = users[i:i + batch_size]

            try:
                result = collection.insert_many(batch, ordered=False)
                total_inserted += len(result.inserted_ids)
                print(f"Inserted batch {i // batch_size + 1}: {len(result.inserted_ids)} users")

            except Exception as e:
                print(f"Error in batch {i // batch_size + 1}: {e}")

        print(f"Total inserted: {total_inserted} users")
        return total_inserted

    def batch_update_users(updates, batch_size=500):
        """Perform updates in batches"""
        operations = []

        for update_data in updates:
            operation = UpdateOne(
                update_data["filter"],
                update_data["update"]
            )
            operations.append(operation)

            # Execute batch when it reaches batch_size
            if len(operations) >= batch_size:
                result = collection.bulk_write(operations, ordered=False)
                print(f"Batch update: {result.modified_count} documents modified")
                operations = []

        # Execute remaining operations
        if operations:
            result = collection.bulk_write(operations, ordered=False)
            print(f"Final batch: {result.modified_count} documents modified")

# Usage
sample_users = [{"name": f"User {i}", "email": f"user{i}@example.com"}
                for i in range(10000)]
batch_insert_users(sample_users, batch_size=1000)
```

## Best Practices

### General CRUD Best Practices

```python
def crud_best_practices():
    """Demonstrate CRUD best practices"""

    # 1. Always use proper error handling
    def best_practice_insert(document):
        """Insert with proper error handling and validation"""
        try:
            # Validate document before insertion
            if not document.get('email'):
                raise ValueError("Email is required")

            # Add timestamps
            document.update({
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })

            result = collection.insert_one(document)
            return result.inserted_id

        except (DuplicateKeyError, WriteError) as e:
            print(f"Database error: {e}")
            raise
        except ValueError as e:
            print(f"Validation error: {e}")
            raise

    # 2. Use transactions for multi-document operations
    def best_practice_multi_operation():
        """Multi-document operation with transaction"""
        with client.start_session() as session:
            with session.start_transaction():
                try:
                    # Multiple operations that should succeed or fail together
                    collection.update_one(
                        {"_id": ObjectId("507f1f77bcf86cd799439011")},
                        {"$inc": {"balance": -100}},
                        session=session
                    )

                    collection.update_one(
                        {"_id": ObjectId("507f1f77bcf86cd799439012")},
                        {"$inc": {"balance": 100}},
                        session=session
                    )

                    # If we reach here, commit the transaction
                    print("✅ Transaction completed successfully")

                except Exception as e:
                    print(f"❌ Transaction failed: {e}")
                    raise  # This will abort the transaction

    # 3. Use appropriate write concerns
    def best_practice_write_concern():
        """Use appropriate write concern for reliability"""

        # For critical data, use majority write concern
        critical_result = collection.insert_one(
            {"type": "critical", "data": "important"},
            write_concern={"w": "majority", "wtimeout": 5000}
        )

        # For non-critical data, use default write concern
        regular_result = collection.insert_one(
            {"type": "regular", "data": "normal"}
        )

        return critical_result, regular_result

    # 4. Always close cursors and connections properly
    def best_practice_resource_management():
        """Proper resource management"""

        # Use context manager for connections
        with MongoClient('mongodb://localhost:27017/') as client:
            db = client.myapp
            collection = db.users

            # Use cursor properly
            cursor = collection.find({"active": True})
            try:
                for document in cursor:
                    # Process document
                    pass
            finally:
                cursor.close()

    # 5. Use indexes for better performance
    def ensure_indexes():
        """Ensure proper indexes exist"""

        # Create indexes for common query patterns
        collection.create_index("email", unique=True)
        collection.create_index([("department", 1), ("created_at", -1)])
        collection.create_index("last_login")

        # Create text index for search functionality
        collection.create_index([("name", "text"), ("bio", "text")])

        print("✅ Indexes created/verified")

# Usage
crud_best_practices()
```

### Performance Monitoring

```python
def crud_performance_monitoring():
    """Monitor CRUD operation performance"""

    import time
    from functools import wraps

    def monitor_performance(operation_name):
        """Decorator to monitor operation performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    print(f"✅ {operation_name} completed in {duration:.3f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    print(f"❌ {operation_name} failed in {duration:.3f}s: {e}")
                    raise
            return wrapper
        return decorator

    @monitor_performance("User Creation")
    def monitored_create_user(user_data):
        return collection.insert_one(user_data)

    @monitor_performance("User Query")
    def monitored_find_users(query):
        return list(collection.find(query))

    @monitor_performance("User Update")
    def monitored_update_user(filter_dict, update_dict):
        return collection.update_one(filter_dict, update_dict)

    # Usage
    new_user_id = monitored_create_user({"name": "Monitored User", "email": "monitored@example.com"})
    users = monitored_find_users({"name": "Monitored User"})
    update_result = monitored_update_user({"_id": new_user_id}, {"$set": {"updated": True}})

# Usage
crud_performance_monitoring()
```

## Next Steps

After mastering CRUD operations:

1. **Advanced Queries**: [Query Operators](./07_query_operators.md)
2. **Aggregation**: [Aggregation Framework](../advanced/01_aggregation_framework.md)
3. **Indexing**: [Indexing with PyMongo](../advanced/02_indexing.md)
4. **Transactions**: [Transactions](../advanced/03_transactions.md)

## Additional Resources

- [PyMongo CRUD Documentation](https://pymongo.readthedocs.io/en/stable/tutorial.html)
- [MongoDB CRUD Operations](https://docs.mongodb.com/manual/crud/)
- [Write Concern](https://docs.mongodb.com/manual/reference/write-concern/)
- [Bulk Write Operations](https://docs.mongodb.com/manual/core/bulk-write-operations/)
