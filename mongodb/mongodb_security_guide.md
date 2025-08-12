# MongoDB Security: Complete Guide

This comprehensive guide covers all aspects of MongoDB security, from authentication and authorization to network security and encryption. Security should be implemented at multiple layers to protect your data effectively.

## Table of Contents

1. [Security Overview](#security-overview)
2. [Authentication](#authentication)
3. [Authorization and Roles](#authorization-and-roles)
4. [Network Security](#network-security)
5. [Encryption](#encryption)
6. [Auditing](#auditing)
7. [Security Best Practices](#security-best-practices)
8. [Common Security Configurations](#common-configurations)
9. [Troubleshooting](#troubleshooting)

## Security Overview {#security-overview}

MongoDB security operates on multiple layers:

1. **Authentication**: Verifying user identity
2. **Authorization**: Controlling access to resources
3. **Network Security**: Securing communications
4. **Encryption**: Protecting data at rest and in transit
5. **Auditing**: Monitoring access and changes

### Default Security State

By default, MongoDB:

- Has no authentication enabled
- Allows any user to perform any action
- Binds to localhost only
- Does not encrypt data

**⚠️ Warning**: Never run MongoDB in production without proper security configuration.

## Authentication {#authentication}

### Enabling Authentication

```javascript
// 1. Start MongoDB without authentication
// 2. Create an admin user
use admin
db.createUser({
  user: "admin",
  pwd: "securePassword123",
  roles: ["root"]
})

// 3. Restart MongoDB with authentication enabled
// mongod --auth --config /path/to/mongod.conf
```

### Authentication Mechanisms

#### 1. SCRAM (Default)

```javascript
// SCRAM-SHA-1 and SCRAM-SHA-256 (recommended)
db.createUser({
  user: "myuser",
  pwd: "mypassword",
  roles: ["readWrite"],
  mechanisms: ["SCRAM-SHA-256"],
});
```

#### 2. x.509 Certificate Authentication

```javascript
// Create user for certificate authentication
db.createUser({
  user: "CN=myName,OU=myOrgUnit,O=myOrg,L=myLocality,ST=myState,C=myCountry",
  roles: ["readWrite"],
});
```

#### 3. LDAP Authentication

```javascript
// External user (requires MongoDB Enterprise)
db.createUser(
  {
    user: "username",
    roles: ["readWrite"],
  },
  {
    authenticationRestrictions: [
      {
        clientSource: ["192.168.1.0/24"],
        serverAddress: ["192.168.1.100"],
      },
    ],
  }
);
```

### User Management

#### Creating Users

```javascript
// Basic user creation
use myapp
db.createUser({
  user: "appuser",
  pwd: "apppassword",
  roles: [
    { role: "readWrite", db: "myapp" },
    { role: "read", db: "logs" }
  ]
})

// User with custom role
db.createUser({
  user: "analyst",
  pwd: "analystpass",
  roles: [
    { role: "read", db: "analytics" },
    { role: "customAnalystRole", db: "analytics" }
  ],
  authenticationRestrictions: [
    {
      clientSource: ["10.0.0.0/8"],
      serverAddress: ["10.0.1.100"]
    }
  ]
})
```

#### Updating Users

```javascript
// Update user password
db.updateUser("appuser", {
  pwd: "newSecurePassword",
});

// Update user roles
db.updateUser("appuser", {
  roles: [
    { role: "readWrite", db: "myapp" },
    { role: "readWrite", db: "newdb" },
    { role: "read", db: "shared" },
  ],
});

// Add roles to existing user
db.grantRolesToUser("appuser", [{ role: "backup", db: "admin" }]);

// Remove roles from user
db.revokeRolesFromUser("appuser", [{ role: "backup", db: "admin" }]);
```

#### User Authentication

```javascript
// Authenticate within MongoDB shell
db.auth("username", "password");

// Connection string authentication
// mongodb://username:password@host:port/database

// Connection from application
const { MongoClient } = require("mongodb");
const client = new MongoClient(
  "mongodb://username:password@localhost:27017/myapp",
  {
    authSource: "admin",
  }
);
```

## Authorization and Roles {#authorization-and-roles}

### Built-in Roles

#### Database-Level Roles

```javascript
// Read-only access
{ role: "read", db: "myapp" }

// Read-write access
{ role: "readWrite", db: "myapp" }

// Database administration
{ role: "dbAdmin", db: "myapp" }

// User administration for database
{ role: "userAdmin", db: "myapp" }

// All database privileges
{ role: "dbOwner", db: "myapp" }
```

#### Collection-Level Roles

```javascript
// Read any collection in database
{ role: "readAnyDatabase", db: "admin" }

// Write any collection in database
{ role: "readWriteAnyDatabase", db: "admin" }

// Admin any database
{ role: "dbAdminAnyDatabase", db: "admin" }

// User admin any database
{ role: "userAdminAnyDatabase", db: "admin" }
```

#### Cluster Administration Roles

```javascript
// Cluster monitoring
{ role: "clusterMonitor", db: "admin" }

// Cluster management
{ role: "clusterManager", db: "admin" }

// Host management
{ role: "hostManager", db: "admin" }

// All cluster privileges
{ role: "clusterAdmin", db: "admin" }
```

#### Backup and Restore Roles

```javascript
// Backup operations
{ role: "backup", db: "admin" }

// Restore operations
{ role: "restore", db: "admin" }
```

#### Super User Roles

```javascript
// All privileges on all databases
{ role: "root", db: "admin" }
```

### Custom Roles

#### Creating Custom Roles

```javascript
// Custom role for application monitoring
use admin
db.createRole({
  role: "appMonitor",
  privileges: [
    {
      resource: { db: "myapp", collection: "" },
      actions: ["find", "listCollections", "listIndexes"]
    },
    {
      resource: { db: "myapp", collection: "logs" },
      actions: ["find", "insert"]
    }
  ],
  roles: [
    { role: "read", db: "config" }
  ]
})

// Custom role for analytics
db.createRole({
  role: "analyticsUser",
  privileges: [
    {
      resource: { db: "analytics", collection: "" },
      actions: ["find", "createIndex", "listIndexes"]
    },
    {
      resource: { cluster: true },
      actions: ["listSessions"]
    }
  ],
  roles: []
})
```

#### Role Management

```javascript
// View role details
db.getRole("appMonitor", { showPrivileges: true });

// Update role
db.updateRole("appMonitor", {
  privileges: [
    {
      resource: { db: "myapp", collection: "" },
      actions: ["find", "listCollections", "listIndexes", "insert"],
    },
  ],
});

// Grant privileges to role
db.grantPrivilegesToRole("appMonitor", [
  {
    resource: { db: "myapp", collection: "metrics" },
    actions: ["update"],
  },
]);

// Drop role
db.dropRole("oldRole");
```

### Permission Scopes

#### Database Actions

```javascript
// Database-level permissions
const dbActions = [
  "changeCustomData",
  "changePassword",
  "createCollection",
  "createIndex",
  "createRole",
  "createUser",
  "dropCollection",
  "dropRole",
  "dropUser",
  "emptycapped",
  "enableProfiler",
  "grantRole",
  "killCursors",
  "revokeRole",
  "unlock",
  "viewRole",
  "viewUser",
];
```

#### Collection Actions

```javascript
// Collection-level permissions
const collectionActions = [
  "bypassDocumentValidation",
  "changeStream",
  "collStats",
  "convertToCapped",
  "createIndex",
  "dbHash",
  "dbStats",
  "find",
  "findAndModify",
  "insert",
  "killCursors",
  "listCollections",
  "listIndexes",
  "planCacheRead",
  "reIndex",
  "remove",
  "renameCollectionSameDB",
  "update",
  "validate",
];
```

## Network Security {#network-security}

### IP Whitelisting

```yaml
# mongod.conf
net:
  bindIp: 127.0.0.1,192.168.1.100 # Specific IPs only
  port: 27017
```

### SSL/TLS Configuration

```yaml
# mongod.conf
net:
  ssl:
    mode: requireSSL
    PEMKeyFile: /path/to/mongodb.pem
    CAFile: /path/to/ca.pem
    allowConnectionsWithoutCertificates: false
    allowInvalidHostnames: false
```

### Firewall Configuration

```bash
# Ubuntu/Debian iptables
sudo iptables -A INPUT -p tcp --dport 27017 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 27017 -j DROP

# CentOS/RHEL firewalld
sudo firewall-cmd --permanent --add-rich-rule="rule family='ipv4' source address='192.168.1.0/24' port protocol='tcp' port='27017' accept"
sudo firewall-cmd --reload
```

## Encryption {#encryption}

### Encryption at Rest

```yaml
# mongod.conf - WiredTiger encryption
storage:
  wiredTiger:
    engineConfig:
      configString: "encryption=(name=AES256-CBC,keyid='mykey')"
security:
  kmip:
    serverName: kmip.example.com
    port: 5696
    serverCAFile: /path/to/ca.pem
    clientCertificateFile: /path/to/client.pem
```

### Encryption in Transit (TLS/SSL)

```yaml
# mongod.conf
net:
  ssl:
    mode: requireSSL
    PEMKeyFile: /etc/ssl/mongodb.pem
    PEMKeyPassword: "password"
    clusterFile: /etc/ssl/mongodb-cluster.pem
    clusterPassword: "clusterPassword"
    CAFile: /etc/ssl/ca.pem
    CRLFile: /etc/ssl/crl.pem
    allowConnectionsWithoutCertificates: false
    allowInvalidHostnames: false
    disabledProtocols: "TLS1_0,TLS1_1"
```

### Field-Level Encryption

```javascript
// Client-side field level encryption (MongoDB 4.2+)
const clientEncryption = new ClientEncryption(keyVault, {
  keyVaultNamespace: "encryption.__keyVault",
  kmsProviders: {
    local: {
      key: localMasterKey,
    },
  },
});

// Encrypt field
const encryptedField = await clientEncryption.encrypt(sensitiveData, {
  algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
  keyId: dataEncryptionKey,
});
```

## Auditing {#auditing}

### Enabling Auditing

```yaml
# mongod.conf
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: '{ "ts" : { "$gte" : { "$date" : "2023-01-01T00:00:00.000Z" } } }'
```

### Audit Event Types

```javascript
// Common audit filters
const auditFilters = {
  // Authentication events
  authenticationFilter: {
    atype: { $in: ["authenticate", "logout"] },
  },

  // Authorization failures
  authorizationFilter: {
    atype: "authCheck",
    result: 13, // Authorization failed
  },

  // Administrative operations
  adminFilter: {
    atype: { $in: ["createUser", "dropUser", "createRole", "dropRole"] },
  },

  // Data modifications
  dataModificationFilter: {
    atype: { $in: ["insert", "update", "delete"] },
    "param.ns": /^myapp\./,
  },
};
```

### Sample Audit Configuration

```yaml
# mongod.conf - Comprehensive auditing
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: |
    {
      $or: [
        { atype: { $in: ["authenticate", "logout", "createUser", "dropUser"] } },
        { 
          atype: { $in: ["insert", "update", "delete"] },
          "param.ns": { $regex: "^(myapp|sensitive)" }
        },
        {
          atype: "authCheck",
          result: { $ne: 0 }
        }
      ]
    }
```

## Security Best Practices {#security-best-practices}

### 1. Authentication Best Practices

```javascript
// Strong password policy
const passwordPolicy = {
  minLength: 12,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,
  preventReuse: 5,
};

// Implement password rotation
db.updateUser("appuser", {
  pwd: generateSecurePassword(),
  customData: {
    passwordChanged: new Date(),
    mustChangePassword: false,
  },
});
```

### 2. Role-Based Access Control

```javascript
// Principle of least privilege
const roles = {
  // Application users - minimal permissions
  appUser: {
    roles: [
      { role: "readWrite", db: "myapp" },
      { role: "read", db: "reference" },
    ],
  },

  // Read-only analysts
  analyst: {
    roles: [
      { role: "read", db: "analytics" },
      { role: "read", db: "logs" },
    ],
  },

  // Backup operators
  backupOperator: {
    roles: [
      { role: "backup", db: "admin" },
      { role: "clusterMonitor", db: "admin" },
    ],
  },
};
```

### 3. Network Security

```yaml
# Secure network configuration
net:
  bindIp: 127.0.0.1,10.0.1.100  # Specific interfaces only
  port: 27017
  maxIncomingConnections: 1000
  ipv6: false

# Use non-standard port (security through obscurity)
net:
  port: 27018  # Change from default 27017
```

### 4. Monitoring and Alerting

```javascript
// Monitor failed authentications
db.adminCommand({
  setParameter: 1,
  failIndexKeyTooLong: false,
  maxIndexNameLength: 127,
});

// Set up alerts for security events
const securityAlerts = {
  failedLogins: {
    threshold: 5,
    timeWindow: "5m",
    action: "block_ip",
  },

  privilegeEscalation: {
    events: ["grantRole", "createUser"],
    action: "immediate_alert",
  },

  dataExfiltration: {
    threshold: "1GB",
    timeWindow: "1h",
    action: "rate_limit",
  },
};
```

### 5. Regular Security Maintenance

```javascript
// Regular security tasks
const securityMaintenance = {
  weekly: [
    "Review user access logs",
    "Check for unused accounts",
    "Verify role assignments",
  ],

  monthly: [
    "Rotate service account passwords",
    "Review custom roles",
    "Update security patches",
  ],

  quarterly: [
    "Security audit",
    "Penetration testing",
    "Review encryption keys",
  ],
};

// Script to find inactive users
db.adminCommand("listCollections").cursor.firstBatch.forEach(function (
  collection
) {
  if (collection.name === "system.users") {
    db.system.users.find().forEach(function (user) {
      // Check last authentication time
      const lastAuth = user.customData?.lastAuthentication;
      if (!lastAuth || new Date() - lastAuth > 90 * 24 * 60 * 60 * 1000) {
        print("Inactive user: " + user.user);
      }
    });
  }
});
```

## Common Security Configurations {#common-configurations}

### Development Environment

```yaml
# mongod-dev.conf
security:
  authorization: enabled

net:
  bindIp: 127.0.0.1
  port: 27017

systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
```

### Production Environment

```yaml
# mongod-prod.conf
security:
  authorization: enabled
  keyFile: /etc/mongodb/replica-set-key

net:
  bindIp: 10.0.1.100,10.0.1.101,10.0.1.102
  port: 27017
  ssl:
    mode: requireSSL
    PEMKeyFile: /etc/ssl/mongodb.pem
    CAFile: /etc/ssl/ca.pem

auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json

storage:
  wiredTiger:
    engineConfig:
      configString: "encryption=(name=AES256-CBC)"
```

### Replica Set Security

```javascript
// Generate keyfile for replica set
// openssl rand -base64 756 > /etc/mongodb/replica-set-key
// chmod 400 /etc/mongodb/replica-set-key

// Initialize replica set with authentication
rs.initiate({
  _id: "myReplicaSet",
  members: [
    { _id: 0, host: "mongo1:27017" },
    { _id: 1, host: "mongo2:27017" },
    { _id: 2, host: "mongo3:27017" },
  ],
});
```

## Troubleshooting {#troubleshooting}

### Common Authentication Issues

#### 1. Authentication Failed

```javascript
// Error: Authentication failed
// Solution: Check username, password, and authSource
mongosh "mongodb://user:pass@host:27017/mydb?authSource=admin"

// Verify user exists
use admin
db.getUser("username")
```

#### 2. Authorization Errors

```javascript
// Error: not authorized on db to execute command
// Solution: Check user roles and permissions
db.runCommand({
  usersInfo: "username",
  showCredentials: false,
  showPrivileges: true,
});
```

#### 3. SSL/TLS Connection Issues

```bash
# Test SSL connection
mongosh --ssl \
  --sslCAFile /path/to/ca.pem \
  --sslPEMKeyFile /path/to/client.pem \
  --host hostname:27017

# Verify certificate
openssl x509 -in /path/to/cert.pem -text -noout
```

### Security Checklist

```javascript
const securityChecklist = {
  authentication: [
    "✓ Authentication enabled",
    "✓ Strong admin password set",
    "✓ Service accounts created with minimal privileges",
    "✓ Default users removed or secured",
  ],

  authorization: [
    "✓ Role-based access control implemented",
    "✓ Custom roles created for specific needs",
    "✓ Principle of least privilege followed",
    "✓ Regular access reviews conducted",
  ],

  network: [
    "✓ Firewall configured",
    "✓ IP whitelisting enabled",
    "✓ Non-standard port used (optional)",
    "✓ SSL/TLS encryption enabled",
  ],

  monitoring: [
    "✓ Audit logging enabled",
    "✓ Failed login monitoring",
    "✓ Administrative action logging",
    "✓ Alert system configured",
  ],

  encryption: [
    "✓ Encryption at rest enabled",
    "✓ Encryption in transit enabled",
    "✓ Key management system configured",
    "✓ Field-level encryption for sensitive data",
  ],
};
```

## References

- [MongoDB Security Documentation](https://docs.mongodb.com/manual/security/)
- [MongoDB Authentication](https://docs.mongodb.com/manual/core/authentication/)
- [MongoDB Authorization](https://docs.mongodb.com/manual/core/authorization/)
- [MongoDB Encryption](https://docs.mongodb.com/manual/core/security-encryption/)
- [MongoDB Auditing](https://docs.mongodb.com/manual/core/auditing/)
- [Security Best Practices](https://docs.mongodb.com/manual/administration/security-checklist/)
