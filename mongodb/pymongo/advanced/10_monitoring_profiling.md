# PyMongo Monitoring and Profiling

A concise guide to monitoring and analyzing MongoDB performance with PyMongo.

## Monitoring Basics

```python
from pymongo import MongoClient
import time
from datetime import datetime, timedelta
import json

# Connection
client = MongoClient('mongodb://localhost:27017/')
db = client.monitoring_demo
collection = db.test_data
```

## Performance Monitoring

```python
def performance_monitoring():
    """Monitor database performance"""

    # Server statistics
    def server_status():
        """Get server status"""
        status = db.command("serverStatus")

        print("Server statistics:")
        print(f"  Version: {status.get('version', 'N/A')}")
        print(f"  Uptime: {status.get('uptime', 0)} seconds")

        # Memory
        mem = status.get('mem', {})
        print(f"  Resident memory: {mem.get('resident', 0)} MB")
        print(f"  Virtual memory: {mem.get('virtual', 0)} MB")

        # Connections
        connections = status.get('connections', {})
        print(f"  Current connections: {connections.get('current', 0)}")
        print(f"  Available connections: {connections.get('available', 0)}")

        # Operations
        opcounters = status.get('opcounters', {})
        print(f"  Query count: {opcounters.get('query', 0):,}")
        print(f"  Insert count: {opcounters.get('insert', 0):,}")
        print(f"  Update count: {opcounters.get('update', 0):,}")

    # Database statistics
    def database_stats():
        """Database statistics"""
        stats = db.command("dbStats")

        print(f"\nDatabase statistics '{db.name}':")
        print(f"  Collections: {stats.get('collections', 0)}")
        print(f"  Data size: {stats.get('dataSize', 0):,} bytes")
        print(f"  Storage size: {stats.get('storageSize', 0):,} bytes")
        print(f"  Index count: {stats.get('indexes', 0)}")
        print(f"  Index size: {stats.get('indexSize', 0):,} bytes")

    # Collection statistics
    def collection_stats():
        """Collection statistics"""
        stats = db.command("collStats", "test_data")

        print(f"\nCollection statistics 'test_data':")
        print(f"  Document count: {stats.get('count', 0):,}")
        print(f"  Data size: {stats.get('size', 0):,} bytes")
        print(f"  Average document size: {stats.get('avgObjSize', 0):,} bytes")
        print(f"  Storage size: {stats.get('storageSize', 0):,} bytes")

    server_status()
    database_stats()
    collection_stats()

performance_monitoring()
```

## Query Profiler

```python
def query_profiling():
    """Analyze queries with the Profiler"""

    # Enable profiler
    def enable_profiler():
        """Enable profiler for slow queries"""

        # Enable profiler for queries longer than 100ms
        db.set_profiling_level(1, slow_ms=100)

        print("✅ Profiler enabled for queries > 100ms")

    # Run test queries
    def run_test_queries():
        """Run test queries"""

        # Insert sample data
        if collection.estimated_document_count() == 0:
            test_data = [
                {"user_id": i, "name": f"User{i}", "score": i % 100}
                for i in range(10000)
            ]
            collection.insert_many(test_data)
            print("Sample data inserted")

        # Fast query (with index)
        collection.create_index("user_id")
        collection.find_one({"user_id": 1000})

        # Slow query (without index)
        list(collection.find({"score": {"$gte": 50}}).limit(100))

        # Aggregation query
        list(collection.aggregate([
            {"$group": {"_id": "$score", "count": {"$sum": 1}}}
            ,{"$sort": {"count": -1}}
        ]))

        print("Test queries executed")

    # Analyze profiler results
    def analyze_profile_data():
        """Analyze profiler data"""

        # Fetch slow operations
        slow_ops = list(db.system.profile.find().sort("ts", -1).limit(10))

        print(f"\nSlow operations ({len(slow_ops)}):")

        for i, op in enumerate(slow_ops, 1):
            if 'command' in op:
                operation = op['command'].get('find', op['command'].get('aggregate', 'unknown'))
                duration = op.get('millis', 0)
                timestamp = op.get('ts', datetime.utcnow())

                print(f"  {i}. Operation: {operation}")
                print(f"     Duration: {duration}ms")
                print(f"     Time: {timestamp}")

                # Execution stats
                exec_stats = op.get('execStats', {})
                if exec_stats:
                    print(f"     Docs examined: {exec_stats.get('totalDocsExamined', 0)}")
                    print(f"     Docs returned: {exec_stats.get('totalDocsReturned', 0)}")
                print()

    # Run analysis
    enable_profiler()
    run_test_queries()
    time.sleep(1)  # Wait for ops to be recorded
    analyze_profile_data()

    # Disable profiler
    db.set_profiling_level(0)
    print("Profiler disabled")

query_profiling()
```

## Index Monitoring

```python
def index_monitoring():
    """Monitor index usage and performance"""

    # Index statistics
    def index_stats():
        """Index statistics"""

        indexes = collection.list_indexes()

        print("Collection indexes:")
        for idx in indexes:
            name = idx.get('name', 'Unnamed')
            keys = idx.get('key', {})
            size = idx.get('size', 0)

            print(f"  - {name}: {dict(keys)}")
            if size > 0:
                print(f"    Size: {size:,} bytes")

    # Index usage monitoring
    def index_usage_stats():
        """Index usage statistics"""

        # Get usage statistics
        stats = db.command("collStats", "test_data", indexDetails=True)

        index_sizes = stats.get('indexSizes', {})
        print("\nIndex sizes:")
        for index_name, size in index_sizes.items():
            print(f"  {index_name}: {size:,} bytes")

        # Analyze index usage via aggregation
        pipeline = [
            {"$indexStats": {}},
            {"$project": {
                "name": 1,
                "accesses": "$accesses.ops",
                "since": "$accesses.since"
            }}
        ]

        try:
            usage_stats = list(collection.aggregate(pipeline))
            print("\nIndex usage statistics:")
            for stat in usage_stats:
                print(f"  {stat['name']}: {stat.get('accesses', 0):,} accesses")
        except Exception as e:
            print(f"Failed to get usage stats: {e}")

    # Test index performance
    def test_index_performance():
        """Test index performance"""

        # Query without index
        start = time.time()
        list(collection.find({"name": "User5000"}))
        no_index_time = time.time() - start

        # Create index
        collection.create_index("name")

        # Query with index
        start = time.time()
        list(collection.find({"name": "User5000"}))
        with_index_time = time.time() - start

        print(f"\nIndex performance comparison:")
        print(f"  Without index: {no_index_time:.3f}s")
        print(f"  With index: {with_index_time:.3f}s")

        if no_index_time > 0:
            improvement = no_index_time / with_index_time
            print(f"  Performance improvement: {improvement:.1f}x")

    index_stats()
    index_usage_stats()
    test_index_performance()

index_monitoring()
```

## Memory and Resource Monitoring

```python
def resource_monitoring():
    """Monitor memory and resource usage"""

    def memory_usage():
        """Monitor memory usage"""

        # Server status
        status = db.command("serverStatus")
        mem = status.get('mem', {})

        print("Memory usage:")
        print(f"  Resident memory: {mem.get('resident', 0)} MB")
        print(f"  Virtual memory: {mem.get('virtual', 0)} MB")
        print(f"  Supported: {mem.get('supported', False)}")

        # WiredTiger cache (if available)
        wt = status.get('wiredTiger', {})
        if wt:
            cache = wt.get('cache', {})
            cache_size = cache.get('maximum bytes configured', 0)
            cache_used = cache.get('bytes currently in the cache', 0)

            print(f"  Cache size: {cache_size // (1024*1024)} MB")
            print(f"  Cache used: {cache_used // (1024*1024)} MB")

            if cache_size > 0:
                cache_ratio = (cache_used / cache_size) * 100
                print(f"  Cache utilization: {cache_ratio:.1f}%")

    def connection_monitoring():
        """Monitor connections"""

        status = db.command("serverStatus")
        connections = status.get('connections', {})

        print(f"\nConnections:")
        print(f"  Current: {connections.get('current', 0)}")
        print(f"  Available: {connections.get('available', 0)}")
        print(f"  Total created: {connections.get('totalCreated', 0)}")

        # Connection usage ratio
        current = connections.get('current', 0)
        available = connections.get('available', 0)
        total_possible = current + available

        if total_possible > 0:
            usage_ratio = (current / total_possible) * 100
            print(f"  Usage ratio: {usage_ratio:.1f}%")

    def operation_counters():
        """Operation counters"""

        status = db.command("serverStatus")
        opcounters = status.get('opcounters', {})

        print(f"\nOperation counters:")
        operations = ['insert', 'query', 'update', 'delete', 'getmore', 'command']

        for op in operations:
            count = opcounters.get(op, 0)
            print(f"  {op}: {count:,}")

    memory_usage()
    connection_monitoring()
    operation_counters()

resource_monitoring()
```

## Creating Monitoring Dashboard

```python
def create_monitoring_dashboard():
    """Create a simple monitoring dashboard"""

    def collect_metrics():
        """Collect metrics"""

        metrics = {
            "timestamp": datetime.utcnow(),
            "server": {},
            "database": {},
            "collection": {}
        }

        try:
            # Server information
            server_status = db.command("serverStatus")
            metrics["server"] = {
                "uptime": server_status.get('uptime', 0),
                "connections": server_status.get('connections', {}),
                "memory": server_status.get('mem', {}),
                "operations": server_status.get('opcounters', {})
            }

            # Database information
            db_stats = db.command("dbStats")
            metrics["database"] = {
                "collections": db_stats.get('collections', 0),
                "dataSize": db_stats.get('dataSize', 0),
                "storageSize": db_stats.get('storageSize', 0),
                "indexes": db_stats.get('indexes', 0)
            }

            # Collection information
            coll_stats = db.command("collStats", "test_data")
            metrics["collection"] = {
                "count": coll_stats.get('count', 0),
                "size": coll_stats.get('size', 0),
                "avgObjSize": coll_stats.get('avgObjSize', 0)
            }

        except Exception as e:
            print(f"Error collecting metrics: {e}")

        return metrics

    def display_dashboard(metrics):
        """Display the monitoring dashboard"""

        print("\n" + "="*50)
        print("           MongoDB Monitoring Dashboard")
        print("="*50)
        print(f"Update time: {metrics['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        # Server
        server = metrics.get('server', {})
        if server:
            print(f"\n🖥️  Server:")
            uptime_hours = server.get('uptime', 0) / 3600
            print(f"   Uptime: {uptime_hours:.1f} hours")

            connections = server.get('connections', {})
            print(f"   Connections: {connections.get('current', 0)}/{connections.get('current', 0) + connections.get('available', 0)}")

            memory = server.get('memory', {})
            print(f"   Memory: {memory.get('resident', 0)} MB")

        # Database
        database = metrics.get('database', {})
        if database:
            print(f"\n💾 Database:")
            print(f"   Collections: {database.get('collections', 0)}")
            print(f"   Data size: {database.get('dataSize', 0) // (1024*1024)} MB")
            print(f"   Indexes: {database.get('indexes', 0)}")

        # Collection
        collection_data = metrics.get('collection', {})
        if collection_data:
            print(f"\n📊 Collection:")
            print(f"   Documents: {collection_data.get('count', 0):,}")
            print(f"   Size: {collection_data.get('size', 0) // 1024} KB")
            print(f"   Average document size: {collection_data.get('avgObjSize', 0)} bytes")

    def monitoring_loop(duration_minutes=1):
        """Continuous monitoring loop"""

        print(f"Starting monitoring for {duration_minutes} minute(s)...")
        end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)

        while datetime.utcnow() < end_time:
            metrics = collect_metrics()
            display_dashboard(metrics)

            # Wait 10 seconds
            print("\nWaiting 10 seconds...")
            time.sleep(10)

        print("Monitoring finished")

    # Run dashboard once
    metrics = collect_metrics()
    display_dashboard(metrics)

    # Short loop for demo
    # monitoring_loop(0.5)  # half a minute

create_monitoring_dashboard()
```

## Best Practices

```python
def monitoring_best_practices():
    """Monitoring best practices"""

    practices = {
        "Basic metrics": [
            "Monitor query response times",
            "Track memory and CPU usage",
            "Monitor the number of active connections",
            "Track database size growth"
        ],
        "Profiling": [
            "Enable the profiler for slow queries",
            "Review profiler operations regularly",
            "Set appropriate time thresholds",
            "Purge old profiler data"
        ],
        "Alerts": [
            "Set alerts for high memory usage",
            "Watch for connection drops",
            "Alert on slow queries",
            "Monitor available disk space"
        ],
        "Optimization": [
            "Use index statistics for tuning",
            "Monitor query efficiency",
            "Analyze usage patterns",
            "Tune server configuration as needed"
        ]
    }

    for category, items in practices.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ✅ {item}")

    # Recommended monitoring tools
    print("\nRecommended monitoring tools:")
    tools = [
        "MongoDB Compass (GUI)",
        "MongoDB Atlas (Cloud monitoring)",
        "Prometheus + Grafana",
        "MongoDB Ops Manager",
        "Third-party APM tools"
    ]

    for tool in tools:
        print(f"  🔧 {tool}")

monitoring_best_practices()
```

## Summary

Monitoring basics in MongoDB:

- Profiler: to analyze slow queries
- Server Status: to monitor server health
- Collection Stats: for collection statistics
- Index Monitoring: to monitor index performance

Key metrics:

- Query response times
- Memory and CPU usage
- Number of active connections
- Database size and growth

Best Practices:

- Continuously monitor vital metrics
- Use the profiler to analyze performance
- Set up alerts for potential issues
- Review and optimize indexes regularly

### Next: [Security and Authentication](./11_authentication.md)
