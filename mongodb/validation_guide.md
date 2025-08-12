# MongoDB Schema Validation for `posts` Collection

This guide explains the two scripts in this folder and how they work together to enforce and adjust schema validation using `$jsonSchema`.

## What the schema enforces

The `posts` documents must be objects with required fields:

- `title`: string (required)
- `text`: string (required)
- `creator`: objectId (required)
- `comments`: array of comment objects (required)
  - Each comment requires:
    - `text`: string (required)
    - `author`: objectId (required)

## 1) Create collection with schema (`validationCreate.js`)

Creates the `posts` collection with a `$jsonSchema` validator:

```javascript
db.createCollection("posts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "text", "creator", "comments"],
      properties: {
        title: {
          bsonType: "string",
          description: "must be a string and is required",
        },
        text: {
          bsonType: "string",
          description: "must be a string and is required",
        },
        creator: {
          bsonType: "objectId",
          description: "must be an objectId and is required",
        },
        comments: {
          bsonType: "array",
          description: "must be an array and is required",
          items: {
            bsonType: "object",
            required: ["text", "author"],
            properties: {
              text: {
                bsonType: "string",
                description: "must be a string and is required",
              },
              author: {
                bsonType: "objectId",
                description: "must be an objectId and is required",
              },
            },
          },
        },
      },
    },
  },
});
```

Use this when creating the collection for the first time.

## 2) Modify validation on an existing collection (`validationChange.js`)

Adjusts the validator on the already-created `posts` collection and sets the enforcement mode to warn:

```javascript
db.runCommand({
  collMod: "posts",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "text", "creator", "comments"],
      properties: {
        title: {
          bsonType: "string",
          description: "must be a string and is required",
        },
        text: {
          bsonType: "string",
          description: "must be a string and is required",
        },
        creator: {
          bsonType: "objectId",
          description: "must be an objectId and is required",
        },
        comments: {
          bsonType: "array",
          description: "must be an array and is required",
          items: {
            bsonType: "object",
            required: ["text", "author"],
            properties: {
              text: {
                bsonType: "string",
                description: "must be a string and is required",
              },
              author: {
                bsonType: "objectId",
                description: "must be an objectId and is required",
              },
            },
          },
        },
      },
    },
  },
  validationAction: "warn",
});
```

- `validationAction: 'warn'`: writes that violate the schema are allowed, but MongoDB logs a warning.
- Alternative: `validationAction: 'error'` rejects non-conforming writes.
- You can also use `validationLevel` (e.g., `strict` or `moderate`) to control how existing documents are treated (not set here; default is `strict`).

## Quick tests in mongosh

Assumes the collection exists and the validator is in place.

Valid insert (should succeed):

```javascript
const postOk = {
  title: "Hello",
  text: "World",
  creator: ObjectId(),
  comments: [{ text: "Nice!", author: ObjectId() }],
};
db.posts.insertOne(postOk);
```

Invalid insert examples:

- Missing required field (e.g., no `creator`)

```javascript
db.posts.insertOne({ title: "X", text: "Y", comments: [] });
// 'warn': insert succeeds with a warning; 'error': insert fails
```

- Wrong type (e.g., `creator` not an ObjectId)

```javascript
db.posts.insertOne({
  title: "X",
  text: "Y",
  creator: "not-an-oid",
  comments: [],
});
```

## Switch enforcement to errors (optional)

Reject invalid writes (use after cleaning up data or once you’re confident):

```javascript
db.runCommand({
  collMod: "posts",
  validator: {
    /* same $jsonSchema */
  },
  validationAction: "error",
});
```

## Tips and troubleshooting

- Use `ObjectId()` for `creator` and `comments.author` when inserting from mongosh.
- Existing invalid documents remain until updated; validators apply to inserts/updates.
- To find nonconforming documents, you can approximate checks with aggregation and `$type`/`$expr` or run app-level audits.
- Validators don’t replace application-level validation; they complement it.

## References

- MongoDB Schema Validation: https://www.mongodb.com/docs/manual/core/schema-validation/
- `$jsonSchema` keywords: https://www.mongodb.com/docs/manual/reference/operator/query/jsonSchema/
