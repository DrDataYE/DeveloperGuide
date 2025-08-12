# PyMongo Connection Pooling

A concise guide to managing and improving connection pooling in PyMongo.

## Connection Pooling Basics

```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import threading
import time
from datetime import datetime

# Optimized connection pool configuration
def create_optimized_client():
    """Create an optimized client with connection pooling"""

    client = MongoClient(
        'mongodb://localhost:27017/',

        # Connection pooling settings
        maxPoolSize=50,           # Up to 50 connections
        minPoolSize=10,           # At least 10 connections
        maxIdleTimeMS=30000,      # 30s idle before closing
        waitQueueTimeoutMS=5000,  # 5s wait for a connection

        # Network settings
        connectTimeoutMS=10000,   # 10s to connect
        socketTimeoutMS=20000,    # 20s for read/write

        # Retry settings
        retryWrites=True,
        retryReads=True,

        # Server monitoring
        heartbeatFrequencyMS=10000,          # Check every 10s
        serverSelectionTimeoutMS=30000       # 30s server selection timeout
    )

    return client

# Create optimized client
client = create_optimized_client()
db = client.connection_pool_demo
collection = db.test_data
```

## Connection Pool Monitoring

```python
def monitor_connection_pool():
    """Monitor connection pooling state"""

    def get_pool_stats():
        """Get connection pooling statistics"""

        # Get server info
        try:
            server_info = client.server_info()
            print("✅ Connection is active")
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return

        # Client info
        print(f"Client: {client.address}")
        print(f"Database: {db.name}")

        # Performance statistics
        try:
            # Run command to collect statistics
            stats = db.command("serverStatus")
            connections = stats.get("connections", {})

            print(f"Current connections: {connections.get('current', 'N/A')}")
            print(f"Available connections: {connections.get('available', 'N/A')}")
            print(f"Total connections created: {connections.get('totalCreated', 'N/A')}")

        except Exception as e:
            print(f"Could not get detailed statistics: {e}")

    def test_concurrent_connections():
        """Test concurrent connections"""

        def worker_thread(thread_id):
            """Worker function for thread"""
            try:
                # Use the same client from multiple threads
                for i in range(5):
                    result = collection.find_one({"test": True})
                    print(f"Thread {thread_id}: query {i+1} completed")
                    time.sleep(0.1)

            except Exception as e:
                print(f"Error in thread {thread_id}: {e}")

        print("\nTesting concurrent connections:")

        # Insert test data
        collection.delete_many({})
        collection.insert_one({"test": True, "created": datetime.utcnow()})

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        print("✅ All threads completed")

    get_pool_stats()
    test_concurrent_connections()

monitor_connection_pool()
```

## Connection Lifecycle Management

```python
def connection_lifecycle_management():
    """Manage the connection lifecycle"""

    def connection_health_check():
        """Connection health check"""
        try:
            # Simple connectivity check
            start_time = time.time()
            result = client.admin.command('ping')
            response_time = time.time() - start_time

            if result.get('ok') == 1:
                print(f"✅ Connection healthy (response time: {response_time:.3f}s)")
                return True
            else:
                print("❌ Invalid response from server")
                return False

        except ConnectionFailure:
            print("❌ Connection failure")
            return False
        except ServerSelectionTimeoutError:
            print("❌ Server selection timed out")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def reconnection_strategy():
        """Reconnection strategy"""
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            print(f"Connection attempt {attempt + 1}/{max_retries}")

            if connection_health_check():
                print("✅ Connected successfully")
                return True

            if attempt < max_retries - 1:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        print("❌ Failed to reconnect after all attempts")
        return False

    def graceful_shutdown():
        """Graceful shutdown of connections"""
        try:
            print("Starting to close connections...")

            # Close the client safely
            client.close()
            print("✅ All connections closed")

        except Exception as e:
            print(f"Error during shutdown: {e}")

    # Run checks
    connection_health_check()

    # Test reconnection strategy
    print("\nTesting reconnection strategy:")
    success = reconnection_strategy()

    if not success:
        print("Failed to re-establish connection")

connection_lifecycle_management()
```

## Performance Optimization with Connection Pooling

```python
def connection_pool_optimization():
    """Optimize connection pooling performance"""

    def optimal_pool_sizing():
        """Calculate optimal pool size"""

        # Measure expected load
        expected_concurrent_requests = 20
        avg_request_duration = 0.1  # 100ms
        safety_margin = 1.5

        optimal_size = int(expected_concurrent_requests * avg_request_duration * safety_margin)
        optimal_size = max(10, min(optimal_size, 100))  # between 10 and 100

        print(f"Optimal pool size: {optimal_size}")

        return optimal_size

    def performance_comparison():
        """Compare performance with different settings"""

        # Different configurations to test
        configurations = [
            {"maxPoolSize": 5, "minPoolSize": 1},
            {"maxPoolSize": 20, "minPoolSize": 5},
            {"maxPoolSize": 50, "minPoolSize": 10}
        ]

        for config in configurations:
            print(f"\nTesting config: {config}")

            # Create a temporary client for testing
            test_client = MongoClient(
                'mongodb://localhost:27017/',
                **config,
                waitQueueTimeoutMS=5000
            )

            try:
                # Measure performance
                start_time = time.time()

                # Run several queries
                for i in range(10):
                    test_client.connection_pool_demo.test_data.find_one()

                duration = time.time() - start_time
                print(f"  Execution time: {duration:.3f}s")

            except Exception as e:
                print(f"  Error: {e}")
            finally:
                test_client.close()

    def connection_pool_monitoring():
        """Continuous monitoring of connection pooling"""

        print("Starting continuous monitoring...")

        # Simulate workload
        def simulate_workload():
            """Simulate a workload"""
            for i in range(20):
                try:
                    collection.find_one({"_id": f"test_{i}"})
                    if i % 5 == 0:
                        print(f"  {i+1} queries executed")
                except Exception as e:
                    print(f"  Query error {i}: {e}")

        # Run the workload simulation
        start_time = time.time()
        simulate_workload()
        duration = time.time() - start_time

        print(f"Workload duration: {duration:.3f}s")

    # Run optimizations
    optimal_size = optimal_pool_sizing()
    performance_comparison()
    connection_pool_monitoring()

connection_pool_optimization()
```

## Error and Exception Handling

```python
def connection_error_handling():
    """Handle connection errors"""

    from pymongo.errors import (
        ConnectionFailure,
        ServerSelectionTimeoutError,
        NetworkTimeout,
        AutoReconnect
    )

    def robust_database_operation(operation_func, max_retries=3):
        """Execute a database operation with error handling"""

        for attempt in range(max_retries):
            try:
                result = operation_func()
                return result

            except AutoReconnect as e:
                print(f"AutoReconnect (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff wait

            except ConnectionFailure as e:
                print(f"Connection failure (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)

            except ServerSelectionTimeoutError as e:
                print(f"Server selection timed out (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)

            except NetworkTimeout as e:
                print(f"Network timeout (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)

            except Exception as e:
                print(f"Unexpected error: {e}")
                raise

    def test_error_handling():
        """Test error handling"""

        # Normal database operation
        def normal_operation():
            return collection.find_one({"test": True})

        # Operation that may fail
        def potentially_failing_operation():
            # Simulate a query that may fail
            return collection.find_one({"_id": "nonexistent"})

        try:
            print("Testing normal operation:")
            result = robust_database_operation(normal_operation)
            print(f"✅ Operation succeeded: {result is not None}")

            print("\nTesting potentially failing operation:")
            result = robust_database_operation(potentially_failing_operation)
            print(f"✅ Operation handled: {result is None}")

        except Exception as e:
            print(f"❌ Operation ultimately failed: {e}")

    test_error_handling()

connection_error_handling()
```

## Best Practices

```python
def connection_pooling_best_practices():
    """Best practices for connection pooling"""

    practices = {
        "Pool configuration": [
            "Set maxPoolSize based on expected load",
            "Use an appropriate minPoolSize for the application",
            "Set reasonable timeout values",
            "Enable retryWrites and retryReads"
        ],
        "Performance monitoring": [
            "Monitor number of active connections",
            "Track connection wait times",
            "Monitor connection create/close rate",
            "Use appropriate logging"
        ],
        "Error handling": [
            "Handle AutoReconnect correctly",
            "Use smart retries",
            "Close connections safely on shutdown",
            "Regularly check connection health"
        ],
        "Optimization": [
            "Share a single client across the application",
            "Avoid creating unnecessary multiple clients",
            "Use appropriate read preferences",
            "Adjust write concern as needed"
        ]
    }

    for category, items in practices.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ✅ {item}")

    # Key monitoring metrics
    print("\nMonitoring metrics:")
    metrics = [
        "Number of active/available connections",
        "Average connection wait time",
        "Connection failure rate",
        "Pool memory usage",
        "Database response time"
    ]

    for metric in metrics:
        print(f"  📊 {metric}")

connection_pooling_best_practices()
```

## Summary

Managing connection pooling:

- Optimal configuration: set maxPoolSize and minPoolSize based on load
- Continuous monitoring: track pool state and performance
- Error handling: handle connectivity interruptions intelligently
- Optimization: use a single shared client across the application

Best Practices:

- Share a single MongoClient across the application
- Set appropriate timeout values
- Continuously monitor performance metrics
- Use robust error handling

### Next: [bulk operations](./09_bulk_operations.md)
