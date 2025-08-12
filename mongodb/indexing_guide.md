# MongoDB Indexing: Complete Guide

This comprehensive guide covers all aspects of MongoDB indexing, from basic concepts to advanced optimization techniques, providing the knowledge needed to design efficient database schemas and queries.

## Table of Contents

1. [Indexing Overview](#indexing-overview)
2. [Index Types](#index-types)
3. [Single Field Indexes](#single-field-indexes)
4. [Compound Indexes](#compound-indexes)
5. [Multikey Indexes](#multikey-indexes)
6. [Text Indexes](#text-indexes)
7. [Geospatial Indexes](#geospatial-indexes)
8. [Special Index Types](#special-index-types)
9. [Index Properties](#index-properties)
10. [Index Management](#index-management)
11. [Query Optimization](#query-optimization)
12. [Performance Monitoring](#performance-monitoring)
13. [Best Practices](#best-practices)

## Indexing Overview {#indexing-overview}

Indexes are special data structures that improve the speed of data retrieval operations on a collection. They create shortcuts to data based on the values of one or more fields.

### How Indexes Work

```javascript
// Without index: Collection scan
db.users.find({ email: "john@example.com" });
// MongoDB examines every document

// With index: Index scan
db.users.createIndex({ email: 1 });
db.users.find({ email: "john@example.com" });
// MongoDB uses index to quickly locate document
```

### Index Benefits and Costs

```javascript
const indexTradeoffs = {
  benefits: [
    "Faster query execution",
    "Efficient sorting",
    "Quick range queries",
    "Unique constraint enforcement",
  ],

  costs: [
    "Additional storage space",
    "Slower write operations",
    "Memory overhead",
    "Maintenance complexity",
  ],
};
```

### Default \_id Index

```javascript
// Every collection automatically has an index on _id
db.users.getIndexes();
/*
[
  {
    "v": 2,
    "key": { "_id": 1 },
    "name": "_id_"
  }
]
*/

// _id index cannot be dropped
// db.users.dropIndex("_id_")  // This will fail
```

## Index Types {#index-types}

### Index Direction

```javascript
// Ascending index (1)
db.users.createIndex({ age: 1 });

// Descending index (-1)
db.users.createIndex({ createdAt: -1 });

// For single-field indexes, direction doesn't matter for simple queries
db.users.find({ age: 25 }); // Uses index regardless of direction
db.users.find().sort({ age: 1 }); // Ascending sort
db.users.find().sort({ age: -1 }); // Descending sort (may be slower with ascending index)
```

### B-Tree Indexes (Default)

```javascript
// Standard B-tree index for most use cases
db.products.createIndex({ category: 1 });
db.products.createIndex({ price: 1 });
db.products.createIndex({ category: 1, price: 1 });

// B-tree indexes support:
// - Equality matches
// - Range queries
// - Sorting
// - Prefix matching (for compound indexes)
```

## Single Field Indexes {#single-field-indexes}

### Creating Single Field Indexes

```javascript
// Basic single field index
db.users.createIndex({ email: 1 });

// Index on nested field
db.users.createIndex({ "profile.location": 1 });

// Index with options
db.users.createIndex(
  { email: 1 },
  {
    unique: true,
    name: "unique_email_index",
    background: true,
  }
);
```

### Single Field Index Use Cases

```javascript
// Equality queries
db.users.find({ email: "john@example.com" });

// Range queries
db.products.createIndex({ price: 1 });
db.products.find({ price: { $gte: 100, $lte: 500 } });

// Sorting
db.orders.createIndex({ orderDate: -1 });
db.orders.find().sort({ orderDate: -1 });

// Regex queries (prefix matching)
db.users.createIndex({ lastName: 1 });
db.users.find({ lastName: /^Smith/ });
```

### Performance Characteristics

```javascript
// Analyze single field index performance
db.users.find({ email: "john@example.com" }).explain("executionStats");

// Key metrics to examine:
const indexMetrics = {
  executionTimeMillis: "Total query time",
  totalDocsExamined: "Documents scanned",
  totalDocsReturned: "Documents returned",
  stage: "IXSCAN (good) vs COLLSCAN (bad)",
  indexesUsed: "Which indexes were utilized",
};
```

## Compound Indexes {#compound-indexes}

Compound indexes contain references to multiple fields and are crucial for optimizing complex queries.

### Creating Compound Indexes

```javascript
// Basic compound index
db.users.createIndex({ department: 1, age: 1 });

// Three-field compound index
db.products.createIndex({
  category: 1,
  brand: 1,
  price: -1,
});

// Mixed data types in compound index
db.events.createIndex({
  userId: 1, // ObjectId
  eventType: 1, // String
  timestamp: -1, // Date
});
```

### ESR Rule (Equality, Sort, Range)

```javascript
// Optimal compound index design follows ESR rule
db.orders.createIndex({
  customerId: 1, // Equality queries
  status: 1, // Equality queries
  orderDate: -1, // Sort field
  amount: 1, // Range queries
});

// Query that benefits from ESR ordering
db.orders
  .find({
    customerId: ObjectId("..."), // Equality
    status: "shipped", // Equality
    amount: { $gte: 100 }, // Range
  })
  .sort({ orderDate: -1 }); // Sort
```

### Index Prefix Usage

```javascript
// Compound index: { a: 1, b: 1, c: 1 }
db.collection.createIndex({ category: 1, brand: 1, price: 1 });

// These queries can use the index (prefixes):
db.collection.find({ category: "electronics" }); // {category}
db.collection.find({ category: "electronics", brand: "Apple" }); // {category, brand}
db.collection.find({ category: "electronics", brand: "Apple", price: 500 }); // {category, brand, price}

// These queries CANNOT efficiently use the index:
db.collection.find({ brand: "Apple" }); // Missing first field
db.collection.find({ brand: "Apple", price: 500 }); // Missing first field
db.collection.find({ category: "electronics", price: 500 }); // Missing middle field (b)
```

### Compound Index Query Patterns

```javascript
// User activity tracking
db.activities.createIndex({
  userId: 1,
  eventType: 1,
  timestamp: -1,
});

// Efficient queries using this index:
db.activities.find({ userId: ObjectId("...") }).sort({ timestamp: -1 });

db.activities
  .find({
    userId: ObjectId("..."),
    eventType: "login",
  })
  .sort({ timestamp: -1 });

db.activities.find({
  userId: ObjectId("..."),
  eventType: "purchase",
  timestamp: { $gte: lastWeek },
});
```

### Index Intersection

```javascript
// MongoDB can use multiple single-field indexes together
db.inventory.createIndex({ category: 1 });
db.inventory.createIndex({ supplier: 1 });
db.inventory.createIndex({ inStock: 1 });

// This query might use index intersection
db.inventory.find({
  category: "electronics",
  supplier: "ACME Corp",
  inStock: true,
});

// However, a compound index is usually more efficient
db.inventory.createIndex({
  category: 1,
  supplier: 1,
  inStock: 1,
});
```

## Multikey Indexes {#multikey-indexes}

Multikey indexes are automatically created when indexing array fields.

### Array Field Indexing

```javascript
// Document with array field
const product = {
  _id: ObjectId(),
  name: "Smartphone",
  tags: ["electronics", "mobile", "communication"],
  features: ["waterproof", "fast-charging", "wireless"],
};

// Create index on array field (becomes multikey)
db.products.createIndex({ tags: 1 });

// Query array elements
db.products.find({ tags: "electronics" }); // Matches array element
db.products.find({ tags: { $in: ["mobile", "tech"] } }); // Matches any element
```

### Compound Multikey Indexes

```javascript
// Index with both regular and array fields
db.products.createIndex({
  category: 1, // Regular field
  tags: 1, // Array field (multikey)
});

// Limitation: At most one array field per compound index
// This is NOT allowed:
// db.products.createIndex({ tags: 1, features: 1 })  // Error: both are arrays

// Efficient queries
db.products.find({
  category: "electronics",
  tags: "smartphone",
});
```

### Array of Objects Indexing

```javascript
// Document with array of objects
const blog = {
  _id: ObjectId(),
  title: "MongoDB Tutorial",
  comments: [
    { author: "John", rating: 5, date: new Date() },
    { author: "Jane", rating: 4, date: new Date() },
  ],
};

// Index on nested field in array
db.blogs.createIndex({ "comments.author": 1 });
db.blogs.createIndex({ "comments.rating": 1 });

// Compound index with array field
db.blogs.createIndex({
  title: 1,
  "comments.rating": 1,
});

// Query nested array fields
db.blogs.find({ "comments.author": "John" });
db.blogs.find({ "comments.rating": { $gte: 4 } });
```

### Multikey Index Performance

```javascript
// Monitor multikey index usage
db.products.find({ tags: "electronics" }).explain("executionStats");

// Multikey indexes are larger and may be slower than single-key indexes
// Consider these optimizations:

// 1. Limit array size
const optimizedProduct = {
  tags: ["primary-tag", "secondary-tag"], // Limit to 2-3 most important tags
  allTags: "electronics mobile communication", // Store as searchable text
};

// 2. Use text index for large tag arrays
db.products.createIndex({ allTags: "text" });
db.products.find({ $text: { $search: "electronics mobile" } });
```

## Text Indexes {#text-indexes}

Text indexes provide powerful full-text search capabilities.

### Creating Text Indexes

```javascript
// Single field text index
db.articles.createIndex({ content: "text" });

// Multiple field text index
db.articles.createIndex({
  title: "text",
  content: "text",
  tags: "text",
});

// Text index with weights
db.articles.createIndex(
  {
    title: "text",
    content: "text",
  },
  {
    weights: {
      title: 10, // Title matches are 10x more important
      content: 1, // Content matches have normal weight
    },
    default_language: "english",
    name: "article_text_index",
  }
);
```

### Text Search Queries

```javascript
// Basic text search
db.articles.find({ $text: { $search: "mongodb database" } });

// Phrase search
db.articles.find({ $text: { $search: '"MongoDB performance"' } });

// Exclude terms
db.articles.find({ $text: { $search: "mongodb -mysql" } });

// Text search with score
db.articles
  .find(
    { $text: { $search: "mongodb performance optimization" } },
    { score: { $meta: "textScore" } }
  )
  .sort({ score: { $meta: "textScore" } });
```

### Text Index Languages

```javascript
// Language-specific text index
db.articles.createIndex(
  { title: "text", content: "text" },
  { default_language: "spanish" }
);

// Document-level language override
const spanishArticle = {
  title: "Artículo en Español",
  content: "Contenido en español...",
  language: "spanish",
};

// Query with language consideration
db.articles.find({
  $text: {
    $search: "mongodb",
    $language: "english",
  },
});
```

### Text Index Limitations

```javascript
const textIndexLimitations = {
  perCollection: "Only one text index per collection",
  compoundLimitation:
    "Text index can be part of compound index but with restrictions",
  sortLimitation: "Cannot sort on fields other than textScore",

  // Workaround for multiple text indexes
  workaround:
    "Use different fields or combine fields into one searchable field",
};

// Example workaround
const article = {
  title: "MongoDB Guide",
  content: "Comprehensive MongoDB tutorial...",
  searchableText: "MongoDB Guide Comprehensive MongoDB tutorial...", // Combined field
};

db.articles.createIndex({ searchableText: "text" });
```

## Geospatial Indexes {#geospatial-indexes}

Geospatial indexes enable location-based queries and spatial operations.

### 2dsphere Indexes (Recommended)

```javascript
// Create 2dsphere index for GeoJSON data
db.places.createIndex({ location: "2dsphere" });

// Sample GeoJSON document
const restaurant = {
  name: "Pizza Palace",
  location: {
    type: "Point",
    coordinates: [-73.9857, 40.7484], // [longitude, latitude]
  },
  address: "123 Main St, New York, NY",
};

db.restaurants.insertOne(restaurant);
```

### Geospatial Queries

```javascript
// Find places near a point
db.restaurants.find({
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.9857, 40.7484],
      },
      $maxDistance: 1000, // meters
    },
  },
});

// Find places within a polygon
db.restaurants.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-74.0, 40.7],
            [-74.0, 40.8],
            [-73.9, 40.8],
            [-73.9, 40.7],
            [-74.0, 40.7], // Close the polygon
          ],
        ],
      },
    },
  },
});

// Geospatial aggregation with $geoNear
db.restaurants.aggregate([
  {
    $geoNear: {
      near: {
        type: "Point",
        coordinates: [-73.9857, 40.7484],
      },
      key: "location",
      distanceField: "distance",
      maxDistance: 2000,
      spherical: true,
    },
  },
  { $limit: 10 },
]);
```

### 2d Indexes (Legacy)

```javascript
// 2d index for flat coordinate system
db.places.createIndex({ coordinates: "2d" });

// Document format for 2d index
const place = {
  name: "Central Park",
  coordinates: [40.7829, -73.9654], // [x, y] or [lat, lng]
};

// 2d index queries
db.places.find({ coordinates: { $near: [40.7829, -73.9654] } });
```

### Compound Geospatial Indexes

```javascript
// Compound index with geospatial field
db.restaurants.createIndex({
  category: 1,
  location: "2dsphere",
});

// Query by category and location
db.restaurants.find({
  category: "italian",
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.9857, 40.7484],
      },
      $maxDistance: 500,
    },
  },
});
```

## Special Index Types {#special-index-types}

### Hashed Indexes

```javascript
// Create hashed index for even distribution
db.users.createIndex({ _id: "hashed" });

// Hashed indexes are useful for:
// - Sharding with even distribution
// - Equality queries only (no range queries)

// Query with hashed index
db.users.find({ _id: ObjectId("...") }); // Equality only

// Hashed indexes do NOT support:
// db.users.find({ _id: { $gt: ObjectId("...") } })  // Range queries
// db.users.find().sort({ _id: 1 })                   // Sorting
```

### Wildcard Indexes

```javascript
// Wildcard index for dynamic schemas
db.products.createIndex({ "customAttributes.$**": 1 });

// Documents with varying schemas
db.products.insertMany([
  { name: "Laptop", customAttributes: { cpu: "Intel i7", ram: "16GB" } },
  { name: "Phone", customAttributes: { storage: "256GB", camera: "12MP" } },
]);

// Query any custom attribute
db.products.find({ "customAttributes.cpu": "Intel i7" });
db.products.find({ "customAttributes.storage": "256GB" });

// Wildcard index with specific path
db.products.createIndex({ "specs.$.dimensions.$**": 1 });
```

### Partial Indexes

```javascript
// Index only documents matching filter expression
db.orders.createIndex(
  { customerId: 1, orderDate: -1 },
  {
    partialFilterExpression: {
      status: { $in: ["pending", "processing"] },
    },
  }
);

// Only active orders are indexed
db.users.createIndex(
  { email: 1 },
  {
    partialFilterExpression: { active: true },
    unique: true, // Enforce uniqueness only for active users
  }
);
```

### Sparse Indexes

```javascript
// Index only documents that have the indexed field
db.users.createIndex({ phone: 1 }, { sparse: true });

// Only users with phone numbers are indexed
const users = [
  { name: "John", email: "john@example.com", phone: "555-1234" }, // Indexed
  { name: "Jane", email: "jane@example.com" }, // Not indexed
];

// Sparse vs dense index behavior
db.users.find({ phone: { $exists: true } }); // Uses sparse index
db.users.find().sort({ phone: 1 }); // May not use sparse index (missing docs)
```

### TTL Indexes (Time To Live)

```javascript
// Automatically expire documents
db.sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 3600 } // 1 hour
);

// Documents are automatically deleted when they expire
const session = {
  userId: ObjectId(),
  token: "abc123",
  createdAt: new Date(), // Will be deleted after 1 hour
};

// TTL with compound index
db.logs.createIndex(
  { userId: 1, createdAt: 1 },
  { expireAfterSeconds: 86400 } // 24 hours
);
```

## Index Properties {#index-properties}

### Unique Indexes

```javascript
// Create unique index
db.users.createIndex({ email: 1 }, { unique: true });

// Unique compound index
db.products.createIndex({ manufacturer: 1, model: 1 }, { unique: true });

// Handle unique constraint violations
try {
  await db.users.insertOne({
    email: "existing@example.com",
  });
} catch (error) {
  if (error.code === 11000) {
    console.log("Email already exists");
  }
}
```

### Case-Insensitive Indexes

```javascript
// Collation for case-insensitive queries
db.users.createIndex(
  { email: 1 },
  {
    collation: {
      locale: "en",
      strength: 1, // Case-insensitive
    },
  }
);

// Query with same collation
db.users.find(
  { email: "JOHN@EXAMPLE.COM" },
  { collation: { locale: "en", strength: 1 } }
);
```

### Background Index Building

```javascript
// Build index in background (recommended for production)
db.largeCollection.createIndex({ field: 1 }, { background: true });

// Monitor index build progress
db.currentOp({
  $or: [
    { op: "command", "command.createIndexes": { $exists: true } },
    { op: "command", "command.reIndex": { $exists: true } },
  ],
});
```

## Index Management {#index-management}

### Viewing Indexes

```javascript
// List all indexes on collection
db.users.getIndexes();

// Get index statistics
db.users.aggregate([{ $indexStats: {} }]);

// Check if collection is indexed
db.users.totalIndexSize();
db.users.stats().indexSizes;
```

### Creating Indexes Efficiently

```javascript
// Create multiple indexes efficiently
db.users.createIndexes([
  { email: 1 },
  { department: 1, joinDate: -1 },
  { "profile.skills": 1 },
]);

// Index creation with options
db.users.createIndex(
  { email: 1 },
  {
    name: "unique_email",
    unique: true,
    background: true,
    sparse: true,
    expireAfterSeconds: null,
    partialFilterExpression: { active: true },
  }
);
```

### Dropping Indexes

```javascript
// Drop specific index by name
db.users.dropIndex("email_1");

// Drop index by specification
db.users.dropIndex({ email: 1 });

// Drop multiple indexes
db.users.dropIndexes(["email_1", "department_1"]);

// Drop all indexes except _id
db.users.dropIndexes();
```

### Rebuilding Indexes

```javascript
// Rebuild all indexes (use with caution)
db.users.reIndex();

// Drop and recreate specific index
db.users.dropIndex("email_1");
db.users.createIndex({ email: 1 }, { unique: true });

// Monitor rebuild progress
db.currentOp();
```

### Index Size Management

```javascript
// Analyze index sizes
const stats = db.users.stats();
console.log({
  collectionSize: stats.size,
  totalIndexSize: stats.totalIndexSize,
  indexSizes: stats.indexSizes,
});

// Calculate index overhead
const indexOverhead = (stats.totalIndexSize / stats.size) * 100;
console.log(`Index overhead: ${indexOverhead.toFixed(2)}%`);

// Find largest indexes
db.users.aggregate([
  { $indexStats: {} },
  { $sort: { "accesses.ops": -1 } },
  { $project: { name: 1, "accesses.ops": 1 } },
]);
```

## Query Optimization {#query-optimization}

### Using explain() for Optimization

```javascript
// Basic explain
db.users.find({ age: { $gte: 25 } }).explain();

// Detailed execution stats
const explanation = db.users
  .find({ age: { $gte: 25 } })
  .explain("executionStats");

// Key metrics to analyze
const metrics = {
  stage: explanation.executionStats.executionStages.stage,
  executionTimeMillis: explanation.executionStats.executionTimeMillis,
  totalDocsExamined: explanation.executionStats.totalDocsExamined,
  totalDocsReturned: explanation.executionStats.totalDocsReturned,
  indexesUsed: explanation.executionStats.executionStages.indexName,
};
```

### Query Plan Analysis

```javascript
// Winning plan analysis
function analyzeQuery(collection, query) {
  const explanation = collection.find(query).explain("executionStats");

  return {
    isIndexed: explanation.executionStats.executionStages.stage === "IXSCAN",
    executionTime: explanation.executionStats.executionTimeMillis,
    docsExamined: explanation.executionStats.totalDocsExamined,
    docsReturned: explanation.executionStats.totalDocsReturned,
    efficiency:
      explanation.executionStats.totalDocsReturned /
      explanation.executionStats.totalDocsExamined,
    indexUsed: explanation.executionStats.executionStages.indexName,
  };
}

// Usage
const analysis = analyzeQuery(db.users, { department: "Engineering" });
console.log("Query efficiency:", analysis.efficiency);
```

### Hint Usage

```javascript
// Force specific index usage
db.users
  .find({ department: "Engineering" })
  .hint({ department: 1, joinDate: -1 });

// Force collection scan (for testing)
db.users.find({ department: "Engineering" }).hint({ $natural: 1 });

// Hint with index name
db.users.find({ email: "john@example.com" }).hint("unique_email_index");
```

### Covered Queries

```javascript
// Create index that covers query fields
db.users.createIndex({
  department: 1,
  name: 1,
  email: 1,
});

// Covered query - all fields in index
db.users.find(
  { department: "Engineering" },
  { name: 1, email: 1, _id: 0 } // Projection matches index fields
);

// Check if query is covered
const explanation = db.users
  .find({ department: "Engineering" }, { name: 1, email: 1, _id: 0 })
  .explain("executionStats");

// Look for stage: "PROJECTION_COVERED"
```

## Performance Monitoring {#performance-monitoring}

### Index Usage Statistics

```javascript
// Get index usage statistics
db.users.aggregate([
  { $indexStats: {} },
  {
    $project: {
      name: 1,
      usageCount: "$accesses.ops",
      since: "$accesses.since",
    },
  },
  { $sort: { usageCount: -1 } },
]);

// Find unused indexes
db.users.aggregate([
  { $indexStats: {} },
  { $match: { "accesses.ops": 0 } },
  { $project: { name: 1 } },
]);
```

### Performance Profiling

```javascript
// Enable profiling for slow operations
db.setProfilingLevel(2, { slowms: 100 });

// Analyze index usage in profile data
db.system.profile
  .find({
    ts: { $gte: new Date(Date.now() - 3600000) },
  })
  .sort({ ts: -1 });

// Find queries not using indexes
db.system.profile.find({
  "executionStats.stage": "COLLSCAN",
  millis: { $gte: 100 },
});
```

### Index Monitoring Script

```javascript
// Comprehensive index monitoring
function monitorIndexes(collectionName) {
  const collection = db.getCollection(collectionName);

  // Get collection stats
  const stats = collection.stats();

  // Get index usage
  const indexStats = collection.aggregate([{ $indexStats: {} }]).toArray();

  const report = {
    collection: collectionName,
    documentCount: stats.count,
    collectionSize: stats.size,
    totalIndexSize: stats.totalIndexSize,
    indexOverhead: ((stats.totalIndexSize / stats.size) * 100).toFixed(2) + "%",
    indexes: indexStats.map((idx) => ({
      name: idx.name,
      usageCount: idx.accesses.ops,
      size: stats.indexSizes[idx.name],
      lastUsed: idx.accesses.since,
    })),
  };

  return report;
}

// Usage
const report = monitorIndexes("users");
console.log(JSON.stringify(report, null, 2));
```

## Best Practices {#best-practices}

### Index Design Best Practices

```javascript
const indexBestPractices = {
  design: [
    "Follow ESR rule for compound indexes",
    "Index fields used in queries, not just displayed",
    "Consider query patterns when designing indexes",
    "Use compound indexes for multi-field queries",
  ],

  performance: [
    "Create indexes before importing large datasets",
    "Use background builds for large collections",
    "Monitor index usage and remove unused indexes",
    "Consider index size vs. collection size ratio",
  ],

  maintenance: [
    "Regularly analyze query patterns",
    "Remove redundant or unused indexes",
    "Rebuild fragmented indexes",
    "Monitor index build operations",
  ],
};
```

### Query Pattern Optimization

```javascript
// Common query patterns and optimal indexes

// 1. Equality + Sort pattern
// Query: find({ status: "active" }).sort({ createdAt: -1 })
db.orders.createIndex({ status: 1, createdAt: -1 });

// 2. Range + Equality pattern
// Query: find({ price: { $gte: 100 }, category: "electronics" })
db.products.createIndex({ category: 1, price: 1 }); // Equality first

// 3. Multiple equality fields
// Query: find({ userId: ObjectId(), type: "purchase" })
db.transactions.createIndex({ userId: 1, type: 1 });

// 4. Pagination pattern
// Query: find({}).sort({ _id: 1 }).skip(100).limit(20)
// Use default _id index or create: { _id: 1 }
```

### Index Maintenance Strategy

```javascript
// Regular index maintenance tasks
const maintenanceTasks = {
  daily: [
    "Check slow query log",
    "Monitor index usage statistics",
    "Review new query patterns",
  ],

  weekly: [
    "Analyze index efficiency",
    "Check for missing indexes on frequent queries",
    "Review index size growth",
  ],

  monthly: [
    "Full index usage analysis",
    "Remove unused indexes",
    "Optimize compound index order",
    "Plan for new index requirements",
  ],

  quarterly: [
    "Complete index strategy review",
    "Rebuild fragmented indexes",
    "Capacity planning for index growth",
  ],
};

// Automated index analysis script
function generateIndexReport() {
  const collections = db.adminCommand("listCollections").cursor.firstBatch;

  const report = collections
    .map((col) => {
      const name = col.name;
      if (name.startsWith("system.")) return null;

      return monitorIndexes(name);
    })
    .filter(Boolean);

  return {
    timestamp: new Date(),
    totalCollections: report.length,
    recommendations: generateRecommendations(report),
    details: report,
  };
}
```

### Anti-Patterns to Avoid

```javascript
const indexAntiPatterns = {
  overIndexing: [
    "Creating indexes on every field",
    "Multiple similar compound indexes",
    "Indexes on rarely queried fields",
  ],

  underIndexing: [
    "Missing indexes on frequently queried fields",
    "Using collection scans for large collections",
    "No compound indexes for multi-field queries",
  ],

  poorDesign: [
    "Wrong field order in compound indexes",
    "Using multikey indexes unnecessarily",
    "Ignoring query patterns when designing indexes",
  ],
};

// Example of poor index design
// BAD: Wrong order for compound index
db.orders.createIndex({ amount: 1, customerId: 1, status: 1 });
// Query: find({ customerId: ObjectId(), status: "pending" })
// This query can't use the index efficiently

// GOOD: Correct order following ESR rule
db.orders.createIndex({ customerId: 1, status: 1, amount: 1 });
```

## References

- [MongoDB Indexes Documentation](https://docs.mongodb.com/manual/indexes/)
- [Index Types](https://docs.mongodb.com/manual/indexes/#index-types)
- [Compound Indexes](https://docs.mongodb.com/manual/core/index-compound/)
- [Index Performance](https://docs.mongodb.com/manual/core/index-creation/)
- [Query Optimization](https://docs.mongodb.com/manual/core/query-optimization/)
- [ESR Rule](https://docs.mongodb.com/manual/tutorial/equality-sort-range-rule/)
