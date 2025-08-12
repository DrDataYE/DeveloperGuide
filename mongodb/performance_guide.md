# MongoDB Performance Optimization: Complete Guide

This comprehensive guide covers all aspects of MongoDB performance optimization, from indexing strategies to query optimization, hardware considerations, and monitoring techniques.

## Table of Contents

1. [Performance Overview](#performance-overview)
2. [Indexing Strategies](#indexing-strategies)
3. [Query Optimization](#query-optimization)
4. [Schema Design for Performance](#schema-design)
5. [Hardware and Infrastructure](#hardware-infrastructure)
6. [Memory Management](#memory-management)
7. [Connection Management](#connection-management)
8. [Monitoring and Profiling](#monitoring-profiling)
9. [Capped Collections](#capped-collections)
10. [Sharding for Performance](#sharding-performance)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

## Performance Overview {#performance-overview}

MongoDB performance depends on several key factors:

### Performance Factors

- **Indexing**: Proper indexes for query patterns
- **Schema Design**: Document structure and relationships
- **Query Patterns**: How data is accessed and modified
- **Hardware**: CPU, RAM, storage, and network
- **Configuration**: MongoDB settings and parameters
- **Data Size**: Working set size vs. available memory

### Performance Metrics to Monitor

```javascript
// Key performance indicators
const performanceMetrics = {
  queryPerformance: [
    "Query execution time",
    "Documents examined vs returned",
    "Index usage efficiency",
    "Query plan stability",
  ],

  systemResources: [
    "CPU utilization",
    "Memory usage (resident vs virtual)",
    "Disk I/O (read/write operations)",
    "Network bandwidth utilization",
  ],

  databaseMetrics: [
    "Operations per second (ops/sec)",
    "Connection count",
    "Lock percentage",
    "Cache hit ratio",
  ],
};
```

## Indexing Strategies {#indexing-strategies}

Proper indexing is crucial for MongoDB performance. Indexes provide fast access paths to data but come with storage and write performance costs.

### Single Field Indexes

```javascript
// Basic single field index
db.users.createIndex({ email: 1 });

// Compound query on indexed field
db.users.find({ email: "user@example.com" });

// Range queries benefit from indexes
db.orders.createIndex({ orderDate: 1 });
db.orders.find({
  orderDate: {
    $gte: ISODate("2023-01-01"),
    $lte: ISODate("2023-12-31"),
  },
});
```

### Compound Indexes

```javascript
// Compound index - order matters!
db.products.createIndex({
  category: 1, // First: equality queries
  price: 1, // Second: range queries
  createdAt: -1, // Third: sort field
});

// Efficient queries using compound index
db.products
  .find({ category: "electronics", price: { $gte: 100 } })
  .sort({ createdAt: -1 });

// Index prefixes are also efficient
db.products.find({ category: "electronics" }); // Uses index
db.products.find({ category: "electronics", price: { $gte: 100 } }); // Uses index
```

### Index Types and Use Cases

#### 1. Text Indexes

```javascript
// Text search index
db.articles.createIndex(
  {
    title: "text",
    content: "text",
  },
  {
    weights: { title: 10, content: 1 },
    default_language: "english",
  }
);

// Text search query
db.articles.find({ $text: { $search: "mongodb performance" } });
```

#### 2. Geospatial Indexes

```javascript
// 2dsphere index for geospatial queries
db.places.createIndex({ location: "2dsphere" });

// Geospatial query
db.places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-73.9857, 40.7484] },
      $maxDistance: 1000,
    },
  },
});
```

#### 3. Sparse Indexes

```javascript
// Sparse index - only indexes documents with the field
db.users.createIndex(
  {
    optionalField: 1,
  },
  {
    sparse: true,
  }
);

// Useful for optional fields to save space
```

#### 4. Partial Indexes

```javascript
// Partial index - indexes subset of collection
db.orders.createIndex(
  { status: 1, orderDate: 1 },
  {
    partialFilterExpression: {
      status: { $in: ["pending", "processing"] },
    },
  }
);

// More efficient for queries on specific document subsets
```

#### 5. TTL Indexes

```javascript
// TTL index for automatic document expiration
db.sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 3600 } // 1 hour
);

// Documents automatically deleted after expiration
```

### Index Best Practices

#### 1. ESR Rule (Equality, Sort, Range)

```javascript
// Optimal compound index order
db.orders.createIndex({
  customerId: 1, // Equality
  status: 1, // Equality
  orderDate: -1, // Sort
  amount: 1, // Range
});

// Query that benefits from ESR ordering
db.orders
  .find({
    customerId: ObjectId("..."),
    status: "pending",
    amount: { $gte: 100 },
  })
  .sort({ orderDate: -1 });
```

#### 2. Index Intersection

```javascript
// Multiple single-field indexes can be combined
db.inventory.createIndex({ category: 1 });
db.inventory.createIndex({ price: 1 });
db.inventory.createIndex({ inStock: 1 });

// MongoDB can use multiple indexes for this query
db.inventory.find({
  category: "electronics",
  price: { $gte: 100, $lte: 500 },
  inStock: true,
});
```

#### 3. Index Monitoring

```javascript
// Monitor index usage
db.collection.aggregate([{ $indexStats: {} }]);

// Find unused indexes
db.runCommand({ planCacheClear: "collection" });
db.collection.find().explain("executionStats");

// Index size and statistics
db.stats();
db.collection.totalIndexSize();
```

## Query Optimization {#query-optimization}

### Query Analysis with explain()

```javascript
// Basic explain
db.users.find({ age: { $gte: 25 } }).explain();

// Detailed execution statistics
db.users.find({ age: { $gte: 25 } }).explain("executionStats");

// Query planner information
db.users.find({ age: { $gte: 25 } }).explain("queryPlanner");

// All available information
db.users.find({ age: { $gte: 25 } }).explain("allPlansExecution");
```

### Understanding Explain Output

```javascript
// Key metrics in explain output
const explainMetrics = {
  executionStats: {
    totalDocsExamined: 1000, // Documents scanned
    totalDocsReturned: 50, // Documents returned
    executionTimeMillis: 45, // Total execution time
    indexesUsed: ["age_1"], // Indexes utilized
    stage: "IXSCAN", // Execution stage type
  },

  // Ideal ratios
  efficiency: {
    examineRatio: "totalDocsReturned / totalDocsExamined", // Target: close to 1.0
    indexUsage: "should use IXSCAN, not COLLSCAN",
    executionTime: "should be < 100ms for most queries",
  },
};
```

### Query Optimization Techniques

#### 1. Selective Queries

```javascript
// BAD: Non-selective query
db.users.find({ active: true }); // If 90% of users are active

// GOOD: More selective query
db.users.find({
  active: true,
  lastLogin: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) },
});
```

#### 2. Projection to Reduce Network Transfer

```javascript
// BAD: Return all fields
db.users.find({ age: { $gte: 25 } });

// GOOD: Return only needed fields
db.users.find({ age: { $gte: 25 } }, { name: 1, email: 1, _id: 0 });
```

#### 3. Limit and Skip Optimization

```javascript
// BAD: Large skip values are expensive
db.posts.find().skip(10000).limit(10);

// GOOD: Use range queries instead
db.posts
  .find({
    _id: { $gt: lastSeenId },
  })
  .limit(10)
  .sort({ _id: 1 });
```

#### 4. Aggregation Pipeline Optimization

```javascript
// BAD: Filter after grouping
db.orders.aggregate([
  { $group: { _id: "$customerId", total: { $sum: "$amount" } } },
  { $match: { total: { $gte: 1000 } } },
]);

// GOOD: Filter early in pipeline
db.orders.aggregate([
  { $match: { amount: { $gte: 100 } } }, // Filter first
  { $group: { _id: "$customerId", total: { $sum: "$amount" } } },
  { $match: { total: { $gte: 1000 } } },
]);
```

### Query Patterns and Anti-Patterns

#### Efficient Patterns

```javascript
// 1. Use indexes effectively
db.users.find({ email: "user@example.com" }); // Indexed field

// 2. Combine filters efficiently
db.products.find({
  category: "electronics", // Indexed
  price: { $gte: 100, $lte: 500 }, // Range on indexed field
  inStock: true, // Additional filter
});

// 3. Use covered queries when possible
db.users
  .find({ age: { $gte: 25 } }, { name: 1, age: 1, _id: 0 })
  .hint({ age: 1, name: 1 });
```

#### Anti-Patterns to Avoid

```javascript
// 1. Avoid regex at beginning of string
// BAD
db.users.find({ name: /^John.*/ });
// GOOD
db.users.find({ name: { $gte: "John", $lt: "Joho" } });

// 2. Avoid negation queries
// BAD
db.users.find({ status: { $ne: "inactive" } });
// GOOD
db.users.find({ status: { $in: ["active", "pending"] } });

// 3. Avoid large $in arrays
// BAD
db.products.find({
  _id: {
    $in: [
      /* 1000+ IDs */
    ],
  },
});
// GOOD: Use multiple smaller queries or redesign schema
```

## Schema Design for Performance {#schema-design}

### Document Structure Optimization

#### 1. Embedding vs. Referencing

```javascript
// Embedding - good for read performance
const blogPostEmbedded = {
  _id: ObjectId(),
  title: "MongoDB Performance",
  content: "...",
  comments: [
    { author: "John", text: "Great post!", date: new Date() },
    { author: "Jane", text: "Very helpful", date: new Date() },
  ],
};

// Referencing - good for write performance and data consistency
const blogPostReferenced = {
  _id: ObjectId(),
  title: "MongoDB Performance",
  content: "...",
};

const comments = [
  { _id: ObjectId(), postId: ObjectId(), author: "John", text: "Great post!" },
  { _id: ObjectId(), postId: ObjectId(), author: "Jane", text: "Very helpful" },
];
```

#### 2. Array Optimization

```javascript
// BAD: Large arrays hurt performance
const userWithManyTags = {
  _id: ObjectId(),
  name: "John",
  tags: [
    /* 1000+ tags */
  ], // Avoid large arrays
};

// GOOD: Separate collection for many-to-many relationships
const user = {
  _id: ObjectId(),
  name: "John",
};

const userTags = [
  { userId: ObjectId(), tag: "developer" },
  { userId: ObjectId(), tag: "mongodb" },
];
```

#### 3. Field Naming and Size

```javascript
// BAD: Long field names waste space
const inefficientDoc = {
  veryLongFieldNameThatWastesSpace: "value",
  anotherUnnecessarilyLongFieldName: "value",
};

// GOOD: Shorter field names
const efficientDoc = {
  title: "value", // or 't' for extreme optimization
  content: "value", // or 'c' for extreme optimization
};
```

### Data Type Optimization

```javascript
// Choose appropriate data types for performance
const optimizedDocument = {
  // Use ObjectId for references (12 bytes)
  userId: ObjectId("507f1f77bcf86cd799439011"),

  // Use NumberInt for small integers (4 bytes vs 8 for double)
  count: NumberInt(42),

  // Use NumberLong for large integers (8 bytes)
  timestamp: NumberLong(Date.now()),

  // Use NumberDecimal only when precision is critical (16 bytes)
  price: NumberDecimal("19.99"),

  // Use boolean instead of strings
  isActive: true, // Not "true" or "active"

  // Use dates for temporal data
  createdAt: new Date(), // Not timestamp strings

  // Use arrays efficiently
  tags: ["tag1", "tag2"], // Not "tag1,tag2"
};
```

## Hardware and Infrastructure {#hardware-infrastructure}

### Hardware Considerations

#### 1. Memory (RAM)

```javascript
// Monitor memory usage
db.serverStatus().mem;
/*
{
  resident: 1024,    // Physical memory used (MB)
  virtual: 2048,     // Virtual memory used (MB)
  mapped: 512,       // Memory-mapped files (MB)
  mappedWithJournal: 1024
}
*/

// Calculate working set size
const workingSetSize = {
  indexSize: db.stats().indexSize,
  hotData: "Frequently accessed documents",
  recommendation: "RAM >= working set size for optimal performance",
};
```

#### 2. Storage (Disk)

```javascript
// Monitor disk I/O
db.serverStatus().wiredTiger.cache;
/*
{
  "bytes currently in the cache": 1073741824,
  "maximum bytes configured": 2147483648,
  "pages read into cache": 12345,
  "pages written from cache": 6789
}
*/

// Storage best practices
const storageGuidelines = {
  ssd: "Recommended for production workloads",
  raid10: "Best for write-heavy applications",
  separateJournal: "Place journal on separate disk",
  dataDirectory: "/data/db on fast storage",
};
```

#### 3. CPU and Network

```javascript
// Monitor CPU usage
db.serverStatus().extra_info;
/*
{
  note: "fields vary by platform",
  page_faults: 123,
  user_time_us: 456789,
  system_time_us: 123456
}
*/

// Network optimization
const networkOptimization = {
  compression: "Enable wire protocol compression",
  connectionPooling: "Use connection pooling in applications",
  locality: "Place MongoDB near application servers",
};
```

### MongoDB Configuration Optimization

```yaml
# mongod.conf optimizations
storage:
  wiredTiger:
    engineConfig:
      # Adjust cache size (default: 50% of RAM - 1GB)
      cacheSizeGB: 8
      # Set journal commit interval (10-300ms)
      journalCompressor: snappy
    collectionConfig:
      # Default compression
      blockCompressor: snappy
    indexConfig:
      # Index compression
      prefixCompression: true

# Network settings
net:
  maxIncomingConnections: 1000
  wireObjectCheck: false

# Operation profiling
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100

# Set log level
systemLog:
  verbosity: 0
```

## Memory Management {#memory-management}

### WiredTiger Cache Management

```javascript
// Monitor cache statistics
db.serverStatus().wiredTiger.cache;

// Key cache metrics
const cacheMetrics = {
  bytesInCache: "Current cache usage",
  maxBytesConfigured: "Maximum cache size",
  pagesReadIntoCache: "Cache misses",
  pagesWrittenFromCache: "Cache evictions",
  hitRatio: "Cache efficiency",
};

// Calculate cache hit ratio
const cacheStats = db.serverStatus().wiredTiger.cache;
const hitRatio =
  (cacheStats["pages read into cache"] -
    cacheStats["pages requested from the cache"]) /
  cacheStats["pages read into cache"];
```

### Memory Optimization Techniques

```javascript
// 1. Index optimization for memory
db.collection.aggregate([
  { $indexStats: {} },
  {
    $project: {
      name: "$name",
      size: "$spec",
      usageCount: "$accesses.ops",
    },
  },
  { $sort: { usageCount: 1 } }, // Find least used indexes
]);

// 2. Document size optimization
db.collection.aggregate([
  {
    $project: {
      size: { $bsonSize: "$$ROOT" },
      _id: 1,
    },
  },
  { $sort: { size: -1 } },
  { $limit: 10 }, // Find largest documents
]);

// 3. Working set analysis
const workingSetAnalysis = {
  frequently_accessed: "Documents accessed in last 24 hours",
  index_usage: "Indexes used in recent queries",
  memory_requirement: "Hot data that should fit in RAM",
};
```

## Connection Management {#connection-management}

### Connection Pool Optimization

```javascript
// Application connection configuration
const MongoClient = require("mongodb").MongoClient;

const client = new MongoClient(uri, {
  maxPoolSize: 100, // Maximum connections in pool
  minPoolSize: 5, // Minimum connections maintained
  maxIdleTimeMS: 30000, // Close connections after 30s idle
  waitQueueTimeoutMS: 5000, // Wait 5s for available connection
  serverSelectionTimeoutMS: 5000, // Server selection timeout

  // Connection monitoring
  monitorCommands: true,

  // Read preferences for performance
  readPreference: "secondaryPreferred",
  readConcern: { level: "local" },
});
```

### Connection Monitoring

```javascript
// Monitor connections
db.serverStatus().connections;
/*
{
  current: 25,      // Current open connections
  available: 975,   // Available connections
  totalCreated: 1234 // Total connections created
}
*/

// Connection pool diagnostics
const connectionDiagnostics = {
  activeConnections: "Connections currently processing operations",
  availableConnections: "Idle connections ready for use",
  connectionPoolSize: "Total connections in pool",
  connectionTurnover: "Rate of connection creation/destruction",
};
```

## Monitoring and Profiling {#monitoring-profiling}

### Database Profiling

```javascript
// Enable profiling for slow operations
db.setProfilingLevel(2, { slowms: 100 });

// Profile specific operations
db.setProfilingLevel(2, {
  slowms: 0,
  filter: {
    op: { $in: ["insert", "update", "delete"] },
  },
});

// Analyze profiling data
db.system.profile.find().limit(5).sort({ ts: -1 }).pretty();

// Common profiling queries
db.system.profile
  .find({
    ts: { $gte: new Date(Date.now() - 3600000) }, // Last hour
    millis: { $gte: 100 }, // Slow operations
  })
  .sort({ millis: -1 });
```

### Performance Monitoring Queries

```javascript
// Current operations
db.currentOp();

// Current operations taking longer than 1 second
db.currentOp({ secs_running: { $gte: 1 } });

// Kill long-running operation
db.killOp(operationId);

// Server status overview
const serverStatus = db.serverStatus();
const keyMetrics = {
  uptime: serverStatus.uptime,
  connections: serverStatus.connections,
  opcounters: serverStatus.opcounters,
  memory: serverStatus.mem,
  locks: serverStatus.locks,
};
```

### Custom Monitoring Scripts

```javascript
// Performance monitoring script
function monitorPerformance() {
  const stats = db.serverStatus();

  const metrics = {
    timestamp: new Date(),

    // Connection metrics
    connections: {
      current: stats.connections.current,
      available: stats.connections.available,
    },

    // Operation counters
    operations: {
      insert: stats.opcounters.insert,
      query: stats.opcounters.query,
      update: stats.opcounters.update,
      delete: stats.opcounters.delete,
    },

    // Memory usage
    memory: {
      resident: stats.mem.resident,
      virtual: stats.mem.virtual,
      mapped: stats.mem.mapped,
    },

    // Cache statistics
    cache: {
      size: stats.wiredTiger?.cache?.["bytes currently in the cache"],
      maxSize: stats.wiredTiger?.cache?.["maximum bytes configured"],
    },
  };

  // Store metrics for analysis
  db.performanceMetrics.insertOne(metrics);

  return metrics;
}

// Run monitoring every minute
setInterval(monitorPerformance, 60000);
```

## Capped Collections {#capped-collections}

Capped collections provide high-performance fixed-size collections ideal for logging and caching scenarios.

### Creating and Using Capped Collections

```javascript
// Create capped collection for logs
db.createCollection("logs", {
  capped: true,
  size: 100000000, // 100MB
  max: 50000, // Maximum 50,000 documents
});

// Create capped collection for real-time data
db.createCollection("sensorData", {
  capped: true,
  size: 50000000, // 50MB
  max: 10000, // Maximum 10,000 readings
});
```

### Capped Collection Benefits

```javascript
// Performance characteristics
const cappedCollectionBenefits = {
  insertPerformance: "Very fast inserts (no index overhead)",
  queryPerformance: "Fast natural order queries",
  diskUsage: "Fixed size, predictable storage",
  maintenance: "Automatic old document removal",

  useCases: [
    "Application logs",
    "Real-time sensor data",
    "Chat messages",
    "Audit trails",
    "Cache storage",
  ],
};

// High-performance logging pattern
function logEvent(level, message, metadata) {
  db.logs.insertOne({
    timestamp: new Date(),
    level: level,
    message: message,
    metadata: metadata,
    hostname: process.env.HOSTNAME,
  });
}

// Tailable cursor for real-time processing
const cursor = db.logs.find({}, { tailable: true, awaitData: true });
cursor.forEach(function (doc) {
  // Process log entry in real-time
  processLogEntry(doc);
});
```

### Capped Collection Monitoring

```javascript
// Monitor capped collection statistics
db.logs.stats();

// Check if collection is capped
db.logs.isCapped();

// Convert regular collection to capped
db.runCommand({
  convertToCapped: "regularCollection",
  size: 100000000,
});
```

## Sharding for Performance {#sharding-performance}

### Shard Key Selection

```javascript
// Good shard key characteristics
const goodShardKey = {
  highCardinality: "Many possible values",
  evenDistribution: "Values distributed evenly",
  queryIsolation: "Queries target specific shards",
  writeScaling: "Writes distributed across shards",
};

// Examples of effective shard keys
const shardKeyExamples = {
  // User data sharded by user ID
  userShardKey: { userId: 1 },

  // Time-series data with compound key
  timeSeriesShardKey: { deviceId: 1, timestamp: 1 },

  // Geographic data
  geoShardKey: { region: 1, customerId: 1 },

  // Hash-based for even distribution
  hashShardKey: { _id: "hashed" },
};
```

### Sharding Configuration

```javascript
// Enable sharding on database
sh.enableSharding("myapp");

// Shard collection with appropriate key
sh.shardCollection("myapp.users", { userId: 1 });

// Monitor shard distribution
sh.status();

// Analyze chunk distribution
db.chunks.find({ ns: "myapp.users" }).count();

// Balance shards
sh.enableBalancing("myapp.users");
```

## Best Practices {#best-practices}

### 1. Index Best Practices

```javascript
const indexBestPractices = {
  creation: [
    "Create indexes before importing large datasets",
    "Build indexes during low-traffic periods",
    "Use background: true for production systems",
    "Monitor index creation progress",
  ],

  maintenance: [
    "Regularly review index usage statistics",
    "Remove unused indexes",
    "Rebuild fragmented indexes",
    "Monitor index size vs collection size",
  ],

  optimization: [
    "Follow ESR rule for compound indexes",
    "Use partial indexes for subset queries",
    "Consider sparse indexes for optional fields",
    "Use TTL indexes for time-based data",
  ],
};
```

### 2. Query Best Practices

```javascript
const queryBestPractices = {
  design: [
    "Design queries around your indexes",
    "Use explain() to analyze query performance",
    "Prefer equality matches over range queries",
    "Limit result sets appropriately",
  ],

  patterns: [
    "Use projection to reduce network transfer",
    "Batch operations when possible",
    "Use aggregation pipeline efficiently",
    "Avoid large skip() operations",
  ],

  monitoring: [
    "Profile slow queries regularly",
    "Monitor query patterns in production",
    "Set up alerts for performance degradation",
    "Review and optimize based on usage patterns",
  ],
};
```

### 3. Application Design Patterns

```javascript
// Connection pooling
const connectionPool = {
  maxConnections: 100,
  minConnections: 10,
  idleTimeout: 30000,

  // Monitor pool health
  healthCheck: function () {
    return {
      active: this.activeConnections,
      idle: this.idleConnections,
      total: this.totalConnections,
    };
  },
};

// Batch operations for efficiency
async function batchInsert(documents) {
  const batchSize = 1000;

  for (let i = 0; i < documents.length; i += batchSize) {
    const batch = documents.slice(i, i + batchSize);
    await db.collection.insertMany(batch, { ordered: false });
  }
}

// Read preferences for scaling
const readPreferences = {
  primary: "Consistency required",
  primaryPreferred: "Consistency preferred, availability secondary",
  secondary: "Read scaling, eventual consistency OK",
  secondaryPreferred: "Read scaling preferred",
  nearest: "Lowest latency",
};
```

## Troubleshooting {#troubleshooting}

### Common Performance Issues

#### 1. Slow Queries

```javascript
// Identify slow queries
db.setProfilingLevel(2, { slowms: 100 });

// Analyze slow query patterns
db.system.profile.aggregate([
  { $match: { ts: { $gte: new Date(Date.now() - 3600000) } } },
  {
    $group: {
      _id: "$command.find",
      count: { $sum: 1 },
      avgTime: { $avg: "$millis" },
      maxTime: { $max: "$millis" },
    },
  },
  { $sort: { avgTime: -1 } },
]);
```

#### 2. High Memory Usage

```javascript
// Check memory usage
const memStats = db.serverStatus().mem;
const wiredTigerCache = db.serverStatus().wiredTiger.cache;

// Investigate large documents
db.collection.aggregate([
  { $project: { size: { $bsonSize: "$$ROOT" } } },
  { $match: { size: { $gte: 16000000 } } }, // > 16MB
  { $sort: { size: -1 } },
  { $limit: 10 },
]);
```

#### 3. Lock Contention

```javascript
// Monitor lock statistics
db.serverStatus().locks;

// Identify locking operations
db.currentOp({
  $or: [
    { "locks.Global.acquireCount.r": { $exists: true } },
    { "locks.Global.acquireCount.w": { $exists: true } },
  ],
});
```

### Performance Tuning Checklist

```javascript
const performanceTuningChecklist = {
  indexes: [
    "☐ Appropriate indexes for query patterns",
    "☐ Compound indexes follow ESR rule",
    "☐ No unused indexes",
    "☐ Index sizes are reasonable",
  ],

  queries: [
    "☐ Query patterns analyzed with explain()",
    "☐ Selective queries (good examine ratio)",
    "☐ Appropriate use of projections",
    "☐ Minimal use of skip() operations",
  ],

  schema: [
    "☐ Document structure optimized",
    "☐ Appropriate embedding vs referencing",
    "☐ Field names optimized for size",
    "☐ Data types chosen efficiently",
  ],

  infrastructure: [
    "☐ Sufficient RAM for working set",
    "☐ Fast storage (SSD recommended)",
    "☐ Proper network configuration",
    "☐ MongoDB configuration optimized",
  ],

  monitoring: [
    "☐ Performance monitoring in place",
    "☐ Alerting configured",
    "☐ Regular performance reviews",
    "☐ Capacity planning performed",
  ],
};
```

## References

- [MongoDB Performance Best Practices](https://docs.mongodb.com/manual/administration/analyzing-mongodb-performance/)
- [Indexing Strategies](https://docs.mongodb.com/manual/applications/indexes/)
- [Query Optimization](https://docs.mongodb.com/manual/core/query-optimization/)
- [Hardware and OS Configuration](https://docs.mongodb.com/manual/administration/production-notes/)
- [WiredTiger Storage Engine](https://docs.mongodb.com/manual/core/wiredtiger/)
- [Sharding Guide](https://docs.mongodb.com/manual/sharding/)
