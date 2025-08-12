# PyMongo Indexing Strategies

This comprehensive guide covers MongoDB indexing strategies using PyMongo, including index creation, optimization, and performance monitoring.

## Table of Contents

1. [Index Fundamentals](#index-fundamentals)
2. [Index Types](#index-types)
3. [Creating and Managing Indexes](#creating-and-managing-indexes)
4. [Index Performance Analysis](#index-performance-analysis)
5. [Advanced Indexing Strategies](#advanced-indexing-strategies)
6. [Index Optimization](#index-optimization)
7. [Real-World Examples](#real-world-examples)
8. [Best Practices](#best-practices)

## Index Fundamentals

Understanding how indexes work in MongoDB and how to use them effectively with PyMongo.

### Basic Index Concepts

```python
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT, GEO2D, GEOSPHERE
from bson import ObjectId
import time
import json
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.indexing_demo
collection = db.products

def setup_sample_data():
    """Setup comprehensive sample data for indexing examples"""

    # Clear existing data
    collection.delete_many({})

    # Sample products with various data types
    sample_products = []

    categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Sports']
    brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE']

    for i in range(10000):
        product = {
            "name": f"Product {i}",
            "sku": f"SKU-{i:06d}",
            "price": round(10 + (i % 1000) * 0.5, 2),
            "category": categories[i % len(categories)],
            "brand": brands[i % len(brands)],
            "in_stock": i % 3 != 0,  # 2/3 of products in stock
            "quantity": i % 100,
            "rating": round(1 + (i % 50) * 0.1, 1),
            "created_at": datetime.utcnow() - timedelta(days=i % 365),
            "tags": [f"tag{i % 10}", f"tag{(i + 1) % 10}"],
            "description": f"This is a detailed description for product {i} " * 3,
            "specifications": {
                "weight": round(0.1 + (i % 100) * 0.1, 2),
                "dimensions": {
                    "length": i % 50 + 1,
                    "width": i % 30 + 1,
                    "height": i % 20 + 1
                }
            },
            "location": {
                "type": "Point",
                "coordinates": [
                    -180 + (i % 360),  # longitude
                    -90 + (i % 180)    # latitude
                ]
            }
        }
        sample_products.append(product)

    # Insert in batches for better performance
    batch_size = 1000
    for i in range(0, len(sample_products), batch_size):
        batch = sample_products[i:i + batch_size]
        collection.insert_many(batch)

    print(f"✅ Inserted {len(sample_products)} sample products")
    return len(sample_products)

# Setup data
product_count = setup_sample_data()
```

### Index Performance Comparison

```python
def demonstrate_index_impact():
    """Demonstrate the performance impact of indexes"""

    print("=== Index Performance Demonstration ===")

    # Drop all indexes except _id
    collection.drop_indexes()

    # Query without index
    start_time = time.time()
    results_no_index = list(collection.find({"category": "Electronics"}).limit(100))
    time_no_index = time.time() - start_time

    print(f"Query without index: {time_no_index:.4f} seconds")
    print(f"Results found: {len(results_no_index)}")

    # Create index on category
    collection.create_index("category")

    # Query with index
    start_time = time.time()
    results_with_index = list(collection.find({"category": "Electronics"}).limit(100))
    time_with_index = time.time() - start_time

    print(f"Query with index: {time_with_index:.4f} seconds")
    print(f"Results found: {len(results_with_index)}")

    if time_no_index > 0:
        improvement = time_no_index / time_with_index
        print(f"Performance improvement: {improvement:.1f}x faster")

    return time_no_index, time_with_index

# Demonstrate index impact
index_demo = demonstrate_index_impact()
```

## Index Types

### Single Field Indexes

```python
def single_field_indexes():
    """Examples of single field indexes"""

    print("=== Single Field Indexes ===")

    # Basic single field index (ascending)
    collection.create_index("price")
    print("✅ Created ascending index on 'price'")

    # Descending index
    collection.create_index([("created_at", DESCENDING)])
    print("✅ Created descending index on 'created_at'")

    # Index on nested field
    collection.create_index("specifications.weight")
    print("✅ Created index on nested field 'specifications.weight'")

    # Index on array field
    collection.create_index("tags")
    print("✅ Created index on array field 'tags'")

    # Test queries that use these indexes

    # Price range query (uses price index)
    expensive_products = list(collection.find({
        "price": {"$gte": 100, "$lte": 200}
    }).limit(5))

    # Recent products (uses created_at index)
    recent_products = list(collection.find().sort([
        ("created_at", DESCENDING)
    ]).limit(5))

    # Products by weight (uses nested field index)
    light_products = list(collection.find({
        "specifications.weight": {"$lt": 5.0}
    }).limit(5))

    # Products by tag (uses array index)
    tagged_products = list(collection.find({
        "tags": "tag1"
    }).limit(5))

    print(f"Expensive products: {len(expensive_products)}")
    print(f"Recent products: {len(recent_products)}")
    print(f"Light products: {len(light_products)}")
    print(f"Tagged products: {len(tagged_products)}")

    return {
        "expensive": expensive_products,
        "recent": recent_products,
        "light": light_products,
        "tagged": tagged_products
    }

# Execute single field index examples
single_field_results = single_field_indexes()
```

### Compound Indexes

```python
def compound_indexes():
    """Examples of compound indexes"""

    print("\n=== Compound Indexes ===")

    # Compound index on multiple fields
    collection.create_index([
        ("category", ASCENDING),
        ("brand", ASCENDING),
        ("price", DESCENDING)
    ])
    print("✅ Created compound index on 'category', 'brand', 'price'")

    # Another compound index for different query patterns
    collection.create_index([
        ("in_stock", ASCENDING),
        ("rating", DESCENDING),
        ("created_at", DESCENDING)
    ])
    print("✅ Created compound index on 'in_stock', 'rating', 'created_at'")

    # ESR Rule demonstration (Equality, Sort, Range)

    # Good query: follows ESR rule
    # Equality on category, Sort by price, Range on rating
    esr_query = list(collection.find({
        "category": "Electronics",  # Equality
        "rating": {"$gte": 4.0}     # Range
    }).sort([("price", DESCENDING)]).limit(10))  # Sort

    # Query using prefix of compound index
    prefix_query = list(collection.find({
        "category": "Electronics",
        "brand": "BrandA"
    }).limit(10))

    # Query that can use the index for sorting
    sort_query = list(collection.find({
        "category": "Books"
    }).sort([
        ("brand", ASCENDING),
        ("price", DESCENDING)
    ]).limit(10))

    print(f"ESR query results: {len(esr_query)}")
    print(f"Prefix query results: {len(prefix_query)}")
    print(f"Sort query results: {len(sort_query)}")

    # Demonstrate index prefix usage
    def demonstrate_index_prefixes():
        """Show how compound indexes can serve multiple query patterns"""

        # Index: (category, brand, price)
        # Can serve queries on:
        # - category
        # - category + brand
        # - category + brand + price
        # Cannot efficiently serve:
        # - brand only
        # - price only
        # - brand + price

        print("\nIndex prefix demonstration:")
        print("Compound index: (category, brand, price)")
        print("✅ Can serve: category")
        print("✅ Can serve: category + brand")
        print("✅ Can serve: category + brand + price")
        print("❌ Cannot efficiently serve: brand only")
        print("❌ Cannot efficiently serve: price only")
        print("❌ Cannot efficiently serve: brand + price")

    demonstrate_index_prefixes()

    return {
        "esr_query": esr_query,
        "prefix_query": prefix_query,
        "sort_query": sort_query
    }

# Execute compound index examples
compound_results = compound_indexes()
```

### Text Indexes

```python
def text_indexes():
    """Examples of text indexes for full-text search"""

    print("\n=== Text Indexes ===")

    # Create text index on name and description
    collection.create_index([
        ("name", TEXT),
        ("description", TEXT)
    ])
    print("✅ Created text index on 'name' and 'description'")

    # Text search examples

    # Basic text search
    text_search_results = list(collection.find({
        "$text": {"$search": "Product"}
    }).limit(10))

    # Text search with multiple terms
    multi_term_results = list(collection.find({
        "$text": {"$search": "Product detailed"}
    }).limit(10))

    # Text search with phrase
    phrase_search_results = list(collection.find({
        "$text": {"$search": "\"detailed description\""}
    }).limit(10))

    # Text search with negation
    negation_results = list(collection.find({
        "$text": {"$search": "Product -Electronics"}
    }).limit(10))

    # Text search with score
    scored_results = list(collection.find(
        {"$text": {"$search": "Product detailed"}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).limit(10))

    print(f"Basic text search: {len(text_search_results)} results")
    print(f"Multi-term search: {len(multi_term_results)} results")
    print(f"Phrase search: {len(phrase_search_results)} results")
    print(f"Negation search: {len(negation_results)} results")
    print(f"Scored search: {len(scored_results)} results")

    # Show text search scores
    if scored_results:
        print("\nTop text search results with scores:")
        for result in scored_results[:5]:
            print(f"  {result['name']}: score {result['score']:.2f}")

    return {
        "basic": text_search_results,
        "multi_term": multi_term_results,
        "phrase": phrase_search_results,
        "scored": scored_results
    }

# Execute text index examples
text_results = text_indexes()
```

### Geospatial Indexes

```python
def geospatial_indexes():
    """Examples of geospatial indexes"""

    print("\n=== Geospatial Indexes ===")

    # Create 2dsphere index for GeoJSON data
    collection.create_index([("location", GEOSPHERE)])
    print("✅ Created 2dsphere index on 'location'")

    # Geospatial queries

    # Find products near a specific location
    near_query = list(collection.find({
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [0, 0]  # Greenwich, UK
                },
                "$maxDistance": 1000000  # 1000 km in meters
            }
        }
    }).limit(10))

    # Find products within a polygon
    polygon_query = list(collection.find({
        "location": {
            "$geoWithin": {
                "$geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-10, -10],
                        [10, -10],
                        [10, 10],
                        [-10, 10],
                        [-10, -10]
                    ]]
                }
            }
        }
    }).limit(10))

    # Find products within a circle
    circle_query = list(collection.find({
        "location": {
            "$geoWithin": {
                "$centerSphere": [
                    [0, 0],  # Center coordinates
                    10 / 3963.2  # Radius in radians (10 miles)
                ]
            }
        }
    }).limit(10))

    print(f"Near query results: {len(near_query)}")
    print(f"Polygon query results: {len(polygon_query)}")
    print(f"Circle query results: {len(circle_query)}")

    # Aggregation with geospatial operations
    geo_aggregation = list(collection.aggregate([
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [0, 0]},
                "distanceField": "distance",
                "maxDistance": 1000000,
                "spherical": True
            }
        },
        {
            "$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "avg_distance": {"$avg": "$distance"}
            }
        },
        {"$sort": {"count": -1}}
    ]))

    print(f"Geo aggregation results: {len(geo_aggregation)}")
    if geo_aggregation:
        print("Category distribution by proximity:")
        for result in geo_aggregation:
            print(f"  {result['_id']}: {result['count']} products, "
                  f"avg distance: {result['avg_distance']:.0f}m")

    return {
        "near": near_query,
        "polygon": polygon_query,
        "circle": circle_query,
        "aggregation": geo_aggregation
    }

# Execute geospatial index examples
geo_results = geospatial_indexes()
```

### Partial Indexes

```python
def partial_indexes():
    """Examples of partial indexes for selective indexing"""

    print("\n=== Partial Indexes ===")

    # Index only in-stock products
    collection.create_index(
        "price",
        partialFilterExpression={"in_stock": True}
    )
    print("✅ Created partial index on 'price' for in-stock products only")

    # Index only high-rated products
    collection.create_index(
        [("category", ASCENDING), ("rating", DESCENDING)],
        partialFilterExpression={"rating": {"$gte": 4.0}}
    )
    print("✅ Created partial compound index for high-rated products")

    # Index only expensive products
    collection.create_index(
        "brand",
        partialFilterExpression={"price": {"$gte": 100}}
    )
    print("✅ Created partial index on 'brand' for expensive products")

    # Queries that use partial indexes

    # Query that matches partial filter (will use index)
    in_stock_expensive = list(collection.find({
        "in_stock": True,
        "price": {"$gte": 50, "$lte": 150}
    }).limit(10))

    # Query that doesn't match partial filter (won't use this specific index)
    out_of_stock_query = list(collection.find({
        "in_stock": False,
        "price": {"$gte": 50, "$lte": 150}
    }).limit(10))

    # High-rated products query
    high_rated_electronics = list(collection.find({
        "category": "Electronics",
        "rating": {"$gte": 4.5}
    }).sort([("rating", DESCENDING)]).limit(10))

    print(f"In-stock expensive products: {len(in_stock_expensive)}")
    print(f"Out-of-stock products: {len(out_of_stock_query)}")
    print(f"High-rated electronics: {len(high_rated_electronics)}")

    # Demonstrate space savings of partial indexes
    def demonstrate_partial_index_benefits():
        """Show benefits of partial indexes"""

        print("\nPartial Index Benefits:")
        print("✅ Reduced index size (only indexes matching documents)")
        print("✅ Faster index maintenance")
        print("✅ Reduced memory usage")
        print("✅ Better cache efficiency")
        print("⚠ Only helps queries that match the filter expression")

    demonstrate_partial_index_benefits()

    return {
        "in_stock_expensive": in_stock_expensive,
        "out_of_stock": out_of_stock_query,
        "high_rated": high_rated_electronics
    }

# Execute partial index examples
partial_results = partial_indexes()
```

### Sparse Indexes

```python
def sparse_indexes():
    """Examples of sparse indexes"""

    print("\n=== Sparse Indexes ===")

    # Add some documents with missing fields for demonstration
    collection.insert_many([
        {"name": "Product with discount", "price": 50, "discount_percentage": 10},
        {"name": "Product without discount", "price": 60},
        {"name": "Product with zero discount", "price": 70, "discount_percentage": 0}
    ])

    # Create sparse index (only indexes documents that have the field)
    collection.create_index("discount_percentage", sparse=True)
    print("✅ Created sparse index on 'discount_percentage'")

    # Create sparse compound index
    collection.create_index([
        ("category", ASCENDING),
        ("discount_percentage", DESCENDING)
    ], sparse=True)
    print("✅ Created sparse compound index")

    # Queries with sparse indexes

    # This query will only return documents that have discount_percentage field
    discounted_products = list(collection.find({
        "discount_percentage": {"$gt": 0}
    }).limit(10))

    # This query might not return all documents without discount_percentage
    # depending on the query planner's choice
    all_products_sort_by_discount = list(collection.find().sort([
        ("discount_percentage", DESCENDING)
    ]).limit(10))

    print(f"Discounted products: {len(discounted_products)}")
    print(f"All products sorted by discount: {len(all_products_sort_by_discount)}")

    # Demonstrate sparse vs non-sparse behavior
    def demonstrate_sparse_behavior():
        """Show the difference between sparse and regular indexes"""

        print("\nSparse Index Behavior:")
        print("✅ Only indexes documents that contain the indexed field")
        print("✅ Reduces index size for fields that are often missing")
        print("⚠ Queries that sort by sparse-indexed fields may miss documents")
        print("⚠ Use hint() to force use of sparse index when needed")

        # Example of forcing sparse index usage
        forced_sparse_query = list(collection.find().sort([
            ("discount_percentage", DESCENDING)
        ]).hint([("discount_percentage", 1)]).limit(5))

        print(f"Forced sparse index query: {len(forced_sparse_query)} results")

    demonstrate_sparse_behavior()

    return {
        "discounted": discounted_products,
        "sorted_by_discount": all_products_sort_by_discount
    }

# Execute sparse index examples
sparse_results = sparse_indexes()
```

## Creating and Managing Indexes

### Index Creation and Options

```python
def index_creation_management():
    """Comprehensive index creation and management examples"""

    print("\n=== Index Creation and Management ===")

    # Create index with various options

    # Background index creation (non-blocking)
    try:
        collection.create_index(
            "sku",
            background=True,  # Deprecated in MongoDB 4.2+, but shown for completeness
            unique=True,
            name="sku_unique_index"
        )
        print("✅ Created unique background index on 'sku'")
    except Exception as e:
        print(f"Index creation note: {e}")

    # TTL (Time To Live) index for automatic document expiration
    # Note: This would typically be on a date field in a real scenario
    collection.create_index(
        "created_at",
        expireAfterSeconds=30 * 24 * 60 * 60,  # 30 days
        name="created_at_ttl"
    )
    print("✅ Created TTL index on 'created_at' (30 days expiration)")

    # Index with custom collation
    collection.create_index(
        "name",
        name="name_case_insensitive",
        collation={
            'locale': 'en',
            'strength': 1  # Case-insensitive
        }
    )
    print("✅ Created case-insensitive index on 'name'")

    # Manage indexes

    # List all indexes
    indexes = list(collection.list_indexes())
    print(f"\nCurrent indexes ({len(indexes)}):")
    for idx in indexes:
        print(f"  - {idx['name']}: {idx.get('key', {})}")

    # Get index information
    index_info = collection.index_information()
    print(f"\nIndex information: {len(index_info)} indexes")

    # Check if specific index exists
    def index_exists(index_name):
        """Check if an index exists"""
        return index_name in index_info

    print(f"SKU index exists: {index_exists('sku_unique_index')}")
    print(f"TTL index exists: {index_exists('created_at_ttl')}")

    # Drop specific index
    try:
        collection.drop_index("name_case_insensitive")
        print("✅ Dropped case-insensitive name index")
    except Exception as e:
        print(f"Drop index note: {e}")

    return {
        "indexes": indexes,
        "index_info": index_info
    }

# Execute index management examples
index_mgmt_results = index_creation_management()
```

### Index Maintenance Operations

```python
def index_maintenance():
    """Index maintenance and monitoring operations"""

    print("\n=== Index Maintenance ===")

    # Reindex collection (recreate all indexes)
    def reindex_collection():
        """Reindex a collection (use with caution in production)"""

        try:
            result = db.command("reIndex", "products")
            print(f"✅ Reindexed collection: {result}")
        except Exception as e:
            print(f"Reindex note: {e}")

    # Get index statistics
    def get_index_stats():
        """Get detailed index statistics"""

        try:
            stats = db.command("collStats", "products", indexDetails=True)

            print("Collection statistics:")
            print(f"  Total documents: {stats.get('count', 0):,}")
            print(f"  Total size: {stats.get('size', 0):,} bytes")
            print(f"  Total index size: {stats.get('totalIndexSize', 0):,} bytes")

            # Index details
            index_sizes = stats.get('indexSizes', {})
            print("\nIndex sizes:")
            for index_name, size in index_sizes.items():
                print(f"  {index_name}: {size:,} bytes")

            return stats

        except Exception as e:
            print(f"Stats error: {e}")
            return {}

    # Monitor index usage
    def monitor_index_usage():
        """Monitor index usage statistics"""

        try:
            # Get index usage stats (MongoDB 3.2+)
            pipeline = [{"$indexStats": {}}]
            index_usage = list(collection.aggregate(pipeline))

            print("\nIndex usage statistics:")
            for stat in index_usage:
                name = stat.get('name', 'unknown')
                ops = stat.get('accesses', {}).get('ops', 0)
                since = stat.get('accesses', {}).get('since', 'unknown')
                print(f"  {name}: {ops} operations since {since}")

            return index_usage

        except Exception as e:
            print(f"Index usage monitoring: {e}")
            return []

    # Analyze index effectiveness
    def analyze_index_effectiveness():
        """Analyze how effective indexes are for common queries"""

        sample_queries = [
            {"category": "Electronics"},
            {"price": {"$gte": 100}},
            {"in_stock": True, "rating": {"$gte": 4.0}},
            {"$text": {"$search": "Product"}}
        ]

        print("\nQuery performance analysis:")

        for i, query in enumerate(sample_queries):
            try:
                # Use explain to analyze query performance
                explanation = collection.find(query).explain()

                execution_stats = explanation.get('executionStats', {})
                winning_plan = explanation.get('queryPlanner', {}).get('winningPlan', {})

                print(f"\nQuery {i+1}: {query}")
                print(f"  Execution time: {execution_stats.get('executionTimeMillis', 'unknown')} ms")
                print(f"  Documents examined: {execution_stats.get('totalDocsExamined', 'unknown')}")
                print(f"  Documents returned: {execution_stats.get('totalDocsReturned', 'unknown')}")
                print(f"  Index used: {winning_plan.get('inputStage', {}).get('indexName', 'collection scan')}")

            except Exception as e:
                print(f"  Query {i+1} analysis error: {e}")

    # Execute maintenance operations
    stats = get_index_stats()
    usage_stats = monitor_index_usage()
    analyze_index_effectiveness()

    return {
        "stats": stats,
        "usage": usage_stats
    }

# Execute maintenance examples
maintenance_results = index_maintenance()
```

## Index Performance Analysis

### Query Explanation and Optimization

```python
def query_performance_analysis():
    """Detailed query performance analysis using explain()"""

    print("\n=== Query Performance Analysis ===")

    # Different explain verbosity levels
    def analyze_query_with_explain(query, sort=None):
        """Analyze a query using different explain modes"""

        print(f"\nAnalyzing query: {query}")
        if sort:
            print(f"Sort: {sort}")

        cursor = collection.find(query)
        if sort:
            cursor = cursor.sort(sort)

        # Query planner information
        plan = cursor.explain()

        query_planner = plan.get('queryPlanner', {})
        winning_plan = query_planner.get('winningPlan', {})

        print("Query Planner Analysis:")
        print(f"  Namespace: {query_planner.get('namespace', 'unknown')}")
        print(f"  Index filter set: {query_planner.get('indexFilterSet', False)}")
        print(f"  Winning plan stage: {winning_plan.get('stage', 'unknown')}")

        if 'inputStage' in winning_plan:
            input_stage = winning_plan['inputStage']
            print(f"  Input stage: {input_stage.get('stage', 'unknown')}")
            if 'indexName' in input_stage:
                print(f"  Index used: {input_stage['indexName']}")

        # Execution statistics (more detailed)
        exec_stats = cursor.explain('executionStats')
        execution = exec_stats.get('executionStats', {})

        print("Execution Statistics:")
        print(f"  Execution success: {execution.get('executionSuccess', False)}")
        print(f"  Execution time: {execution.get('executionTimeMillis', 0)} ms")
        print(f"  Total docs examined: {execution.get('totalDocsExamined', 0)}")
        print(f"  Total docs returned: {execution.get('totalDocsReturned', 0)}")
        print(f"  Total keys examined: {execution.get('totalKeysExamined', 0)}")

        # Calculate efficiency ratio
        docs_examined = execution.get('totalDocsExamined', 0)
        docs_returned = execution.get('totalDocsReturned', 0)

        if docs_examined > 0:
            efficiency = docs_returned / docs_examined
            print(f"  Efficiency ratio: {efficiency:.3f} (higher is better)")

            if efficiency < 0.1:
                print("  ⚠ Low efficiency - consider adding indexes")
            elif efficiency < 0.5:
                print("  📈 Moderate efficiency - optimization possible")
            else:
                print("  ✅ Good efficiency")

        return plan

    # Analyze various query patterns

    # 1. Equality query
    analyze_query_with_explain({"category": "Electronics"})

    # 2. Range query
    analyze_query_with_explain({"price": {"$gte": 100, "$lte": 200}})

    # 3. Compound query
    analyze_query_with_explain({
        "category": "Electronics",
        "brand": "BrandA",
        "in_stock": True
    })

    # 4. Sort query
    analyze_query_with_explain(
        {"category": "Books"},
        [("price", DESCENDING)]
    )

    # 5. Text search
    analyze_query_with_explain({"$text": {"$search": "Product detailed"}})

# Execute performance analysis
query_performance_analysis()
```

### Index Selectivity Analysis

```python
def index_selectivity_analysis():
    """Analyze index selectivity to optimize compound indexes"""

    print("\n=== Index Selectivity Analysis ===")

    def calculate_field_selectivity(field_name):
        """Calculate selectivity of a field"""

        # Get total document count
        total_docs = collection.count_documents({})

        # Get distinct value count
        distinct_values = len(collection.distinct(field_name))

        # Calculate selectivity (higher is more selective)
        selectivity = distinct_values / total_docs if total_docs > 0 else 0

        return {
            "field": field_name,
            "total_docs": total_docs,
            "distinct_values": distinct_values,
            "selectivity": selectivity,
            "selectivity_percentage": selectivity * 100
        }

    # Analyze selectivity of various fields
    fields_to_analyze = ["category", "brand", "in_stock", "sku", "price"]

    selectivity_results = []

    print("Field selectivity analysis:")
    print("(Higher selectivity = more unique values = better for leading index position)")
    print()

    for field in fields_to_analyze:
        try:
            result = calculate_field_selectivity(field)
            selectivity_results.append(result)

            print(f"{field}:")
            print(f"  Total documents: {result['total_docs']:,}")
            print(f"  Distinct values: {result['distinct_values']:,}")
            print(f"  Selectivity: {result['selectivity']:.3f} ({result['selectivity_percentage']:.1f}%)")

            # Provide recommendations
            if result['selectivity'] > 0.8:
                print("  ✅ High selectivity - excellent for indexes")
            elif result['selectivity'] > 0.3:
                print("  📈 Good selectivity - suitable for indexes")
            elif result['selectivity'] > 0.1:
                print("  ⚠ Moderate selectivity - consider compound indexes")
            else:
                print("  ❌ Low selectivity - not ideal for leading index position")

            print()

        except Exception as e:
            print(f"Error analyzing {field}: {e}")

    # Sort by selectivity to recommend compound index order
    selectivity_results.sort(key=lambda x: x['selectivity'], reverse=True)

    print("Recommended compound index order (highest selectivity first):")
    for i, result in enumerate(selectivity_results):
        print(f"  {i+1}. {result['field']} (selectivity: {result['selectivity']:.3f})")

    return selectivity_results

# Execute selectivity analysis
selectivity_results = index_selectivity_analysis()
```

## Advanced Indexing Strategies

### ESR Rule Implementation

```python
def esr_rule_examples():
    """Examples of implementing the ESR (Equality, Sort, Range) rule"""

    print("\n=== ESR Rule Implementation ===")

    print("ESR Rule: Design compound indexes in the order:")
    print("1. Equality conditions")
    print("2. Sort conditions")
    print("3. Range conditions")
    print()

    # Example query pattern analysis
    def analyze_query_pattern(query_description, match_stage, sort_stage=None):
        """Analyze a query pattern and recommend index design"""

        print(f"Query Pattern: {query_description}")
        print(f"Match stage: {match_stage}")
        if sort_stage:
            print(f"Sort stage: {sort_stage}")

        # Identify equality, sort, and range conditions
        equality_fields = []
        range_fields = []

        for field, condition in match_stage.items():
            if isinstance(condition, dict):
                # Range operators
                if any(op in condition for op in ['$gte', '$gt', '$lte', '$lt', '$in']):
                    range_fields.append(field)
                else:
                    equality_fields.append(field)
            else:
                # Direct equality
                equality_fields.append(field)

        sort_fields = []
        if sort_stage:
            for field, direction in sort_stage:
                sort_fields.append((field, direction))

        # Recommend index design
        recommended_index = []

        # Add equality fields first
        for field in equality_fields:
            recommended_index.append((field, ASCENDING))

        # Add sort fields second
        for field, direction in sort_fields:
            if field not in equality_fields:  # Avoid duplicates
                recommended_index.append((field, direction))

        # Add range fields last
        for field in range_fields:
            if field not in equality_fields and field not in [f[0] for f in sort_fields]:
                recommended_index.append((field, ASCENDING))

        print(f"Recommended index: {recommended_index}")
        print()

        return recommended_index

    # Common query patterns

    # Pattern 1: E-commerce product search
    recommend1 = analyze_query_pattern(
        "E-commerce: Find products in category, sort by price",
        {"category": "Electronics", "in_stock": True},
        [("price", DESCENDING)]
    )

    # Pattern 2: Time-based queries
    recommend2 = analyze_query_pattern(
        "Time-based: Recent products in category with rating range",
        {
            "category": "Books",
            "rating": {"$gte": 4.0}
        },
        [("created_at", DESCENDING)]
    )

    # Pattern 3: Complex filtering
    recommend3 = analyze_query_pattern(
        "Complex: Brand and stock status with price range",
        {
            "brand": "BrandA",
            "in_stock": True,
            "price": {"$gte": 50, "$lte": 200}
        }
    )

    # Create the recommended indexes
    print("Creating recommended indexes...")

    try:
        collection.create_index(recommend1, name="esr_category_stock_price")
        print("✅ Created E-commerce index")
    except Exception as e:
        print(f"E-commerce index: {e}")

    try:
        collection.create_index(recommend2, name="esr_category_created_rating")
        print("✅ Created time-based index")
    except Exception as e:
        print(f"Time-based index: {e}")

    try:
        collection.create_index(recommend3, name="esr_brand_stock_price")
        print("✅ Created complex filtering index")
    except Exception as e:
        print(f"Complex filtering index: {e}")

    return {
        "ecommerce": recommend1,
        "time_based": recommend2,
        "complex": recommend3
    }

# Execute ESR examples
esr_results = esr_rule_examples()
```

### Index Intersection Strategies

```python
def index_intersection_strategies():
    """Strategies for using multiple indexes in a single query"""

    print("\n=== Index Intersection Strategies ===")

    # Create multiple single-field indexes
    single_indexes = ["category", "brand", "in_stock", "rating"]

    for field in single_indexes:
        try:
            collection.create_index(field, name=f"single_{field}")
            print(f"✅ Created single index on '{field}'")
        except Exception as e:
            print(f"Single index {field}: {e}")

    # Query that can use index intersection
    intersection_query = {
        "category": "Electronics",
        "brand": "BrandA",
        "in_stock": True,
        "rating": {"$gte": 4.0}
    }

    print("\nQuery using potential index intersection:")
    print(f"Query: {intersection_query}")

    # Analyze the query execution
    explanation = collection.find(intersection_query).explain('executionStats')

    execution_stats = explanation.get('executionStats', {})
    winning_plan = explanation.get('queryPlanner', {}).get('winningPlan', {})

    print("Execution analysis:")
    print(f"  Winning plan stage: {winning_plan.get('stage', 'unknown')}")
    print(f"  Execution time: {execution_stats.get('executionTimeMillis', 0)} ms")
    print(f"  Documents examined: {execution_stats.get('totalDocsExamined', 0)}")
    print(f"  Documents returned: {execution_stats.get('totalDocsReturned', 0)}")

    # Check if index intersection was used
    if winning_plan.get('stage') == 'AND_SORTED' or winning_plan.get('stage') == 'AND_HASH':
        print("  ✅ Index intersection was used!")
        input_stages = winning_plan.get('inputStages', [])
        print(f"  Number of indexes intersected: {len(input_stages)}")
        for i, stage in enumerate(input_stages):
            index_name = stage.get('indexName', 'unknown')
            print(f"    Index {i+1}: {index_name}")
    else:
        print("  📝 Single index or collection scan was used")

    # Compare with compound index approach
    print("\nComparing with compound index approach...")

    # Create a compound index for the same query
    try:
        compound_index = [
            ("category", ASCENDING),
            ("brand", ASCENDING),
            ("in_stock", ASCENDING),
            ("rating", ASCENDING)
        ]
        collection.create_index(compound_index, name="compound_all_fields")
        print("✅ Created compound index for comparison")

        # Test the same query with compound index
        compound_explanation = collection.find(intersection_query).explain('executionStats')
        compound_stats = compound_explanation.get('executionStats', {})

        print("Compound index performance:")
        print(f"  Execution time: {compound_stats.get('executionTimeMillis', 0)} ms")
        print(f"  Documents examined: {compound_stats.get('totalDocsExamined', 0)}")

        # Compare performance
        intersection_time = execution_stats.get('executionTimeMillis', 0)
        compound_time = compound_stats.get('executionTimeMillis', 0)

        if compound_time > 0 and intersection_time > 0:
            if compound_time < intersection_time:
                improvement = intersection_time / compound_time
                print(f"  ✅ Compound index is {improvement:.1f}x faster")
            else:
                degradation = compound_time / intersection_time
                print(f"  📈 Index intersection is {degradation:.1f}x faster")

    except Exception as e:
        print(f"Compound index comparison: {e}")

    # Best practices for index intersection
    print("\nIndex Intersection Best Practices:")
    print("✅ Works well when query selectivity is high")
    print("✅ Good for ad-hoc queries with varying filter combinations")
    print("✅ Reduces the need for many compound indexes")
    print("⚠ May be slower than a well-designed compound index")
    print("⚠ Limited to a maximum number of indexes (usually 2-3)")
    print("❌ Not suitable for queries requiring specific sort orders")

    return {
        "intersection_query": intersection_query,
        "intersection_stats": execution_stats,
        "winning_plan": winning_plan
    }

# Execute index intersection examples
intersection_results = index_intersection_strategies()
```

## Real-World Examples

### E-commerce Product Catalog Indexing

```python
def ecommerce_indexing_strategy():
    """Complete indexing strategy for an e-commerce product catalog"""

    print("\n=== E-commerce Indexing Strategy ===")

    # Drop existing indexes to start fresh
    collection.drop_indexes()
    print("🧹 Dropped all existing indexes")

    # Define common query patterns for e-commerce
    query_patterns = {
        "product_browse": {
            "description": "Browse products by category with sorting",
            "query": {"category": "Electronics", "in_stock": True},
            "sort": [("price", DESCENDING)],
            "frequency": "very_high"
        },
        "search_with_filters": {
            "description": "Search with brand and price filters",
            "query": {"brand": "BrandA", "price": {"$gte": 50, "$lte": 200}},
            "sort": [("rating", DESCENDING)],
            "frequency": "high"
        },
        "text_search": {
            "description": "Full-text search in product names and descriptions",
            "query": {"$text": {"$search": "wireless bluetooth"}},
            "sort": [("score", {"$meta": "textScore"})],
            "frequency": "high"
        },
        "inventory_management": {
            "description": "Find low-stock products",
            "query": {"quantity": {"$lte": 10}, "in_stock": True},
            "sort": [("quantity", ASCENDING)],
            "frequency": "medium"
        },
        "recent_products": {
            "description": "Recently added products",
            "query": {},
            "sort": [("created_at", DESCENDING)],
            "frequency": "medium"
        },
        "sku_lookup": {
            "description": "Direct product lookup by SKU",
            "query": {"sku": "SKU-001234"},
            "sort": None,
            "frequency": "very_high"
        }
    }

    # Design indexes based on query patterns
    indexes_to_create = []

    # 1. Unique index for SKU (critical for data integrity)
    indexes_to_create.append({
        "index": "sku",
        "options": {"unique": True, "name": "sku_unique"},
        "purpose": "Unique product identification"
    })

    # 2. Product browsing (ESR: category=equality, in_stock=equality, price=sort)
    indexes_to_create.append({
        "index": [("category", ASCENDING), ("in_stock", ASCENDING), ("price", DESCENDING)],
        "options": {"name": "browse_products"},
        "purpose": "Category browsing with price sorting"
    })

    # 3. Search with filters (ESR: brand=equality, rating=sort, price=range)
    indexes_to_create.append({
        "index": [("brand", ASCENDING), ("rating", DESCENDING), ("price", ASCENDING)],
        "options": {"name": "brand_search"},
        "purpose": "Brand filtering with rating sort"
    })

    # 4. Text search index
    indexes_to_create.append({
        "index": [("name", TEXT), ("description", TEXT)],
        "options": {"name": "text_search"},
        "purpose": "Full-text search"
    })

    # 5. Inventory management (partial index for efficiency)
    indexes_to_create.append({
        "index": [("in_stock", ASCENDING), ("quantity", ASCENDING)],
        "options": {
            "name": "inventory_management",
            "partialFilterExpression": {"quantity": {"$lte": 50}}
        },
        "purpose": "Low stock inventory tracking"
    })

    # 6. Recent products
    indexes_to_create.append({
        "index": [("created_at", DESCENDING)],
        "options": {"name": "recent_products"},
        "purpose": "Recently added products"
    })

    # 7. Compound index for complex queries
    indexes_to_create.append({
        "index": [("category", ASCENDING), ("brand", ASCENDING), ("in_stock", ASCENDING), ("rating", DESCENDING)],
        "options": {"name": "complex_search"},
        "purpose": "Complex multi-field searches"
    })

    # Create all indexes
    print("Creating optimized indexes...")

    for idx_config in indexes_to_create:
        try:
            collection.create_index(idx_config["index"], **idx_config["options"])
            print(f"✅ {idx_config['options']['name']}: {idx_config['purpose']}")
        except Exception as e:
            print(f"❌ {idx_config['options']['name']}: {e}")

    # Test the indexing strategy
    print("\nTesting indexing strategy performance...")

    def test_query_performance(pattern_name, pattern_config):
        """Test performance of a specific query pattern"""

        query = pattern_config["query"]
        sort = pattern_config["sort"]

        cursor = collection.find(query)
        if sort:
            cursor = cursor.sort(sort)

        # Get execution stats
        explanation = cursor.explain('executionStats')
        execution_stats = explanation.get('executionStats', {})

        time_ms = execution_stats.get('executionTimeMillis', 0)
        docs_examined = execution_stats.get('totalDocsExamined', 0)
        docs_returned = execution_stats.get('totalDocsReturned', 0)

        efficiency = docs_returned / docs_examined if docs_examined > 0 else 0

        print(f"\n{pattern_name}: {pattern_config['description']}")
        print(f"  Execution time: {time_ms} ms")
        print(f"  Efficiency: {efficiency:.3f}")

        if efficiency > 0.8:
            print("  ✅ Excellent performance")
        elif efficiency > 0.3:
            print("  📈 Good performance")
        else:
            print("  ⚠ Consider optimization")

        return {
            "time_ms": time_ms,
            "efficiency": efficiency,
            "docs_examined": docs_examined,
            "docs_returned": docs_returned
        }

    # Test all query patterns
    performance_results = {}
    for pattern_name, pattern_config in query_patterns.items():
        try:
            performance_results[pattern_name] = test_query_performance(pattern_name, pattern_config)
        except Exception as e:
            print(f"Error testing {pattern_name}: {e}")

    # Index maintenance recommendations
    print("\n=== Index Maintenance Recommendations ===")
    print("✅ Monitor index usage with $indexStats aggregation")
    print("✅ Regular performance testing with explain()")
    print("✅ Consider dropping unused indexes")
    print("✅ Monitor index size vs collection size ratio")
    print("⚠ Be cautious with too many indexes (impacts write performance)")
    print("📊 Aim for <10-15 indexes on frequently written collections")

    return {
        "indexes_created": indexes_to_create,
        "performance_results": performance_results
    }

# Execute e-commerce indexing strategy
ecommerce_results = ecommerce_indexing_strategy()
```

## Best Practices

### Comprehensive Indexing Best Practices

```python
def indexing_best_practices():
    """Comprehensive indexing best practices and guidelines"""

    print("\n=== Indexing Best Practices ===")

    # 1. Index Design Principles
    print("1. INDEX DESIGN PRINCIPLES")
    print("=" * 40)
    print("✅ Follow the ESR rule: Equality, Sort, Range")
    print("✅ Create indexes based on query patterns, not data structure")
    print("✅ Use compound indexes for multi-field queries")
    print("✅ Put most selective fields first in compound indexes")
    print("✅ Consider query frequency when designing indexes")
    print()

    # 2. Performance Guidelines
    print("2. PERFORMANCE GUIDELINES")
    print("=" * 40)
    print("✅ Index fields used in WHERE clauses")
    print("✅ Index fields used for sorting")
    print("✅ Use partial indexes for large collections with selective queries")
    print("✅ Use sparse indexes for fields that are often missing")
    print("✅ Monitor index usage with $indexStats")
    print("⚠ Limit the number of indexes (each index slows writes)")
    print("⚠ Avoid redundant indexes")
    print("❌ Don't index everything (it hurts write performance)")
    print()

    # 3. Index Maintenance
    print("3. INDEX MAINTENANCE")
    print("=" * 40)
    print("✅ Regularly analyze query performance")
    print("✅ Drop unused indexes")
    print("✅ Monitor index size")
    print("✅ Use background index builds for large collections")
    print("✅ Plan index builds during low-traffic periods")
    print()

    # 4. Common Anti-patterns
    print("4. COMMON ANTI-PATTERNS TO AVOID")
    print("=" * 40)
    print("❌ Creating indexes without analyzing query patterns")
    print("❌ Too many single-field indexes instead of compound indexes")
    print("❌ Wrong field order in compound indexes")
    print("❌ Indexing low-selectivity fields first")
    print("❌ Creating redundant indexes")
    print("❌ Ignoring index maintenance")
    print()

    # 5. Practical recommendations
    def practical_recommendations():
        """Practical recommendations for different scenarios"""

        recommendations = {
            "small_collections": {
                "description": "Collections < 1000 documents",
                "tips": [
                    "Minimal indexing needed",
                    "Focus on unique constraints",
                    "Collection scans are often acceptable"
                ]
            },
            "medium_collections": {
                "description": "Collections 1K-1M documents",
                "tips": [
                    "Index most common query patterns",
                    "Use compound indexes strategically",
                    "Monitor query performance regularly"
                ]
            },
            "large_collections": {
                "description": "Collections > 1M documents",
                "tips": [
                    "Carefully design all indexes",
                    "Use partial and sparse indexes",
                    "Consider sharding implications",
                    "Monitor index memory usage"
                ]
            },
            "write_heavy": {
                "description": "High write volume applications",
                "tips": [
                    "Minimize number of indexes",
                    "Use partial indexes when possible",
                    "Consider write performance vs query performance tradeoffs"
                ]
            },
            "read_heavy": {
                "description": "High read volume applications",
                "tips": [
                    "Optimize for all common query patterns",
                    "Use more indexes for better read performance",
                    "Consider read replicas for scaling"
                ]
            }
        }

        print("5. SCENARIO-SPECIFIC RECOMMENDATIONS")
        print("=" * 40)

        for scenario, config in recommendations.items():
            print(f"\n{scenario.upper()}: {config['description']}")
            for tip in config['tips']:
                print(f"  • {tip}")

        return recommendations

    # 6. Index monitoring script
    def create_index_monitoring_script():
        """Create a monitoring script template"""

        monitoring_script = """
def monitor_indexes(collection):
    \"\"\"Monitor index performance and usage\"\"\"

    # Get index usage statistics
    index_usage = list(collection.aggregate([{"$indexStats": {}}]))

    print("Index Usage Report:")
    print("=" * 50)

    for stat in index_usage:
        name = stat.get('name', 'unknown')
        ops = stat.get('accesses', {}).get('ops', 0)
        since = stat.get('accesses', {}).get('since', 'unknown')

        print(f"Index: {name}")
        print(f"  Operations: {ops}")
        print(f"  Since: {since}")

        if ops == 0:
            print("  ⚠ WARNING: Unused index - consider dropping")
        elif ops < 100:
            print("  📝 Low usage - review necessity")
        else:
            print("  ✅ Active index")
        print()

    # Get collection statistics
    stats = collection.database.command("collStats", collection.name)

    total_index_size = stats.get('totalIndexSize', 0)
    data_size = stats.get('size', 0)

    if data_size > 0:
        index_ratio = total_index_size / data_size
        print(f"Index to Data Ratio: {index_ratio:.2f}")

        if index_ratio > 1.0:
            print("  ⚠ High index overhead - review index strategy")
        elif index_ratio > 0.5:
            print("  📈 Moderate index overhead")
        else:
            print("  ✅ Reasonable index overhead")

# Usage: monitor_indexes(your_collection)
"""

        print("\n6. INDEX MONITORING SCRIPT TEMPLATE")
        print("=" * 40)
        print(monitoring_script)

        return monitoring_script

    # Execute best practices
    recommendations = practical_recommendations()
    monitoring_script = create_index_monitoring_script()

    # Final summary
    print("\n" + "=" * 60)
    print("INDEXING STRATEGY CHECKLIST")
    print("=" * 60)
    print("□ Analyzed query patterns")
    print("□ Designed indexes following ESR rule")
    print("□ Considered index selectivity")
    print("□ Planned for both read and write performance")
    print("□ Set up index monitoring")
    print("□ Scheduled regular index maintenance")
    print("=" * 60)

    return {
        "recommendations": recommendations,
        "monitoring_script": monitoring_script
    }

# Execute best practices
best_practices_results = indexing_best_practices()
```

## Summary and Next Steps

This comprehensive guide covered:

1. **Index Fundamentals** - Understanding how indexes work
2. **Index Types** - Single field, compound, text, geospatial, partial, sparse
3. **Index Management** - Creation, maintenance, and monitoring
4. **Performance Analysis** - Using explain() and optimization techniques
5. **Advanced Strategies** - ESR rule, index intersection, selectivity analysis
6. **Real-World Examples** - E-commerce indexing strategy
7. **Best Practices** - Comprehensive guidelines and recommendations

### Next Steps

1. **Transactions**: [MongoDB Transactions with PyMongo](./03_transactions.md)
2. **Performance Optimization**: [Advanced Performance Tuning](./07_performance_optimization.md)
3. **Aggregation Framework**: [Advanced Aggregation](./01_aggregation_framework.md)
4. **Monitoring**: [Database Monitoring](./10_monitoring_logging.md)

### Additional Resources

- [MongoDB Index Documentation](https://docs.mongodb.com/manual/indexes/)
- [PyMongo Index Examples](https://pymongo.readthedocs.io/en/stable/tutorial.html#indexing)
- [Index Performance Best Practices](https://docs.mongodb.com/manual/applications/indexes/)
- [MongoDB University Indexing Course](https://university.mongodb.com/)
