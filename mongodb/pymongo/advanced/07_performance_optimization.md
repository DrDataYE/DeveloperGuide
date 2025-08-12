# PyMongo performance optimization

A concise guide to optimizing MongoDB performance with PyMongo.

## performance optimization Basics

```python
from pymongo import MongoClient, ASCENDING, DESCENDING
import time
from datetime import datetime
import cProfile

# Optimized connection
client = MongoClient(
    'mongodb://localhost:27017/',
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000,
    waitQueueTimeoutMS=5000
)

db = client.performance_demo
collection = db.test_data
```

## Query Optimization

```python
def query_optimization():
    """Query optimization"""

    # Setup test data
    if collection.estimated_document_count() == 0:
        test_data = [
            {
                "user_id": i,
                "name": f"User{i}",
                "age": 20 + (i % 50),
                "status": "active" if i % 2 == 0 else "inactive",
                "created_at": datetime.utcnow(),
                "score": i % 100
            }
            for i in range(10000)
        ]
        collection.insert_many(test_data)
        print("✅ Test data inserted")

    # Create optimized indexes
    collection.create_index([("user_id", ASCENDING)])
    collection.create_index([("status", ASCENDING), ("age", ASCENDING)])
    collection.create_index([("score", DESCENDING)])

    # Unoptimized query
    def slow_query():
        start = time.time()
        results = list(collection.find({"age": {"$gte": 30}, "status": "active"}))
        end = time.time()
        return len(results), end - start

    # Optimized query with index
    def fast_query():
        start = time.time()
        results = list(collection.find(
            {"status": "active", "age": {"$gte": 30}}
        ).hint([("status", ASCENDING), ("age", ASCENDING)]))
        end = time.time()
        return len(results), end - start

    # Performance test
    slow_count, slow_time = slow_query()
    fast_count, fast_time = fast_query()

    print(f"Query without index: {slow_count} results in {slow_time:.3f}s")
    print(f"Query with index: {fast_count} results in {fast_time:.3f}s")
    print(f"Performance improvement: {slow_time/fast_time:.1f}x faster")

query_optimization()
```

## Insert and Update Optimization

```python
def insertion_optimization():
    """Optimize insert and update operations"""

    # Clear collection for test
    collection.delete_many({})

    # Single inserts (slow)
    def single_inserts():
        start = time.time()
        for i in range(1000):
            collection.insert_one({"value": i, "type": "single"})
        return time.time() - start

    # Bulk insert (fast)
    def bulk_inserts():
        start = time.time()
        docs = [{"value": i, "type": "bulk"} for i in range(1000)]
        collection.insert_many(docs, ordered=False)
        return time.time() - start

    # Insert test
    collection.delete_many({})
    single_time = single_inserts()

    collection.delete_many({})
    bulk_time = bulk_inserts()

    print(f"Single insert: {single_time:.3f}s")
    print(f"Bulk insert: {bulk_time:.3f}s")
    print(f"Performance improvement: {single_time/bulk_time:.1f}x faster")

    # Optimized bulk update
    from pymongo import UpdateOne

    def bulk_updates():
        start = time.time()

        operations = [
            UpdateOne(
                {"value": i},
                {"$set": {"updated": True, "timestamp": datetime.utcnow()}}
            )
            for i in range(0, 1000, 10)
        ]

        collection.bulk_write(operations)
        return time.time() - start

    update_time = bulk_updates()
    print(f"Bulk update: {update_time:.3f}s")

insertion_optimization()
```

## Aggregation Optimization

```python
def aggregation_optimization():
    """Optimize aggregation operations"""

    # Setup indexes for aggregation
    collection.create_index([("type", ASCENDING), ("value", ASCENDING)])

    # Optimized aggregation
    def optimized_aggregation():
        start = time.time()

        pipeline = [
            # Early filtering
            {"$match": {"type": "bulk"}},

            # Drop unnecessary fields
            {"$project": {"value": 1, "type": 1}},

            # Group
            {"$group": {
                "_id": {"$mod": ["$value", 10]},
                "count": {"$sum": 1},
                "avg_value": {"$avg": "$value"}
            }},

            # Sort
            {"$sort": {"count": -1}},

            # Limit results
            {"$limit": 5}
        ]

        results = list(collection.aggregate(pipeline))
        return time.time() - start, len(results)

    # Aggregation with allowDiskUse for large datasets
    def large_aggregation():
        start = time.time()

        pipeline = [
            {"$group": {
                "_id": "$type",
                "total": {"$sum": "$value"},
                "count": {"$sum": 1},
                "values": {"$push": "$value"}  # can be large
            }},
            {"$sort": {"total": -1}}
        ]

        results = list(collection.aggregate(pipeline, allowDiskUse=True))
        return time.time() - start, len(results)

    agg_time, agg_count = optimized_aggregation()
    large_time, large_count = large_aggregation()

    print(f"Optimized aggregation: {agg_count} results in {agg_time:.3f}s")
    print(f"Large aggregation: {large_count} results in {large_time:.3f}s")

aggregation_optimization()
```

## Performance Monitoring

```python
def performance_monitoring():
    """Monitoring database performance"""

    # Collection statistics
    def collection_stats():
        stats = db.command("collStats", "test_data")
        print("Collection statistics:")
        print(f"  Document count: {stats.get('count', 0):,}")
        print(f"  Data size: {stats.get('size', 0):,} bytes")
        print(f"  Average document size: {stats.get('avgObjSize', 0):,} bytes")
        print(f"  Number of indexes: {stats.get('nindexes', 0)}")
        print(f"  Total index size: {stats.get('totalIndexSize', 0):,} bytes")

    # Database statistics
    def database_stats():
        stats = db.command("dbStats")
        print("\nDatabase statistics:")
        print(f"  Collections: {stats.get('collections', 0)}")
        print(f"  Database size: {stats.get('dataSize', 0):,} bytes")
        print(f"  Storage size: {stats.get('storageSize', 0):,} bytes")

    # Monitor slow queries
    def slow_query_monitoring():
        # Enable profiler for slow queries
        db.set_profiling_level(1, slow_ms=100)

        # Run query
        collection.find({"value": {"$gte": 500}}).limit(10).to_list()

        # Check slow queries
        slow_queries = list(db.system.profile.find().limit(3))
        print(f"\nSlow queries: {len(slow_queries)}")

        for query in slow_queries:
            if 'ts' in query:
                print(f"  - Execution time: {query.get('millis', 0)}ms")

    collection_stats()
    database_stats()
    slow_query_monitoring()

performance_monitoring()
```

## Best Practices

```python
def performance_best_practices():
    """Best practices for performance optimization"""

    practices = {
        "Indexing": [
            "Create indexes for frequently queried fields",
            "Use compound indexes for complex queries",
            "Monitor index usage regularly",
            "Drop unused indexes"
        ],
        "Queries": [
            "Use projection to reduce data transfer",
            "Use early filtering in aggregations",
            "Use limit() for large result sets",
            "Avoid unoptimized regex"
        ],
        "Operations": [
            "Use bulk operations for efficiency",
            "Set ordered=False for faster inserts",
            "Use upsert when needed",
            "Monitor document sizes"
        ],
        "Connection": [
            "Use connection pooling",
            "Set appropriate timeouts",
            "Use read preferences for reads",
            "Monitor memory usage"
        ]
    }

    for category, items in practices.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ✅ {item}")

    # Key performance indicators
    print("\nKey performance indicators:")
    kpis = [
        "Query response time",
        "Data throughput",
        "Memory usage",
        "CPU utilization",
        "Database size",
        "Number of active connections"
    ]

    for kpi in kpis:
        print(f"  📊 {kpi}")

performance_best_practices()
```

## Performance Testing

```python
def performance_testing():
    """Comprehensive performance testing"""

    def benchmark_operations():
        """Measure performance of different operations"""

        operations = {
            "Search with index": lambda: list(collection.find({"user_id": 1000})),
            "Search without index": lambda: list(collection.find({"name": "User1000"})),
            "Single update": lambda: collection.update_one({"user_id": 1000}, {"$set": {"last_seen": datetime.utcnow()}}),
            "Simple aggregation": lambda: list(collection.aggregate([{"$group": {"_id": "$status", "count": {"$sum": 1}}}]))
        }

        print("Operation performance test:")
        for name, operation in operations.items():
            start = time.time()
            try:
                result = operation()
                duration = time.time() - start
                print(f"  {name}: {duration:.3f}s")
            except Exception as e:
                print(f"  {name}: Error - {e}")

    def memory_usage_test():
        """Memory usage test"""
        import tracemalloc

        tracemalloc.start()

        # Memory-intensive operation
        large_results = list(collection.find().limit(1000))

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"\nMemory usage:")
        print(f"  Current: {current / 1024 / 1024:.1f} MB")
        print(f"  Peak: {peak / 1024 / 1024:.1f} MB")

    benchmark_operations()
    memory_usage_test()

performance_testing()
```

## Summary

Performance optimization techniques:

- Smart Indexing: Create appropriate indexes for queries
- bulk operations: Use insert_many and bulk_write
- Query Optimization: Projection and early filtering
- Performance Monitoring: Use profiler and database stats

Best Practices:

- Monitor query performance regularly
- Only use appropriate indexes
- Rely on bulk operations
- Tune connection configuration

### Next: [connection pooling](./08_connection_pooling.md)
