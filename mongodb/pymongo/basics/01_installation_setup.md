# PyMongo Installation and Setup

This guide covers everything you need to install and configure PyMongo for MongoDB development with Python.

## Table of Contents

1. [Installation Methods](#installation-methods)
2. [Dependencies and Requirements](#dependencies-and-requirements)
3. [Virtual Environment Setup](#virtual-environment-setup)
4. [MongoDB Server Setup](#mongodb-server-setup)
5. [Verification](#verification)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Installation Methods

### Basic Installation

```bash
# Install PyMongo using pip
pip install pymongo

# Install with specific version
pip install pymongo==4.5.0

# Upgrade to latest version
pip install --upgrade pymongo
```

### Installation with Extra Dependencies

```bash
# Install with SSL/TLS support
pip install pymongo[tls]

# Install with AWS IAM authentication
pip install pymongo[aws]

# Install with Kerberos/GSSAPI support
pip install pymongo[gssapi]

# Install with OCSP support
pip install pymongo[ocsp]

# Install with SRV record support
pip install pymongo[srv]

# Install all optional dependencies
pip install pymongo[srv,tls,gssapi,aws,ocsp]
```

### Development Installation

```bash
# Install from GitHub (latest development version)
pip install git+https://github.com/mongodb/mongo-python-driver.git

# Clone and install from source
git clone https://github.com/mongodb/mongo-python-driver.git
cd mongo-python-driver
python setup.py install
```

## Dependencies and Requirements

### Python Version Requirements

```python
# Check Python version
import sys
print(f"Python version: {sys.version}")

# PyMongo requires Python 3.7+
if sys.version_info < (3, 7):
    raise RuntimeError("PyMongo requires Python 3.7 or later")
```

### Core Dependencies

```bash
# PyMongo automatically installs these dependencies:
# - dnspython (for SRV record support)
# - pymongo-auth-aws (for AWS authentication)
```

### Optional Dependencies

```python
# Check installed optional dependencies
try:
    import ssl
    print("SSL/TLS support: Available")
except ImportError:
    print("SSL/TLS support: Not available")

try:
    import dns.resolver
    print("SRV record support: Available")
except ImportError:
    print("SRV record support: Install with pip install pymongo[srv]")

try:
    import kerberos
    print("Kerberos support: Available")
except ImportError:
    print("Kerberos support: Install with pip install pymongo[gssapi]")
```

## Virtual Environment Setup

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv mongodb_env

# Activate virtual environment
# On Windows:
mongodb_env\Scripts\activate
# On macOS/Linux:
source mongodb_env/bin/activate

# Install PyMongo in virtual environment
pip install pymongo

# Create requirements.txt
pip freeze > requirements.txt
```

### Using conda

```bash
# Create conda environment
conda create --name mongodb_env python=3.9

# Activate environment
conda activate mongodb_env

# Install PyMongo
conda install -c conda-forge pymongo
# or
pip install pymongo
```

### Requirements File

```text
# requirements.txt
pymongo>=4.0.0
dnspython>=2.0.0
certifi>=2020.6.20
```

```bash
# Install from requirements file
pip install -r requirements.txt
```

## MongoDB Server Setup

### Local MongoDB Installation

#### Windows

```bash
# Download and install MongoDB Community Server
# From: https://www.mongodb.com/try/download/community

# Start MongoDB service
net start MongoDB

# Or start manually
mongod --dbpath C:\data\db
```

#### macOS

```bash
# Install using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb/brew/mongodb-community

# Or start manually
mongod --config /usr/local/etc/mongod.conf
```

#### Linux (Ubuntu/Debian)

```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

# Update package list and install
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Docker MongoDB Setup

```bash
# Run MongoDB in Docker
docker run --name mongodb -d -p 27017:27017 mongo:latest

# Run with authentication
docker run --name mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -d -p 27017:27017 \
  mongo:latest

# Run with persistent storage
docker run --name mongodb \
  -v mongodb_data:/data/db \
  -d -p 27017:27017 \
  mongo:latest
```

### Cloud MongoDB (MongoDB Atlas)

```python
# Connection string for MongoDB Atlas
connection_string = "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
```

## Verification

### Basic Connection Test

```python
# test_connection.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        # Create client with short timeout for testing
        client = MongoClient('mongodb://localhost:27017/',
                           serverSelectionTimeoutMS=5000)

        # Try to connect
        client.admin.command('ismaster')
        print("✅ MongoDB connection successful!")

        # Test database operations
        db = client.test_database
        collection = db.test_collection

        # Insert test document
        test_doc = {"name": "test", "status": "connected"}
        result = collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")

        # Find test document
        found_doc = collection.find_one({"name": "test"})
        print(f"✅ Test document found: {found_doc}")

        # Clean up
        collection.delete_one({"name": "test"})
        print("✅ Test document cleaned up")

        return True

    except ConnectionFailure:
        print("❌ MongoDB server not available")
        return False
    except ServerSelectionTimeoutError:
        print("❌ MongoDB connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    test_mongodb_connection()
```

### Version Information

```python
# check_versions.py
import pymongo
import sys
import platform

def check_versions():
    """Check PyMongo and system versions"""
    print("=== System Information ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")

    print("\n=== PyMongo Information ===")
    print(f"PyMongo version: {pymongo.version}")
    print(f"PyMongo version info: {pymongo.version_tuple}")

    # Check MongoDB server version
    try:
        client = MongoClient('mongodb://localhost:27017/')
        server_info = client.server_info()
        print(f"\n=== MongoDB Server Information ===")
        print(f"MongoDB version: {server_info['version']}")
        print(f"Git version: {server_info['gitVersion']}")
        print(f"OpenSSL version: {server_info.get('openssl', 'N/A')}")
        client.close()
    except Exception as e:
        print(f"\n❌ Could not connect to MongoDB: {e}")

if __name__ == "__main__":
    check_versions()
```

## Configuration

### Basic Configuration

```python
# config.py
import os
from pymongo import MongoClient
from urllib.parse import quote_plus

class MongoConfig:
    """MongoDB configuration class"""

    def __init__(self):
        # Basic connection settings
        self.host = os.getenv('MONGO_HOST', 'localhost')
        self.port = int(os.getenv('MONGO_PORT', 27017))
        self.database = os.getenv('MONGO_DATABASE', 'myapp')

        # Authentication
        self.username = os.getenv('MONGO_USERNAME')
        self.password = os.getenv('MONGO_PASSWORD')
        self.auth_source = os.getenv('MONGO_AUTH_SOURCE', 'admin')

        # Connection options
        self.max_pool_size = int(os.getenv('MONGO_MAX_POOL_SIZE', 100))
        self.min_pool_size = int(os.getenv('MONGO_MIN_POOL_SIZE', 0))
        self.server_selection_timeout = int(os.getenv('MONGO_SERVER_SELECTION_TIMEOUT', 30000))
        self.socket_timeout = int(os.getenv('MONGO_SOCKET_TIMEOUT', 30000))
        self.connect_timeout = int(os.getenv('MONGO_CONNECT_TIMEOUT', 30000))

        # SSL/TLS
        self.use_ssl = os.getenv('MONGO_USE_SSL', 'false').lower() == 'true'
        self.ssl_cert_reqs = os.getenv('MONGO_SSL_CERT_REQS', 'required')

    def get_connection_string(self):
        """Generate MongoDB connection string"""
        if self.username and self.password:
            username = quote_plus(self.username)
            password = quote_plus(self.password)
            connection_string = f"mongodb://{username}:{password}@{self.host}:{self.port}/{self.database}?authSource={self.auth_source}"
        else:
            connection_string = f"mongodb://{self.host}:{self.port}/{self.database}"

        return connection_string

    def get_client_options(self):
        """Get client options dictionary"""
        options = {
            'maxPoolSize': self.max_pool_size,
            'minPoolSize': self.min_pool_size,
            'serverSelectionTimeoutMS': self.server_selection_timeout,
            'socketTimeoutMS': self.socket_timeout,
            'connectTimeoutMS': self.connect_timeout,
        }

        if self.use_ssl:
            options.update({
                'ssl': True,
                'ssl_cert_reqs': self.ssl_cert_reqs
            })

        return options

# Usage example
config = MongoConfig()
client = MongoClient(config.get_connection_string(), **config.get_client_options())
```

### Environment Variables

```bash
# .env file
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=myapp
MONGO_USERNAME=myuser
MONGO_PASSWORD=mypassword
MONGO_AUTH_SOURCE=admin
MONGO_MAX_POOL_SIZE=100
MONGO_USE_SSL=false
```

```python
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Now use MongoConfig class
config = MongoConfig()
```

## Troubleshooting

### Common Installation Issues

#### SSL Certificate Issues

```python
import ssl
import certifi
from pymongo import MongoClient

# Fix SSL certificate issues
def create_ssl_client():
    """Create MongoDB client with proper SSL configuration"""
    return MongoClient(
        'mongodb://localhost:27017/',
        ssl=True,
        ssl_cert_reqs=ssl.CERT_REQUIRED,
        ssl_ca_certs=certifi.where()
    )
```

#### DNS Resolution Issues

```bash
# Install dnspython for SRV record support
pip install dnspython

# Or install PyMongo with SRV support
pip install pymongo[srv]
```

#### Connection Timeout Issues

```python
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

def create_robust_client():
    """Create MongoDB client with robust connection settings"""
    try:
        client = MongoClient(
            'mongodb://localhost:27017/',
            serverSelectionTimeoutMS=5000,  # 5 seconds
            connectTimeoutMS=10000,         # 10 seconds
            socketTimeoutMS=30000,          # 30 seconds
            retryWrites=True,
            retryReads=True
        )

        # Test connection
        client.admin.command('ismaster')
        return client

    except ServerSelectionTimeoutError:
        print("❌ Could not connect to MongoDB server")
        raise
```

### Platform-Specific Issues

#### Windows Issues

```python
# Windows path handling
import os
import platform

if platform.system() == 'Windows':
    # Use raw strings for Windows paths
    mongo_path = r"C:\Program Files\MongoDB\Server\5.0\bin\mongod.exe"
    data_path = r"C:\data\db"
```

#### macOS Issues

```bash
# Fix macOS SSL issues
pip install --upgrade certifi

# Or use system certificates
export SSL_CERT_FILE=/etc/ssl/cert.pem
```

#### Linux Issues

```bash
# Install system dependencies
sudo apt-get install python3-dev libssl-dev libffi-dev

# Or for CentOS/RHEL
sudo yum install python3-devel openssl-devel libffi-devel
```

### Testing Installation

```python
# comprehensive_test.py
import pymongo
from pymongo import MongoClient
from pymongo.errors import *
import ssl
import dns.resolver
import sys

def comprehensive_test():
    """Comprehensive PyMongo installation test"""
    print("=== PyMongo Installation Test ===\n")

    # 1. Check PyMongo version
    print(f"✓ PyMongo version: {pymongo.version}")

    # 2. Check Python version
    print(f"✓ Python version: {sys.version}")

    # 3. Check optional dependencies
    try:
        import dns.resolver
        print("✓ DNS resolution support available")
    except ImportError:
        print("⚠ DNS resolution support not available")

    try:
        import ssl
        print("✓ SSL/TLS support available")
    except ImportError:
        print("❌ SSL/TLS support not available")

    # 4. Test MongoDB connection
    try:
        client = MongoClient('mongodb://localhost:27017/',
                           serverSelectionTimeoutMS=3000)
        client.admin.command('ismaster')
        print("✓ MongoDB connection successful")

        # Test operations
        db = client.test_db
        collection = db.test_collection

        # Insert
        result = collection.insert_one({"test": "document"})
        print(f"✓ Insert operation successful: {result.inserted_id}")

        # Find
        doc = collection.find_one({"test": "document"})
        print(f"✓ Find operation successful: {doc}")

        # Update
        result = collection.update_one(
            {"test": "document"},
            {"$set": {"updated": True}}
        )
        print(f"✓ Update operation successful: {result.modified_count} modified")

        # Delete
        result = collection.delete_one({"test": "document"})
        print(f"✓ Delete operation successful: {result.deleted_count} deleted")

        client.close()

    except ServerSelectionTimeoutError:
        print("❌ MongoDB server not reachable")
    except Exception as e:
        print(f"❌ Error testing MongoDB: {e}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    comprehensive_test()
```

## Next Steps

After successful installation and setup:

1. **Learn Basic Operations**: Move to [Connection Management](./02_connection_management.md)
2. **Explore CRUD Operations**: Check out [CRUD Operations](./04_crud_operations.md)
3. **Practice with Examples**: Try the [Examples](../examples/) directory
4. **Set up Development Environment**: Configure your IDE with MongoDB extensions

## Additional Resources

- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Installation Guide](https://docs.mongodb.com/manual/installation/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Docker MongoDB Setup](https://hub.docker.com/_/mongo)
