# PyMongo Connection Management

This guide covers all aspects of managing MongoDB connections using PyMongo, from basic connections to advanced configuration and connection pooling.

## Table of Contents

1. [Basic Connection](#basic-connection)
2. [Connection Strings](#connection-strings)
3. [Connection Options](#connection-options)
4. [Authentication](#authentication)
5. [SSL/TLS Configuration](#ssltls-configuration)
6. [Connection Pooling](#connection-pooling)
7. [Connection Management Patterns](#connection-management-patterns)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

## Basic Connection

### Simple Local Connection

```python
from pymongo import MongoClient

# Basic connection to local MongoDB
client = MongoClient()  # Defaults to mongodb://localhost:27017/

# Explicit connection
client = MongoClient('mongodb://localhost:27017/')

# Access database and collection
db = client.myapp
collection = db.users

# Always close connection when done
client.close()
```

### Connection with Context Manager

```python
from pymongo import MongoClient

# Recommended approach using context manager
def get_user_count():
    with MongoClient('mongodb://localhost:27017/') as client:
        db = client.myapp
        return db.users.count_documents({})

# Usage
user_count = get_user_count()
print(f"Total users: {user_count}")
```

### Connection to Specific Database

```python
from pymongo import MongoClient

# Connect to specific database
client = MongoClient('mongodb://localhost:27017/myapp')
db = client.get_default_database()  # Gets 'myapp' database

# Or specify database explicitly
client = MongoClient('mongodb://localhost:27017/')
db = client.myapp  # or client['myapp']
```

## Connection Strings

### Standard Connection String Format

```python
# Basic format
# mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]

# Examples
connection_strings = {
    'local': 'mongodb://localhost:27017/',
    'with_database': 'mongodb://localhost:27017/myapp',
    'with_auth': 'mongodb://user:password@localhost:27017/myapp',
    'replica_set': 'mongodb://host1:27017,host2:27017,host3:27017/myapp?replicaSet=rs0',
    'atlas': 'mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/myapp?retryWrites=true&w=majority'
}
```

### URL Encoding for Credentials

```python
from urllib.parse import quote_plus

# Safely encode credentials with special characters
username = "my user"
password = "my@password!"

# URL encode credentials
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

connection_string = f"mongodb://{encoded_username}:{encoded_password}@localhost:27017/myapp"
client = MongoClient(connection_string)
```

### MongoDB Atlas Connection

```python
from pymongo import MongoClient
import os

# MongoDB Atlas connection
def connect_to_atlas():
    """Connect to MongoDB Atlas"""
    # Store credentials in environment variables
    username = os.getenv('ATLAS_USERNAME')
    password = os.getenv('ATLAS_PASSWORD')
    cluster_url = os.getenv('ATLAS_CLUSTER_URL')

    connection_string = f"mongodb+srv://{username}:{password}@{cluster_url}/myapp?retryWrites=true&w=majority"

    client = MongoClient(connection_string)

    # Test connection
    try:
        client.admin.command('ismaster')
        print("✅ Connected to MongoDB Atlas")
        return client
    except Exception as e:
        print(f"❌ Atlas connection failed: {e}")
        raise

# Usage
client = connect_to_atlas()
```

## Connection Options

### Client Configuration Options

```python
from pymongo import MongoClient

# Comprehensive client configuration
client = MongoClient(
    'mongodb://localhost:27017/',

    # Pool settings
    maxPoolSize=100,                    # Maximum connections in pool
    minPoolSize=0,                      # Minimum connections to maintain
    maxIdleTimeMS=30000,               # Close connections after 30s idle

    # Timeout settings
    serverSelectionTimeoutMS=30000,     # Server selection timeout
    socketTimeoutMS=0,                  # Socket timeout (0 = no timeout)
    connectTimeoutMS=20000,             # Connection timeout
    heartbeatFrequencyMS=10000,         # Heartbeat frequency

    # Retry settings
    retryWrites=True,                   # Retry writes on network errors
    retryReads=True,                    # Retry reads on network errors

    # Read/Write preferences
    readPreference='secondaryPreferred',
    readConcernLevel='local',
    writeConcern={'w': 'majority', 'wtimeout': 5000},

    # Application settings
    appName='MyPythonApp',              # Application name for logging
    compressors='snappy,zlib',          # Compression algorithms

    # SSL/TLS (covered in detail below)
    tls=False,
    tlsAllowInvalidCertificates=False,

    # Event monitoring
    event_listeners=[],                 # Custom event listeners
)
```

### Database and Collection Level Options

```python
# Database with options
db = client.get_database(
    'myapp',
    read_preference=ReadPreference.SECONDARY_PREFERRED,
    read_concern=ReadConcern('majority'),
    write_concern=WriteConcern(w='majority', wtimeout=5000)
)

# Collection with options
collection = db.get_collection(
    'users',
    read_preference=ReadPreference.PRIMARY,
    read_concern=ReadConcern('local'),
    write_concern=WriteConcern(w=1, j=True)
)
```

## Authentication

### Username/Password Authentication

```python
from pymongo import MongoClient

# Method 1: In connection string
client = MongoClient('mongodb://username:password@localhost:27017/myapp?authSource=admin')

# Method 2: Separate parameters
client = MongoClient(
    host='localhost',
    port=27017,
    username='myuser',
    password='mypassword',
    authSource='admin',  # Authentication database
    authMechanism='SCRAM-SHA-256'  # Authentication mechanism
)

# Method 3: Using database authentication
client = MongoClient('mongodb://localhost:27017/')
db = client.admin
db.authenticate('myuser', 'mypassword')
```

### Different Authentication Mechanisms

```python
from pymongo import MongoClient

# SCRAM-SHA-256 (default and recommended)
client = MongoClient(
    'mongodb://user:pass@localhost:27017/',
    authMechanism='SCRAM-SHA-256'
)

# SCRAM-SHA-1 (legacy)
client = MongoClient(
    'mongodb://user:pass@localhost:27017/',
    authMechanism='SCRAM-SHA-1'
)

# X.509 Certificate Authentication
client = MongoClient(
    'mongodb://localhost:27017/',
    authMechanism='MONGODB-X509',
    tls=True,
    tlsCertificateKeyFile='/path/to/client.pem'
)

# AWS IAM Authentication (for DocumentDB)
client = MongoClient(
    'mongodb://user:pass@docdb-cluster.cluster-xxx.us-east-1.docdb.amazonaws.com:27017/',
    authMechanism='MONGODB-AWS',
    authSource='$external'
)
```

### Environment-Based Authentication

```python
import os
from pymongo import MongoClient

def create_authenticated_client():
    """Create client with environment-based authentication"""
    auth_config = {
        'host': os.getenv('MONGO_HOST', 'localhost'),
        'port': int(os.getenv('MONGO_PORT', 27017)),
        'username': os.getenv('MONGO_USERNAME'),
        'password': os.getenv('MONGO_PASSWORD'),
        'authSource': os.getenv('MONGO_AUTH_SOURCE', 'admin'),
        'authMechanism': os.getenv('MONGO_AUTH_MECHANISM', 'SCRAM-SHA-256')
    }

    # Remove None values
    auth_config = {k: v for k, v in auth_config.items() if v is not None}

    return MongoClient(**auth_config)

# Usage with .env file
from dotenv import load_dotenv
load_dotenv()

client = create_authenticated_client()
```

## SSL/TLS Configuration

### Basic SSL/TLS Setup

```python
from pymongo import MongoClient
import ssl

# Basic TLS connection
client = MongoClient(
    'mongodb://localhost:27017/',
    tls=True,
    tlsCAFile='/path/to/ca.pem',           # Certificate Authority file
    tlsCertificateKeyFile='/path/to/client.pem',  # Client certificate
    tlsAllowInvalidCertificates=False,      # Validate certificates
    tlsAllowInvalidHostnames=False          # Validate hostnames
)
```

### Advanced SSL/TLS Configuration

```python
import ssl
from pymongo import MongoClient

def create_ssl_client():
    """Create MongoDB client with custom SSL configuration"""

    # Create SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    # Load certificates
    ssl_context.load_cert_chain('/path/to/client.pem')
    ssl_context.load_verify_locations('/path/to/ca.pem')

    client = MongoClient(
        'mongodb://localhost:27017/',
        ssl=True,
        ssl_context=ssl_context
    )

    return client
```

### MongoDB Atlas SSL

```python
# MongoDB Atlas automatically uses TLS
client = MongoClient(
    'mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/myapp?retryWrites=true&w=majority',
    # TLS is automatically enabled for mongodb+srv:// URLs
)
```

## Connection Pooling

### Pool Configuration

```python
from pymongo import MongoClient

# Configure connection pool
client = MongoClient(
    'mongodb://localhost:27017/',

    # Pool size settings
    maxPoolSize=100,        # Maximum connections in pool
    minPoolSize=10,         # Minimum connections to maintain

    # Pool timeout settings
    maxIdleTimeMS=30000,    # Close idle connections after 30 seconds
    waitQueueTimeoutMS=5000,  # Wait 5 seconds for available connection

    # Pool monitoring
    maxConnecting=2,        # Maximum concurrent connection attempts
)
```

### Pool Monitoring

```python
from pymongo import MongoClient, monitoring

class ConnectionPoolLogger(monitoring.ConnectionPoolListener):
    """Log connection pool events"""

    def pool_created(self, event):
        print(f"Pool created: {event.address}")

    def pool_cleared(self, event):
        print(f"Pool cleared: {event.address}")

    def connection_created(self, event):
        print(f"Connection created: {event.connection_id}")

    def connection_ready(self, event):
        print(f"Connection ready: {event.connection_id}")

    def connection_closed(self, event):
        print(f"Connection closed: {event.connection_id}, Reason: {event.reason}")

    def connection_check_out_started(self, event):
        print(f"Connection checkout started: {event.address}")

    def connection_check_out_failed(self, event):
        print(f"Connection checkout failed: {event.address}, Reason: {event.reason}")

    def connection_checked_out(self, event):
        print(f"Connection checked out: {event.connection_id}")

    def connection_checked_in(self, event):
        print(f"Connection checked in: {event.connection_id}")

# Create client with pool monitoring
client = MongoClient(
    'mongodb://localhost:27017/',
    event_listeners=[ConnectionPoolLogger()]
)
```

### Pool Health Monitoring

```python
def monitor_connection_pool(client):
    """Monitor connection pool health"""
    try:
        # Get server info to check connection
        server_info = client.server_info()

        # Check if client is healthy
        client.admin.command('ping')

        print("Connection pool status:")
        print(f"✅ MongoDB version: {server_info['version']}")
        print("✅ Connection pool is healthy")

        return True

    except Exception as e:
        print(f"❌ Connection pool issue: {e}")
        return False

# Usage
is_healthy = monitor_connection_pool(client)
```

## Connection Management Patterns

### Singleton Pattern

```python
from pymongo import MongoClient
import threading

class MongoDBConnection:
    """Singleton MongoDB connection manager"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._client = None
        return cls._instance

    def get_client(self):
        """Get MongoDB client (create if not exists)"""
        if self._client is None:
            self._client = MongoClient(
                'mongodb://localhost:27017/',
                maxPoolSize=50,
                minPoolSize=5
            )
        return self._client

    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None

# Usage
db_connection = MongoDBConnection()
client = db_connection.get_client()
```

### Factory Pattern

```python
from pymongo import MongoClient
from enum import Enum

class ConnectionType(Enum):
    LOCAL = "local"
    ATLAS = "atlas"
    REPLICA_SET = "replica_set"

class MongoClientFactory:
    """Factory for creating MongoDB clients"""

    @staticmethod
    def create_client(connection_type: ConnectionType, **kwargs):
        """Create MongoDB client based on type"""

        if connection_type == ConnectionType.LOCAL:
            return MongoClientFactory._create_local_client(**kwargs)
        elif connection_type == ConnectionType.ATLAS:
            return MongoClientFactory._create_atlas_client(**kwargs)
        elif connection_type == ConnectionType.REPLICA_SET:
            return MongoClientFactory._create_replica_set_client(**kwargs)
        else:
            raise ValueError(f"Unsupported connection type: {connection_type}")

    @staticmethod
    def _create_local_client(**kwargs):
        """Create local MongoDB client"""
        defaults = {
            'host': 'localhost',
            'port': 27017,
            'maxPoolSize': 50
        }
        defaults.update(kwargs)
        return MongoClient(**defaults)

    @staticmethod
    def _create_atlas_client(**kwargs):
        """Create MongoDB Atlas client"""
        required = ['username', 'password', 'cluster_url']
        for key in required:
            if key not in kwargs:
                raise ValueError(f"Missing required parameter: {key}")

        connection_string = (
            f"mongodb+srv://{kwargs['username']}:{kwargs['password']}"
            f"@{kwargs['cluster_url']}/myapp?retryWrites=true&w=majority"
        )

        return MongoClient(connection_string, maxPoolSize=100)

    @staticmethod
    def _create_replica_set_client(**kwargs):
        """Create replica set client"""
        hosts = kwargs.get('hosts', ['localhost:27017'])
        replica_set = kwargs.get('replica_set', 'rs0')

        connection_string = f"mongodb://{','.join(hosts)}/?replicaSet={replica_set}"
        return MongoClient(connection_string, maxPoolSize=100)

# Usage
client = MongoClientFactory.create_client(
    ConnectionType.ATLAS,
    username='myuser',
    password='mypass',
    cluster_url='cluster0.xxxxx.mongodb.net'
)
```

### Context Manager Pattern

```python
from pymongo import MongoClient
from contextlib import contextmanager

class MongoDBManager:
    """MongoDB connection manager with context manager support"""

    def __init__(self, connection_string, **client_options):
        self.connection_string = connection_string
        self.client_options = client_options
        self._client = None

    @contextmanager
    def get_client(self):
        """Context manager for MongoDB client"""
        client = None
        try:
            client = MongoClient(self.connection_string, **self.client_options)
            yield client
        except Exception as e:
            print(f"Error with MongoDB client: {e}")
            raise
        finally:
            if client:
                client.close()

    @contextmanager
    def get_database(self, db_name):
        """Context manager for database"""
        with self.get_client() as client:
            yield client[db_name]

    @contextmanager
    def get_collection(self, db_name, collection_name):
        """Context manager for collection"""
        with self.get_database(db_name) as db:
            yield db[collection_name]

# Usage
mongo_manager = MongoDBManager('mongodb://localhost:27017/')

# Use client
with mongo_manager.get_client() as client:
    print(client.server_info())

# Use database
with mongo_manager.get_database('myapp') as db:
    print(db.list_collection_names())

# Use collection
with mongo_manager.get_collection('myapp', 'users') as collection:
    print(collection.count_documents({}))
```

## Error Handling

### Connection Error Handling

```python
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    ConfigurationError,
    OperationFailure
)
import time

def create_robust_client(connection_string, max_retries=3, retry_delay=1):
    """Create MongoDB client with retry logic"""

    for attempt in range(max_retries):
        try:
            client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=30000
            )

            # Test connection
            client.admin.command('ismaster')
            print(f"✅ Connected to MongoDB on attempt {attempt + 1}")
            return client

        except ServerSelectionTimeoutError:
            print(f"❌ Attempt {attempt + 1}: Server selection timeout")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

        except ConnectionFailure as e:
            print(f"❌ Attempt {attempt + 1}: Connection failed - {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

        except ConfigurationError as e:
            print(f"❌ Configuration error: {e}")
            raise  # Don't retry configuration errors

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

# Usage
try:
    client = create_robust_client('mongodb://localhost:27017/')
except Exception as e:
    print(f"Failed to connect after retries: {e}")
```

### Connection Health Monitoring

```python
import threading
import time
from pymongo import MongoClient
from pymongo.errors import PyMongoError

class ConnectionHealthMonitor:
    """Monitor MongoDB connection health"""

    def __init__(self, client, check_interval=30):
        self.client = client
        self.check_interval = check_interval
        self.is_healthy = False
        self.monitoring = False
        self._monitor_thread = None

    def start_monitoring(self):
        """Start connection health monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
            print("Started connection health monitoring")

    def stop_monitoring(self):
        """Stop connection health monitoring"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join()
        print("Stopped connection health monitoring")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Ping the database
                self.client.admin.command('ping')
                if not self.is_healthy:
                    print("✅ Connection restored")
                self.is_healthy = True

            except PyMongoError as e:
                if self.is_healthy:
                    print(f"❌ Connection lost: {e}")
                self.is_healthy = False

            time.sleep(self.check_interval)

    def get_health_status(self):
        """Get current health status"""
        return {
            'is_healthy': self.is_healthy,
            'monitoring': self.monitoring,
            'last_check': time.time()
        }

# Usage
client = MongoClient('mongodb://localhost:27017/')
health_monitor = ConnectionHealthMonitor(client)
health_monitor.start_monitoring()

# Check health status
status = health_monitor.get_health_status()
print(f"Connection healthy: {status['is_healthy']}")
```

## Best Practices

### Connection Best Practices

```python
from pymongo import MongoClient
import atexit

class BestPracticeClient:
    """MongoDB client following best practices"""

    def __init__(self, connection_string):
        self.client = MongoClient(
            connection_string,

            # Connection pool optimization
            maxPoolSize=100,        # Adjust based on application needs
            minPoolSize=0,          # Let pool grow as needed
            maxIdleTimeMS=30000,    # Close idle connections

            # Timeout configuration
            serverSelectionTimeoutMS=30000,  # 30 seconds for server selection
            socketTimeoutMS=0,               # No socket timeout (use heartbeat)
            connectTimeoutMS=20000,          # 20 seconds for initial connection

            # Reliability settings
            retryWrites=True,       # Retry writes on network errors
            retryReads=True,        # Retry reads on network errors

            # Application identification
            appName='MyPythonApp',  # Helps with monitoring

            # Compression for better network performance
            compressors='snappy,zlib'
        )

        # Register cleanup function
        atexit.register(self.close)

    def get_database(self, name):
        """Get database with consistent configuration"""
        return self.client.get_database(
            name,
            # Consistent read/write preferences
            read_preference='primaryPreferred',
            write_concern={'w': 'majority', 'wtimeout': 5000}
        )

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'client'):
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage
with BestPracticeClient('mongodb://localhost:27017/') as mongo:
    db = mongo.get_database('myapp')
    # Use database...
```

### Connection Configuration Checklist

```python
def validate_client_configuration(client):
    """Validate MongoDB client configuration"""

    checks = []

    # Check connection pool settings
    options = client.options

    if options.max_pool_size > 0:
        checks.append("✅ Max pool size configured")
    else:
        checks.append("⚠ Consider setting max pool size")

    if options.server_selection_timeout_ms > 0:
        checks.append("✅ Server selection timeout configured")
    else:
        checks.append("❌ Server selection timeout not set")

    if hasattr(options, 'retry_writes') and options.retry_writes:
        checks.append("✅ Retry writes enabled")
    else:
        checks.append("⚠ Consider enabling retry writes")

    if options.app_name:
        checks.append(f"✅ Application name set: {options.app_name}")
    else:
        checks.append("⚠ Consider setting application name")

    return checks

# Usage
client = MongoClient('mongodb://localhost:27017/')
validation_results = validate_client_configuration(client)
for result in validation_results:
    print(result)
```

## Next Steps

After mastering connection management:

1. **Learn Database Operations**: [Database and Collection Operations](./03_database_collection_operations.md)
2. **Explore CRUD Operations**: [CRUD Operations](./04_crud_operations.md)
3. **Advanced Features**: [Connection Pooling](../advanced/08_connection_pooling.md)
4. **Security**: [Authentication](../advanced/11_authentication.md)

## Additional Resources

- [PyMongo Connection Documentation](https://pymongo.readthedocs.io/en/stable/tutorial.html#making-a-connection)
- [MongoDB Connection String Format](https://docs.mongodb.com/manual/reference/connection-string/)
- [MongoDB Atlas Connection Guide](https://docs.atlas.mongodb.com/connect-to-cluster/)
- [SSL/TLS Configuration](https://pymongo.readthedocs.io/en/stable/examples/tls.html)
