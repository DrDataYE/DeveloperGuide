# PyMongo Query Operators

This comprehensive guide covers all MongoDB query operators available in PyMongo, with practical examples and use cases.

## Table of Contents

1. [Query Operator Overview](#query-operator-overview)
2. [Comparison Operators](#comparison-operators)
3. [Logical Operators](#logical-operators)
4. [Element Operators](#element-operators)
5. [Evaluation Operators](#evaluation-operators)
6. [Array Operators](#array-operators)
7. [Comments and Meta Operators](#comments-and-meta-operators)
8. [Geospatial Operators](#geospatial-operators)
9. [Bitwise Operators](#bitwise-operators)
10. [Complex Query Examples](#complex-query-examples)
11. [Performance Considerations](#performance-considerations)
12. [Best Practices](#best-practices)

## Query Operator Overview

PyMongo supports all MongoDB query operators through dictionary syntax. Understanding these operators is crucial for building effective queries.

### Basic Query Structure

```python
from pymongo import MongoClient
from bson import ObjectId, Regex
from datetime import datetime, timedelta
import re

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.ecommerce
products = db.products
users = db.users
orders = db.orders

# Basic query structure
query = {
    "field": {"$operator": "value"},
    "another_field": {"$operator": "value"}
}

results = collection.find(query)
```

### Sample Data Setup

```python
def setup_sample_data():
    """Setup sample data for testing queries"""

    # Clear existing data
    products.delete_many({})
    users.delete_many({})
    orders.delete_many({})

    # Insert sample products
    sample_products = [
        {
            "_id": ObjectId(),
            "name": "Laptop Pro",
            "price": 1299.99,
            "category": "Electronics",
            "brand": "TechBrand",
            "stock": 15,
            "rating": 4.5,
            "tags": ["laptop", "computer", "portable"],
            "specs": {
                "cpu": "Intel i7",
                "ram": "16GB",
                "storage": "512GB SSD"
            },
            "created_at": datetime(2023, 1, 15),
            "active": True
        },
        {
            "_id": ObjectId(),
            "name": "Wireless Headphones",
            "price": 199.99,
            "category": "Electronics",
            "brand": "AudioTech",
            "stock": 0,
            "rating": 4.2,
            "tags": ["headphones", "wireless", "audio"],
            "specs": {
                "battery_life": "20 hours",
                "noise_cancellation": True
            },
            "created_at": datetime(2023, 2, 10),
            "active": True
        },
        {
            "_id": ObjectId(),
            "name": "Running Shoes",
            "price": 89.99,
            "category": "Sports",
            "brand": "RunFast",
            "stock": 25,
            "rating": 4.0,
            "tags": ["shoes", "running", "sports"],
            "specs": {
                "material": "mesh",
                "size_range": [6, 7, 8, 9, 10, 11, 12]
            },
            "created_at": datetime(2023, 3, 5),
            "active": False
        },
        {
            "_id": ObjectId(),
            "name": "Coffee Maker",
            "price": 79.99,
            "category": "Home",
            "brand": "BrewMaster",
            "stock": 12,
            "rating": 3.8,
            "tags": ["coffee", "kitchen", "appliance"],
            "specs": {
                "capacity": "12 cups",
                "programmable": True
            },
            "created_at": datetime(2023, 1, 20),
            "active": True
        }
    ]

    products.insert_many(sample_products)

    # Insert sample users
    sample_users = [
        {
            "_id": ObjectId(),
            "username": "john_doe",
            "email": "john@example.com",
            "age": 28,
            "city": "New York",
            "preferences": ["electronics", "books"],
            "member_since": datetime(2022, 6, 1),
            "premium": True,
            "total_orders": 15
        },
        {
            "_id": ObjectId(),
            "username": "jane_smith",
            "email": "jane@example.com",
            "age": 34,
            "city": "San Francisco",
            "preferences": ["sports", "home"],
            "member_since": datetime(2021, 3, 15),
            "premium": False,
            "total_orders": 8
        }
    ]

    users.insert_many(sample_users)
    print("✅ Sample data inserted successfully")

# Setup data
setup_sample_data()
```

## Comparison Operators

### $eq (Equal) and $ne (Not Equal)

```python
def comparison_eq_ne_examples():
    """Examples of $eq and $ne operators"""

    # $eq - Equal (implicit when not specified)
    electronics = list(products.find({"category": {"$eq": "Electronics"}}))
    # Same as:
    electronics_implicit = list(products.find({"category": "Electronics"}))

    # $ne - Not equal
    non_electronics = list(products.find({"category": {"$ne": "Electronics"}}))

    # Multiple conditions
    active_non_electronics = list(products.find({
        "category": {"$ne": "Electronics"},
        "active": {"$eq": True}
    }))

    print(f"Electronics products: {len(electronics)}")
    print(f"Non-electronics products: {len(non_electronics)}")

    return electronics, non_electronics

# Usage
electronics, non_electronics = comparison_eq_ne_examples()
```

### $gt, $gte, $lt, $lte (Greater/Less Than)

```python
def comparison_range_examples():
    """Examples of range comparison operators"""

    # $gt - Greater than
    expensive_products = list(products.find({"price": {"$gt": 100}}))

    # $gte - Greater than or equal
    min_price_products = list(products.find({"price": {"$gte": 100}}))

    # $lt - Less than
    cheap_products = list(products.find({"price": {"$lt": 100}}))

    # $lte - Less than or equal
    max_price_products = list(products.find({"price": {"$lte": 100}}))

    # Range queries (combining operators)
    mid_range_products = list(products.find({
        "price": {"$gte": 80, "$lte": 200}
    }))

    # Date range queries
    recent_products = list(products.find({
        "created_at": {"$gte": datetime(2023, 2, 1)}
    }))

    # Numeric field ranges
    well_rated_products = list(products.find({
        "rating": {"$gte": 4.0},
        "stock": {"$gt": 0}
    }))

    print(f"Expensive products (>$100): {len(expensive_products)}")
    print(f"Mid-range products ($80-$200): {len(mid_range_products)}")
    print(f"Recent products: {len(recent_products)}")

    return mid_range_products

# Usage
mid_range = comparison_range_examples()
```

### $in and $nin (In/Not In Array)

```python
def comparison_in_nin_examples():
    """Examples of $in and $nin operators"""

    # $in - Match any value in array
    electronics_home = list(products.find({
        "category": {"$in": ["Electronics", "Home"]}
    }))

    # $nin - Does not match any value in array
    not_sports_electronics = list(products.find({
        "category": {"$nin": ["Sports", "Electronics"]}
    }))

    # $in with numbers
    specific_prices = list(products.find({
        "price": {"$in": [79.99, 199.99, 1299.99]}
    }))

    # $in with ObjectIds
    specific_ids = [
        ObjectId("507f1f77bcf86cd799439011"),
        ObjectId("507f1f77bcf86cd799439012")
    ]
    specific_products = list(products.find({
        "_id": {"$in": specific_ids}
    }))

    # $in with nested fields
    preferred_brands = list(products.find({
        "brand": {"$in": ["TechBrand", "AudioTech"]}
    }))

    # Complex $in queries
    user_preferences = ["electronics", "sports"]
    matching_users = list(users.find({
        "preferences": {"$in": user_preferences}
    }))

    print(f"Electronics/Home products: {len(electronics_home)}")
    print(f"Non-sports/electronics: {len(not_sports_electronics)}")
    print(f"Preferred brands: {len(preferred_brands)}")

    return electronics_home

# Usage
filtered_products = comparison_in_nin_examples()
```

## Logical Operators

### $and, $or, $not, $nor

```python
def logical_operators_examples():
    """Examples of logical operators"""

    # $and - All conditions must be true
    expensive_electronics = list(products.find({
        "$and": [
            {"category": "Electronics"},
            {"price": {"$gt": 150}},
            {"active": True}
        ]
    }))

    # Implicit $and (more common)
    expensive_electronics_implicit = list(products.find({
        "category": "Electronics",
        "price": {"$gt": 150},
        "active": True
    }))

    # $or - At least one condition must be true
    popular_or_cheap = list(products.find({
        "$or": [
            {"rating": {"$gte": 4.5}},
            {"price": {"$lt": 100}}
        ]
    }))

    # $nor - None of the conditions should be true
    not_expensive_not_electronics = list(products.find({
        "$nor": [
            {"price": {"$gt": 200}},
            {"category": "Electronics"}
        ]
    }))

    # $not - Negates the condition
    not_electronics = list(products.find({
        "category": {"$not": {"$eq": "Electronics"}}
    }))

    # Complex logical combinations
    complex_query = list(products.find({
        "$and": [
            {
                "$or": [
                    {"category": "Electronics"},
                    {"category": "Sports"}
                ]
            },
            {"price": {"$lt": 500}},
            {"active": True}
        ]
    }))

    # Nested logical operators
    premium_conditions = list(products.find({
        "$or": [
            {
                "$and": [
                    {"category": "Electronics"},
                    {"price": {"$gt": 1000}}
                ]
            },
            {
                "$and": [
                    {"rating": {"$gte": 4.5}},
                    {"brand": "TechBrand"}
                ]
            }
        ]
    }))

    print(f"Expensive electronics: {len(expensive_electronics)}")
    print(f"Popular or cheap: {len(popular_or_cheap)}")
    print(f"Complex query results: {len(complex_query)}")

    return complex_query

# Usage
results = logical_operators_examples()
```

## Element Operators

### $exists and $type

```python
def element_operators_examples():
    """Examples of element operators"""

    # $exists - Check if field exists
    products_with_specs = list(products.find({"specs": {"$exists": True}}))
    products_without_rating = list(products.find({"rating": {"$exists": False}}))

    # $exists with nested fields
    products_with_cpu = list(products.find({"specs.cpu": {"$exists": True}}))

    # $type - Check field type
    string_prices = list(products.find({"price": {"$type": "string"}}))
    number_prices = list(products.find({"price": {"$type": "number"}}))

    # $type with type codes
    object_ids = list(products.find({"_id": {"$type": 7}}))  # 7 = ObjectId

    # $type with multiple types
    numeric_or_null = list(products.find({
        "price": {"$type": ["number", "null"]}
    }))

    # Practical use cases
    def find_incomplete_products():
        """Find products missing critical information"""
        incomplete = list(products.find({
            "$or": [
                {"price": {"$exists": False}},
                {"category": {"$exists": False}},
                {"name": {"$exists": False}}
            ]
        }))
        return incomplete

    def find_data_type_inconsistencies():
        """Find documents with unexpected data types"""
        price_issues = list(products.find({
            "price": {"$not": {"$type": "number"}}
        }))

        rating_issues = list(products.find({
            "rating": {"$type": "string"}  # Should be number
        }))

        return price_issues, rating_issues

    incomplete_products = find_incomplete_products()
    price_issues, rating_issues = find_data_type_inconsistencies()

    print(f"Products with specs: {len(products_with_specs)}")
    print(f"Products without rating: {len(products_without_rating)}")
    print(f"Incomplete products: {len(incomplete_products)}")

    return products_with_specs

# Usage
products_with_specs = element_operators_examples()
```

## Evaluation Operators

### $regex, $text, $where, $expr

```python
def evaluation_operators_examples():
    """Examples of evaluation operators"""

    # $regex - Regular expression matching
    tech_products = list(products.find({
        "name": {"$regex": r"^(Laptop|Wireless)", "$options": "i"}
    }))

    # Using Python re.compile
    pattern = re.compile(r".*tech.*", re.IGNORECASE)
    regex_products = list(products.find({"brand": {"$regex": pattern}}))

    # Email validation with regex
    valid_emails = list(users.find({
        "email": {"$regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
    }))

    # $text - Text search (requires text index)
    def setup_text_search():
        """Setup text index for search"""
        try:
            products.create_index([("name", "text"), ("tags", "text")])

            # Text search examples
            search_results = list(products.find({
                "$text": {"$search": "laptop computer"}
            }))

            # Text search with score
            scored_results = list(products.find(
                {"$text": {"$search": "wireless audio"}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]))

            # Exact phrase search
            phrase_results = list(products.find({
                "$text": {"$search": "\"running shoes\""}
            }))

            return search_results, scored_results

        except Exception as e:
            print(f"Text search setup error: {e}")
            return [], []

    # $where - JavaScript expression (use sparingly)
    def where_examples():
        """Examples of $where operator (use with caution)"""

        # Find products where price equals stock * 10
        custom_condition = list(products.find({
            "$where": "this.price === this.stock * 10"
        }))

        # Complex JavaScript condition
        complex_where = list(products.find({
            "$where": "this.name.length > 10 && this.rating > 4.0"
        }))

        return custom_condition

    # $expr - Use aggregation expressions in queries
    def expr_examples():
        """Examples of $expr operator"""

        # Compare two fields
        price_vs_rating = list(products.find({
            "$expr": {"$gt": ["$price", {"$multiply": ["$rating", 100]}]}
        }))

        # Complex expressions
        complex_expr = list(products.find({
            "$expr": {
                "$and": [
                    {"$gt": ["$stock", 0]},
                    {"$gte": ["$rating", 4.0]},
                    {"$lt": ["$price", 200]}
                ]
            }
        }))

        # Date calculations
        recent_expr = list(products.find({
            "$expr": {
                "$gte": [
                    "$created_at",
                    {"$dateSubtract": {
                        "startDate": "$$NOW",
                        "unit": "month",
                        "amount": 6
                    }}
                ]
            }
        }))

        return price_vs_rating, complex_expr

    # Execute examples
    search_results, scored_results = setup_text_search()
    custom_condition = where_examples()
    price_vs_rating, complex_expr = expr_examples()

    print(f"Tech products (regex): {len(tech_products)}")
    print(f"Text search results: {len(search_results)}")
    print(f"Custom condition results: {len(custom_condition)}")
    print(f"Expression query results: {len(complex_expr)}")

    return tech_products

# Usage
eval_results = evaluation_operators_examples()
```

## Array Operators

### $all, $elemMatch, $size

```python
def array_operators_examples():
    """Examples of array operators"""

    # Setup array data
    def setup_array_data():
        """Setup collections with array data"""

        # Clear and setup blog posts with tags and comments
        blogs = db.blogs
        blogs.delete_many({})

        sample_blogs = [
            {
                "_id": ObjectId(),
                "title": "Python Tutorial",
                "tags": ["python", "programming", "tutorial"],
                "ratings": [4, 5, 3, 4, 5],
                "comments": [
                    {"author": "John", "rating": 5, "text": "Great tutorial!"},
                    {"author": "Jane", "rating": 4, "text": "Very helpful"},
                    {"author": "Bob", "rating": 3, "text": "Good but could be better"}
                ],
                "categories": ["Programming", "Education"]
            },
            {
                "_id": ObjectId(),
                "title": "MongoDB Guide",
                "tags": ["mongodb", "database", "nosql"],
                "ratings": [5, 4, 5, 4],
                "comments": [
                    {"author": "Alice", "rating": 5, "text": "Excellent guide!"},
                    {"author": "Charlie", "rating": 4, "text": "Clear explanations"}
                ],
                "categories": ["Database", "MongoDB"]
            },
            {
                "_id": ObjectId(),
                "title": "Web Development",
                "tags": ["web", "javascript", "html", "css"],
                "ratings": [3, 4, 4, 3, 5],
                "comments": [
                    {"author": "Dave", "rating": 4, "text": "Comprehensive"},
                    {"author": "Eve", "rating": 3, "text": "Okay introduction"}
                ],
                "categories": ["Web Development"]
            }
        ]

        blogs.insert_many(sample_blogs)
        return blogs

    blogs = setup_array_data()

    # $all - All elements must be present
    programming_education = list(blogs.find({
        "categories": {"$all": ["Programming", "Education"]}
    }))

    # $all with specific tags
    web_tech_posts = list(blogs.find({
        "tags": {"$all": ["web", "javascript"]}
    }))

    # $elemMatch - At least one array element matches all conditions
    high_rated_comments = list(blogs.find({
        "comments": {
            "$elemMatch": {
                "rating": {"$gte": 4},
                "author": {"$regex": "^J"}  # Author starts with 'J'
            }
        }
    }))

    # $elemMatch with multiple conditions
    detailed_high_comments = list(blogs.find({
        "comments": {
            "$elemMatch": {
                "rating": {"$gte": 4},
                "text": {"$regex": "excellent|great", "$options": "i"}
            }
        }
    }))

    # $size - Array has exact size
    posts_with_three_tags = list(blogs.find({
        "tags": {"$size": 3}
    }))

    posts_with_four_ratings = list(blogs.find({
        "ratings": {"$size": 4}
    }))

    # Array element matching (without $elemMatch)
    posts_with_python = list(blogs.find({"tags": "python"}))
    posts_with_high_rating = list(blogs.find({"ratings": {"$gte": 5}}))

    # Complex array queries
    def complex_array_queries():
        """Complex array query examples"""

        # Find posts with specific rating patterns
        consistent_high_ratings = list(blogs.find({
            "ratings": {"$not": {"$elemMatch": {"$lt": 4}}}
        }))

        # Find posts with comments from specific authors
        john_or_jane_comments = list(blogs.find({
            "comments.author": {"$in": ["John", "Jane"]}
        }))

        # Multiple array conditions
        quality_posts = list(blogs.find({
            "tags": {"$size": {"$gte": 3}},
            "ratings": {"$not": {"$size": 0}},
            "comments": {"$elemMatch": {"rating": {"$gte": 4}}}
        }))

        return consistent_high_ratings, john_or_jane_comments

    consistent_ratings, author_comments = complex_array_queries()

    print(f"Programming & Education posts: {len(programming_education)}")
    print(f"High-rated comments: {len(high_rated_comments)}")
    print(f"Posts with 3 tags: {len(posts_with_three_tags)}")
    print(f"Consistent high ratings: {len(consistent_ratings)}")

    return blogs

# Usage
blogs_collection = array_operators_examples()
```

### Advanced Array Operations

```python
def advanced_array_operations():
    """Advanced array query patterns"""

    # Setup complex product data with arrays
    advanced_products = db.advanced_products
    advanced_products.delete_many({})

    sample_data = [
        {
            "_id": ObjectId(),
            "name": "Gaming Laptop",
            "variants": [
                {"size": "15inch", "price": 1200, "stock": 5},
                {"size": "17inch", "price": 1400, "stock": 3}
            ],
            "reviews": [
                {"user": "gamer1", "score": 5, "verified": True},
                {"user": "gamer2", "score": 4, "verified": False},
                {"user": "pro_user", "score": 5, "verified": True}
            ],
            "features": ["RGB", "High Refresh", "Mechanical Keyboard"],
            "compatibility": ["Windows", "Linux"]
        },
        {
            "_id": ObjectId(),
            "name": "Ultrabook",
            "variants": [
                {"size": "13inch", "price": 900, "stock": 8},
                {"size": "14inch", "price": 1000, "stock": 12}
            ],
            "reviews": [
                {"user": "business1", "score": 4, "verified": True},
                {"user": "student1", "score": 5, "verified": True}
            ],
            "features": ["Lightweight", "Long Battery"],
            "compatibility": ["Windows", "macOS"]
        }
    ]

    advanced_products.insert_many(sample_data)

    # Find products with variants under $1000
    budget_variants = list(advanced_products.find({
        "variants": {
            "$elemMatch": {
                "price": {"$lt": 1000},
                "stock": {"$gt": 0}
            }
        }
    }))

    # Find products with high verified reviews
    verified_quality = list(advanced_products.find({
        "reviews": {
            "$elemMatch": {
                "score": {"$gte": 5},
                "verified": True
            }
        }
    }))

    # Find products with specific feature combinations
    gaming_features = list(advanced_products.find({
        "features": {"$all": ["RGB", "High Refresh"]}
    }))

    # Cross-platform compatibility
    cross_platform = list(advanced_products.find({
        "compatibility": {"$all": ["Windows", "Linux"]}
    }))

    # Complex nested array queries
    premium_available = list(advanced_products.find({
        "$and": [
            {"variants": {"$elemMatch": {"price": {"$gt": 1200}}}},
            {"reviews": {"$elemMatch": {"score": {"$gte": 4}}}},
            {"features": {"$size": {"$gte": 2}}}
        ]
    }))

    print(f"Budget variants available: {len(budget_variants)}")
    print(f"High verified reviews: {len(verified_quality)}")
    print(f"Gaming features: {len(gaming_features)}")

    return advanced_products

# Usage
advanced_collection = advanced_array_operations()
```

## Geospatial Operators

### $near, $geoWithin, $geoIntersects

```python
def geospatial_operators_examples():
    """Examples of geospatial operators"""

    # Setup location data
    locations = db.locations
    locations.delete_many({})

    # Create geospatial index
    locations.create_index([("location", "2dsphere")])

    # Sample location data
    sample_locations = [
        {
            "_id": ObjectId(),
            "name": "Central Park",
            "type": "park",
            "location": {
                "type": "Point",
                "coordinates": [-73.9654, 40.7829]  # [longitude, latitude]
            }
        },
        {
            "_id": ObjectId(),
            "name": "Times Square",
            "type": "landmark",
            "location": {
                "type": "Point",
                "coordinates": [-73.9851, 40.7580]
            }
        },
        {
            "_id": ObjectId(),
            "name": "Brooklyn Bridge",
            "type": "bridge",
            "location": {
                "type": "Point",
                "coordinates": [-73.9969, 40.7061]
            }
        },
        {
            "_id": ObjectId(),
            "name": "Manhattan",
            "type": "area",
            "location": {
                "type": "Polygon",
                "coordinates": [[
                    [-74.0479, 40.6829],
                    [-73.9067, 40.6829],
                    [-73.9067, 40.8820],
                    [-74.0479, 40.8820],
                    [-74.0479, 40.6829]
                ]]
            }
        }
    ]

    locations.insert_many(sample_locations)

    # $near - Find locations near a point
    near_times_square = list(locations.find({
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [-73.9851, 40.7580]  # Times Square
                },
                "$maxDistance": 2000  # 2000 meters
            }
        }
    }))

    # $geoWithin - Find points within a geometry
    within_circle = list(locations.find({
        "location": {
            "$geoWithin": {
                "$centerSphere": [
                    [-73.9654, 40.7829],  # Center point (Central Park)
                    1000 / 6378100  # Radius in radians (1000m)
                ]
            }
        }
    }))

    # $geoWithin with polygon
    within_polygon = list(locations.find({
        "location": {
            "$geoWithin": {
                "$geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-74.0, 40.7],
                        [-73.9, 40.7],
                        [-73.9, 40.8],
                        [-74.0, 40.8],
                        [-74.0, 40.7]
                    ]]
                }
            }
        }
    }))

    # $geoIntersects - Find geometries that intersect
    intersecting_areas = list(locations.find({
        "location": {
            "$geoIntersects": {
                "$geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-74.1, 40.6],
                        [-73.8, 40.6],
                        [-73.8, 40.9],
                        [-74.1, 40.9],
                        [-74.1, 40.6]
                    ]]
                }
            }
        }
    }))

    # Practical geospatial queries
    def find_nearby_restaurants():
        """Find restaurants near a location"""
        restaurants = db.restaurants
        restaurants.delete_many({})

        sample_restaurants = [
            {
                "name": "Pizza Palace",
                "cuisine": "Italian",
                "location": {
                    "type": "Point",
                    "coordinates": [-73.9851, 40.7580]
                },
                "rating": 4.2
            },
            {
                "name": "Burger Joint",
                "cuisine": "American",
                "location": {
                    "type": "Point",
                    "coordinates": [-73.9654, 40.7829]
                },
                "rating": 3.8
            }
        ]

        restaurants.insert_many(sample_restaurants)
        restaurants.create_index([("location", "2dsphere")])

        # Find restaurants within 500m of a user's location
        user_location = [-73.9800, 40.7700]  # User's coordinates

        nearby_restaurants = list(restaurants.find({
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": user_location
                    },
                    "$maxDistance": 500
                }
            },
            "rating": {"$gte": 4.0}
        }))

        return nearby_restaurants

    nearby_restaurants = find_nearby_restaurants()

    print(f"Near Times Square: {len(near_times_square)}")
    print(f"Within circle: {len(within_circle)}")
    print(f"Intersecting areas: {len(intersecting_areas)}")
    print(f"Nearby restaurants: {len(nearby_restaurants)}")

    return locations

# Usage
geo_collection = geospatial_operators_examples()
```

## Complex Query Examples

### Real-World Query Scenarios

```python
def complex_real_world_queries():
    """Complex queries for real-world scenarios"""

    # E-commerce product search
    def advanced_product_search(filters):
        """Advanced product search with multiple filters"""

        query = {}

        # Price range
        if filters.get('min_price') or filters.get('max_price'):
            price_filter = {}
            if filters.get('min_price'):
                price_filter['$gte'] = filters['min_price']
            if filters.get('max_price'):
                price_filter['$lte'] = filters['max_price']
            query['price'] = price_filter

        # Categories
        if filters.get('categories'):
            query['category'] = {'$in': filters['categories']}

        # Brands
        if filters.get('brands'):
            query['brand'] = {'$in': filters['brands']}

        # Rating
        if filters.get('min_rating'):
            query['rating'] = {'$gte': filters['min_rating']}

        # In stock only
        if filters.get('in_stock_only'):
            query['stock'] = {'$gt': 0}

        # Text search
        if filters.get('search_text'):
            query['$text'] = {'$search': filters['search_text']}

        # Tags
        if filters.get('tags'):
            query['tags'] = {'$all': filters['tags']}

        # Active products only
        query['active'] = True

        return list(products.find(query))

    # User activity analysis
    def analyze_user_behavior():
        """Analyze user behavior patterns"""

        # Active premium users
        active_premium = list(users.find({
            'premium': True,
            'total_orders': {'$gte': 5},
            'member_since': {'$lte': datetime.now() - timedelta(days=365)}
        }))

        # Users who need re-engagement
        inactive_users = list(users.find({
            '$or': [
                {'total_orders': {'$eq': 0}},
                {'member_since': {'$gte': datetime.now() - timedelta(days=30)}}
            ],
            'premium': False
        }))

        # Users by city preference analysis
        preference_by_city = list(users.aggregate([
            {'$group': {
                '_id': '$city',
                'user_count': {'$sum': 1},
                'avg_orders': {'$avg': '$total_orders'},
                'premium_percentage': {
                    '$avg': {'$cond': ['$premium', 1, 0]}
                }
            }}
        ]))

        return active_premium, inactive_users, preference_by_city

    # Inventory management queries
    def inventory_management_queries():
        """Queries for inventory management"""

        # Low stock alerts
        low_stock = list(products.find({
            'stock': {'$lte': 5, '$gt': 0},
            'active': True
        }))

        # Out of stock items
        out_of_stock = list(products.find({
            'stock': {'$eq': 0},
            'active': True
        }))

        # Overstock analysis
        overstock = list(products.find({
            'stock': {'$gte': 50},
            'created_at': {'$lte': datetime.now() - timedelta(days=180)}
        }))

        # Price optimization candidates
        price_optimization = list(products.find({
            '$expr': {
                '$and': [
                    {'$lt': ['$rating', 3.5]},
                    {'$gt': ['$stock', 10]},
                    {'$gt': ['$price', 100]}
                ]
            }
        }))

        return low_stock, out_of_stock, overstock, price_optimization

    # Performance analytics
    def performance_analytics():
        """Performance and trend analysis"""

        # Trending products (high rating, recent)
        trending = list(products.find({
            'rating': {'$gte': 4.0},
            'created_at': {'$gte': datetime.now() - timedelta(days=90)},
            'active': True
        }).sort([('rating', -1), ('created_at', -1)]))

        # Category performance
        category_performance = list(products.aggregate([
            {'$match': {'active': True}},
            {'$group': {
                '_id': '$category',
                'avg_rating': {'$avg': '$rating'},
                'avg_price': {'$avg': '$price'},
                'total_stock': {'$sum': '$stock'},
                'product_count': {'$sum': 1}
            }},
            {'$sort': {'avg_rating': -1}}
        ]))

        return trending, category_performance

    # Execute examples
    search_filters = {
        'min_price': 50,
        'max_price': 500,
        'categories': ['Electronics'],
        'min_rating': 4.0,
        'in_stock_only': True
    }

    search_results = advanced_product_search(search_filters)
    active_premium, inactive_users, city_analysis = analyze_user_behavior()
    low_stock, out_of_stock, overstock, price_opt = inventory_management_queries()
    trending, category_perf = performance_analytics()

    print("=== Query Results ===")
    print(f"Search results: {len(search_results)}")
    print(f"Active premium users: {len(active_premium)}")
    print(f"Inactive users: {len(inactive_users)}")
    print(f"Low stock items: {len(low_stock)}")
    print(f"Trending products: {len(trending)}")

    return {
        'search_results': search_results,
        'user_analysis': (active_premium, inactive_users),
        'inventory': (low_stock, out_of_stock, overstock),
        'performance': (trending, category_perf)
    }

# Usage
analysis_results = complex_real_world_queries()
```

## Performance Considerations

### Query Optimization

```python
def query_performance_optimization():
    """Examples of query performance optimization"""

    # Index creation for better performance
    def create_performance_indexes():
        """Create indexes for common query patterns"""

        # Single field indexes
        products.create_index("category")
        products.create_index("price")
        products.create_index("rating")
        products.create_index("active")

        # Compound indexes (order matters!)
        products.create_index([
            ("category", 1),
            ("active", 1),
            ("price", 1)
        ])

        products.create_index([
            ("active", 1),
            ("rating", -1),
            ("created_at", -1)
        ])

        # Text index for search
        products.create_index([
            ("name", "text"),
            ("tags", "text")
        ])

        # Sparse index for optional fields
        products.create_index("specs.cpu", sparse=True)

        print("✅ Performance indexes created")

    # Query analysis
    def analyze_query_performance():
        """Analyze query execution performance"""

        # Simple query explanation
        explain_simple = products.find({"category": "Electronics"}).explain()

        # Complex query explanation
        explain_complex = products.find({
            "category": "Electronics",
            "active": True,
            "price": {"$gte": 100, "$lte": 500}
        }).explain()

        # Print execution stats
        def print_execution_stats(explain_result, query_name):
            """Print readable execution statistics"""
            exec_stats = explain_result.get('executionStats', {})

            print(f"\n=== {query_name} Performance ===")
            print(f"Execution time: {exec_stats.get('executionTimeMillis', 0)}ms")
            print(f"Documents examined: {exec_stats.get('totalDocsExamined', 0)}")
            print(f"Documents returned: {exec_stats.get('totalDocsReturned', 0)}")
            print(f"Index used: {'Yes' if exec_stats.get('totalDocsExamined', 0) == exec_stats.get('totalDocsReturned', 0) else 'No'}")

        print_execution_stats(explain_simple, "Simple Query")
        print_execution_stats(explain_complex, "Complex Query")

        return explain_simple, explain_complex

    # Optimized query patterns
    def optimized_query_patterns():
        """Examples of optimized query patterns"""

        # Use projection to reduce data transfer
        optimized_search = list(products.find(
            {"category": "Electronics", "active": True},
            {"name": 1, "price": 1, "rating": 1, "_id": 0}
        ))

        # Use hint to force index usage
        forced_index = list(products.find({
            "category": "Electronics",
            "price": {"$gte": 100}
        }).hint([("category", 1), ("active", 1), ("price", 1)]))

        # Limit results for pagination
        paginated_results = list(products.find({"active": True})
                                .sort("created_at", -1)
                                .skip(0)
                                .limit(20))

        # Use allowDiskUse for large sorts (if needed)
        # large_sort = list(products.find().sort("name", 1).allow_disk_use(True))

        return optimized_search, forced_index, paginated_results

    # Query performance monitoring
    def monitor_slow_queries():
        """Monitor and log slow queries"""

        import time
        from functools import wraps

        def time_query(func):
            """Decorator to time query execution"""
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()

                execution_time = (end_time - start_time) * 1000  # Convert to ms
                if execution_time > 100:  # Log queries taking > 100ms
                    print(f"⚠ Slow query detected: {func.__name__} took {execution_time:.2f}ms")

                return result
            return wrapper

        @time_query
        def monitored_complex_query():
            return list(products.find({
                "$and": [
                    {"category": {"$in": ["Electronics", "Sports"]}},
                    {"price": {"$gte": 50, "$lte": 500}},
                    {"rating": {"$gte": 3.5}},
                    {"active": True}
                ]
            }))

        result = monitored_complex_query()
        return result

    # Execute optimization examples
    create_performance_indexes()
    explain_simple, explain_complex = analyze_query_performance()
    optimized_search, forced_index, paginated = optimized_query_patterns()
    monitored_result = monitor_slow_queries()

    return {
        'explanations': (explain_simple, explain_complex),
        'optimized_results': (optimized_search, forced_index, paginated),
        'monitored': monitored_result
    }

# Usage
performance_results = query_performance_optimization()
```

## Best Practices

### Query Best Practices

```python
def query_best_practices():
    """Demonstrate query best practices"""

    # 1. Use appropriate data types
    def correct_data_types():
        """Use correct data types in queries"""

        # ❌ Wrong: String comparison for numbers
        # wrong_price = products.find({"price": {"$gt": "100"}})

        # ✅ Correct: Numeric comparison
        correct_price = products.find({"price": {"$gt": 100}})

        # ❌ Wrong: String date comparison
        # wrong_date = products.find({"created_at": {"$gt": "2023-01-01"}})

        # ✅ Correct: Date object comparison
        correct_date = products.find({
            "created_at": {"$gt": datetime(2023, 1, 1)}
        })

        return list(correct_price), list(correct_date)

    # 2. Optimize query structure
    def optimize_query_structure():
        """Structure queries for optimal performance"""

        # ✅ Most selective fields first
        optimized_query = products.find({
            "active": True,  # Boolean field (highly selective)
            "category": "Electronics",  # Indexed field
            "price": {"$gte": 100, "$lte": 500}  # Range query
        })

        # ✅ Use $and explicitly for complex conditions
        explicit_and = products.find({
            "$and": [
                {"category": "Electronics"},
                {"rating": {"$gte": 4.0}},
                {"$or": [
                    {"brand": "TechBrand"},
                    {"price": {"$lt": 200}}
                ]}
            ]
        })

        # ✅ Combine compatible operators
        combined_operators = products.find({
            "price": {"$gte": 50, "$lte": 200},
            "rating": {"$gte": 3.5},
            "stock": {"$gt": 0}
        })

        return list(optimized_query), list(explicit_and), list(combined_operators)

    # 3. Proper error handling
    def proper_error_handling():
        """Handle query errors properly"""

        try:
            # Query that might fail
            result = products.find({
                "price": {"$gte": 0},
                "category": {"$regex": "^Electronics$", "$options": "i"}
            })

            # Convert cursor to list safely
            products_list = []
            for product in result:
                products_list.append(product)
                if len(products_list) >= 1000:  # Prevent memory issues
                    break

            return products_list

        except Exception as e:
            print(f"Query error: {e}")
            return []

    # 4. Use projections efficiently
    def efficient_projections():
        """Use projections to reduce data transfer"""

        # ✅ Include only needed fields
        summary_projection = list(products.find(
            {"active": True},
            {"name": 1, "price": 1, "rating": 1}  # Include _id by default
        ))

        # ✅ Exclude _id if not needed
        no_id_projection = list(products.find(
            {"category": "Electronics"},
            {"name": 1, "price": 1, "_id": 0}
        ))

        # ✅ Exclude large fields
        exclude_large_fields = list(products.find(
            {},
            {"specs": 0, "tags": 0}  # Exclude potentially large arrays/objects
        ))

        return summary_projection, no_id_projection, exclude_large_fields

    # 5. Pagination best practices
    def pagination_best_practices():
        """Implement efficient pagination"""

        def get_page(page_number, page_size=20):
            """Get a specific page of results"""
            skip_count = (page_number - 1) * page_size

            return list(products.find({"active": True})
                       .sort("created_at", -1)
                       .skip(skip_count)
                       .limit(page_size))

        def get_total_count(query=None):
            """Get total count for pagination"""
            if query is None:
                query = {"active": True}
            return products.count_documents(query)

        # Example usage
        page_1 = get_page(1, 10)
        total_products = get_total_count({"active": True})
        total_pages = (total_products + 9) // 10  # Ceiling division

        return page_1, total_products, total_pages

    # 6. Query validation
    def validate_queries():
        """Validate query parameters"""

        def safe_query(filters):
            """Build safe query from user input"""
            query = {}

            # Validate and sanitize price range
            if 'min_price' in filters:
                try:
                    min_price = float(filters['min_price'])
                    if min_price >= 0:
                        query.setdefault('price', {})['$gte'] = min_price
                except (ValueError, TypeError):
                    pass  # Ignore invalid values

            # Validate category (whitelist approach)
            valid_categories = ['Electronics', 'Sports', 'Home', 'Books']
            if 'category' in filters and filters['category'] in valid_categories:
                query['category'] = filters['category']

            # Validate rating
            if 'min_rating' in filters:
                try:
                    min_rating = float(filters['min_rating'])
                    if 0 <= min_rating <= 5:
                        query['rating'] = {'$gte': min_rating}
                except (ValueError, TypeError):
                    pass

            # Always filter active products
            query['active'] = True

            return query

        # Example usage
        user_filters = {
            'min_price': '100',
            'category': 'Electronics',
            'min_rating': '4.0'
        }

        safe_query_dict = safe_query(user_filters)
        safe_results = list(products.find(safe_query_dict))

        return safe_results

    # Execute all best practices
    correct_types = correct_data_types()
    optimized_structure = optimize_query_structure()
    error_handled = proper_error_handling()
    projections = efficient_projections()
    pagination = pagination_best_practices()
    validated = validate_queries()

    print("=== Best Practices Results ===")
    print(f"Correct data types: {len(correct_types[0])} products")
    print(f"Optimized structure: {len(optimized_structure[0])} products")
    print(f"Error handling: {len(error_handled)} products")
    print(f"Efficient projections: {len(projections[0])} summaries")
    print(f"Pagination: Page 1 has {len(pagination[0])} items, Total: {pagination[1]}")
    print(f"Validated queries: {len(validated)} products")

    return {
        'correct_types': correct_types,
        'optimized': optimized_structure,
        'projections': projections,
        'pagination': pagination,
        'validated': validated
    }

# Usage
best_practices_results = query_best_practices()
```

## Next Steps

After mastering query operators:

1. **Aggregation Framework**: [Advanced Aggregation](../advanced/01_aggregation_framework.md)
2. **Indexing Strategies**: [Indexing in PyMongo](../advanced/02_indexing.md)
3. **Full-Text Search**: [Text Search and Analysis](../advanced/06_text_search.md)
4. **Geospatial Queries**: [Advanced Geospatial Operations](../advanced/07_geospatial.md)

## Additional Resources

- [MongoDB Query Operators](https://docs.mongodb.com/manual/reference/operator/query/)
- [PyMongo Query Documentation](https://pymongo.readthedocs.io/en/stable/tutorial.html#querying-for-more-than-one-document)
- [Query Optimization](https://docs.mongodb.com/manual/core/query-optimization/)
- [Index Usage and Performance](https://docs.mongodb.com/manual/applications/indexes/)
