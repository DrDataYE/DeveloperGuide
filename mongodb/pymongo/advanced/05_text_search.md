# PyMongo Text Search - Text Indexing and Search

Comprehensive guide for text search in MongoDB using PyMongo.

## Basics

```python
from pymongo import MongoClient, TEXT
import re

# Connection
client = MongoClient('mongodb://localhost:27017/')
db = client.text_search_demo
collection = db.articles

# Clear previous data
collection.drop()
```

## Creating Text Indexes

```python
def create_text_indexes():
    """Create text search indexes"""

    # Insert sample data
    articles = [
        {
            "title": "Python Programming Guide",
            "content": "Learn Python programming with examples and best practices",
            "tags": ["python", "programming", "tutorial"],
            "category": "technology"
        },
        {
            "title": "MongoDB Database Tutorial",
            "content": "Complete guide to MongoDB database operations and queries",
            "tags": ["mongodb", "database", "nosql"],
            "category": "technology"
        },
        {
            "title": "Web Development with Flask",
            "content": "Build web applications using Flask framework and Python",
            "tags": ["flask", "web", "python"],
            "category": "technology"
        }
    ]

    collection.insert_many(articles)

    # Create text index on multiple fields
    collection.create_index([
        ("title", TEXT),
        ("content", TEXT),
        ("tags", TEXT)
    ])

    print("✅ Text index created")

create_text_indexes()
```

## Basic Text Search

```python
def basic_text_search():
    """Basic text search operations"""

    # Simple search
    results = collection.find({"$text": {"$search": "Python"}})
    print("Search for 'Python':")
    for doc in results:
        print(f"  - {doc['title']}")

    # Search with multiple terms
    results = collection.find({"$text": {"$search": "MongoDB database"}})
    print("\nSearch for 'MongoDB database':")
    for doc in results:
        print(f"  - {doc['title']}")

    # Exact phrase search
    results = collection.find({"$text": {"$search": "\"Python programming\""}})
    print("\nSearch for exact phrase 'Python programming':")
    for doc in results:
        print(f"  - {doc['title']}")

    # Exclude words
    results = collection.find({"$text": {"$search": "programming -Flask"}})
    print("\nSearch for 'programming' excluding 'Flask':")
    for doc in results:
        print(f"  - {doc['title']}")

basic_text_search()
```

## Advanced Search with Results

```python
def advanced_text_search():
    """Advanced text search with result scoring"""

    # Search with relevance score
    results = collection.find(
        {"$text": {"$search": "Python programming"}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})])

    print("Search with relevance score:")
    for doc in results:
        print(f"  - {doc['title']} (Score: {doc['score']:.2f})")

    # Combined search with other conditions
    results = collection.find({
        "$text": {"$search": "tutorial"},
        "category": "technology"
    })

    print("\nCombined search:")
    for doc in results:
        print(f"  - {doc['title']} ({doc['category']})")

    # Search in different languages
    collection.create_index([("title", TEXT)], default_language='arabic')
    print("✅ Arabic text index created")

advanced_text_search()
```

## Analytics and Analysis

```python
def text_search_analytics():
    """Text search analytics and statistics"""

    # Analyze most searched words
    pipeline = [
        {"$match": {"$text": {"$search": "programming"}}},
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1},
            "avg_score": {"$avg": {"$meta": "textScore"}}
        }}
    ]

    results = list(collection.aggregate(pipeline))
    print("Search statistics:")
    for result in results:
        print(f"  {result['_id']}: {result['count']} documents")

text_search_analytics()
```

## Best Practices

```python
def text_search_best_practices():
    """Best practices for text search"""

    practices = {
        "Index Design": [
            "Use only one text index per collection",
            "Index only important fields",
            "Use different weights for fields based on importance"
        ],
        "Query Optimization": [
            "Use limits to improve performance",
            "Combine text search with other filters",
            "Use projection to reduce data transfer"
        ],
        "Performance": [
            "Monitor text index size",
            "Use aggregation for complex analysis",
            "Consider alternatives for big data"
        ]
    }

    for category, items in practices.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ✅ {item}")

text_search_best_practices()
```

## Summary

Key Features:

- **Text Indexing**: `create_index([(field, TEXT)])`
- **Simple Search**: `{"$text": {"$search": "term"}}`
- **Phrase Search**: `{"$text": {"$search": "\"exact phrase\""}}`
- **Result Scoring**: `{"score": {"$meta": "textScore"}}`
- **Word Exclusion**: `{"$text": {"$search": "include -exclude"}}`

Best Practices:

- Use only one text index per collection
- Combine text search with other filters
- Monitor text query performance
- Use different weights for fields

### Next: [Geospatial Queries](./06_geospatial_queries.md)
