# PyMongo Bulk Operations

A concise guide for high-performance bulk operations in PyMongo.

## Bulk Operations Basics

```python
from pymongo import MongoClient, InsertOne, UpdateOne, UpdateMany, DeleteOne, DeleteMany, ReplaceOne
from pymongo.errors import BulkWriteError
import time
from datetime import datetime

# Connection
client = MongoClient('mongodb://localhost:27017/')
db = client.bulk_operations_demo
collection = db.test_data
```

## Basic Bulk Operations

```python
def basic_bulk_operations():
    """Basic bulk operations"""

    # Clear previous data
    collection.delete_many({})

    # 1. Bulk insert
    def bulk_insert_example():
        """Example of bulk insert"""

        print("=== Bulk insert ===")

        # Prepare data to insert
        documents = [
            {"user_id": i, "name": f"User{i}", "score": i * 10, "active": True}
            for i in range(1, 1001)
        ]

        start_time = time.time()

        # Bulk insert
        result = collection.insert_many(documents, ordered=False)

        duration = time.time() - start_time

        print(f"Inserted {len(result.inserted_ids)} documents in {duration:.3f}s")
        print(f"Insert rate: {len(documents)/duration:.0f} docs/sec")

    # 2. Bulk update
    def bulk_update_example():
        """Example of bulk update"""

        print("\n=== Bulk update ===")

        start_time = time.time()

        # Update all active users
        result = collection.update_many(
            {"active": True},
            {
                "$set": {"last_updated": datetime.utcnow()},
                "$inc": {"score": 5}
            }
        )

        duration = time.time() - start_time

        print(f"Updated {result.modified_count} documents in {duration:.3f}s")

    # 3. Bulk delete
    def bulk_delete_example():
        """Example of bulk delete"""

        print("\n=== Bulk delete ===")

        start_time = time.time()

        # Delete users with low scores
        result = collection.delete_many({"score": {"$lt": 50}})

        duration = time.time() - start_time

        print(f"Deleted {result.deleted_count} documents in {duration:.3f}s")

    # Run examples
    bulk_insert_example()
    bulk_update_example()
    bulk_delete_example()

basic_bulk_operations()
```

## bulk_write for Complex Operations

```python
def advanced_bulk_operations():
    """Advanced bulk operations using bulk_write"""

    print("=== Advanced bulk operations ===")

    # Prepare mixed operations
    def mixed_bulk_operations():
        """Mixed bulk operations"""

        operations = []

        # Insert new users
        for i in range(1001, 1051):
            operations.append(
                InsertOne({
                    "user_id": i,
                    "name": f"NewUser{i}",
                    "score": 0,
                    "active": True,
                    "created_at": datetime.utcnow()
                })
            )

        # Update scores of existing users
        for i in range(100, 200):
            operations.append(
                UpdateOne(
                    {"user_id": i},
                    {
                        "$inc": {"score": 10},
                        "$set": {"bonus_applied": True}
                    }
                )
            )

        # Replace specific users
        for i in range(200, 210):
            operations.append(
                ReplaceOne(
                    {"user_id": i},
                    {
                        "user_id": i,
                        "name": f"ReplacedUser{i}",
                        "score": 100,
                        "active": True,
                        "replaced_at": datetime.utcnow()
                    }
                )
            )

        # Delete inactive users
        operations.append(
            DeleteMany({"active": False})
        )

        print(f"Prepared {len(operations)} bulk operations")

        return operations

    # Execute bulk operations
    def execute_bulk_operations():
        """Execute bulk operations"""

        operations = mixed_bulk_operations()

        start_time = time.time()

        try:
            # Execute all operations
            result = collection.bulk_write(operations, ordered=False)

            duration = time.time() - start_time

            print(f"\nBulk operations results:")
            print(f"  Inserted: {result.inserted_count}")
            print(f"  Matched: {result.matched_count}")
            print(f"  Modified: {result.modified_count}")
            print(f"  Deleted: {result.deleted_count}")
            print(f"  Upserted: {result.upserted_count}")
            print(f"  Elapsed time: {duration:.3f}s")

            return result

        except BulkWriteError as e:
            print(f"Bulk operations error: {e.details}")
            return None

    # Execute mixed operations
    result = execute_bulk_operations()

    return result

advanced_bulk_operations()
```

## Error Handling in Bulk Operations

```python
def bulk_error_handling():
    """Error handling in bulk operations"""

    print("\n=== Handling bulk operations errors ===")

    def handle_bulk_errors():
        """Handle bulk operations errors"""

        # Prepare operations that might fail
        operations = [
            # Valid operation
            InsertOne({"user_id": 9999, "name": "ValidUser"}),

            # Operation that may fail (duplicate key)
            InsertOne({"user_id": 100, "name": "DuplicateUser"}),

            # Valid update
            UpdateOne(
                {"user_id": 101},
                {"$set": {"updated": True}}
            ),

            # Update that may fail (wrong data type)
            UpdateOne(
                {"user_id": "invalid"},
                {"$set": {"score": "not_a_number"}}
            )
        ]

        try:
            result = collection.bulk_write(operations, ordered=False)
            print("✅ All operations succeeded")
            print(f"Inserted: {result.inserted_count}, Modified: {result.modified_count}")

        except BulkWriteError as bwe:
            print("⚠️ Some operations failed:")

            # Print successful operations
            if bwe.details.get('nInserted', 0) > 0:
                print(f"  Insert succeeded: {bwe.details['nInserted']}")
            if bwe.details.get('nModified', 0) > 0:
                print(f"  Update succeeded: {bwe.details['nModified']}")

            # Print errors
            write_errors = bwe.details.get('writeErrors', [])
            print(f"  Write errors: {len(write_errors)}")

            for error in write_errors[:3]:  # First 3 errors only
                print(f"    - Operation {error['index']}: {error['errmsg']}")

    def retry_failed_operations():
        """Retry failed operations"""

        failed_operations = []

        operations = [
            InsertOne({"user_id": i, "name": f"RetryUser{i}"})
            for i in range(2000, 2010)
        ]

        max_retries = 3

        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    current_ops = operations
                else:
                    current_ops = failed_operations
                    failed_operations = []

                result = collection.bulk_write(current_ops, ordered=False)
                print(f"✅ Attempt {attempt + 1} succeeded: {result.inserted_count} inserted")
                break

            except BulkWriteError as bwe:
                print(f"⚠️ Attempt {attempt + 1} failed")

                # Extract failed operations
                write_errors = bwe.details.get('writeErrors', [])
                for error in write_errors:
                    index = error['index']
                    failed_operations.append(current_ops[index])

                if attempt == max_retries - 1:
                    print(f"❌ Final failure: {len(failed_operations)} operations")

    # Run error handling
    handle_bulk_errors()
    retry_failed_operations()

bulk_error_handling()
```

## Bulk Operations performance optimization

```python
def bulk_performance_optimization():
    """Optimize bulk operations performance"""

    print("\n=== Optimize bulk operations performance ===")

    def batch_size_optimization():
        """Optimize batch size"""

        # Different batch sizes to test
        batch_sizes = [100, 500, 1000, 5000]

        for batch_size in batch_sizes:
            print(f"\nTesting batch size: {batch_size}")

            # Clear data
            collection.delete_many({"test_batch": True})

            # Prepare data
            total_docs = 10000
            batches = []

            for i in range(0, total_docs, batch_size):
                batch = [
                    {
                        "batch_id": j,
                        "test_batch": True,
                        "value": j * 2,
                        "created": datetime.utcnow()
                    }
                    for j in range(i, min(i + batch_size, total_docs))
                ]
                batches.append(batch)

            # Measure performance
            start_time = time.time()

            total_inserted = 0
            for batch in batches:
                result = collection.insert_many(batch, ordered=False)
                total_inserted += len(result.inserted_ids)

            duration = time.time() - start_time
            rate = total_inserted / duration

            print(f"  Inserted: {total_inserted}")
            print(f"  Time: {duration:.3f}s")
            print(f"  Rate: {rate:.0f} docs/sec")

    def parallel_bulk_operations():
        """Parallel bulk operations"""

        import threading

        def worker_thread(thread_id, start_id, count):
            """Worker function"""
            operations = [
                InsertOne({
                    "thread_id": thread_id,
                    "doc_id": start_id + i,
                    "value": (start_id + i) * 10,
                    "created": datetime.utcnow()
                })
                for i in range(count)
            ]

            try:
                result = collection.bulk_write(operations, ordered=False)
                print(f"Thread {thread_id}: inserted {result.inserted_count}")
                return result.inserted_count
            except Exception as e:
                print(f"Error in thread {thread_id}: {e}")
                return 0

        print("\nParallel bulk operations:")

        # Clear data
        collection.delete_many({"thread_id": {"$exists": True}})

        # Set up threads
        num_threads = 4
        docs_per_thread = 1000

        threads = []
        start_time = time.time()

        for i in range(num_threads):
            thread = threading.Thread(
                target=worker_thread,
                args=(i, i * docs_per_thread, docs_per_thread)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        duration = time.time() - start_time
        total_docs = num_threads * docs_per_thread

        print(f"Total time: {duration:.3f}s")
        print(f"Total documents: {total_docs}")
        print(f"Insert rate: {total_docs/duration:.0f} docs/sec")

    # Run optimizations
    batch_size_optimization()
    parallel_bulk_operations()

bulk_performance_optimization()
```

## Bulk Operations Monitoring

```python
def bulk_operations_monitoring():
    """Monitor bulk operations"""

    print("\n=== Monitor bulk operations ===")

    def monitor_bulk_performance():
        """Monitor bulk operations performance"""

        # Stats before operation
        initial_stats = db.command("collStats", "test_data")
        initial_count = initial_stats.get('count', 0)
        initial_size = initial_stats.get('size', 0)

        print(f"Before operation:")
        print(f"  Documents: {initial_count:,}")
        print(f"  Size: {initial_size:,} bytes")

        # Execute a bulk operation
        operations = [
            InsertOne({
                "monitor_test": True,
                "value": i,
                "timestamp": datetime.utcnow()
            })
            for i in range(5000)
        ]

        start_time = time.time()
        result = collection.bulk_write(operations, ordered=False)
        duration = time.time() - start_time

        # Stats after operation
        final_stats = db.command("collStats", "test_data")
        final_count = final_stats.get('count', 0)
        final_size = final_stats.get('size', 0)

        print(f"\nAfter operation:")
        print(f"  Documents: {final_count:,}")
        print(f"  Size: {final_size:,} bytes")
        print(f"  Inserted: {result.inserted_count:,}")
        print(f"  Time: {duration:.3f}s")
        print(f"  Size increase: {final_size - initial_size:,} bytes")

    def track_bulk_metrics():
        """Track bulk operations metrics"""

        metrics = {
            "operations_performed": 0,
            "total_documents": 0,
            "total_time": 0,
            "errors_encountered": 0
        }

        # Multiple bulk operations for measurement
        for batch_num in range(3):
            operations = [
                UpdateOne(
                    {"user_id": 100 + i},
                    {"$inc": {"batch_updates": 1}},
                    upsert=True
                )
                for i in range(100)
            ]

            start_time = time.time()

            try:
                result = collection.bulk_write(operations, ordered=False)
                duration = time.time() - start_time

                metrics["operations_performed"] += 1
                metrics["total_documents"] += result.matched_count + result.upserted_count
                metrics["total_time"] += duration

                print(f"Batch {batch_num + 1}: {result.matched_count + result.upserted_count} documents in {duration:.3f}s")

            except BulkWriteError as e:
                metrics["errors_encountered"] += 1
                print(f"Error in batch {batch_num + 1}")

        # Print final stats
        print(f"\nOperations statistics:")
        print(f"  Operations performed: {metrics['operations_performed']}")
        print(f"  Total documents: {metrics['total_documents']:,}")
        print(f"  Total time: {metrics['total_time']:.3f}s")
        print(f"  Throughput: {metrics['total_documents']/metrics['total_time']:.0f} docs/sec")
        print(f"  Errors: {metrics['errors_encountered']}")

    monitor_bulk_performance()
    track_bulk_metrics()

bulk_operations_monitoring()
```

## Best Practices

```python
def bulk_operations_best_practices():
    """Best practices for bulk operations"""

    practices = {
        "Operation design": [
            "Use ordered=False for best performance",
            "Group similar operations together",
            "Use an appropriate batch size (1000-10000)",
            "Avoid overly large bulk operations"
        ],
        "Error handling": [
            "Handle BulkWriteError properly",
            "Inspect writeErrors for details",
            "Use a retry strategy",
            "Log failed operations for review"
        ],
        "performance optimization": [
            "Test different batch sizes",
            "Use appropriate indexes",
            "Monitor memory usage",
            "Consider parallelism for large workloads"
        ],
        "Monitoring": [
            "Track completion rates",
            "Monitor collection sizes",
            "Record execution times",
            "Monitor resource usage"
        ]
    }

    for category, items in practices.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ✅ {item}")

    # Examples of common errors
    print("\nCommon errors:")
    common_mistakes = [
        "Using overly large batches",
        "Ignoring error handling",
        "Not using appropriate indexes",
        "Mixing operation types without optimization"
    ]

    for mistake in common_mistakes:
        print(f"  ❌ {mistake}")

bulk_operations_best_practices()
```

## Summary

Bulk operations in PyMongo:

- High performance: efficiently process thousands of documents
- Flexibility: support mixed operations in a single batch
- Error handling: handle partial failures
- Optimization: tune batch size and parallelism

Types of bulk operations:

- `insert_many()` for simple bulk inserts
- `bulk_write()` for complex mixed operations
- `update_many()` and `delete_many()` for updates and deletes

Best Practices:

- Use suitable batch sizes (1000–10000)
- Enable `ordered=False` for best performance
- Properly handle `BulkWriteError`
- Monitor performance and resources

### Next: [monitoring and profiling](./10_monitoring_profiling.md)
