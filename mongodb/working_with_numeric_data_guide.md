# MongoDB: Working with Numeric Data - Complete Guide

This comprehensive guide covers all aspects of handling numeric data in MongoDB, including data types, operations, aggregations, and best practices for optimal performance and accuracy.

## Table of Contents

1. [Numeric Data Types](#numeric-data-types)
2. [Storing Numeric Data](#storing-numeric-data)
3. [Numeric Operations](#numeric-operations)
4. [Aggregation with Numbers](#aggregation-with-numbers)
5. [Data Type Conversion](#data-type-conversion)
6. [Precision and Accuracy](#precision-and-accuracy)
7. [Performance Considerations](#performance-considerations)
8. [Common Patterns](#common-patterns)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Numeric Data Types {#numeric-data-types}

MongoDB supports several numeric data types, each with specific use cases and characteristics.

### BSON Numeric Types

#### 1. Double (64-bit floating point)

- Default numeric type in MongoDB
- IEEE 754 double precision
- Range: ±1.7976931348623157 × 10^308

```javascript
// Examples of double values
{
  price: 29.99;
}
{
  temperature: -15.5;
}
{
  pi: 3.14159265359;
}
```

#### 2. 32-bit Integer

- Whole numbers from -2,147,483,648 to 2,147,483,647
- More memory efficient than doubles for small integers

```javascript
// Explicit 32-bit integer creation
{
  count: NumberInt(42);
}
{
  status: NumberInt(1);
}
```

#### 3. 64-bit Integer (Long)

- Large whole numbers from -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
- Useful for IDs, timestamps, large counters

```javascript
// Explicit 64-bit integer creation
{
  userId: NumberLong("9223372036854775807");
}
{
  timestamp: NumberLong(Date.now());
}
```

#### 4. Decimal128

- High-precision decimal arithmetic
- Exact decimal representation (no floating-point errors)
- Essential for financial calculations

```javascript
// Decimal128 for precise calculations
{
  balance: NumberDecimal("12345.67");
}
{
  interestRate: NumberDecimal("0.025");
}
{
  totalCost: NumberDecimal("999.999");
}
```

### Type Checking and Identification

```javascript
// Check numeric types in queries
db.products.find({ price: { $type: "double" } });
db.products.find({ count: { $type: "int" } });
db.products.find({ id: { $type: "long" } });
db.products.find({ balance: { $type: "decimal" } });

// Using type numbers
db.products.find({ price: { $type: 1 } }); // double
db.products.find({ count: { $type: 16 } }); // 32-bit int
db.products.find({ id: { $type: 18 } }); // 64-bit int
db.products.find({ balance: { $type: 19 } }); // decimal128
```

## Storing Numeric Data {#storing-numeric-data}

### Choosing the Right Type

```javascript
// Financial data - use Decimal128
const financialRecord = {
  accountId: NumberLong("1234567890"),
  balance: NumberDecimal("15250.75"),
  interestRate: NumberDecimal("0.0325"),
  transactionFee: NumberDecimal("2.50"),
};

// Scientific data - double is usually fine
const measurement = {
  temperature: 23.7,
  humidity: 65.2,
  pressure: 1013.25,
};

// Counters and IDs - use appropriate integer type
const statistics = {
  views: NumberInt(1542), // Small numbers
  userId: NumberLong("987654321"), // Large IDs
  sessionCount: NumberInt(5),
};
```

### Schema Design Considerations

```javascript
// Product catalog with mixed numeric types
const product = {
  _id: ObjectId(),
  sku: "PROD-001",
  name: "Laptop Computer",

  // Pricing (use Decimal128 for exact values)
  price: NumberDecimal("1299.99"),
  cost: NumberDecimal("850.00"),
  tax: NumberDecimal("0.08"),

  // Inventory (integers for counting)
  stockQuantity: NumberInt(25),
  reorderLevel: NumberInt(5),

  // Specifications (doubles for measurements)
  weight: 2.1, // kg
  screenSize: 15.6, // inches
  batteryLife: 8.5, // hours

  // Ratings and reviews
  averageRating: 4.7,
  reviewCount: NumberInt(1834),

  // Timestamps
  createdAt: NumberLong(Date.now()),
  lastUpdated: NumberLong(Date.now()),
};
```

## Numeric Operations {#numeric-operations}

### Basic Arithmetic Operations

```javascript
// Update operations with arithmetic
db.products.updateOne(
  { _id: productId },
  {
    $inc: { stockQuantity: -1 }, // Decrement
    $mul: { price: NumberDecimal("1.1") }, // Increase by 10%
    $min: { minPrice: NumberDecimal("50") }, // Set minimum
    $max: { maxPrice: NumberDecimal("2000") }, // Set maximum
  }
);

// Increment with different types
db.counters.updateOne(
  { name: "pageViews" },
  { $inc: { count: NumberLong(1) } }
);
```

### Mathematical Operations in Queries

```javascript
// Range queries
db.products.find({
  price: {
    $gte: NumberDecimal("100"),
    $lte: NumberDecimal("500"),
  },
});

// Modulo operations
db.products.find({
  productId: { $mod: [10, 0] }, // Find products with IDs divisible by 10
});

// Comparison with tolerance for floating-point
const searchPrice = 29.99;
const tolerance = 0.01;
db.products.find({
  price: {
    $gte: searchPrice - tolerance,
    $lte: searchPrice + tolerance,
  },
});
```

## Aggregation with Numbers {#aggregation-with-numbers}

### Statistical Operations

```javascript
// Basic statistics
db.products.aggregate([
  {
    $group: {
      _id: "$category",
      averagePrice: { $avg: "$price" },
      minPrice: { $min: "$price" },
      maxPrice: { $max: "$price" },
      totalValue: { $sum: { $multiply: ["$price", "$stockQuantity"] } },
      productCount: { $sum: 1 },
      standardDeviation: { $stdDevPop: "$price" },
    },
  },
]);
```

### Advanced Mathematical Operations

```javascript
// Complex calculations
db.sales.aggregate([
  {
    $project: {
      orderId: 1,
      subtotal: 1,
      taxRate: 1,

      // Calculate tax amount
      taxAmount: {
        $multiply: ["$subtotal", "$taxRate"],
      },

      // Calculate total with tax
      total: {
        $add: ["$subtotal", { $multiply: ["$subtotal", "$taxRate"] }],
      },

      // Calculate discount percentage
      discountPercentage: {
        $cond: {
          if: { $gt: ["$originalPrice", 0] },
          then: {
            $multiply: [
              {
                $divide: [
                  { $subtract: ["$originalPrice", "$subtotal"] },
                  "$originalPrice",
                ],
              },
              100,
            ],
          },
          else: 0,
        },
      },
    },
  },
]);
```

### Working with Arrays of Numbers

```javascript
// Analyze exam scores
db.students.aggregate([
  {
    $project: {
      name: 1,
      scores: 1,

      // Calculate average score
      averageScore: { $avg: "$scores" },

      // Find highest score
      highestScore: { $max: "$scores" },

      // Count number of scores above 80
      scoresAbove80: {
        $size: {
          $filter: {
            input: "$scores",
            cond: { $gt: ["$$this", 80] },
          },
        },
      },

      // Calculate grade point average
      gpa: {
        $divide: [{ $sum: "$scores" }, { $size: "$scores" }],
      },
    },
  },
]);
```

### Numeric Bucketing and Grouping

```javascript
// Group products by price ranges
db.products.aggregate([
  {
    $bucket: {
      groupBy: "$price",
      boundaries: [
        NumberDecimal("0"),
        NumberDecimal("50"),
        NumberDecimal("100"),
        NumberDecimal("500"),
        NumberDecimal("1000"),
      ],
      default: "expensive",
      output: {
        count: { $sum: 1 },
        averagePrice: { $avg: "$price" },
        products: { $push: "$name" },
      },
    },
  },
]);

// Automatic bucketing by price
db.products.aggregate([
  {
    $bucketAuto: {
      groupBy: "$price",
      buckets: 5,
      output: {
        count: { $sum: 1 },
        minPrice: { $min: "$price" },
        maxPrice: { $max: "$price" },
        avgPrice: { $avg: "$price" },
      },
    },
  },
]);
```

## Data Type Conversion {#data-type-conversion}

### Using $convert Operator

```javascript
// Convert string prices to Decimal128
db.products.aggregate([
  {
    $project: {
      name: 1,
      originalPrice: "$price",
      numericPrice: {
        $convert: {
          input: "$price",
          to: "decimal",
          onError: NumberDecimal("0"),
          onNull: NumberDecimal("0"),
        },
      },
    },
  },
]);
```

### Type-Specific Conversion Operators

```javascript
// Various conversion examples
db.data.aggregate([
  {
    $project: {
      // Convert to specific types
      asDouble: { $toDouble: "$stringNumber" },
      asInt: { $toInt: "$floatNumber" },
      asLong: { $toLong: "$intNumber" },
      asDecimal: { $toDecimal: "$stringPrice" },

      // Safe conversion with error handling
      safeConversion: {
        $convert: {
          input: "$maybeNumber",
          to: "decimal",
          onError: "Invalid Number",
          onNull: "No Value",
        },
      },
    },
  },
]);
```

### Bulk Data Type Updates

```javascript
// Convert existing string prices to Decimal128
db.products.find({ price: { $type: "string" } }).forEach(function (doc) {
  db.products.updateOne(
    { _id: doc._id },
    {
      $set: {
        price: NumberDecimal(doc.price),
      },
    }
  );
});

// Using aggregation pipeline for updates (MongoDB 4.2+)
db.products.updateMany({ price: { $type: "string" } }, [
  {
    $set: {
      price: {
        $convert: {
          input: "$price",
          to: "decimal",
          onError: NumberDecimal("0"),
        },
      },
    },
  },
]);
```

## Precision and Accuracy {#precision-and-accuracy}

### Floating-Point Precision Issues

```javascript
// Demonstrating floating-point precision problems
const result = 0.1 + 0.2; // Result: 0.30000000000000004

// Problems in MongoDB queries
db.transactions.find({ amount: 0.3 }); // May not find 0.1 + 0.2

// Solution: Use tolerance-based queries
const target = 0.3;
const epsilon = 0.0001;
db.transactions.find({
  amount: {
    $gte: target - epsilon,
    $lte: target + epsilon,
  },
});
```

### Using Decimal128 for Financial Calculations

```javascript
// Precise financial calculations
const invoice = {
  items: [
    {
      description: "Widget A",
      quantity: NumberInt(3),
      unitPrice: NumberDecimal("12.99"),
      total: NumberDecimal("38.97"), // 3 * 12.99
    },
    {
      description: "Widget B",
      quantity: NumberInt(2),
      unitPrice: NumberDecimal("25.50"),
      total: NumberDecimal("51.00"), // 2 * 25.50
    },
  ],
  subtotal: NumberDecimal("89.97"),
  taxRate: NumberDecimal("0.08"),
  taxAmount: NumberDecimal("7.20"), // 89.97 * 0.08
  total: NumberDecimal("97.17"), // 89.97 + 7.20
};

// Aggregation for financial totals
db.invoices.aggregate([
  {
    $project: {
      subtotal: {
        $sum: {
          $map: {
            input: "$items",
            as: "item",
            in: {
              $multiply: ["$$item.quantity", "$$item.unitPrice"],
            },
          },
        },
      },
    },
  },
  {
    $project: {
      subtotal: 1,
      taxAmount: {
        $multiply: ["$subtotal", "$taxRate"],
      },
      total: {
        $add: ["$subtotal", { $multiply: ["$subtotal", "$taxRate"] }],
      },
    },
  },
]);
```

## Performance Considerations {#performance-considerations}

### Indexing Numeric Fields

```javascript
// Create indexes on numeric fields
db.products.createIndex({ price: 1 });
db.products.createIndex({ stockQuantity: 1 });
db.products.createIndex({ category: 1, price: 1 }); // Compound index

// Sparse indexes for optional numeric fields
db.products.createIndex({ discount: 1 }, { sparse: true });

// Partial indexes for specific ranges
db.products.createIndex(
  { price: 1 },
  {
    partialFilterExpression: {
      price: { $gte: NumberDecimal("100") },
    },
  }
);
```

### Query Optimization

```javascript
// Use appropriate data types in queries
// BAD: Mixed types can prevent index usage
db.products.find({ price: "100" }); // String comparison

// GOOD: Use same type as stored data
db.products.find({ price: NumberDecimal("100") });

// Use hint() for complex queries
db.products
  .find({
    price: { $gte: NumberDecimal("50") },
    category: "electronics",
  })
  .hint({ category: 1, price: 1 });
```

### Memory Usage Optimization

```javascript
// Use appropriate numeric types to save memory
const optimizedDoc = {
  // Use Int32 for small numbers
  quantity: NumberInt(10), // 4 bytes instead of 8

  // Use Int64 for large numbers that fit
  userId: NumberLong("123456"), // 8 bytes vs potential 16 for Decimal128

  // Use Double for approximate values
  rating: 4.5, // 8 bytes

  // Use Decimal128 only when precision is critical
  price: NumberDecimal("29.99"), // 16 bytes but exact
};
```

## Common Patterns {#common-patterns}

### Running Totals and Counters

```javascript
// Implement atomic counters
function getNextSequence(name) {
  const counter = db.counters.findOneAndUpdate(
    { _id: name },
    { $inc: { seq: NumberLong(1) } },
    {
      returnNewDocument: true,
      upsert: true,
    }
  );
  return counter.seq;
}

// Usage
const orderId = getNextSequence("order");
```

### Inventory Management

```javascript
// Atomic inventory updates
function purchaseProduct(productId, quantity) {
  const result = db.products.updateOne(
    {
      _id: productId,
      stockQuantity: { $gte: NumberInt(quantity) },
    },
    {
      $inc: { stockQuantity: NumberInt(-quantity) },
      $currentDate: { lastSold: true },
    }
  );

  return result.modifiedCount > 0;
}
```

### Price Calculations with Aggregation

```javascript
// Dynamic pricing based on various factors
db.products.aggregate([
  {
    $project: {
      name: 1,
      basePrice: "$price",

      // Calculate dynamic price
      dynamicPrice: {
        $multiply: [
          "$price",
          {
            $add: [
              1, // Base multiplier

              // Demand adjustment (higher stock = lower price)
              {
                $cond: {
                  if: { $gt: ["$stockQuantity", 100] },
                  then: NumberDecimal("-0.05"), // 5% discount
                  else: {
                    $cond: {
                      if: { $lt: ["$stockQuantity", 10] },
                      then: NumberDecimal("0.10"), // 10% premium
                      else: NumberDecimal("0"), // No change
                    },
                  },
                },
              },

              // Seasonal adjustment
              {
                $cond: {
                  if: { $eq: ["$category", "winter-clothing"] },
                  then: {
                    $cond: {
                      if: { $gte: [{ $month: new Date() }, 11] },
                      then: NumberDecimal("0.20"), // 20% winter premium
                      else: NumberDecimal("-0.30"), // 30% off-season discount
                    },
                  },
                  else: NumberDecimal("0"),
                },
              },
            ],
          },
        ],
      },
    },
  },
]);
```

## Best Practices {#best-practices}

### 1. Choose Appropriate Data Types

```javascript
// Good practices for type selection
const bestPractices = {
  // Financial data - always use Decimal128
  monetaryAmount: NumberDecimal("1234.56"),

  // Counters - use smallest appropriate integer type
  pageViews: NumberInt(1500), // < 2B
  userCount: NumberLong("50000000"), // > 2B

  // Measurements - double is usually fine
  temperature: 23.5,
  distance: 15.7,

  // Percentages - consider precision needs
  percentage: NumberDecimal("0.125"), // Exact: 12.5%
  rating: 4.3, // Approximate ok: 4.3/5
};
```

### 2. Validate Numeric Input

```javascript
// Schema validation for numeric fields
db.createCollection("orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["total", "quantity"],
      properties: {
        total: {
          bsonType: "decimal",
          minimum: 0,
          description: "Order total must be a positive decimal",
        },
        quantity: {
          bsonType: "int",
          minimum: 1,
          maximum: 1000,
          description: "Quantity must be between 1 and 1000",
        },
        discount: {
          bsonType: "decimal",
          minimum: 0,
          maximum: 1,
          description: "Discount must be between 0 and 1",
        },
      },
    },
  },
});
```

### 3. Handle Conversions Safely

```javascript
// Safe conversion pattern
function safeDecimalConvert(value) {
  return {
    $convert: {
      input: value,
      to: "decimal",
      onError: {
        $cond: {
          if: { $eq: [{ $type: value }, "string"] },
          then: "INVALID_STRING",
          else: "INVALID_TYPE",
        },
      },
      onNull: NumberDecimal("0"),
    },
  };
}
```

### 4. Performance Optimization

- **Index numeric fields** used in queries and sorts
- **Use compound indexes** for multi-field numeric queries
- **Consider partial indexes** for filtered numeric ranges
- **Use projection** to limit numeric data transfer
- **Choose smallest appropriate types** to save memory

### 5. Precision Guidelines

- **Use Decimal128** for financial calculations
- **Use Double** for scientific/measurement data
- **Use Integers** for counts and IDs
- **Consider rounding** for display purposes
- **Implement tolerance** for floating-point comparisons

## Troubleshooting {#troubleshooting}

### Common Issues and Solutions

#### 1. Type Mismatch in Queries

```javascript
// Problem: Query not finding documents due to type mismatch
db.products.find({ price: "100" }); // String vs Decimal128

// Solution: Use correct type
db.products.find({ price: NumberDecimal("100") });

// Or use $expr for type conversion
db.products.find({
  $expr: {
    $eq: [{ $toString: "$price" }, "100"],
  },
});
```

#### 2. Floating-Point Precision Issues

```javascript
// Problem: Exact equality fails
db.measurements.find({ value: 0.1 + 0.2 }); // May return no results

// Solution: Use range queries
const target = 0.3;
const epsilon = 0.000001;
db.measurements.find({
  value: {
    $gte: target - epsilon,
    $lte: target + epsilon,
  },
});
```

#### 3. Aggregation Type Errors

```javascript
// Problem: Cannot perform math on mixed types
// Solution: Convert types first
db.data.aggregate([
  {
    $project: {
      result: {
        $add: [{ $toDecimal: "$stringNumber" }, "$numericValue"],
      },
    },
  },
]);
```

#### 4. Index Not Being Used

```javascript
// Check if index is used
db.products
  .find({ price: { $gte: NumberDecimal("100") } })
  .explain("executionStats");

// Ensure query type matches index type
// If index was created on NumberDecimal, query with NumberDecimal
```

## References

- [MongoDB BSON Types Documentation](https://docs.mongodb.com/manual/reference/bson-types/)
- [Aggregation Arithmetic Operators](https://docs.mongodb.com/manual/reference/operator/aggregation/#arithmetic-expression-operators)
- [Query and Projection Operators](https://docs.mongodb.com/manual/reference/operator/query/)
- [Decimal128 Best Practices](https://docs.mongodb.com/manual/tutorial/model-monetary-data/)
- [MongoDB Indexing Strategies](https://docs.mongodb.com/manual/applications/indexes/)
