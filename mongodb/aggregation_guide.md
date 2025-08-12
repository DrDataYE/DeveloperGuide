# MongoDB Aggregation Framework: Complete Guide

The MongoDB Aggregation Framework is a powerful data processing pipeline that allows you to transform and analyze data within the database. This guide covers all major aggregation operations with practical examples.

## Table of Contents

1. [Introduction to Aggregation](#introduction)
2. [Pipeline Stages](#pipeline-stages)
3. [Matching and Filtering](#matching-and-filtering)
4. [Grouping Data](#grouping-data)
5. [Projection and Reshaping](#projection-and-reshaping)
6. [String Operations](#string-operations)
7. [Array Operations](#array-operations)
8. [Sorting and Limiting](#sorting-and-limiting)
9. [Bucketing](#bucketing)
10. [Geospatial Aggregation](#geospatial-aggregation)
11. [Output Operations](#output-operations)
12. [Best Practices](#best-practices)

## Introduction to Aggregation {#introduction}

The aggregation pipeline processes documents through a sequence of stages, where each stage transforms the documents as they pass through the pipeline.

### Basic Syntax

```javascript
db.collection.aggregate([{ stage1 }, { stage2 }, { stage3 }]);
```

## Pipeline Stages {#pipeline-stages}

### Common Pipeline Stages

- `$match`: Filters documents
- `$group`: Groups documents and performs calculations
- `$project`: Reshapes documents
- `$sort`: Sorts documents
- `$limit`: Limits the number of documents
- `$skip`: Skips a specified number of documents
- `$unwind`: Deconstructs arrays
- `$lookup`: Performs joins
- `$out`: Writes results to a collection

## Matching and Filtering {#matching-and-filtering}

Use `$match` to filter documents early in the pipeline for better performance.

```javascript
// Filter female persons
db.persons.aggregate([
  {
    $match: {
      gender: "female",
    },
  },
]);
```

**Best Practice**: Place `$match` stages as early as possible to reduce the number of documents processed by subsequent stages.

## Grouping Data {#grouping-data}

The `$group` stage groups documents by specified fields and performs accumulator operations.

### Basic Grouping

```javascript
// Count female persons by state
db.persons.aggregate([
  {
    $match: {
      gender: "female",
    },
  },
  {
    $group: {
      _id: { state: "$location.state" },
      totalPersons: { $sum: 1 },
    },
  },
  {
    $sort: { totalPersons: -1 },
  },
]);
```

### Group Accumulator Operators

- `$sum`: Calculates sum
- `$avg`: Calculates average
- `$min`: Finds minimum value
- `$max`: Finds maximum value
- `$push`: Adds values to an array
- `$addToSet`: Adds unique values to an array
- `$first`: Gets first value in group
- `$last`: Gets last value in group

### Advanced Grouping Examples

```javascript
// Group friends by age and collect all hobbies
db.friends.aggregate([
  {
    $group: {
      _id: { age: "$age" },
      allHobbies: { $push: "$hobbies" },
    },
  },
]);

// Group with unique hobbies using $unwind and $addToSet
db.friends.aggregate([
  { $unwind: "$hobbies" },
  {
    $group: {
      _id: { age: "$age" },
      allHobbies: { $addToSet: "$hobbies" },
    },
  },
]);
```

## Projection and Reshaping {#projection-and-reshaping}

The `$project` stage reshapes documents by including, excluding, or transforming fields.

### Basic Projection

```javascript
// Select specific fields and create new ones
db.persons.aggregate([
  {
    $project: {
      _id: 0, // Exclude _id
      gender: 1, // Include gender
      fullName: {
        $concat: ["$name.first", " ", "$name.last"],
      },
    },
  },
]);
```

### Data Type Conversions

```javascript
// Convert coordinates to proper GeoJSON format
db.persons.aggregate([
  {
    $project: {
      _id: 0,
      name: 1,
      email: 1,
      birthdate: { $toDate: "$dob.date" },
      age: "$dob.age",
      location: {
        type: "Point",
        coordinates: [
          {
            $convert: {
              input: "$location.coordinates.longitude",
              to: "double",
              onError: 0.0,
              onNull: 0.0,
            },
          },
          {
            $convert: {
              input: "$location.coordinates.latitude",
              to: "double",
              onError: 0.0,
              onNull: 0.0,
            },
          },
        ],
      },
    },
  },
]);
```

## String Operations {#string-operations}

MongoDB provides powerful string manipulation operators for text processing.

### String Concatenation and Case Conversion

```javascript
// Create uppercase full names
db.persons.aggregate([
  {
    $project: {
      _id: 0,
      gender: 1,
      fullName: {
        $concat: [{ $toUpper: "$name.first" }, " ", { $toUpper: "$name.last" }],
      },
    },
  },
]);
```

### Advanced String Manipulation

```javascript
// Capitalize first letter of each name
db.persons.aggregate([
  {
    $project: {
      _id: 0,
      gender: 1,
      fullName: {
        $concat: [
          { $toUpper: { $substrCP: ["$name.first", 0, 1] } },
          {
            $substrCP: [
              "$name.first",
              1,
              { $subtract: [{ $strLenCP: "$name.first" }, 1] },
            ],
          },
          " ",
          { $toUpper: { $substrCP: ["$name.last", 0, 1] } },
          {
            $substrCP: [
              "$name.last",
              1,
              { $subtract: [{ $strLenCP: "$name.last" }, 1] },
            ],
          },
        ],
      },
    },
  },
]);
```

### String Operators Reference

- `$concat`: Concatenates strings
- `$toUpper`: Converts to uppercase
- `$toLower`: Converts to lowercase
- `$substrCP`: Extracts substring by code points
- `$strLenCP`: Returns string length in code points

## Array Operations {#array-operations}

MongoDB provides several operators for working with arrays in aggregation pipelines.

### Array Slicing and Sizing

```javascript
// Get first exam score only
db.friends.aggregate([
  {
    $project: {
      _id: 0,
      examScore: { $slice: ["$examScores", 1] },
    },
  },
]);

// Count number of scores
db.friends.aggregate([
  {
    $project: {
      _id: 0,
      numScores: { $size: "$examScores" },
    },
  },
]);
```

### Array Filtering

```javascript
// Filter scores greater than 60
db.friends.aggregate([
  {
    $project: {
      _id: 0,
      scores: {
        $filter: {
          input: "$examScores",
          as: "sc",
          cond: { $gt: ["$$sc.score", 60] },
        },
      },
    },
  },
]);
```

### Unwinding Arrays

```javascript
// Unwind exam scores and find maximum score per person
db.friends.aggregate([
  { $unwind: "$examScores" },
  {
    $project: {
      _id: 1,
      name: 1,
      age: 1,
      score: "$examScores.score",
    },
  },
  { $sort: { score: -1 } },
  {
    $group: {
      _id: "$_id",
      name: { $first: "$name" },
      maxScore: { $max: "$score" },
    },
  },
  { $sort: { maxScore: -1 } },
]);
```

### Array Operators Reference

- `$slice`: Returns subset of array
- `$size`: Returns array length
- `$filter`: Filters array elements
- `$unwind`: Deconstructs arrays into separate documents
- `$push`: Adds elements to array (in $group)
- `$addToSet`: Adds unique elements to array (in $group)

## Sorting and Limiting {#sorting-and-limiting}

Control the order and quantity of results using `$sort`, `$limit`, and `$skip`.

```javascript
// Sort by birthdate, skip first 10, limit to next 10
db.persons.aggregate([
  {
    $match: {
      gender: "male",
    },
  },
  {
    $project: {
      _id: 0,
      gender: 1,
      name: { $concat: ["$name.first", " ", "$name.last"] },
      birthdate: { $toDate: "$dob.date" },
      age: "$dob.age",
    },
  },
  {
    $sort: { birthdate: 1 },
  },
  {
    $skip: 10,
  },
  {
    $limit: 10,
  },
]);
```

**Performance Tip**: Use indexes on sort fields to improve performance.

## Bucketing {#bucketing}

Bucketing allows you to group documents into ranges or categories.

### Manual Bucketing with $bucket

```javascript
// Group persons by age ranges
db.persons.aggregate([
  {
    $bucket: {
      groupBy: "$dob.age",
      boundaries: [0, 18, 30, 50, 80, 120],
      output: {
        numPersons: { $sum: 1 },
        averageAge: { $avg: "$dob.age" },
      },
    },
  },
]);
```

### Automatic Bucketing with $bucketAuto

```javascript
// Automatically create 5 age buckets
db.persons.aggregate([
  {
    $bucketAuto: {
      groupBy: "$dob.age",
      buckets: 5,
      output: {
        numPersons: { $sum: 1 },
        averageAge: { $avg: "$dob.age" },
      },
    },
  },
]);
```

## Geospatial Aggregation {#geospatial-aggregation}

Use `$geoNear` for proximity-based aggregation queries.

```javascript
// Find nearest transformed persons with additional filters
db.transformedPersons.aggregate([
  {
    $geoNear: {
      near: {
        type: "Point",
        coordinates: [-18.4, 33.456],
      },
      distanceField: "distance",
      maxDistance: 1000000,
      query: { age: { $gt: 30 } },
      spherical: true,
      key: "location",
    },
  },
  { $limit: 10 },
]);
```

**Requirements**:

- Collection must have a 2dsphere index
- Only one `$geoNear` stage allowed per pipeline
- Must be the first stage in pipeline

## Output Operations {#output-operations}

### Writing Results to Collections

```javascript
// Transform and save to new collection
db.persons.aggregate([
  {
    $project: {
      _id: 0,
      name: 1,
      email: 1,
      birthdate: { $toDate: "$dob.date" },
      // ... other transformations
    },
  },
  {
    $out: "transformedPersons",
  },
]);
```

**Note**: `$out` replaces the target collection entirely. Use `$merge` for more flexible output options.

## Best Practices {#best-practices}

### Performance Optimization

1. **Filter Early**: Use `$match` as early as possible
2. **Index Support**: Ensure sort and match fields are indexed
3. **Limit Data**: Use `$limit` when you don't need all results
4. **Project Only Needed Fields**: Reduce memory usage with `$project`

### Pipeline Design

1. **Stage Order Matters**: Optimize the sequence of operations
2. **Use explain()**: Analyze query performance
   ```javascript
   db.collection.aggregate(pipeline).explain("executionStats");
   ```
3. **Test with Sample Data**: Validate pipelines on small datasets first

### Memory Considerations

- Each pipeline stage has a 16MB memory limit
- Use `allowDiskUse: true` for large datasets
- Consider breaking complex pipelines into multiple steps

### Error Handling

- Use `$convert` with `onError` and `onNull` for type conversions
- Validate data types before operations
- Test edge cases (empty arrays, null values, etc.)

## Common Patterns

### Date Grouping

```javascript
// Group by birth year
{
  $group: {
    _id: { birthYear: { $isoWeekYear: "$birthdate" } },
    numPersons: { $sum: 1 }
  }
}
```

### Conditional Logic

```javascript
// Add conditional fields
{
  $project: {
    name: 1,
    ageGroup: {
      $switch: {
        branches: [
          { case: { $lt: ["$age", 18] }, then: "Minor" },
          { case: { $lt: ["$age", 65] }, then: "Adult" },
          { case: { $gte: ["$age", 65] }, then: "Senior" }
        ],
        default: "Unknown"
      }
    }
  }
}
```

## References

- [MongoDB Aggregation Pipeline Documentation](https://docs.mongodb.com/manual/aggregation/)
- [Aggregation Pipeline Operators](https://docs.mongodb.com/manual/reference/operator/aggregation/)
- [Aggregation Pipeline Optimization](https://docs.mongodb.com/manual/core/aggregation-pipeline-optimization/)
