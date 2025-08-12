# MongoDB CRUD Operations: Complete Guide

This comprehensive guide covers all aspects of Create, Read, Update, and Delete operations in MongoDB, including advanced techniques, best practices, and real-world examples.

## Table of Contents

1. [CRUD Overview](#crud-overview)
2. [Create Operations](#create-operations)
3. [Read Operations](#read-operations)
4. [Update Operations](#update-operations)
5. [Delete Operations](#delete-operations)
6. [Bulk Operations](#bulk-operations)
7. [Transactions](#transactions)
8. [Error Handling](#error-handling)
9. [Performance Considerations](#performance-considerations)
10. [Best Practices](#best-practices)

## CRUD Overview {#crud-overview}

MongoDB CRUD operations are the foundation of all database interactions. Understanding these operations thoroughly is essential for building efficient applications.

### Basic CRUD Operations

- **Create**: `insertOne()`, `insertMany()`
- **Read**: `find()`, `findOne()`, `aggregate()`
- **Update**: `updateOne()`, `updateMany()`, `replaceOne()`
- **Delete**: `deleteOne()`, `deleteMany()`

### Return Values and Acknowledgments

```javascript
// All write operations return acknowledgment objects
const result = await db.collection.insertOne(document);
console.log(result.acknowledged); // true if operation was acknowledged
console.log(result.insertedId); // ObjectId of inserted document

const updateResult = await db.collection.updateOne(filter, update);
console.log(updateResult.matchedCount); // Documents matched
console.log(updateResult.modifiedCount); // Documents modified
```

## Create Operations {#create-operations}

### insertOne() - Single Document Insert

```javascript
// Basic document insertion
const user = {
  name: "John Doe",
  email: "john@example.com",
  age: 30,
  createdAt: new Date(),
};

const result = await db.users.insertOne(user);
console.log(`Inserted document with ID: ${result.insertedId}`);

// Insert with custom _id
const customDoc = {
  _id: "custom-id-123",
  type: "special",
  data: "important information",
};

await db.documents.insertOne(customDoc);
```

### insertMany() - Multiple Document Insert

```javascript
// Insert multiple documents
const users = [
  { name: "Alice", email: "alice@example.com", department: "Engineering" },
  { name: "Bob", email: "bob@example.com", department: "Marketing" },
  { name: "Charlie", email: "charlie@example.com", department: "Sales" },
];

const result = await db.users.insertMany(users);
console.log(`Inserted ${result.insertedCount} documents`);
console.log("Inserted IDs:", result.insertedIds);

// Insert with options
const result = await db.users.insertMany(users, {
  ordered: false, // Continue on error
  writeConcern: { w: "majority", wtimeout: 5000 },
});
```

### Insert Options and Behaviors

```javascript
// Ordered vs Unordered inserts
const documents = [
  { _id: 1, name: "First" },
  { _id: 2, name: "Second" },
  { _id: 1, name: "Duplicate" }, // This will cause an error
  { _id: 3, name: "Third" },
];

// Ordered insert (default) - stops on first error
try {
  await db.test.insertMany(documents, { ordered: true });
} catch (error) {
  // Only documents 1 and 2 will be inserted
  console.log("Error with ordered insert:", error.message);
}

// Unordered insert - continues despite errors
try {
  await db.test.insertMany(documents, { ordered: false });
} catch (error) {
  // Documents 1, 2, and 3 will be inserted (skipping duplicate)
  console.log("Error with unordered insert:", error.message);
}
```

### Complex Document Structures

```javascript
// Insert complex nested documents
const complexDoc = {
  _id: ObjectId(),

  // Basic fields
  title: "Product Launch",
  status: "active",

  // Nested objects
  metadata: {
    category: "electronics",
    tags: ["smartphone", "mobile", "tech"],
    specifications: {
      weight: "150g",
      dimensions: { width: 71, height: 146, depth: 7.9 },
      features: ["waterproof", "wireless charging"],
    },
  },

  // Arrays of objects
  reviews: [
    {
      reviewId: ObjectId(),
      author: "John Smith",
      rating: 5,
      comment: "Excellent product!",
      date: new Date(),
      helpful: { yes: 10, no: 1 },
    },
  ],

  // Mixed data types
  pricing: {
    base: NumberDecimal("299.99"),
    currency: "USD",
    discounts: [
      { type: "early_bird", percent: 10, validUntil: new Date("2024-12-31") },
    ],
  },

  // Timestamps
  createdAt: new Date(),
  updatedAt: new Date(),
};

await db.products.insertOne(complexDoc);
```

## Read Operations {#read-operations}

### find() - Query Documents

```javascript
// Basic find operations
db.users.find(); // Find all documents
db.users.find({ age: 25 }); // Equality match
db.users.find({ age: { $gte: 18 } }); // Range query
db.users.find({ name: /^John/ }); // Regex match

// Multiple conditions
db.users.find({
  age: { $gte: 18, $lt: 65 },
  department: "Engineering",
  active: true,
});

// Logical operators
db.users.find({
  $or: [{ department: "Engineering" }, { department: "Marketing" }],
});

db.users.find({
  $and: [{ age: { $gte: 25 } }, { salary: { $gte: 50000 } }],
});
```

### findOne() - Single Document Query

```javascript
// Find single document
const user = await db.users.findOne({ email: "john@example.com" });

if (user) {
  console.log(`Found user: ${user.name}`);
} else {
  console.log("User not found");
}

// findOne with projection
const userBasicInfo = await db.users.findOne(
  { _id: userId },
  { projection: { name: 1, email: 1, _id: 0 } }
);
```

### Query Operators

#### Comparison Operators

```javascript
// Numeric comparisons
db.products.find({ price: { $eq: 99.99 } }); // Equal
db.products.find({ price: { $ne: 99.99 } }); // Not equal
db.products.find({ price: { $gt: 50 } }); // Greater than
db.products.find({ price: { $gte: 50 } }); // Greater than or equal
db.products.find({ price: { $lt: 100 } }); // Less than
db.products.find({ price: { $lte: 100 } }); // Less than or equal

// Array and set operations
db.products.find({ category: { $in: ["electronics", "computers"] } });
db.products.find({ category: { $nin: ["discontinued", "recalled"] } });
```

#### Element Operators

```javascript
// Check field existence and type
db.users.find({ phone: { $exists: true } }); // Has phone field
db.users.find({ phone: { $exists: false } }); // Missing phone field
db.users.find({ age: { $type: "number" } }); // Age is a number
db.users.find({ age: { $type: 16 } }); // Age is int32
```

#### Array Operators

```javascript
// Array queries
db.posts.find({ tags: "mongodb" }); // Array contains value
db.posts.find({ tags: { $all: ["mongodb", "database"] } }); // Array contains all values
db.posts.find({ tags: { $size: 3 } }); // Array has exact size
db.posts.find({ "comments.author": "John" }); // Nested array field

// Array element matching
db.posts.find({
  comments: {
    $elemMatch: {
      author: "John",
      rating: { $gte: 4 },
    },
  },
});
```

#### Text Search

```javascript
// Text search (requires text index)
db.articles.createIndex({ title: "text", content: "text" });

db.articles.find({ $text: { $search: "mongodb database" } });

// Text search with score
db.articles
  .find(
    { $text: { $search: "mongodb performance" } },
    { score: { $meta: "textScore" } }
  )
  .sort({ score: { $meta: "textScore" } });
```

### Projection - Selecting Fields

```javascript
// Include specific fields
db.users.find({}, { name: 1, email: 1 }); // Include name and email
db.users.find({}, { name: 1, email: 1, _id: 0 }); // Exclude _id

// Exclude specific fields
db.users.find({}, { password: 0, ssn: 0 }); // Exclude sensitive fields

// Array projection
db.posts.find(
  {},
  {
    title: 1,
    "comments.$": 1, // First matching array element
  }
);

db.posts.find(
  {},
  {
    title: 1,
    comments: { $slice: 5 }, // First 5 array elements
  }
);

db.posts.find(
  {},
  {
    title: 1,
    comments: { $slice: [10, 5] }, // Skip 10, take 5 elements
  }
);
```

### Sorting and Limiting

```javascript
// Sorting
db.users.find().sort({ age: 1 }); // Ascending
db.users.find().sort({ age: -1 }); // Descending
db.users.find().sort({ department: 1, age: -1 }); // Multiple fields

// Limiting and skipping
db.users.find().limit(10); // First 10 documents
db.users.find().skip(20).limit(10); // Skip 20, take 10
db.users.find().sort({ createdAt: -1 }).limit(5); // Latest 5 users

// Pagination pattern
function getUsers(page, pageSize) {
  return db.users
    .find()
    .sort({ _id: 1 })
    .skip((page - 1) * pageSize)
    .limit(pageSize)
    .toArray();
}
```

### Advanced Query Techniques

```javascript
// Aggregation-style queries
db.users.find({
  $expr: {
    $gt: [{ $strLenCP: "$name" }, 10],
  },
});

// Regular expressions
db.users.find({ email: /^[a-zA-Z0-9._%+-]+@gmail\.com$/ });

// Date queries
db.orders.find({
  createdAt: {
    $gte: new Date("2023-01-01"),
    $lt: new Date("2024-01-01"),
  },
});

// Complex nested queries
db.products.find({
  "specifications.dimensions.width": { $gte: 70 },
  "reviews.rating": { $gte: 4 },
});
```

## Update Operations {#update-operations}

### updateOne() - Single Document Update

```javascript
// Basic field update
await db.users.updateOne({ _id: userId }, { $set: { lastLogin: new Date() } });

// Multiple field updates
await db.users.updateOne(
  { email: "john@example.com" },
  {
    $set: {
      name: "John Smith",
      department: "Engineering",
      updatedAt: new Date(),
    },
  }
);

// Update with upsert
const result = await db.users.updateOne(
  { email: "new@example.com" },
  {
    $set: {
      name: "New User",
      createdAt: new Date(),
    },
  },
  { upsert: true }
);

console.log("Upserted ID:", result.upsertedId);
```

### updateMany() - Multiple Document Update

```javascript
// Update multiple documents
await db.users.updateMany(
  { department: "Sales" },
  {
    $set: {
      bonus: 1000,
      bonusDate: new Date(),
    },
  }
);

// Conditional updates
await db.products.updateMany(
  {
    category: "electronics",
    price: { $gt: 500 },
  },
  {
    $mul: { price: 0.9 }, // 10% discount
    $set: { onSale: true },
  }
);
```

### Update Operators

#### Field Update Operators

```javascript
// $set - Set field values
db.users.updateOne(
  { _id: userId },
  {
    $set: {
      "profile.bio": "Updated biography",
      "settings.notifications": true,
    },
  }
);

// $unset - Remove fields
db.users.updateOne(
  { _id: userId },
  {
    $unset: {
      temporaryField: "",
      "nested.obsoleteField": "",
    },
  }
);

// $rename - Rename fields
db.users.updateMany(
  {},
  {
    $rename: {
      oldFieldName: "newFieldName",
      "profile.oldField": "profile.newField",
    },
  }
);
```

#### Numeric Update Operators

```javascript
// $inc - Increment/decrement
db.products.updateOne(
  { _id: productId },
  {
    $inc: {
      views: 1, // Increment by 1
      stock: -5, // Decrement by 5
      "stats.likes": 1, // Increment nested field
    },
  }
);

// $mul - Multiply
db.products.updateMany(
  { onSale: true },
  {
    $mul: { price: 0.8 }, // 20% discount
  }
);

// $min/$max - Set to minimum/maximum
db.auctions.updateOne(
  { _id: auctionId },
  {
    $max: { highestBid: newBid },
    $min: { lowestBid: newBid },
  }
);
```

#### Array Update Operators

```javascript
// $push - Add to array
db.posts.updateOne(
  { _id: postId },
  {
    $push: {
      tags: "new-tag",
      comments: {
        author: "John",
        text: "Great post!",
        date: new Date(),
      },
    },
  }
);

// $push with modifiers
db.posts.updateOne(
  { _id: postId },
  {
    $push: {
      scores: {
        $each: [85, 92, 78], // Add multiple values
        $sort: -1, // Sort descending
        $slice: 10, // Keep only top 10
      },
    },
  }
);

// $addToSet - Add unique values
db.users.updateOne(
  { _id: userId },
  {
    $addToSet: {
      skills: { $each: ["JavaScript", "Python", "MongoDB"] },
    },
  }
);

// $pull - Remove matching elements
db.posts.updateOne(
  { _id: postId },
  {
    $pull: {
      tags: "outdated",
      comments: { author: "spammer" },
    },
  }
);

// $pop - Remove first/last element
db.logs.updateOne(
  { _id: logId },
  {
    $pop: { messages: 1 }, // Remove last element (-1 for first)
  }
);
```

#### Array Element Updates

```javascript
// Update first matching array element
db.posts.updateOne(
  { _id: postId, "comments.author": "John" },
  {
    $set: {
      "comments.$.text": "Updated comment",
      "comments.$.edited": true,
    },
  }
);

// Update all matching array elements
db.posts.updateOne(
  { _id: postId },
  {
    $set: {
      "comments.$[elem].verified": true,
    },
  },
  {
    arrayFilters: [{ "elem.author": { $ne: "anonymous" } }],
  }
);

// Update nested array elements
db.blog.updateOne(
  { _id: blogId },
  {
    $set: {
      "posts.$[post].comments.$[comment].approved": true,
    },
  },
  {
    arrayFilters: [{ "post.published": true }, { "comment.flagged": false }],
  }
);
```

### replaceOne() - Document Replacement

```javascript
// Replace entire document (keeping _id)
const newUserData = {
  name: "John Smith",
  email: "john.smith@example.com",
  department: "Engineering",
  skills: ["JavaScript", "Python", "MongoDB"],
  profile: {
    bio: "Software engineer with 5 years experience",
    location: "San Francisco, CA",
  },
  updatedAt: new Date(),
};

await db.users.replaceOne({ _id: userId }, newUserData);
```

### findOneAndUpdate() - Atomic Update with Return

```javascript
// Update and return updated document
const updatedUser = await db.users.findOneAndUpdate(
  { _id: userId },
  {
    $inc: { loginCount: 1 },
    $set: { lastLogin: new Date() },
  },
  {
    returnDocument: "after", // Return updated document
    projection: { password: 0 },
  }
);

// Update and return original document
const originalUser = await db.users.findOneAndUpdate(
  { _id: userId },
  { $set: { status: "inactive" } },
  { returnDocument: "before" }
);
```

## Delete Operations {#delete-operations}

### deleteOne() - Single Document Deletion

```javascript
// Delete by _id
const result = await db.users.deleteOne({ _id: userId });

if (result.deletedCount === 1) {
  console.log("User deleted successfully");
} else {
  console.log("User not found");
}

// Delete with complex filter
await db.sessions.deleteOne({
  userId: userId,
  expiresAt: { $lt: new Date() },
});
```

### deleteMany() - Multiple Document Deletion

```javascript
// Delete multiple documents
const result = await db.logs.deleteMany({
  level: "debug",
  timestamp: { $lt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) },
});

console.log(`Deleted ${result.deletedCount} old debug logs`);

// Delete all documents in collection
await db.tempData.deleteMany({});
```

### findOneAndDelete() - Atomic Delete with Return

```javascript
// Delete and return deleted document
const deletedSession = await db.sessions.findOneAndDelete({
  token: sessionToken,
  expiresAt: { $gt: new Date() },
});

if (deletedSession) {
  console.log(`Deleted session for user: ${deletedSession.userId}`);
} else {
  console.log("Session not found or already expired");
}
```

### Soft Delete Pattern

```javascript
// Implement soft delete instead of hard delete
async function softDeleteUser(userId) {
  return await db.users.updateOne(
    { _id: userId, deleted: { $ne: true } },
    {
      $set: {
        deleted: true,
        deletedAt: new Date(),
      },
    }
  );
}

// Query excluding soft-deleted documents
function findActiveUsers(query = {}) {
  return db.users.find({
    ...query,
    deleted: { $ne: true },
  });
}

// Restore soft-deleted document
async function restoreUser(userId) {
  return await db.users.updateOne(
    { _id: userId },
    {
      $unset: {
        deleted: "",
        deletedAt: "",
      },
    }
  );
}
```

## Bulk Operations {#bulk-operations}

### Bulk Write Operations

```javascript
// Mixed bulk operations
const bulkOps = [
  {
    insertOne: {
      document: { name: "Alice", department: "Engineering" },
    },
  },
  {
    updateOne: {
      filter: { name: "Bob" },
      update: { $set: { department: "Marketing" } },
    },
  },
  {
    deleteOne: {
      filter: { name: "Charlie", status: "inactive" },
    },
  },
  {
    replaceOne: {
      filter: { _id: ObjectId("...") },
      replacement: { name: "Diana", department: "Sales", active: true },
    },
  },
];

const result = await db.users.bulkWrite(bulkOps, {
  ordered: false, // Continue on error
});

console.log("Bulk operation results:", {
  insertedCount: result.insertedCount,
  matchedCount: result.matchedCount,
  modifiedCount: result.modifiedCount,
  deletedCount: result.deletedCount,
  upsertedCount: result.upsertedCount,
});
```

### Efficient Bulk Patterns

```javascript
// Efficient bulk upsert pattern
async function bulkUpsertUsers(users) {
  const bulkOps = users.map((user) => ({
    updateOne: {
      filter: { email: user.email },
      update: {
        $set: {
          ...user,
          updatedAt: new Date(),
        },
        $setOnInsert: {
          createdAt: new Date(),
        },
      },
      upsert: true,
    },
  }));

  return await db.users.bulkWrite(bulkOps);
}

// Batch processing for large datasets
async function processBatches(documents, batchSize = 1000) {
  for (let i = 0; i < documents.length; i += batchSize) {
    const batch = documents.slice(i, i + batchSize);
    const bulkOps = batch.map((doc) => ({
      updateOne: {
        filter: { _id: doc._id },
        update: { $set: doc },
      },
    }));

    await db.collection.bulkWrite(bulkOps);
    console.log(`Processed batch ${Math.floor(i / batchSize) + 1}`);
  }
}
```

## Transactions {#transactions}

### Single Document Transactions (Atomic Operations)

```javascript
// Built-in atomic operations
await db.accounts.updateOne(
  { _id: fromAccountId, balance: { $gte: amount } },
  { $inc: { balance: -amount } }
);

await db.accounts.updateOne(
  { _id: toAccountId },
  { $inc: { balance: amount } }
);
```

### Multi-Document Transactions

```javascript
// Transaction with session
const session = client.startSession();

try {
  await session.withTransaction(async () => {
    // Transfer money between accounts
    const fromAccount = await db.accounts.findOne(
      { _id: fromAccountId },
      { session }
    );

    if (fromAccount.balance < amount) {
      throw new Error("Insufficient funds");
    }

    await db.accounts.updateOne(
      { _id: fromAccountId },
      { $inc: { balance: -amount } },
      { session }
    );

    await db.accounts.updateOne(
      { _id: toAccountId },
      { $inc: { balance: amount } },
      { session }
    );

    // Log transaction
    await db.transactions.insertOne(
      {
        from: fromAccountId,
        to: toAccountId,
        amount: amount,
        timestamp: new Date(),
        type: "transfer",
      },
      { session }
    );
  });

  console.log("Transaction completed successfully");
} catch (error) {
  console.log("Transaction failed:", error.message);
} finally {
  await session.endSession();
}
```

### Transaction Best Practices

```javascript
// Retry logic for transactions
async function performTransactionWithRetry(transactionFunc, maxRetries = 3) {
  const session = client.startSession();

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await session.withTransaction(transactionFunc);
      console.log("Transaction completed successfully");
      break;
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
      console.log(`Transaction attempt ${attempt} failed, retrying...`);
      await new Promise((resolve) => setTimeout(resolve, 100 * attempt));
    }
  }

  await session.endSession();
}
```

## Error Handling {#error-handling}

### Common Error Types and Handling

```javascript
async function handleCRUDErrors() {
  try {
    // Potential operations that might fail
    await db.users.insertOne(userData);
  } catch (error) {
    switch (error.code) {
      case 11000: // Duplicate key error
        console.log("User already exists:", error.keyValue);
        break;

      case 121: // Document validation error
        console.log("Validation failed:", error.message);
        break;

      case 50: // Exceeded maximum execution time
        console.log("Operation timed out");
        break;

      default:
        console.log("Unexpected error:", error.message);
        throw error;
    }
  }
}

// Specific error handling patterns
async function safeInsert(collection, document) {
  try {
    const result = await collection.insertOne(document);
    return { success: true, id: result.insertedId };
  } catch (error) {
    if (error.code === 11000) {
      return { success: false, reason: "duplicate" };
    }
    throw error;
  }
}
```

### Validation and Data Integrity

```javascript
// Client-side validation before database operations
function validateUser(user) {
  const errors = [];

  if (!user.email || !/^\S+@\S+\.\S+$/.test(user.email)) {
    errors.push("Invalid email address");
  }

  if (!user.name || user.name.length < 2) {
    errors.push("Name must be at least 2 characters");
  }

  if (user.age && (user.age < 0 || user.age > 120)) {
    errors.push("Age must be between 0 and 120");
  }

  return errors;
}

// Use validation before operations
async function createUser(userData) {
  const errors = validateUser(userData);
  if (errors.length > 0) {
    throw new Error(`Validation failed: ${errors.join(", ")}`);
  }

  return await db.users.insertOne({
    ...userData,
    createdAt: new Date(),
    updatedAt: new Date(),
  });
}
```

## Performance Considerations {#performance-considerations}

### Write Performance Optimization

```javascript
// Use insertMany for bulk inserts
const users = [
  /* large array of users */
];

// BAD: Multiple individual inserts
for (const user of users) {
  await db.users.insertOne(user); // Slow - many round trips
}

// GOOD: Single bulk insert
await db.users.insertMany(users, { ordered: false });

// Use bulk operations for mixed operations
const bulkOps = users.map((user) => ({
  updateOne: {
    filter: { email: user.email },
    update: { $set: user },
    upsert: true,
  },
}));

await db.users.bulkWrite(bulkOps);
```

### Read Performance Optimization

```javascript
// Use projection to reduce network transfer
// BAD: Return full documents
const users = await db.users.find({ department: "Engineering" }).toArray();

// GOOD: Return only needed fields
const users = await db.users
  .find(
    { department: "Engineering" },
    { projection: { name: 1, email: 1, _id: 0 } }
  )
  .toArray();

// Use indexes for query performance
db.users.createIndex({ department: 1, joinDate: -1 });

// Use cursor efficiently for large result sets
const cursor = db.users.find({ department: "Engineering" });
for await (const user of cursor) {
  // Process each user individually
  await processUser(user);
}
```

### Memory-Efficient Patterns

```javascript
// Stream processing for large datasets
async function processLargeCollection() {
  const cursor = db.largeCollection.find({}).batchSize(100);

  for await (const document of cursor) {
    await processDocument(document);

    // Process in batches to manage memory
    if (processedCount % 1000 === 0) {
      console.log(`Processed ${processedCount} documents`);
    }
  }
}

// Pagination for API responses
async function paginateResults(page, limit = 20) {
  const skip = (page - 1) * limit;

  const [results, total] = await Promise.all([
    db.collection
      .find({})
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .toArray(),

    db.collection.countDocuments({}),
  ]);

  return {
    results,
    pagination: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit),
    },
  };
}
```

## Best Practices {#best-practices}

### General CRUD Best Practices

```javascript
const crudBestPractices = {
  create: [
    "Validate data before insertion",
    "Use insertMany for bulk operations",
    "Handle duplicate key errors gracefully",
    "Set appropriate write concern for consistency needs",
  ],

  read: [
    "Use indexes to optimize queries",
    "Use projection to limit returned fields",
    "Implement pagination for large result sets",
    "Use cursor.batchSize() for memory efficiency",
  ],

  update: [
    "Use atomic operators ($inc, $push, etc.)",
    "Implement optimistic concurrency control",
    "Use upsert when appropriate",
    "Update only changed fields",
  ],

  delete: [
    "Consider soft delete for important data",
    "Use deleteMany with caution",
    "Implement cascade delete logic in application",
    "Log important deletions for audit trails",
  ],
};
```

### Data Modeling Best Practices

```javascript
// Consistent document structure
const userSchema = {
  _id: ObjectId(),

  // Required fields
  email: String,
  name: String,

  // Optional fields with defaults
  active: { type: Boolean, default: true },
  roles: { type: Array, default: [] },

  // Nested objects
  profile: {
    bio: String,
    avatar: String,
    preferences: {
      theme: { type: String, default: "light" },
      notifications: { type: Boolean, default: true },
    },
  },

  // Timestamps
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now },
};

// Implement version control for important documents
async function updateWithVersion(collection, filter, update) {
  const result = await collection.updateOne(
    { ...filter, version: update.$inc?.version - 1 || 0 },
    {
      ...update,
      $inc: { version: 1 },
      $set: { ...update.$set, updatedAt: new Date() },
    }
  );

  if (result.matchedCount === 0) {
    throw new Error("Document was modified by another process");
  }

  return result;
}
```

### Security Best Practices

```javascript
// Input sanitization
function sanitizeInput(input) {
  if (typeof input === "string") {
    // Remove potential injection attempts
    return input.replace(/[$]/g, "");
  }
  return input;
}

// Safe query construction
function buildSafeQuery(userInput) {
  const query = {};

  // Only allow specific fields
  const allowedFields = ["name", "department", "active"];

  for (const [key, value] of Object.entries(userInput)) {
    if (allowedFields.includes(key)) {
      query[key] = sanitizeInput(value);
    }
  }

  return query;
}

// Implement field-level security
async function getUser(userId, requestingUser) {
  const user = await db.users.findOne({ _id: userId });

  if (!user) return null;

  // Remove sensitive fields based on permissions
  if (requestingUser.role !== "admin" && requestingUser._id !== userId) {
    delete user.email;
    delete user.phone;
    delete user.ssn;
  }

  return user;
}
```

## References

- [MongoDB CRUD Operations](https://docs.mongodb.com/manual/crud/)
- [Update Operators](https://docs.mongodb.com/manual/reference/operator/update/)
- [Query Operators](https://docs.mongodb.com/manual/reference/operator/query/)
- [Bulk Write Operations](https://docs.mongodb.com/manual/core/bulk-write-operations/)
- [Transactions](https://docs.mongodb.com/manual/core/transactions/)
- [Data Modeling](https://docs.mongodb.com/manual/core/data-modeling-introduction/)
