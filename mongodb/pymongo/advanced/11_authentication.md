# PyMongo Authentication

A concise guide to security and authentication in MongoDB with PyMongo.

## Authentication Basics

```python
from pymongo import MongoClient
from pymongo.errors import OperationFailure, AuthenticationFailed
import ssl

# Different authentication type examples
```

## Authentication Types

```python
def authentication_methods():
    """Different authentication types"""

    # 1. Basic authentication (Username/Password)
    def basic_auth():
        """Basic authentication"""

        try:
            client = MongoClient(
                host='localhost',
                port=27017,
                username='admin',
                password='password123',
                authSource='admin',  # Authentication database
                authMechanism='SCRAM-SHA-256'  # Authentication mechanism
            )

            # Test connection
            client.admin.command('ping')
            print("✅ Basic authentication succeeded")

            return client

        except AuthenticationFailed:
            print("❌ Authentication failed: Invalid credentials")
            return None
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return None

    # 2. URI authentication
    def uri_auth():
        """Authentication via URI"""

        try:
            # URI with authentication data
            uri = "mongodb://admin:password123@localhost:27017/admin"

            client = MongoClient(uri)
            client.admin.command('ping')

            print("✅ URI authentication succeeded")
            return client

        except Exception as e:
            print(f"❌ URI authentication error: {e}")
            return None

    # 3. X.509 authentication
    def x509_auth():
        """X.509 certificate authentication"""

        try:
            client = MongoClient(
                host='localhost',
                port=27017,
                ssl=True,
                ssl_cert_reqs=ssl.CERT_REQUIRED,
                ssl_ca_certs='/path/to/ca.pem',
                ssl_certfile='/path/to/client.pem',
                ssl_keyfile='/path/to/client-key.pem',
                authMechanism='MONGODB-X509'
            )

            print("✅ X.509 authentication configured")
            return client

        except Exception as e:
            print(f"⚠️  X.509 authentication requires certificates: {e}")
            return None

    # 4. Kerberos/GSSAPI authentication
    def kerberos_auth():
        """Kerberos authentication"""

        try:
            client = MongoClient(
                host='localhost',
                port=27017,
                username='user@REALM.COM',
                authMechanism='GSSAPI',
                authMechanismProperties='SERVICE_NAME:mongodb'
            )

            print("✅ Kerberos authentication configured")
            return client

        except Exception as e:
            print(f"⚠️  Kerberos authentication requires special configuration: {e}")
            return None

    # Test available methods
    print("Testing authentication methods:")

    basic_client = basic_auth()
    uri_client = uri_auth()
    x509_client = x509_auth()
    kerberos_client = kerberos_auth()

    return {
        "basic": basic_client,
        "uri": uri_client,
        "x509": x509_client,
        "kerberos": kerberos_client
    }

# Test authentication methods
auth_clients = authentication_methods()
```

## User and Role Management

```python
def user_management():
    """Manage users and roles"""

    # Use a client with administrative privileges
    try:
        admin_client = MongoClient('mongodb://localhost:27017/')
        admin_db = admin_client.admin

        # Test privileges
        admin_db.command('ping')

    except Exception as e:
        print(f"Administrative privileges required: {e}")
        return

    # Create users
    def create_users():
        """Create new users"""

        try:
            # Read-only user
            admin_db.command("createUser",
                "readonly_user",
                pwd="readonly123",
                roles=[{"role": "read", "db": "myapp"}]
            )
            print("✅ Read-only user created")

        except Exception as e:
            print(f"Read-only user already exists: {e}")

        try:
            # Read-write user
            admin_db.command("createUser",
                "readwrite_user",
                pwd="readwrite123",
                roles=[{"role": "readWrite", "db": "myapp"}]
            )
            print("✅ Read-write user created")

        except Exception as e:
            print(f"Read-write user already exists: {e}")

        try:
            # Admin user
            admin_db.command("createUser",
                "admin_user",
                pwd="admin123",
                roles=["userAdminAnyDatabase", "dbAdminAnyDatabase"]
            )
            print("✅ Admin user created")

        except Exception as e:
            print(f"Admin user already exists: {e}")

    # Manage roles
    def manage_roles():
        """Manage custom roles"""

        try:
            # Create a custom role
            admin_db.command("createRole",
                "customAnalyst",
                privileges=[
                    {
                        "resource": {"db": "analytics", "collection": ""},
                        "actions": ["find", "aggregate"]
                    },
                    {
                        "resource": {"db": "reports", "collection": ""},
                        "actions": ["find", "insert", "update"]
                    }
                ],
                roles=[]
            )
            print("✅ Custom role created")

        except Exception as e:
            print(f"Custom role already exists: {e}")

    # List users
    def list_users():
        """Display user list"""

        try:
            users = admin_db.command("usersInfo")

            print("\nCurrent users:")
            for user in users.get('users', []):
                username = user.get('user', 'unspecified')
                roles = [f"{role.get('role')}@{role.get('db')}"
                        for role in user.get('roles', [])]

                print(f"  - {username}: {', '.join(roles)}")

        except Exception as e:
            print(f"Error listing users: {e}")

    # Execute user management
    create_users()
    manage_roles()
    list_users()

user_management()
```

## Secure Connection (TLS/SSL)

```python
def secure_connections():
    """Secure connections with TLS/SSL"""

    # SSL/TLS configuration
    def ssl_configuration():
        """Configure SSL connection"""

        ssl_configs = {
            # Basic SSL
            "basic_ssl": {
                "ssl": True,
                "ssl_cert_reqs": ssl.CERT_NONE  # Do not verify certificate
            },

            # SSL with certificate verification
            "verified_ssl": {
                "ssl": True,
                "ssl_cert_reqs": ssl.CERT_REQUIRED,
                "ssl_ca_certs": "/path/to/ca.pem"
            },

            # SSL with client certificate
            "client_cert_ssl": {
                "ssl": True,
                "ssl_cert_reqs": ssl.CERT_REQUIRED,
                "ssl_ca_certs": "/path/to/ca.pem",
                "ssl_certfile": "/path/to/client.pem",
                "ssl_keyfile": "/path/to/client-key.pem"
            }
        }

        print("Available SSL configurations:")
        for name, config in ssl_configs.items():
            print(f"  - {name}: {config}")

        return ssl_configs

    # Test a secure connection
    def test_secure_connection():
        """Test secure connection"""

        try:
            # Basic secure connection
            client = MongoClient(
                'mongodb://localhost:27017/',
                ssl=True,
                ssl_cert_reqs=ssl.CERT_NONE
            )

            client.admin.command('ping')
            print("✅ Secure connection succeeded")

            return client

        except Exception as e:
            print(f"⚠️  Secure connection requires SSL configuration: {e}")
            return None

    # Certificate information
    def certificate_info():
        """Information about using certificates"""

        cert_info = {
            "Certificate types": [
                "CA Certificate - Certificate Authority",
                "Server Certificate",
                "Client Certificate"
            ],
            "Certificate verification": [
                "CERT_NONE - No verification",
                "CERT_OPTIONAL - Optional verification",
                "CERT_REQUIRED - Verification required"
            ],
            "Best practices": [
                "Use trusted certificates in production",
                "Rely on a trusted CA",
                "Rotate certificates regularly",
                "Protect private keys"
            ]
        }

        for category, items in cert_info.items():
            print(f"\n{category}:")
            for item in items:
                print(f"  • {item}")

    ssl_configs = ssl_configuration()
    test_secure_connection()
    certificate_info()

secure_connections()
```

## Security Best Practices

```python
def security_best_practices():
    """Security best practices"""

    # Password security
    def password_security():
        """Password security"""

        import secrets
        import string

        def generate_secure_password(length=16):
            """Generate a strong password"""

            characters = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(characters) for _ in range(length))

            return password

        # Create strong passwords
        secure_passwords = [generate_secure_password() for _ in range(3)]

        print("Strong passwords:")
        for i, pwd in enumerate(secure_passwords, 1):
            print(f"  {i}. {pwd}")

        # Password security tips
        password_tips = [
            "Use long passwords (16+ characters)",
            "Mix letters, numbers, and symbols",
            "Do not reuse passwords",
            "Rotate passwords regularly",
            "Use a password manager"
        ]

        print("\nPassword security tips:")
        for tip in password_tips:
            print(f"  ✅ {tip}")

    # Network security configuration
    def network_security():
        """Network security"""

        security_configs = {
            "Firewall": [
                "Allow connections only from specific IPs",
                "Close unused ports",
                "Use a VPN for remote access"
            ],
            "Network Encryption": [
                "Enable TLS/SSL for all connections",
                "Use the latest TLS versions",
                "Validate server certificates"
            ],
            "Access Control": [
                "Use strong authentication",
                "Enforce least privilege",
                "Review permissions regularly"
            ]
        }

        print("Network security configuration:")
        for category, items in security_configs.items():
            print(f"\n{category}:")
            for item in items:
                print(f"  🔒 {item}")

    # Security audit
    def security_audit():
        """Security audit"""

        audit_checklist = [
            "Verify password strength",
            "Review user privileges",
            "Inspect access logs",
            "Update MongoDB versions",
            "Review firewall configuration",
            "Test backups",
            "Verify data encryption",
            "Review network settings"
        ]

        print("Security audit checklist:")
        for i, item in enumerate(audit_checklist, 1):
            print(f"  {i}. □ {item}")

    password_security()
    network_security()
    security_audit()

security_best_practices()
```

## Security Monitoring

```python
def security_monitoring():
    """Security monitoring and threats"""

    # Monitor login attempts
    def monitor_auth_attempts():
        """Monitor authentication attempts"""

        try:
            # To get the authentication log, audit logging must be enabled
            print("Monitoring authentication attempts:")
            print("⚠️  Requires MongoDB audit logging to be enabled")

            # Simulated authentication statistics
            auth_stats = {
                "successful_logins": 156,
                "failed_attempts": 12,
                "unique_users": 8,
                "suspicious_ips": ["192.168.1.100", "10.0.0.15"]
            }

            print(f"  Successful logins: {auth_stats['successful_logins']}")
            print(f"  Failed attempts: {auth_stats['failed_attempts']}")
            print(f"  Unique users: {auth_stats['unique_users']}")
            print(f"  Suspicious IPs: {len(auth_stats['suspicious_ips'])}")

        except Exception as e:
            print(f"Error monitoring authentication: {e}")

    # Monitor suspicious activities
    def monitor_suspicious_activities():
        """Monitor suspicious activities"""

        suspicious_patterns = [
            "A large number of queries in a short time",
            "Attempts to access sensitive data",
            "Unusual delete or update operations",
            "Connections from unfamiliar locations",
            "Use of typically inactive accounts"
        ]

        print("\nSuspicious activity patterns to monitor:")
        for pattern in suspicious_patterns:
            print(f"  🚨 {pattern}")

    # Security alerts
    def security_alerts():
        """Configure security alerts"""

        alert_conditions = {
            "Failed login attempts": "More than 5 attempts in 5 minutes",
            "Unusual queries": "More than 1000 queries in a minute",
            "Privilege changes": "Any modification to user roles",
            "New connections": "Connections from new IP addresses",
            "Administrative operations": "Creating or dropping databases"
        }

        print("\nSecurity alert conditions:")
        for condition, threshold in alert_conditions.items():
            print(f"  📢 {condition}: {threshold}")

    monitor_auth_attempts()
    monitor_suspicious_activities()
    security_alerts()

security_monitoring()
```

## Data Security

```python
def data_security():
    """Data security and encryption"""

    # Data encryption in transit
    def encryption_in_transit():
        """Encrypt data in transit"""

        print("Data encryption in transit:")
        print("  ✅ Use TLS 1.2 or newer")
        print("  ✅ Enable encryption for all connections")
        print("  ✅ Validate SSL certificates")
        print("  ✅ Use strong cipher suites")

    # Data encryption at rest
    def encryption_at_rest():
        """Encrypt data at rest"""

        print("\nData encryption at rest:")
        print("  🔐 MongoDB Enterprise: WiredTiger Encryption")
        print("  🔐 File System Encryption: LUKS, BitLocker")
        print("  🔐 Application Level: Encrypt sensitive fields")
        print("  🔐 Key Management: Use a key management system")

    # Protect sensitive data
    def sensitive_data_protection():
        """Protect sensitive data"""

        import hashlib
        import hmac

        # Example password hashing
        def hash_password(password, salt=None):
            """Hash a password"""

            if salt is None:
                salt = secrets.token_hex(32)

            # Use PBKDF2
            key = hashlib.pbkdf2_hmac('sha256',
                                    password.encode('utf-8'),
                                    salt.encode('utf-8'),
                                    100000)  # 100,000 iterations

            return f"{salt}:{key.hex()}"

        # Example of masking sensitive fields
        def mask_sensitive_data(data, field):
            """Mask sensitive data"""

            if field in data:
                value = str(data[field])
                if len(value) > 4:
                    data[field] = value[:2] + "*" * (len(value) - 4) + value[-2:]

            return data

        # Test protection
        sample_password = "mySecurePassword123"
        hashed = hash_password(sample_password)
        print(f"\nHashed password: {hashed[:50]}...")

        sample_data = {"credit_card": "1234567890123456", "name": "Ahmed Mohamed"}
        masked = mask_sensitive_data(sample_data.copy(), "credit_card")
        print(f"Masked data: {masked}")

    encryption_in_transit()
    encryption_at_rest()
    sensitive_data_protection()

data_security()
```

## Summary

MongoDB security basics:

- Authentication: Verify user identity
- Authorization: Control access privileges
- Encryption: Protect data in transit and at rest
- Monitoring: Track activities and threats

Authentication types:

- SCRAM-SHA-256 (default)
- X.509 Certificates
- Kerberos/GSSAPI
- LDAP (Enterprise)

Best Practices:

- Use strong passwords
- Enforce least privilege
- Enable TLS/SSL for all connections
- Monitor suspicious access attempts

### Next: [Security Best Practices](./12_security_best_practices.md)
