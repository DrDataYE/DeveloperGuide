# PyMongo Database and Collection Operations

This comprehensive guide covers all database and collection management operations in PyMongo, including creation, configuration, administration, and advanced operations.

## Table of Contents

1. [Database Operations](#database-operations)
2. [Collection Operations](#collection-operations)
3. [Database Administration](#database-administration)
4. [Collection Management](#collection-management)
5. [Indexing Operations](#indexing-operations)
6. [Statistics and Monitoring](#statistics-and-monitoring)
7. [Backup and Restore](#backup-and-restore)
8. [Performance Optimization](#performance-optimization)
9. [Best Practices](#best-practices)

## Database Operations

### Database Connection and Selection

```python
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from datetime import datetime
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')

def database_operations_examples():
    """Examples of database operations"""

    # List all databases
    def list_databases():
        """List all databases on the server"""
        try:
            db_list = client.list_database_names()
            print("Available databases:")
            for db_name in db_list:
                print(f"  - {db_name}")

            # Get detailed database information
            db_info = client.list_databases()
            print("\nDetailed database information:")
            for db in db_info:
                print(f"  {db['name']}: {db.get('sizeOnDisk', 0)} bytes")

            return db_list
        except Exception as e:
            print(f"Error listing databases: {e}")
            return []

    # Select and create databases
    def database_selection():
        """Database selection and creation examples"""

        # Select a database (creates it when first document is inserted)
        myapp_db = client.myapp

        # Alternative syntax
        myapp_db_alt = client['myapp']

        # Database with special characters in name
        special_db = client['my-app-2024']

        # Check if database exists
        if 'myapp' in client.list_database_names():
            print("Database 'myapp' exists")
        else:
            print("Database 'myapp' does not exist yet")

        # Force database creation by creating a collection
        test_collection = myapp_db.test_collection
        test_collection.insert_one({"message": "Database created"})

        print(f"Database created: {'myapp' in client.list_database_names()}")

        return myapp_db

    # Database information
    def get_database_info(db):
        """Get detailed information about a database"""

        try:
            # Database stats
            stats = db.command("dbStats")
            print(f"\nDatabase: {db.name}")
            print(f"Collections: {stats.get('collections', 0)}")
            print(f"Data size: {stats.get('dataSize', 0):,} bytes")
            print(f"Storage size: {stats.get('storageSize', 0):,} bytes")
            print(f"Index size: {stats.get('indexSize', 0):,} bytes")
            print(f"Objects: {stats.get('objects', 0):,}")

            # List collections in database
            collections = db.list_collection_names()
            print(f"Collections in {db.name}: {collections}")

            return stats
        except Exception as e:
            print(f"Error getting database info: {e}")
            return {}

    # Execute examples
    db_list = list_databases()
    myapp_db = database_selection()
    db_stats = get_database_info(myapp_db)

    return db_list, myapp_db, db_stats

# Example usage
db_operations = database_operations_examples()
```

### Database Commands

```python
def database_commands():
    """Examples of database administrative commands"""

    db = client.myapp

    # Server status
    def get_server_status():
        """Get MongoDB server status"""
        try:
            status = db.command("serverStatus")

            print("=== Server Status ===")
            print(f"Host: {status.get('host', 'unknown')}")
            print(f"Version: {status.get('version', 'unknown')}")
            print(f"Uptime: {status.get('uptime', 0)} seconds")
            print(f"Current connections: {status.get('connections', {}).get('current', 0)}")
            print(f"Available connections: {status.get('connections', {}).get('available', 0)}")

            # Memory information
            mem_info = status.get('mem', {})
            print(f"Resident memory: {mem_info.get('resident', 0)} MB")
            print(f"Virtual memory: {mem_info.get('virtual', 0)} MB")

            return status
        except Exception as e:
            print(f"Error getting server status: {e}")
            return {}

    # Database operations
    def database_admin_operations():
        """Administrative database operations"""

        try:
            # Drop database (be careful!)
            # db.command("dropDatabase")

            # Repair database (rarely needed in modern MongoDB)
            # db.command("repairDatabase")

            # Get database profiling level
            profile_level = db.command("profile", -1)
            print(f"Current profiling level: {profile_level.get('was', 0)}")

            # Set profiling level (0=off, 1=slow ops, 2=all ops)
            # db.command("profile", 1, slowms=100)

            # Get current operations
            current_ops = db.command("currentOp")
            active_ops = current_ops.get('inprog', [])
            print(f"Active operations: {len(active_ops)}")

            return profile_level, current_ops

        except Exception as e:
            print(f"Error in admin operations: {e}")
            return {}, {}

    # User management
    def user_management():
        """User management operations"""

        try:
            # Create user (requires admin privileges)
            # db.command("createUser", "appuser",
            #           pwd="password123",
            #           roles=[{"role": "readWrite", "db": "myapp"}])

            # List users
            try:
                users_info = db.command("usersInfo")
                users = users_info.get('users', [])
                print(f"Database users: {len(users)}")
                for user in users:
                    print(f"  - {user.get('user', 'unknown')}")
            except OperationFailure:
                print("No permission to list users or no users exist")

            # Drop user
            # db.command("dropUser", "appuser")

        except Exception as e:
            print(f"Error in user management: {e}")

    # Execute examples
    server_status = get_server_status()
    admin_ops = database_admin_operations()
    user_management()

    return server_status, admin_ops

# Example usage
db_commands = database_commands()
```

## Collection Operations

### Collection Creation and Configuration

```python
def collection_operations():
    """Examples of collection operations"""

    db = client.myapp

    # Basic collection operations
    def basic_collection_ops():
        """Basic collection creation and access"""

        # Create/access collection
        users_collection = db.users

        # Alternative syntax
        users_alt = db['users']

        # Collection with special characters
        special_collection = db['user-data-2024']

        # List all collections
        collections = db.list_collection_names()
        print(f"Collections in database: {collections}")

        # Check if collection exists
        if 'users' in collections:
            print("Users collection exists")
        else:
            print("Users collection does not exist")

        return users_collection

    # Create collection with options
    def create_collection_with_options():
        """Create collections with specific options"""

        # Capped collection (fixed size)
        try:
            db.create_collection("logs",
                                capped=True,
                                size=1000000,  # 1MB
                                max=1000)      # Max 1000 documents
            print("✅ Capped collection 'logs' created")
        except Exception as e:
            print(f"Capped collection creation: {e}")

        # Collection with validation
        user_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["email", "username"],
                "properties": {
                    "email": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                    },
                    "username": {
                        "bsonType": "string",
                        "minLength": 3,
                        "maxLength": 20
                    }
                }
            }
        }

        try:
            db.create_collection("validated_users",
                                validator=user_validator,
                                validationLevel="strict",
                                validationAction="error")
            print("✅ Validated collection 'validated_users' created")
        except Exception as e:
            print(f"Validated collection creation: {e}")

        # Time series collection (MongoDB 5.0+)
        try:
            db.create_collection("metrics",
                                timeseries={
                                    "timeField": "timestamp",
                                    "metaField": "metadata",
                                    "granularity": "seconds"
                                })
            print("✅ Time series collection 'metrics' created")
        except Exception as e:
            print(f"Time series collection creation: {e}")

    # Collection information
    def get_collection_info():
        """Get information about collections"""

        # List collections with details
        collections_info = db.list_collections()

        print("\n=== Collection Information ===")
        for collection_info in collections_info:
            name = collection_info['name']
            coll_type = collection_info.get('type', 'collection')

            print(f"\nCollection: {name}")
            print(f"Type: {coll_type}")

            # Get collection stats
            try:
                stats = db.command("collStats", name)
                print(f"  Documents: {stats.get('count', 0):,}")
                print(f"  Data size: {stats.get('size', 0):,} bytes")
                print(f"  Storage size: {stats.get('storageSize', 0):,} bytes")
                print(f"  Index count: {stats.get('nindexes', 0)}")
                print(f"  Index size: {stats.get('totalIndexSize', 0):,} bytes")

                # Capped collection info
                if stats.get('capped', False):
                    print(f"  Capped: Yes")
                    print(f"  Max size: {stats.get('maxSize', 0):,} bytes")
                    print(f"  Max documents: {stats.get('max', 0):,}")

            except Exception as e:
                print(f"  Error getting stats: {e}")

    # Collection modification
    def modify_collection():
        """Modify collection properties"""

        # Modify collection validator
        new_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["email", "username", "status"],
                "properties": {
                    "email": {"bsonType": "string"},
                    "username": {"bsonType": "string"},
                    "status": {"enum": ["active", "inactive", "pending"]}
                }
            }
        }

        try:
            db.command("collMod", "validated_users",
                      validator=new_validator,
                      validationLevel="moderate")
            print("✅ Collection validator updated")
        except Exception as e:
            print(f"Collection modification error: {e}")

    # Execute examples
    users_coll = basic_collection_ops()
    create_collection_with_options()
    get_collection_info()
    modify_collection()

    return users_coll

# Example usage
collection_ops = collection_operations()
```

### Collection Management

```python
def collection_management():
    """Advanced collection management operations"""

    db = client.myapp

    # Rename collection
    def rename_collection():
        """Rename a collection"""

        # Create a test collection first
        test_collection = db.temp_collection
        test_collection.insert_one({"test": "data"})

        try:
            # Rename collection
            db.temp_collection.rename("renamed_collection")
            print("✅ Collection renamed successfully")

            # Verify rename
            collections = db.list_collection_names()
            if "renamed_collection" in collections:
                print("✅ Renamed collection exists")
            if "temp_collection" not in collections:
                print("✅ Original collection no longer exists")

        except Exception as e:
            print(f"Collection rename error: {e}")

    # Drop collection
    def drop_collection():
        """Drop a collection"""

        try:
            # Drop the renamed collection
            db.renamed_collection.drop()
            print("✅ Collection dropped successfully")

            # Verify drop
            collections = db.list_collection_names()
            if "renamed_collection" not in collections:
                print("✅ Collection successfully removed")

        except Exception as e:
            print(f"Collection drop error: {e}")

    # Clone collection
    def clone_collection():
        """Clone a collection (copy structure and data)"""

        source_collection = db.users
        target_collection = db.users_backup

        try:
            # Insert some test data if collection is empty
            if source_collection.count_documents({}) == 0:
                test_users = [
                    {"username": "user1", "email": "user1@example.com"},
                    {"username": "user2", "email": "user2@example.com"}
                ]
                source_collection.insert_many(test_users)

            # Copy data
            cursor = source_collection.find()
            documents = list(cursor)

            if documents:
                target_collection.insert_many(documents)
                print(f"✅ Cloned {len(documents)} documents")

            # Copy indexes (excluding _id index)
            indexes = source_collection.list_indexes()
            for index in indexes:
                if index['name'] != '_id_':
                    # Recreate index on target collection
                    key = list(index['key'].items())
                    target_collection.create_index(key, **{k: v for k, v in index.items()
                                                         if k not in ['key', 'name', 'ns', 'v']})

            print("✅ Collection cloned successfully")

        except Exception as e:
            print(f"Collection clone error: {e}")

    # Collection maintenance
    def collection_maintenance():
        """Collection maintenance operations"""

        collection = db.users

        try:
            # Compact collection (reclaim space)
            # Note: This requires admin privileges and locks the database
            # db.command("compact", "users")

            # Reindex collection
            collection.reindex()
            print("✅ Collection reindexed")

            # Validate collection
            validation_result = db.command("validate", "users")
            if validation_result.get("valid", False):
                print("✅ Collection validation passed")
            else:
                print("❌ Collection validation failed")
                print(f"Errors: {validation_result.get('errors', [])}")

        except Exception as e:
            print(f"Collection maintenance error: {e}")

    # Execute examples
    rename_collection()
    drop_collection()
    clone_collection()
    collection_maintenance()

# Example usage
collection_management()
```

## Database Administration

### User and Role Management

```python
def database_administration():
    """Database administration operations"""

    # Note: Many of these operations require admin privileges

    def user_role_management():
        """User and role management (requires admin privileges)"""

        admin_db = client.admin
        app_db = client.myapp

        try:
            # Create custom role
            role_definition = {
                "role": "appDeveloper",
                "privileges": [
                    {
                        "resource": {"db": "myapp", "collection": ""},
                        "actions": ["find", "insert", "update", "remove"]
                    },
                    {
                        "resource": {"db": "myapp", "collection": "logs"},
                        "actions": ["find", "insert"]
                    }
                ],
                "roles": []
            }

            # admin_db.command("createRole", **role_definition)
            print("Custom role 'appDeveloper' would be created")

            # Create user with custom role
            user_definition = {
                "user": "developer",
                "pwd": "dev_password_123",
                "roles": [
                    {"role": "appDeveloper", "db": "admin"},
                    {"role": "read", "db": "myapp"}
                ]
            }

            # app_db.command("createUser", **user_definition)
            print("User 'developer' would be created")

            # List users
            try:
                users = app_db.command("usersInfo")
                print(f"Users in database: {len(users.get('users', []))}")
            except Exception:
                print("No permission to list users or no users exist")

            # Update user roles
            # app_db.command("grantRolesToUser", "developer",
            #               roles=[{"role": "readWrite", "db": "myapp"}])

        except Exception as e:
            print(f"User/role management error: {e}")

    def security_configuration():
        """Security configuration examples"""

        # Connection with authentication
        def secure_connection_example():
            """Example of secure connection"""

            # Connection with username/password
            # secure_client = MongoClient(
            #     'mongodb://username:password@localhost:27017/myapp?authSource=admin'
            # )

            # Connection with SSL/TLS
            # ssl_client = MongoClient(
            #     'mongodb://localhost:27017/',
            #     ssl=True,
            #     ssl_cert_reqs='CERT_REQUIRED',
            #     ssl_ca_certs='path/to/ca.pem',
            #     ssl_certfile='path/to/client.pem'
            # )

            print("Secure connection examples provided")

        secure_connection_example()

    # Execute examples
    user_role_management()
    security_configuration()

# Example usage
database_administration()
```

### Database Monitoring

```python
def database_monitoring():
    """Database monitoring and diagnostics"""

    db = client.myapp

    def performance_monitoring():
        """Monitor database performance"""

        # Get server status
        try:
            status = db.command("serverStatus")

            # Connection metrics
            connections = status.get('connections', {})
            print("=== Connection Metrics ===")
            print(f"Current: {connections.get('current', 0)}")
            print(f"Available: {connections.get('available', 0)}")
            print(f"Total created: {connections.get('totalCreated', 0)}")

            # Operation counters
            opcounters = status.get('opcounters', {})
            print("\n=== Operation Counters ===")
            print(f"Inserts: {opcounters.get('insert', 0):,}")
            print(f"Queries: {opcounters.get('query', 0):,}")
            print(f"Updates: {opcounters.get('update', 0):,}")
            print(f"Deletes: {opcounters.get('delete', 0):,}")
            print(f"Commands: {opcounters.get('command', 0):,}")

            # Memory usage
            mem = status.get('mem', {})
            print("\n=== Memory Usage ===")
            print(f"Resident: {mem.get('resident', 0)} MB")
            print(f"Virtual: {mem.get('virtual', 0)} MB")
            print(f"Mapped: {mem.get('mapped', 0)} MB")

            # Network metrics
            network = status.get('network', {})
            print("\n=== Network Metrics ===")
            print(f"Bytes in: {network.get('bytesIn', 0):,}")
            print(f"Bytes out: {network.get('bytesOut', 0):,}")
            print(f"Requests: {network.get('numRequests', 0):,}")

        except Exception as e:
            print(f"Error getting server status: {e}")

    def query_performance_monitoring():
        """Monitor query performance"""

        # Enable profiling for slow operations
        try:
            # Set profiling level (1 = slow operations only)
            db.command("profile", 1, slowms=100)
            print("✅ Profiling enabled for operations > 100ms")

            # Get profiling status
            profile_status = db.command("profile", -1)
            print(f"Profiling level: {profile_status.get('was', 0)}")
            print(f"Slow ms threshold: {profile_status.get('slowms', 100)}")

            # Query the profiler collection
            profiler_collection = db.system.profile
            slow_queries = list(profiler_collection.find().limit(5))

            if slow_queries:
                print(f"\n=== Recent Slow Operations ({len(slow_queries)}) ===")
                for query in slow_queries:
                    print(f"Duration: {query.get('millis', 0)}ms")
                    print(f"Operation: {query.get('op', 'unknown')}")
                    print(f"Namespace: {query.get('ns', 'unknown')}")
                    print(f"Timestamp: {query.get('ts', 'unknown')}")
                    print("---")
            else:
                print("No slow operations recorded")

        except Exception as e:
            print(f"Query performance monitoring error: {e}")

    def index_usage_monitoring():
        """Monitor index usage"""

        collections = db.list_collection_names()

        for coll_name in collections:
            if coll_name.startswith('system.'):
                continue

            collection = db[coll_name]

            try:
                # Get index stats
                index_stats = list(collection.aggregate([
                    {"$indexStats": {}}
                ]))

                if index_stats:
                    print(f"\n=== Index Usage for {coll_name} ===")
                    for stat in index_stats:
                        index_name = stat['name']
                        usage = stat.get('accesses', {})
                        print(f"Index: {index_name}")
                        print(f"  Operations: {usage.get('ops', 0):,}")
                        print(f"  Since: {usage.get('since', 'unknown')}")

            except Exception as e:
                print(f"Error getting index stats for {coll_name}: {e}")

    def disk_usage_monitoring():
        """Monitor disk usage"""

        try:
            # Database stats
            db_stats = db.command("dbStats")

            print("\n=== Disk Usage ===")
            print(f"Data size: {db_stats.get('dataSize', 0):,} bytes")
            print(f"Storage size: {db_stats.get('storageSize', 0):,} bytes")
            print(f"Index size: {db_stats.get('indexSize', 0):,} bytes")
            print(f"File size: {db_stats.get('fileSize', 0):,} bytes")

            # Collection-level stats
            collections = db.list_collection_names()
            for coll_name in collections:
                if coll_name.startswith('system.'):
                    continue

                try:
                    coll_stats = db.command("collStats", coll_name)
                    print(f"\n{coll_name}:")
                    print(f"  Documents: {coll_stats.get('count', 0):,}")
                    print(f"  Data size: {coll_stats.get('size', 0):,} bytes")
                    print(f"  Storage size: {coll_stats.get('storageSize', 0):,} bytes")

                except Exception as e:
                    print(f"  Error getting stats: {e}")

        except Exception as e:
            print(f"Disk usage monitoring error: {e}")

    # Execute monitoring
    performance_monitoring()
    query_performance_monitoring()
    index_usage_monitoring()
    disk_usage_monitoring()

# Example usage
database_monitoring()
```

## Indexing Operations

### Index Management

```python
def indexing_operations():
    """Index management operations"""

    collection = client.myapp.products

    # Create sample data for indexing examples
    if collection.count_documents({}) == 0:
        sample_products = [
            {"name": "Laptop", "price": 999.99, "category": "Electronics", "rating": 4.5},
            {"name": "Mouse", "price": 29.99, "category": "Electronics", "rating": 4.0},
            {"name": "Keyboard", "price": 79.99, "category": "Electronics", "rating": 4.2},
            {"name": "Monitor", "price": 299.99, "category": "Electronics", "rating": 4.3}
        ]
        collection.insert_many(sample_products)

    def create_indexes():
        """Create various types of indexes"""

        # Single field index
        collection.create_index("price")
        print("✅ Created index on 'price'")

        # Compound index
        collection.create_index([("category", 1), ("price", -1)])
        print("✅ Created compound index on 'category' (asc) and 'price' (desc)")

        # Text index
        collection.create_index([("name", "text"), ("category", "text")])
        print("✅ Created text index on 'name' and 'category'")

        # Unique index
        try:
            collection.create_index("name", unique=True)
            print("✅ Created unique index on 'name'")
        except Exception as e:
            print(f"Unique index creation failed: {e}")

        # Sparse index (only indexes documents with the field)
        collection.create_index("discount_price", sparse=True)
        print("✅ Created sparse index on 'discount_price'")

        # Partial index (with filter)
        collection.create_index(
            "rating",
            partialFilterExpression={"rating": {"$gte": 4.0}}
        )
        print("✅ Created partial index on 'rating' for ratings >= 4.0")

        # TTL index (time to live)
        collection.create_index("created_at", expireAfterSeconds=3600)  # 1 hour
        print("✅ Created TTL index on 'created_at' (1 hour expiration)")

    def list_indexes():
        """List all indexes on a collection"""

        indexes = list(collection.list_indexes())

        print("\n=== Collection Indexes ===")
        for index in indexes:
            print(f"Name: {index['name']}")
            print(f"Key: {index['key']}")

            # Additional properties
            if 'unique' in index:
                print(f"Unique: {index['unique']}")
            if 'sparse' in index:
                print(f"Sparse: {index['sparse']}")
            if 'partialFilterExpression' in index:
                print(f"Partial filter: {index['partialFilterExpression']}")
            if 'expireAfterSeconds' in index:
                print(f"TTL: {index['expireAfterSeconds']} seconds")

            print("---")

        return indexes

    def analyze_index_usage():
        """Analyze index usage"""

        # Explain query execution
        explain_result = collection.find({"category": "Electronics"}).explain()

        execution_stats = explain_result.get('executionStats', {})
        print("\n=== Query Execution Analysis ===")
        print(f"Execution time: {execution_stats.get('executionTimeMillis', 0)}ms")
        print(f"Documents examined: {execution_stats.get('totalDocsExamined', 0)}")
        print(f"Documents returned: {execution_stats.get('totalDocsReturned', 0)}")
        print(f"Index used: {explain_result.get('queryPlanner', {}).get('winningPlan', {}).get('inputStage', {}).get('indexName', 'none')}")

        # Index statistics
        try:
            index_stats = list(collection.aggregate([{"$indexStats": {}}]))

            print("\n=== Index Usage Statistics ===")
            for stat in index_stats:
                print(f"Index: {stat['name']}")
                accesses = stat.get('accesses', {})
                print(f"  Operations: {accesses.get('ops', 0):,}")
                print(f"  Since: {accesses.get('since', 'unknown')}")
                print("---")

        except Exception as e:
            print(f"Index stats error: {e}")

    def drop_indexes():
        """Drop indexes"""

        # Drop specific index
        try:
            collection.drop_index("price_1")
            print("✅ Dropped index on 'price'")
        except Exception as e:
            print(f"Index drop error: {e}")

        # Drop multiple indexes
        try:
            collection.drop_index([("category", 1), ("price", -1)])
            print("✅ Dropped compound index")
        except Exception as e:
            print(f"Compound index drop error: {e}")

        # Drop all indexes except _id
        # collection.drop_indexes()
        # print("✅ Dropped all indexes except _id")

    # Execute indexing operations
    create_indexes()
    indexes = list_indexes()
    analyze_index_usage()
    # drop_indexes()  # Uncomment to test dropping indexes

    return indexes

# Example usage
indexing_ops = indexing_operations()
```

## Statistics and Monitoring

### Collection Statistics

```python
def statistics_and_monitoring():
    """Comprehensive statistics and monitoring"""

    db = client.myapp

    def collection_statistics():
        """Get detailed collection statistics"""

        collections = db.list_collection_names()

        for coll_name in collections:
            if coll_name.startswith('system.'):
                continue

            try:
                stats = db.command("collStats", coll_name)

                print(f"\n=== {coll_name} Statistics ===")
                print(f"Namespace: {stats.get('ns', 'unknown')}")
                print(f"Count: {stats.get('count', 0):,} documents")
                print(f"Size: {stats.get('size', 0):,} bytes")
                print(f"Storage size: {stats.get('storageSize', 0):,} bytes")
                print(f"Average document size: {stats.get('avgObjSize', 0):,.2f} bytes")

                # Index information
                print(f"Indexes: {stats.get('nindexes', 0)}")
                print(f"Index size: {stats.get('totalIndexSize', 0):,} bytes")

                # Capped collection info
                if stats.get('capped', False):
                    print(f"Capped: Yes")
                    print(f"Max size: {stats.get('maxSize', 0):,} bytes")
                    print(f"Max documents: {stats.get('max', 0):,}")

                # Sharding info (if applicable)
                if 'sharded' in stats:
                    print(f"Sharded: {stats['sharded']}")

            except Exception as e:
                print(f"Error getting stats for {coll_name}: {e}")

    def database_statistics():
        """Get database-level statistics"""

        try:
            db_stats = db.command("dbStats")

            print("\n=== Database Statistics ===")
            print(f"Database: {db_stats.get('db', 'unknown')}")
            print(f"Collections: {db_stats.get('collections', 0)}")
            print(f"Views: {db_stats.get('views', 0)}")
            print(f"Objects: {db_stats.get('objects', 0):,}")
            print(f"Average object size: {db_stats.get('avgObjSize', 0):,.2f} bytes")
            print(f"Data size: {db_stats.get('dataSize', 0):,} bytes")
            print(f"Storage size: {db_stats.get('storageSize', 0):,} bytes")
            print(f"Indexes: {db_stats.get('indexes', 0)}")
            print(f"Index size: {db_stats.get('indexSize', 0):,} bytes")
            print(f"File size: {db_stats.get('fileSize', 0):,} bytes")

        except Exception as e:
            print(f"Database statistics error: {e}")

    def server_statistics():
        """Get server-level statistics"""

        try:
            server_status = db.command("serverStatus")

            print("\n=== Server Statistics ===")
            print(f"Host: {server_status.get('host', 'unknown')}")
            print(f"Version: {server_status.get('version', 'unknown')}")
            print(f"Process: {server_status.get('process', 'unknown')}")
            print(f"Uptime: {server_status.get('uptime', 0)} seconds")
            print(f"Local time: {server_status.get('localTime', 'unknown')}")

            # Global lock information
            global_lock = server_status.get('globalLock', {})
            if global_lock:
                print(f"\nGlobal lock:")
                print(f"  Total time: {global_lock.get('totalTime', 0)} microseconds")
                print(f"  Current queue: {global_lock.get('currentQueue', {})}")
                print(f"  Active clients: {global_lock.get('activeClients', {})}")

            # WiredTiger stats (if using WiredTiger storage engine)
            wt_stats = server_status.get('wiredTiger', {})
            if wt_stats:
                cache = wt_stats.get('cache', {})
                print(f"\nWiredTiger cache:")
                print(f"  Bytes in cache: {cache.get('bytes currently in the cache', 0):,}")
                print(f"  Max bytes configured: {cache.get('maximum bytes configured', 0):,}")
                print(f"  Pages read into cache: {cache.get('pages read into cache', 0):,}")
                print(f"  Pages written from cache: {cache.get('pages written from cache', 0):,}")

        except Exception as e:
            print(f"Server statistics error: {e}")

    def real_time_monitoring():
        """Real-time monitoring examples"""

        # Monitor current operations
        try:
            current_ops = db.command("currentOp", {"$all": True})
            active_ops = [op for op in current_ops.get('inprog', [])
                         if op.get('active', False)]

            print(f"\n=== Current Operations ===")
            print(f"Active operations: {len(active_ops)}")

            for op in active_ops[:5]:  # Show first 5
                print(f"  Operation: {op.get('op', 'unknown')}")
                print(f"  Namespace: {op.get('ns', 'unknown')}")
                print(f"  Duration: {op.get('microsecs_running', 0) / 1000000:.2f} seconds")
                print(f"  Client: {op.get('client', 'unknown')}")
                print("  ---")

        except Exception as e:
            print(f"Current operations error: {e}")

        # Monitor replica set status (if applicable)
        try:
            rs_status = db.command("replSetGetStatus")
            print(f"\nReplica set: {rs_status.get('set', 'not configured')}")
            print(f"Members: {len(rs_status.get('members', []))}")

        except Exception:
            print("\nNot running as replica set")

    # Execute monitoring
    collection_statistics()
    database_statistics()
    server_statistics()
    real_time_monitoring()

# Example usage
statistics_and_monitoring()
```

## Performance Optimization

### Query and Index Optimization

```python
def performance_optimization():
    """Performance optimization techniques"""

    collection = client.myapp.large_collection

    # Create sample data for performance testing
    def create_test_data():
        """Create test data for performance optimization"""

        if collection.count_documents({}) == 0:
            import random

            print("Creating test data...")
            test_data = []
            categories = ["Electronics", "Books", "Clothing", "Home", "Sports"]

            for i in range(10000):
                doc = {
                    "item_id": f"ITEM_{i:06d}",
                    "name": f"Product {i}",
                    "category": random.choice(categories),
                    "price": round(random.uniform(10, 1000), 2),
                    "rating": round(random.uniform(1, 5), 1),
                    "in_stock": random.choice([True, False]),
                    "created_at": datetime.utcnow(),
                    "tags": random.sample(["new", "popular", "sale", "featured", "limited"],
                                        random.randint(1, 3))
                }
                test_data.append(doc)

                # Insert in batches
                if len(test_data) >= 1000:
                    collection.insert_many(test_data)
                    test_data = []
                    print(f"Inserted {i + 1} documents...")

            if test_data:
                collection.insert_many(test_data)

            print(f"✅ Created {collection.count_documents({}):,} test documents")

    def optimize_queries():
        """Query optimization techniques"""

        import time

        # Test query without index
        start_time = time.time()
        result1 = list(collection.find({"category": "Electronics", "price": {"$gte": 100}}))
        time_without_index = time.time() - start_time

        print(f"Query without index: {time_without_index:.3f}s ({len(result1)} results)")

        # Create compound index
        collection.create_index([("category", 1), ("price", 1)])

        # Test same query with index
        start_time = time.time()
        result2 = list(collection.find({"category": "Electronics", "price": {"$gte": 100}}))
        time_with_index = time.time() - start_time

        print(f"Query with index: {time_with_index:.3f}s ({len(result2)} results)")
        print(f"Performance improvement: {time_without_index / time_with_index:.1f}x faster")

        # Use explain to analyze query performance
        explain_result = collection.find({"category": "Electronics", "price": {"$gte": 100}}).explain()

        execution_stats = explain_result.get('executionStats', {})
        print(f"\nQuery execution analysis:")
        print(f"  Execution time: {execution_stats.get('executionTimeMillis', 0)}ms")
        print(f"  Documents examined: {execution_stats.get('totalDocsExamined', 0):,}")
        print(f"  Documents returned: {execution_stats.get('totalDocsReturned', 0):,}")

        index_used = explain_result.get('queryPlanner', {}).get('winningPlan', {}).get('inputStage', {}).get('indexName')
        print(f"  Index used: {index_used or 'COLLECTION SCAN'}")

    def optimize_projections():
        """Projection optimization"""

        import time

        # Query with all fields
        start_time = time.time()
        all_fields = list(collection.find({"category": "Electronics"}).limit(1000))
        time_all_fields = time.time() - start_time

        # Query with projection (only needed fields)
        start_time = time.time()
        projected = list(collection.find(
            {"category": "Electronics"},
            {"name": 1, "price": 1, "rating": 1, "_id": 0}
        ).limit(1000))
        time_projected = time.time() - start_time

        print(f"\nProjection optimization:")
        print(f"  All fields: {time_all_fields:.3f}s")
        print(f"  Projected fields: {time_projected:.3f}s")
        print(f"  Improvement: {time_all_fields / time_projected:.1f}x faster")

        # Calculate data transfer reduction
        import sys
        all_fields_size = sum(sys.getsizeof(str(doc)) for doc in all_fields[:100])
        projected_size = sum(sys.getsizeof(str(doc)) for doc in projected[:100])

        print(f"  Data transfer reduction: {(1 - projected_size/all_fields_size)*100:.1f}%")

    def optimize_aggregation():
        """Aggregation optimization"""

        import time

        # Create index for aggregation
        collection.create_index([("category", 1), ("rating", -1)])

        # Optimized aggregation pipeline
        pipeline = [
            {"$match": {"category": "Electronics", "in_stock": True}},  # Filter early
            {"$sort": {"rating": -1}},  # Use index for sorting
            {"$limit": 100},  # Limit early
            {"$project": {  # Project only needed fields
                "name": 1,
                "price": 1,
                "rating": 1,
                "_id": 0
            }}
        ]

        start_time = time.time()
        results = list(collection.aggregate(pipeline))
        execution_time = time.time() - start_time

        print(f"\nAggregation optimization:")
        print(f"  Execution time: {execution_time:.3f}s")
        print(f"  Results: {len(results)}")

        # Explain aggregation
        explain_result = collection.aggregate(pipeline, explain=True)
        print(f"  Pipeline stages: {len(pipeline)}")

    def optimize_bulk_operations():
        """Bulk operation optimization"""

        import time

        # Prepare bulk operations
        bulk_ops = []
        for i in range(1000):
            bulk_ops.append({
                "updateOne": {
                    "filter": {"item_id": f"ITEM_{i:06d}"},
                    "update": {"$set": {"last_updated": datetime.utcnow()}},
                    "upsert": False
                }
            })

        # Individual updates (slow)
        start_time = time.time()
        for i in range(100):  # Test with smaller subset
            collection.update_one(
                {"item_id": f"ITEM_{i:06d}"},
                {"$set": {"last_updated": datetime.utcnow()}}
            )
        individual_time = time.time() - start_time

        # Bulk updates (fast)
        start_time = time.time()
        from pymongo import UpdateOne
        bulk_operations = [
            UpdateOne(
                {"item_id": f"ITEM_{i:06d}"},
                {"$set": {"last_updated": datetime.utcnow()}}
            ) for i in range(100, 200)
        ]
        collection.bulk_write(bulk_operations, ordered=False)
        bulk_time = time.time() - start_time

        print(f"\nBulk operation optimization:")
        print(f"  Individual updates (100): {individual_time:.3f}s")
        print(f"  Bulk updates (100): {bulk_time:.3f}s")
        print(f"  Improvement: {individual_time / bulk_time:.1f}x faster")

    # Execute optimization tests
    create_test_data()
    optimize_queries()
    optimize_projections()
    optimize_aggregation()
    optimize_bulk_operations()

# Example usage
performance_optimization()
```

## Best Practices

### Database and Collection Best Practices

```python
def best_practices():
    """Database and collection best practices"""

    def naming_conventions():
        """Database and collection naming best practices"""

        print("=== Naming Conventions ===")
        print("✅ Good database names:")
        print("  - myapp, user_data, analytics_db")
        print("  - Use lowercase with underscores")
        print("  - Be descriptive but concise")

        print("\n❌ Avoid:")
        print("  - Special characters: my-app!, test@db")
        print("  - Spaces: 'my app database'")
        print("  - Starting with numbers: 2024_data")

        print("\n✅ Good collection names:")
        print("  - users, blog_posts, order_items")
        print("  - Use plural nouns")
        print("  - Descriptive and consistent")

        print("\n❌ Avoid:")
        print("  - Mixed case: UserData, blogPosts")
        print("  - Generic names: data, info, stuff")

    def connection_management():
        """Connection management best practices"""

        print("\n=== Connection Management ===")

        # Use connection pooling
        good_client = MongoClient(
            'mongodb://localhost:27017/',
            maxPoolSize=50,  # Maximum connections in pool
            minPoolSize=5,   # Minimum connections to maintain
            maxIdleTimeMS=30000,  # Close connections after 30s idle
            waitQueueTimeoutMS=5000,  # Wait max 5s for available connection
            serverSelectionTimeoutMS=5000,  # Server selection timeout
            connectTimeoutMS=10000,  # Connection timeout
            socketTimeoutMS=20000,   # Socket timeout
        )

        print("✅ Connection pool configured with appropriate timeouts")

        # Use context managers for operations
        def safe_database_operation():
            """Example of safe database operations"""
            try:
                with good_client.start_session() as session:
                    # Perform operations within session
                    db = good_client.myapp
                    collection = db.users

                    # Operations here benefit from session management
                    result = collection.find_one({"username": "test"}, session=session)
                    return result

            except Exception as e:
                print(f"Database operation error: {e}")
                return None

        return safe_database_operation

    def error_handling_patterns():
        """Error handling best practices"""

        print("\n=== Error Handling Patterns ===")

        from pymongo.errors import (
            ConnectionFailure, ServerSelectionTimeoutError,
            DuplicateKeyError, WriteError, WriteConcernError
        )

        def robust_database_operation(collection, document):
            """Robust database operation with proper error handling"""

            try:
                # Attempt the operation
                result = collection.insert_one(document)
                print(f"✅ Document inserted: {result.inserted_id}")
                return result.inserted_id

            except DuplicateKeyError as e:
                print(f"❌ Duplicate key error: {e.details}")
                # Handle duplicate key (maybe update instead)
                return None

            except WriteError as e:
                print(f"❌ Write error: {e.details}")
                # Handle validation errors, etc.
                return None

            except ConnectionFailure as e:
                print(f"❌ Connection failed: {e}")
                # Implement retry logic or fallback
                return None

            except ServerSelectionTimeoutError as e:
                print(f"❌ Server selection timeout: {e}")
                # Handle server unavailability
                return None

            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                # Log and handle unexpected errors
                raise

        return robust_database_operation

    def performance_best_practices():
        """Performance optimization best practices"""

        print("\n=== Performance Best Practices ===")

        # Index strategy
        def index_strategy_example():
            """Example of good indexing strategy"""

            collection = client.myapp.optimized_collection

            # Create indexes based on query patterns

            # 1. Single field indexes for exact matches
            collection.create_index("user_id")
            collection.create_index("status")

            # 2. Compound indexes for multi-field queries
            # Order matters: most selective field first
            collection.create_index([("status", 1), ("created_at", -1)])
            collection.create_index([("user_id", 1), ("category", 1), ("priority", -1)])

            # 3. Partial indexes for subset queries
            collection.create_index(
                "premium_feature",
                partialFilterExpression={"account_type": "premium"}
            )

            # 4. Sparse indexes for optional fields
            collection.create_index("phone_number", sparse=True)

            print("✅ Indexes created based on query patterns")

        # Query optimization
        def query_optimization_example():
            """Example of optimized queries"""

            collection = client.myapp.optimized_collection

            # Use projection to limit data transfer
            optimized_query = collection.find(
                {"status": "active", "user_id": {"$in": ["user1", "user2"]}},
                {"name": 1, "email": 1, "last_login": 1, "_id": 0}
            ).limit(100)

            # Use hint for complex queries if needed
            forced_index_query = collection.find(
                {"status": "active", "created_at": {"$gte": datetime.utcnow()}}
            ).hint([("status", 1), ("created_at", -1)])

            print("✅ Queries optimized with projections and limits")

        index_strategy_example()
        query_optimization_example()

    def security_best_practices():
        """Security best practices"""

        print("\n=== Security Best Practices ===")

        # 1. Authentication and authorization
        print("✅ Always use authentication in production")
        print("✅ Create specific users with minimal required permissions")
        print("✅ Use role-based access control")

        # 2. Network security
        print("✅ Use SSL/TLS for connections")
        print("✅ Restrict network access with firewalls")
        print("✅ Use VPN or private networks when possible")

        # 3. Data validation
        print("✅ Implement schema validation")
        print("✅ Validate input on application level")
        print("✅ Use parameterized queries (PyMongo does this automatically)")

        # Example of secure connection
        def secure_connection_example():
            """Example of secure connection configuration"""

            # SSL/TLS connection
            secure_client = MongoClient(
                'mongodb://username:password@hostname:27017/database_name',
                ssl=True,
                ssl_cert_reqs='CERT_REQUIRED',
                ssl_ca_certs='/path/to/ca.pem',
                authSource='admin',
                authMechanism='SCRAM-SHA-256'
            )

            print("✅ Secure connection configured")
            return secure_client

        return secure_connection_example

    # Execute best practices examples
    naming_conventions()
    safe_op = connection_management()
    robust_op = error_handling_patterns()
    performance_best_practices()
    secure_conn = security_best_practices()

    return {
        "safe_operation": safe_op,
        "robust_operation": robust_op,
        "secure_connection": secure_conn
    }

# Example usage
best_practices_examples = best_practices()
```

## Next Steps

After mastering database and collection operations:

1. **CRUD Operations**: [CRUD Operations Guide](./04_crud_operations.md)
2. **Query Operators**: [Query Operators Guide](./05_query_operators.md)
3. **Data Modeling**: [Data Modeling Guide](./06_data_modeling.md)
4. **Advanced Features**: [Advanced PyMongo Features](../advanced/)

## Additional Resources

- [PyMongo Database Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/database.html)
- [PyMongo Collection Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html)
- [MongoDB Database Commands](https://docs.mongodb.com/manual/reference/command/)
- [MongoDB Administration](https://docs.mongodb.com/manual/administration/)
