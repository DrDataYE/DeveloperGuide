# PyMongo Aggregation Framework

This comprehensive guide covers MongoDB's powerful aggregation framework using PyMongo, including all pipeline stages, operators, and advanced aggregation patterns.

## Table of Contents

1. [Aggregation Overview](#aggregation-overview)
2. [Basic Aggregation Pipeline](#basic-aggregation-pipeline)
3. [Pipeline Stages](#pipeline-stages)
4. [Aggregation Operators](#aggregation-operators)
5. [Advanced Aggregation Patterns](#advanced-aggregation-patterns)
6. [Performance Optimization](#performance-optimization)
7. [Real-World Examples](#real-world-examples)
8. [Best Practices](#best-practices)

## Aggregation Overview

The MongoDB aggregation framework provides a powerful way to process and transform data. It works by passing documents through a pipeline of stages, where each stage transforms the documents.

### Basic Concepts

```python
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.ecommerce
orders = db.orders
products = db.products
customers = db.customers

def setup_sample_data():
    """Setup sample data for aggregation examples"""

    # Clear existing data
    orders.delete_many({})
    products.delete_many({})
    customers.delete_many({})

    # Sample customers
    sample_customers = [
        {
            "_id": ObjectId(),
            "name": "John Doe",
            "email": "john@example.com",
            "age": 28,
            "city": "New York",
            "country": "USA",
            "registration_date": datetime(2023, 1, 15)
        },
        {
            "_id": ObjectId(),
            "name": "Jane Smith",
            "email": "jane@example.com",
            "age": 34,
            "city": "London",
            "country": "UK",
            "registration_date": datetime(2023, 2, 10)
        },
        {
            "_id": ObjectId(),
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "age": 45,
            "city": "Toronto",
            "country": "Canada",
            "registration_date": datetime(2023, 3, 5)
        }
    ]

    customers.insert_many(sample_customers)
    customer_ids = [doc["_id"] for doc in sample_customers]

    # Sample products
    sample_products = [
        {
            "_id": ObjectId(),
            "name": "Laptop Pro",
            "category": "Electronics",
            "price": 1299.99,
            "cost": 800.00,
            "brand": "TechBrand"
        },
        {
            "_id": ObjectId(),
            "name": "Wireless Mouse",
            "category": "Electronics",
            "price": 29.99,
            "cost": 15.00,
            "brand": "TechBrand"
        },
        {
            "_id": ObjectId(),
            "name": "Coffee Mug",
            "category": "Home",
            "price": 12.99,
            "cost": 5.00,
            "brand": "HomeGoods"
        }
    ]

    products.insert_many(sample_products)
    product_ids = [doc["_id"] for doc in sample_products]

    # Sample orders
    sample_orders = [
        {
            "_id": ObjectId(),
            "customer_id": customer_ids[0],
            "order_date": datetime(2023, 6, 1),
            "status": "completed",
            "items": [
                {"product_id": product_ids[0], "quantity": 1, "price": 1299.99},
                {"product_id": product_ids[1], "quantity": 2, "price": 29.99}
            ],
            "shipping_address": {
                "city": "New York",
                "country": "USA"
            },
            "total": 1359.97
        },
        {
            "_id": ObjectId(),
            "customer_id": customer_ids[1],
            "order_date": datetime(2023, 6, 15),
            "status": "completed",
            "items": [
                {"product_id": product_ids[2], "quantity": 3, "price": 12.99}
            ],
            "shipping_address": {
                "city": "London",
                "country": "UK"
            },
            "total": 38.97
        },
        {
            "_id": ObjectId(),
            "customer_id": customer_ids[0],
            "order_date": datetime(2023, 7, 10),
            "status": "pending",
            "items": [
                {"product_id": product_ids[1], "quantity": 1, "price": 29.99}
            ],
            "shipping_address": {
                "city": "New York",
                "country": "USA"
            },
            "total": 29.99
        }
    ]

    orders.insert_many(sample_orders)
    print("✅ Sample data created successfully")

    return customer_ids, product_ids

# Setup data
customer_ids, product_ids = setup_sample_data()
```

## Basic Aggregation Pipeline

### Simple Aggregation Examples

```python
def basic_aggregation_examples():
    """Basic aggregation pipeline examples"""

    # Example 1: Simple match and project
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$project": {
            "customer_id": 1,
            "total": 1,
            "order_date": 1
        }}
    ]

    completed_orders = list(orders.aggregate(pipeline))
    print(f"Completed orders: {len(completed_orders)}")

    # Example 2: Group by customer
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$total"},
            "order_count": {"$sum": 1},
            "avg_order_value": {"$avg": "$total"}
        }}
    ]

    customer_summary = list(orders.aggregate(pipeline))
    print("Customer spending summary:")
    for customer in customer_summary:
        print(f"  Customer {customer['_id']}: ${customer['total_spent']:.2f} "
              f"({customer['order_count']} orders)")

    # Example 3: Sort and limit
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$total"}
        }},
        {"$sort": {"total_spent": -1}},
        {"$limit": 5}
    ]

    top_customers = list(orders.aggregate(pipeline))
    print("Top customers by spending:")
    for customer in top_customers:
        print(f"  Customer {customer['_id']}: ${customer['total_spent']:.2f}")

    return completed_orders, customer_summary, top_customers

# Execute basic examples
basic_results = basic_aggregation_examples()
```

### Pipeline Execution Flow

```python
def pipeline_execution_flow():
    """Demonstrate how aggregation pipeline flows"""

    # Step-by-step pipeline execution
    print("=== Pipeline Execution Flow ===")

    # Step 1: Start with all documents
    all_orders = list(orders.find())
    print(f"1. Initial documents: {len(all_orders)}")

    # Step 2: Apply $match filter
    matched = list(orders.aggregate([
        {"$match": {"status": "completed"}}
    ]))
    print(f"2. After $match: {len(matched)} documents")

    # Step 3: Apply $group
    grouped = list(orders.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$total"}
        }}
    ]))
    print(f"3. After $group: {len(grouped)} documents")

    # Step 4: Apply $sort
    sorted_result = list(orders.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$total"}
        }},
        {"$sort": {"total_spent": -1}}
    ]))
    print(f"4. After $sort: {len(sorted_result)} documents (same count, different order)")

    # Step 5: Apply $limit
    limited = list(orders.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$total"}
        }},
        {"$sort": {"total_spent": -1}},
        {"$limit": 2}
    ]))
    print(f"5. After $limit: {len(limited)} documents")

    return limited

# Execute flow example
pipeline_flow = pipeline_execution_flow()
```

## Pipeline Stages

### $match - Filtering Documents

```python
def match_stage_examples():
    """Examples of $match stage"""

    # Basic match
    basic_match = list(orders.aggregate([
        {"$match": {"status": "completed"}}
    ]))

    # Match with multiple conditions
    complex_match = list(orders.aggregate([
        {"$match": {
            "status": "completed",
            "total": {"$gte": 100}
        }}
    ]))

    # Match with date range
    date_match = list(orders.aggregate([
        {"$match": {
            "order_date": {
                "$gte": datetime(2023, 6, 1),
                "$lt": datetime(2023, 7, 1)
            }
        }}
    ]))

    # Match with array elements
    array_match = list(orders.aggregate([
        {"$match": {
            "items.quantity": {"$gte": 2}
        }}
    ]))

    # Match with regex
    regex_match = list(orders.aggregate([
        {"$match": {
            "shipping_address.city": {"$regex": "New", "$options": "i"}
        }}
    ]))

    print(f"Basic match: {len(basic_match)} orders")
    print(f"Complex match: {len(complex_match)} orders")
    print(f"Date match: {len(date_match)} orders")
    print(f"Array match: {len(array_match)} orders")
    print(f"Regex match: {len(regex_match)} orders")

    return basic_match, complex_match

# Execute match examples
match_results = match_stage_examples()
```

### $project - Reshaping Documents

```python
def project_stage_examples():
    """Examples of $project stage"""

    # Include specific fields
    include_fields = list(orders.aggregate([
        {"$project": {
            "customer_id": 1,
            "total": 1,
            "status": 1
        }}
    ]))

    # Exclude specific fields
    exclude_fields = list(orders.aggregate([
        {"$project": {
            "items": 0,
            "shipping_address": 0
        }}
    ]))

    # Rename fields
    rename_fields = list(orders.aggregate([
        {"$project": {
            "customer": "$customer_id",
            "amount": "$total",
            "date": "$order_date"
        }}
    ]))

    # Create computed fields
    computed_fields = list(orders.aggregate([
        {"$project": {
            "customer_id": 1,
            "total": 1,
            "year": {"$year": "$order_date"},
            "month": {"$month": "$order_date"},
            "is_large_order": {"$gte": ["$total", 100]},
            "item_count": {"$size": "$items"}
        }}
    ]))

    # Nested field projection
    nested_projection = list(orders.aggregate([
        {"$project": {
            "customer_id": 1,
            "shipping_city": "$shipping_address.city",
            "shipping_country": "$shipping_address.country",
            "first_item": {"$arrayElemAt": ["$items", 0]}
        }}
    ]))

    # Conditional projection
    conditional_projection = list(orders.aggregate([
        {"$project": {
            "customer_id": 1,
            "total": 1,
            "status": 1,
            "priority": {
                "$cond": {
                    "if": {"$gte": ["$total", 1000]},
                    "then": "high",
                    "else": "normal"
                }
            }
        }}
    ]))

    print(f"Include fields: {len(include_fields)} documents")
    print(f"Computed fields example:")
    for doc in computed_fields[:2]:
        print(f"  Order {doc['_id']}: {doc['item_count']} items, "
              f"large order: {doc['is_large_order']}")

    return include_fields, computed_fields

# Execute project examples
project_results = project_stage_examples()
```

### $group - Grouping and Aggregating

```python
def group_stage_examples():
    """Examples of $group stage"""

    # Group by single field
    group_by_status = list(orders.aggregate([
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "total_value": {"$sum": "$total"},
            "avg_value": {"$avg": "$total"}
        }}
    ]))

    # Group by multiple fields
    group_by_multiple = list(orders.aggregate([
        {"$group": {
            "_id": {
                "status": "$status",
                "country": "$shipping_address.country"
            },
            "count": {"$sum": 1},
            "total_value": {"$sum": "$total"}
        }}
    ]))

    # Group by date parts
    group_by_date = list(orders.aggregate([
        {"$group": {
            "_id": {
                "year": {"$year": "$order_date"},
                "month": {"$month": "$order_date"}
            },
            "orders": {"$sum": 1},
            "revenue": {"$sum": "$total"}
        }}
    ]))

    # Accumulator operators
    accumulator_examples = list(orders.aggregate([
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$total"},
            "order_count": {"$sum": 1},
            "avg_order": {"$avg": "$total"},
            "min_order": {"$min": "$total"},
            "max_order": {"$max": "$total"},
            "first_order": {"$first": "$order_date"},
            "last_order": {"$last": "$order_date"},
            "all_totals": {"$push": "$total"},
            "unique_statuses": {"$addToSet": "$status"}
        }},
        {"$sort": {"order_count": -1}}
    ]))

    # Group with array operations
    array_operations = list(orders.aggregate([
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_id",
            "total_quantity": {"$sum": "$items.quantity"},
            "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
            "avg_price": {"$avg": "$items.price"},
            "orders": {"$addToSet": "$_id"}
        }},
        {"$sort": {"total_revenue": -1}}
    ]))

    print("=== Group Results ===")
    print("Group by status:")
    for doc in group_by_status:
        print(f"  {doc['_id']}: {doc['count']} orders, ${doc['total_value']:.2f}")

    print("\nAccumulator examples:")
    for doc in accumulator_examples[:2]:
        print(f"  Customer {doc['_id']}: {doc['order_count']} orders, "
              f"${doc['total_spent']:.2f} total")

    print("\nProduct sales:")
    for doc in array_operations[:3]:
        print(f"  Product {doc['_id']}: {doc['total_quantity']} units, "
              f"${doc['total_revenue']:.2f} revenue")

    return group_by_status, accumulator_examples, array_operations

# Execute group examples
group_results = group_stage_examples()
```

### $sort and $limit

```python
def sort_limit_examples():
    """Examples of $sort and $limit stages"""

    # Basic sorting
    sort_by_date = list(orders.aggregate([
        {"$sort": {"order_date": -1}}  # Descending order
    ]))

    # Sort by multiple fields
    sort_multiple = list(orders.aggregate([
        {"$sort": {
            "status": 1,      # Ascending
            "total": -1,      # Descending
            "order_date": -1  # Descending
        }}
    ]))

    # Sort with grouping
    sort_after_group = list(orders.aggregate([
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$total"},
            "order_count": {"$sum": 1}
        }},
        {"$sort": {"total_spent": -1}}
    ]))

    # Top N results with limit
    top_customers = list(orders.aggregate([
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$total"}
        }},
        {"$sort": {"total_spent": -1}},
        {"$limit": 3}
    ]))

    # Skip and limit for pagination
    page_size = 2
    page_number = 2
    skip_amount = (page_number - 1) * page_size

    paginated = list(orders.aggregate([
        {"$sort": {"order_date": -1}},
        {"$skip": skip_amount},
        {"$limit": page_size}
    ]))

    # Sort by computed fields
    sort_computed = list(orders.aggregate([
        {"$addFields": {
            "items_count": {"$size": "$items"}
        }},
        {"$sort": {"items_count": -1, "total": -1}}
    ]))

    print("=== Sort and Limit Results ===")
    print("Top customers by spending:")
    for doc in top_customers:
        print(f"  Customer {doc['_id']}: ${doc['total_spent']:.2f}")

    print(f"\nPaginated results (page {page_number}):")
    for doc in paginated:
        print(f"  Order {doc['_id']}: ${doc['total']:.2f} on {doc['order_date']}")

    return top_customers, paginated

# Execute sort/limit examples
sort_results = sort_limit_examples()
```

### $unwind - Array Deconstruction

```python
def unwind_examples():
    """Examples of $unwind stage"""

    # Basic unwind
    basic_unwind = list(orders.aggregate([
        {"$unwind": "$items"},
        {"$project": {
            "customer_id": 1,
            "order_date": 1,
            "item": "$items"
        }}
    ]))

    # Unwind with preserveNullAndEmptyArrays
    preserve_empty = list(orders.aggregate([
        {"$unwind": {
            "path": "$items",
            "preserveNullAndEmptyArrays": True
        }}
    ]))

    # Unwind with includeArrayIndex
    with_index = list(orders.aggregate([
        {"$unwind": {
            "path": "$items",
            "includeArrayIndex": "item_index"
        }},
        {"$project": {
            "customer_id": 1,
            "item": "$items",
            "position": "$item_index"
        }}
    ]))

    # Unwind and analyze items
    item_analysis = list(orders.aggregate([
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_id",
            "total_quantity": {"$sum": "$items.quantity"},
            "total_revenue": {"$sum": {
                "$multiply": ["$items.quantity", "$items.price"]
            }},
            "avg_quantity_per_order": {"$avg": "$items.quantity"},
            "times_ordered": {"$sum": 1}
        }},
        {"$sort": {"total_revenue": -1}}
    ]))

    # Multiple unwind stages
    # Assuming we have orders with multiple arrays to unwind
    # This is more common in complex document structures

    print("=== Unwind Results ===")
    print(f"Basic unwind: {len(basic_unwind)} item documents")
    print(f"With index: {len(with_index)} item documents")

    print("\nItem analysis:")
    for doc in item_analysis:
        print(f"  Product {doc['_id']}: {doc['total_quantity']} units, "
              f"${doc['total_revenue']:.2f} revenue, ordered {doc['times_ordered']} times")

    return basic_unwind, item_analysis

# Execute unwind examples
unwind_results = unwind_examples()
```

### $lookup - Joining Collections

```python
def lookup_examples():
    """Examples of $lookup stage (joins)"""

    # Basic lookup - join orders with customers
    orders_with_customers = list(orders.aggregate([
        {"$lookup": {
            "from": "customers",
            "localField": "customer_id",
            "foreignField": "_id",
            "as": "customer_info"
        }},
        {"$unwind": "$customer_info"},
        {"$project": {
            "order_date": 1,
            "total": 1,
            "status": 1,
            "customer_name": "$customer_info.name",
            "customer_email": "$customer_info.email",
            "customer_city": "$customer_info.city"
        }}
    ]))

    # Lookup with pipeline (advanced join)
    orders_with_customer_pipeline = list(orders.aggregate([
        {"$lookup": {
            "from": "customers",
            "let": {"customer_id": "$customer_id"},
            "pipeline": [
                {"$match": {
                    "$expr": {"$eq": ["$_id", "$$customer_id"]}
                }},
                {"$project": {
                    "name": 1,
                    "email": 1,
                    "city": 1,
                    "age": 1
                }}
            ],
            "as": "customer"
        }},
        {"$unwind": "$customer"}
    ]))

    # Multiple lookups
    orders_complete_info = list(orders.aggregate([
        # Join with customers
        {"$lookup": {
            "from": "customers",
            "localField": "customer_id",
            "foreignField": "_id",
            "as": "customer"
        }},
        {"$unwind": "$customer"},

        # Unwind items to join with products
        {"$unwind": "$items"},

        # Join with products
        {"$lookup": {
            "from": "products",
            "localField": "items.product_id",
            "foreignField": "_id",
            "as": "product_info"
        }},
        {"$unwind": "$product_info"},

        # Reconstruct the document
        {"$group": {
            "_id": "$_id",
            "customer": {"$first": "$customer"},
            "order_date": {"$first": "$order_date"},
            "status": {"$first": "$status"},
            "total": {"$first": "$total"},
            "items": {
                "$push": {
                    "product_name": "$product_info.name",
                    "product_category": "$product_info.category",
                    "quantity": "$items.quantity",
                    "price": "$items.price",
                    "subtotal": {"$multiply": ["$items.quantity", "$items.price"]}
                }
            }
        }}
    ]))

    # Self lookup (hierarchical data)
    # Example: if we had categories with parent-child relationships

    # Lookup with filtering
    recent_orders_with_customers = list(orders.aggregate([
        {"$match": {
            "order_date": {"$gte": datetime(2023, 6, 1)}
        }},
        {"$lookup": {
            "from": "customers",
            "localField": "customer_id",
            "foreignField": "_id",
            "as": "customer"
        }},
        {"$unwind": "$customer"},
        {"$match": {
            "customer.country": "USA"
        }}
    ]))

    print("=== Lookup Results ===")
    print(f"Orders with customers: {len(orders_with_customers)}")
    print("Sample order with customer:")
    if orders_with_customers:
        order = orders_with_customers[0]
        print(f"  {order['customer_name']} ordered ${order['total']:.2f} "
              f"on {order['order_date']}")

    print(f"\nComplete order info: {len(orders_complete_info)}")
    if orders_complete_info:
        complete_order = orders_complete_info[0]
        print(f"  Customer: {complete_order['customer']['name']}")
        print(f"  Items: {len(complete_order['items'])}")
        for item in complete_order['items']:
            print(f"    - {item['product_name']}: {item['quantity']} x ${item['price']:.2f}")

    return orders_with_customers, orders_complete_info

# Execute lookup examples
lookup_results = lookup_examples()
```

## Aggregation Operators

### Arithmetic Operators

```python
def arithmetic_operators():
    """Examples of arithmetic operators in aggregation"""

    # Basic arithmetic
    order_calculations = list(orders.aggregate([
        {"$project": {
            "customer_id": 1,
            "total": 1,
            "tax_rate": 0.08,
            "tax_amount": {"$multiply": ["$total", 0.08]},
            "total_with_tax": {"$add": ["$total", {"$multiply": ["$total", 0.08]}]},
            "discount_10_percent": {"$subtract": ["$total", {"$multiply": ["$total", 0.1]}]},
            "total_rounded": {"$round": ["$total", 2]}
        }}
    ]))

    # Complex calculations
    item_analysis = list(orders.aggregate([
        {"$unwind": "$items"},
        {"$lookup": {
            "from": "products",
            "localField": "items.product_id",
            "foreignField": "_id",
            "as": "product"
        }},
        {"$unwind": "$product"},
        {"$project": {
            "order_id": "$_id",
            "product_name": "$product.name",
            "quantity": "$items.quantity",
            "price": "$items.price",
            "cost": "$product.cost",
            "revenue": {"$multiply": ["$items.quantity", "$items.price"]},
            "cost_total": {"$multiply": ["$items.quantity", "$product.cost"]},
            "profit": {
                "$subtract": [
                    {"$multiply": ["$items.quantity", "$items.price"]},
                    {"$multiply": ["$items.quantity", "$product.cost"]}
                ]
            },
            "profit_margin": {
                "$divide": [
                    {"$subtract": ["$items.price", "$product.cost"]},
                    "$items.price"
                ]
            }
        }}
    ]))

    # Date arithmetic
    order_age_analysis = list(orders.aggregate([
        {"$project": {
            "customer_id": 1,
            "order_date": 1,
            "total": 1,
            "days_since_order": {
                "$divide": [
                    {"$subtract": [datetime.utcnow(), "$order_date"]},
                    1000 * 60 * 60 * 24  # Convert milliseconds to days
                ]
            },
            "order_year": {"$year": "$order_date"},
            "order_month": {"$month": "$order_date"},
            "order_day_of_week": {"$dayOfWeek": "$order_date"}
        }}
    ]))

    print("=== Arithmetic Operators Results ===")
    print("Order calculations (first 2):")
    for order in order_calculations[:2]:
        print(f"  Order total: ${order['total']:.2f}")
        print(f"  Tax: ${order['tax_amount']:.2f}")
        print(f"  Total with tax: ${order['total_with_tax']:.2f}")
        print("  ---")

    print("Item profit analysis:")
    for item in item_analysis[:3]:
        print(f"  {item['product_name']}: ${item['revenue']:.2f} revenue, "
              f"${item['profit']:.2f} profit ({item['profit_margin']:.1%} margin)")

    return order_calculations, item_analysis

# Execute arithmetic examples
arithmetic_results = arithmetic_operators()
```

### String Operators

```python
def string_operators():
    """Examples of string operators in aggregation"""

    # String manipulation
    customer_string_ops = list(customers.aggregate([
        {"$project": {
            "name": 1,
            "email": 1,
            "name_upper": {"$toUpper": "$name"},
            "name_lower": {"$toLower": "$name"},
            "first_name": {
                "$arrayElemAt": [
                    {"$split": ["$name", " "]}, 0
                ]
            },
            "last_name": {
                "$arrayElemAt": [
                    {"$split": ["$name", " "]}, -1
                ]
            },
            "email_domain": {
                "$arrayElemAt": [
                    {"$split": ["$email", "@"]}, 1
                ]
            },
            "name_length": {"$strLenCP": "$name"},
            "initials": {
                "$concat": [
                    {"$substr": [
                        {"$arrayElemAt": [{"$split": ["$name", " "]}, 0]}, 0, 1
                    ]},
                    ".",
                    {"$substr": [
                        {"$arrayElemAt": [{"$split": ["$name", " "]}, -1]}, 0, 1
                    ]},
                    "."
                ]
            }
        }}
    ]))

    # String pattern matching
    pattern_matching = list(customers.aggregate([
        {"$project": {
            "name": 1,
            "email": 1,
            "has_gmail": {
                "$regexMatch": {
                    "input": "$email",
                    "regex": "gmail\.com$",
                    "options": "i"
                }
            },
            "name_starts_with_j": {
                "$regexMatch": {
                    "input": "$name",
                    "regex": "^J",
                    "options": "i"
                }
            }
        }}
    ]))

    # String replacement and formatting
    formatted_data = list(customers.aggregate([
        {"$project": {
            "name": 1,
            "email": 1,
            "formatted_name": {
                "$concat": [
                    {"$toUpper": {"$substr": ["$name", 0, 1]}},
                    {"$toLower": {"$substr": ["$name", 1, -1]}}
                ]
            },
            "email_masked": {
                "$concat": [
                    {"$substr": ["$email", 0, 3]},
                    "***@",
                    {"$arrayElemAt": [{"$split": ["$email", "@"]}, 1]}
                ]
            },
            "display_text": {
                "$concat": [
                    "$name",
                    " (",
                    {"$toString": "$age"},
                    " years old)"
                ]
            }
        }}
    ]))

    print("=== String Operators Results ===")
    print("Customer string operations:")
    for customer in customer_string_ops:
        print(f"  {customer['name']} -> {customer['initials']}")
        print(f"  Email domain: {customer['email_domain']}")
        print(f"  Name length: {customer['name_length']} characters")
        print("  ---")

    print("Pattern matching:")
    for customer in pattern_matching:
        gmail_status = "✓" if customer['has_gmail'] else "✗"
        j_status = "✓" if customer['name_starts_with_j'] else "✗"
        print(f"  {customer['name']}: Gmail {gmail_status}, Starts with J {j_status}")

    return customer_string_ops, pattern_matching

# Execute string examples
string_results = string_operators()
```

### Array Operators

```python
def array_operators():
    """Examples of array operators in aggregation"""

    # Array manipulation
    order_array_ops = list(orders.aggregate([
        {"$project": {
            "customer_id": 1,
            "items": 1,
            "item_count": {"$size": "$items"},
            "first_item": {"$arrayElemAt": ["$items", 0]},
            "last_item": {"$arrayElemAt": ["$items", -1]},
            "item_quantities": {"$map": {
                "input": "$items",
                "as": "item",
                "in": "$$item.quantity"
            }},
            "total_quantity": {
                "$reduce": {
                    "input": "$items",
                    "initialValue": 0,
                    "in": {"$add": ["$$value", "$$this.quantity"]}
                }
            },
            "expensive_items": {
                "$filter": {
                    "input": "$items",
                    "as": "item",
                    "cond": {"$gte": ["$$item.price", 100]}
                }
            }
        }}
    ]))

    # Array aggregation operations
    item_summary = list(orders.aggregate([
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$customer_id",
            "all_products": {"$push": "$items.product_id"},
            "unique_products": {"$addToSet": "$items.product_id"},
            "total_items": {"$sum": "$items.quantity"},
            "price_range": {
                "$push": "$items.price"
            }
        }},
        {"$project": {
            "unique_product_count": {"$size": "$unique_products"},
            "total_items": 1,
            "min_price": {"$min": "$price_range"},
            "max_price": {"$max": "$price_range"},
            "avg_price": {"$avg": "$price_range"}
        }}
    ]))

    # Complex array operations
    advanced_array_ops = list(orders.aggregate([
        {"$project": {
            "customer_id": 1,
            "items": 1,
            "sorted_items_by_price": {
                "$sortArray": {
                    "input": "$items",
                    "sortBy": {"price": -1}
                }
            },
            "items_with_index": {
                "$zip": {
                    "inputs": [
                        {"$range": [0, {"$size": "$items"}]},
                        "$items"
                    ]
                }
            },
            "price_categories": {
                "$map": {
                    "input": "$items",
                    "as": "item",
                    "in": {
                        "$cond": {
                            "if": {"$gte": ["$$item.price", 100]},
                            "then": "expensive",
                            "else": "affordable"
                        }
                    }
                }
            }
        }}
    ]))

    # Array set operations
    set_operations = list(orders.aggregate([
        {"$group": {
            "_id": None,
            "all_customer_ids": {"$push": "$customer_id"},
            "unique_customer_ids": {"$addToSet": "$customer_id"}
        }},
        {"$project": {
            "total_orders": {"$size": "$all_customer_ids"},
            "unique_customers": {"$size": "$unique_customer_ids"},
            "repeat_customer_ratio": {
                "$divide": [
                    {"$subtract": [
                        {"$size": "$all_customer_ids"},
                        {"$size": "$unique_customer_ids"}
                    ]},
                    {"$size": "$all_customer_ids"}
                ]
            }
        }}
    ]))

    print("=== Array Operators Results ===")
    print("Order array operations:")
    for order in order_array_ops[:2]:
        print(f"  Order: {order['item_count']} items, "
              f"total quantity: {order['total_quantity']}")
        print(f"  Expensive items: {len(order['expensive_items'])}")
        print("  ---")

    print("Customer item summary:")
    for summary in item_summary:
        print(f"  Customer {summary['_id']}: {summary['unique_product_count']} "
              f"unique products, {summary['total_items']} total items")

    return order_array_ops, item_summary

# Execute array examples
array_results = array_operators()
```

## Advanced Aggregation Patterns

### Complex Analytical Queries

```python
def advanced_patterns():
    """Advanced aggregation patterns and analytical queries"""

    # Customer lifetime value analysis
    customer_ltv = list(orders.aggregate([
        # Join with customer data
        {"$lookup": {
            "from": "customers",
            "localField": "customer_id",
            "foreignField": "_id",
            "as": "customer"
        }},
        {"$unwind": "$customer"},

        # Group by customer to calculate metrics
        {"$group": {
            "_id": "$customer_id",
            "customer_name": {"$first": "$customer.name"},
            "customer_age": {"$first": "$customer.age"},
            "registration_date": {"$first": "$customer.registration_date"},
            "total_orders": {"$sum": 1},
            "total_spent": {"$sum": "$total"},
            "avg_order_value": {"$avg": "$total"},
            "first_order": {"$min": "$order_date"},
            "last_order": {"$max": "$order_date"},
            "order_frequency": {
                "$avg": {
                    "$divide": [
                        {"$subtract": ["$order_date", "$customer.registration_date"]},
                        1000 * 60 * 60 * 24  # Days
                    ]
                }
            }
        }},

        # Calculate additional metrics
        {"$addFields": {
            "days_as_customer": {
                "$divide": [
                    {"$subtract": [datetime.utcnow(), "$registration_date"]},
                    1000 * 60 * 60 * 24
                ]
            },
            "customer_value_score": {
                "$multiply": [
                    "$total_spent",
                    {"$divide": ["$total_orders", 30]}  # Orders per month approximation
                ]
            }
        }},

        # Sort by value
        {"$sort": {"customer_value_score": -1}}
    ]))

    # Product performance analysis
    product_performance = list(orders.aggregate([
        {"$unwind": "$items"},

        # Join with product data
        {"$lookup": {
            "from": "products",
            "localField": "items.product_id",
            "foreignField": "_id",
            "as": "product"
        }},
        {"$unwind": "$product"},

        # Group by product
        {"$group": {
            "_id": "$items.product_id",
            "product_name": {"$first": "$product.name"},
            "category": {"$first": "$product.category"},
            "total_quantity_sold": {"$sum": "$items.quantity"},
            "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
            "total_orders": {"$sum": 1},
            "avg_quantity_per_order": {"$avg": "$items.quantity"},
            "price_points": {"$addToSet": "$items.price"}
        }},

        # Calculate metrics
        {"$addFields": {
            "revenue_per_order": {"$divide": ["$total_revenue", "$total_orders"]},
            "price_variation": {
                "$subtract": [
                    {"$max": "$price_points"},
                    {"$min": "$price_points"}
                ]
            }
        }},

        {"$sort": {"total_revenue": -1}}
    ]))

    # Time-based analysis (cohort analysis simplified)
    monthly_cohorts = list(orders.aggregate([
        # Add month fields
        {"$addFields": {
            "order_month": {
                "$dateToString": {
                    "format": "%Y-%m",
                    "date": "$order_date"
                }
            }
        }},

        # Group by month and customer
        {"$group": {
            "_id": {
                "month": "$order_month",
                "customer_id": "$customer_id"
            },
            "orders_in_month": {"$sum": 1},
            "spent_in_month": {"$sum": "$total"}
        }},

        # Group by month
        {"$group": {
            "_id": "$_id.month",
            "unique_customers": {"$sum": 1},
            "total_orders": {"$sum": "$orders_in_month"},
            "total_revenue": {"$sum": "$spent_in_month"},
            "avg_orders_per_customer": {"$avg": "$orders_in_month"},
            "avg_spent_per_customer": {"$avg": "$spent_in_month"}
        }},

        {"$sort": {"_id": 1}}
    ]))

    # Geographic analysis
    geographic_analysis = list(orders.aggregate([
        # Group by shipping location
        {"$group": {
            "_id": {
                "city": "$shipping_address.city",
                "country": "$shipping_address.country"
            },
            "order_count": {"$sum": 1},
            "total_revenue": {"$sum": "$total"},
            "avg_order_value": {"$avg": "$total"},
            "unique_customers": {"$addToSet": "$customer_id"}
        }},

        # Calculate customer count
        {"$addFields": {
            "customer_count": {"$size": "$unique_customers"},
            "orders_per_customer": {"$divide": ["$order_count", {"$size": "$unique_customers"}]}
        }},

        # Sort by revenue
        {"$sort": {"total_revenue": -1}}
    ]))

    print("=== Advanced Analysis Results ===")
    print("Customer LTV Analysis:")
    for customer in customer_ltv[:3]:
        print(f"  {customer['customer_name']}: ${customer['total_spent']:.2f} total, "
              f"{customer['total_orders']} orders, score: {customer['customer_value_score']:.1f}")

    print("\nProduct Performance:")
    for product in product_performance[:3]:
        print(f"  {product['product_name']}: {product['total_quantity_sold']} units, "
              f"${product['total_revenue']:.2f} revenue")

    print("\nMonthly Cohorts:")
    for month in monthly_cohorts:
        print(f"  {month['_id']}: {month['unique_customers']} customers, "
              f"${month['total_revenue']:.2f} revenue")

    return customer_ltv, product_performance, monthly_cohorts

# Execute advanced examples
advanced_results = advanced_patterns()
```

## Performance Optimization

### Aggregation Performance Tips

```python
def aggregation_performance():
    """Aggregation performance optimization techniques"""

    # Index usage in aggregation
    def optimize_with_indexes():
        """Optimize aggregations with proper indexing"""

        # Create indexes for common aggregation patterns
        orders.create_index([("customer_id", 1), ("order_date", -1)])
        orders.create_index([("status", 1), ("total", -1)])
        orders.create_index("order_date")

        print("✅ Indexes created for aggregation optimization")

    # Early filtering with $match
    def early_filtering_example():
        """Use $match early in pipeline to reduce document count"""

        import time

        # Bad: Filter late in pipeline
        start_time = time.time()
        bad_pipeline = list(orders.aggregate([
            {"$lookup": {
                "from": "customers",
                "localField": "customer_id",
                "foreignField": "_id",
                "as": "customer"
            }},
            {"$unwind": "$customer"},
            {"$group": {
                "_id": "$customer_id",
                "total_spent": {"$sum": "$total"}
            }},
            {"$match": {"total_spent": {"$gte": 100}}}  # Filter after expensive operations
        ]))
        bad_time = time.time() - start_time

        # Good: Filter early
        start_time = time.time()
        good_pipeline = list(orders.aggregate([
            {"$match": {"status": "completed"}},  # Filter early
            {"$lookup": {
                "from": "customers",
                "localField": "customer_id",
                "foreignField": "_id",
                "as": "customer"
            }},
            {"$unwind": "$customer"},
            {"$group": {
                "_id": "$customer_id",
                "total_spent": {"$sum": "$total"}
            }},
            {"$match": {"total_spent": {"$gte": 100}}}
        ]))
        good_time = time.time() - start_time

        print(f"Bad pipeline time: {bad_time:.3f}s")
        print(f"Good pipeline time: {good_time:.3f}s")
        print(f"Improvement: {bad_time / good_time:.1f}x faster")

        return good_pipeline

    # Projection optimization
    def projection_optimization():
        """Use projection to reduce data transfer"""

        # Project only needed fields early
        optimized_pipeline = list(orders.aggregate([
            {"$match": {"status": "completed"}},
            {"$project": {  # Project early to reduce data size
                "customer_id": 1,
                "total": 1,
                "order_date": 1
            }},
            {"$group": {
                "_id": "$customer_id",
                "total_spent": {"$sum": "$total"},
                "order_count": {"$sum": 1},
                "latest_order": {"$max": "$order_date"}
            }}
        ]))

        return optimized_pipeline

    # Pipeline stage ordering
    def stage_ordering_tips():
        """Tips for optimal pipeline stage ordering"""

        print("=== Pipeline Stage Ordering Tips ===")
        print("1. $match - Filter early to reduce document count")
        print("2. $project - Remove unnecessary fields early")
        print("3. $sort - Place before $group when possible")
        print("4. $limit - Use after $sort to limit results")
        print("5. $lookup - Place as late as possible")
        print("6. $unwind - Use sparingly, can multiply document count")

    # Memory usage optimization
    def memory_optimization():
        """Techniques to reduce memory usage"""

        # Use allowDiskUse for large datasets
        large_aggregation = orders.aggregate([
            {"$match": {"status": "completed"}},
            {"$group": {
                "_id": "$customer_id",
                "orders": {"$push": "$$ROOT"}  # This could use lots of memory
            }},
            {"$sort": {"_id": 1}}
        ], allowDiskUse=True)  # Allow spilling to disk

        print("✅ Large aggregation configured with allowDiskUse")

        # Alternative: Process in smaller chunks
        def process_in_chunks():
            """Process large datasets in chunks"""

            # Get unique customer IDs first
            customer_ids = orders.distinct("customer_id")

            results = []
            chunk_size = 100

            for i in range(0, len(customer_ids), chunk_size):
                chunk_ids = customer_ids[i:i + chunk_size]

                chunk_result = list(orders.aggregate([
                    {"$match": {"customer_id": {"$in": chunk_ids}}},
                    {"$group": {
                        "_id": "$customer_id",
                        "total_spent": {"$sum": "$total"}
                    }}
                ]))

                results.extend(chunk_result)

            return results

        return process_in_chunks

    # Execute optimization examples
    optimize_with_indexes()
    good_pipeline = early_filtering_example()
    optimized = projection_optimization()
    stage_ordering_tips()
    chunk_processor = memory_optimization()

    return good_pipeline, optimized, chunk_processor

# Execute performance examples
performance_results = aggregation_performance()
```

## Best Practices

### Aggregation Best Practices

```python
def aggregation_best_practices():
    """Best practices for aggregation pipelines"""

    print("=== Aggregation Best Practices ===")

    # 1. Pipeline Design
    print("\n1. Pipeline Design:")
    print("   ✅ Filter early with $match")
    print("   ✅ Project unnecessary fields out early")
    print("   ✅ Use indexes effectively")
    print("   ✅ Limit results when possible")
    print("   ❌ Avoid unnecessary $unwind operations")
    print("   ❌ Don't use $lookup for large collections without filtering")

    # 2. Performance considerations
    def performance_considerations():
        """Performance best practices"""

        # Good pipeline structure
        good_pipeline = [
            {"$match": {"status": "active"}},  # Filter first
            {"$project": {"unnecessary_field": 0}},  # Remove large fields
            {"$sort": {"created_date": -1}},  # Sort before group when possible
            {"$limit": 1000},  # Limit early
            {"$lookup": {  # Lookup last
                "from": "other_collection",
                "localField": "ref_id",
                "foreignField": "_id",
                "as": "related_data"
            }}
        ]

        print("\n2. Performance Considerations:")
        print("   ✅ Create appropriate indexes")
        print("   ✅ Use allowDiskUse for large operations")
        print("   ✅ Monitor pipeline execution with explain()")
        print("   ✅ Consider using $facet for multiple aggregations")

        return good_pipeline

    # 3. Error handling
    def error_handling_in_aggregation():
        """Error handling best practices"""

        def safe_aggregation(collection, pipeline):
            """Safely execute aggregation with error handling"""

            try:
                # Validate pipeline stages
                if not isinstance(pipeline, list):
                    raise ValueError("Pipeline must be a list")

                # Execute with timeout
                cursor = collection.aggregate(
                    pipeline,
                    maxTimeMS=30000,  # 30 second timeout
                    allowDiskUse=True
                )

                # Convert to list (be careful with large results)
                results = list(cursor)

                print(f"✅ Aggregation completed: {len(results)} results")
                return results

            except Exception as e:
                print(f"❌ Aggregation failed: {e}")
                return []

        print("\n3. Error Handling:")
        print("   ✅ Use maxTimeMS for query timeouts")
        print("   ✅ Validate pipeline structure")
        print("   ✅ Handle memory limitations")
        print("   ✅ Use try-catch for robust error handling")

        return safe_aggregation

    # 4. Testing and debugging
    def testing_debugging():
        """Testing and debugging aggregation pipelines"""

        def debug_pipeline(collection, pipeline):
            """Debug aggregation pipeline step by step"""

            print("=== Pipeline Debug ===")

            for i, stage in enumerate(pipeline):
                # Execute pipeline up to current stage
                partial_pipeline = pipeline[:i+1]

                try:
                    result = list(collection.aggregate(partial_pipeline).limit(1))
                    stage_name = list(stage.keys())[0]

                    print(f"Stage {i+1} ({stage_name}): "
                          f"{'✅ Success' if result else '⚠ No results'}")

                    if result:
                        print(f"   Sample result: {json.dumps(result[0], default=str, indent=2)[:200]}...")

                except Exception as e:
                    print(f"Stage {i+1}: ❌ Error - {e}")
                    break

        print("\n4. Testing and Debugging:")
        print("   ✅ Test pipeline stages incrementally")
        print("   ✅ Use explain() to analyze performance")
        print("   ✅ Validate with small datasets first")
        print("   ✅ Monitor memory and execution time")

        return debug_pipeline

    # Execute best practices examples
    good_pipeline = performance_considerations()
    safe_aggregation = error_handling_in_aggregation()
    debug_pipeline = testing_debugging()

    return {
        "good_pipeline": good_pipeline,
        "safe_aggregation": safe_aggregation,
        "debug_pipeline": debug_pipeline
    }

# Execute best practices
best_practices_results = aggregation_best_practices()
```

## Real-World Examples

### Complete Business Intelligence Dashboard

```python
def business_intelligence_example():
    """Complete business intelligence aggregation example"""

    # Sales dashboard aggregation
    sales_dashboard = list(orders.aggregate([
        # Date range filter (last 30 days)
        {"$match": {
            "order_date": {"$gte": datetime.utcnow() - timedelta(days=30)},
            "status": "completed"
        }},

        # Create multiple metrics in parallel using $facet
        {"$facet": {
            # Daily sales trend
            "daily_sales": [
                {"$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$order_date"
                        }
                    },
                    "daily_revenue": {"$sum": "$total"},
                    "daily_orders": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ],

            # Top customers
            "top_customers": [
                {"$group": {
                    "_id": "$customer_id",
                    "total_spent": {"$sum": "$total"},
                    "order_count": {"$sum": 1}
                }},
                {"$sort": {"total_spent": -1}},
                {"$limit": 10},
                {"$lookup": {
                    "from": "customers",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "customer_info"
                }},
                {"$unwind": "$customer_info"},
                {"$project": {
                    "customer_name": "$customer_info.name",
                    "total_spent": 1,
                    "order_count": 1
                }}
            ],

            # Product performance
            "product_performance": [
                {"$unwind": "$items"},
                {"$group": {
                    "_id": "$items.product_id",
                    "quantity_sold": {"$sum": "$items.quantity"},
                    "revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
                }},
                {"$sort": {"revenue": -1}},
                {"$limit": 10},
                {"$lookup": {
                    "from": "products",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "product_info"
                }},
                {"$unwind": "$product_info"},
                {"$project": {
                    "product_name": "$product_info.name",
                    "category": "$product_info.category",
                    "quantity_sold": 1,
                    "revenue": 1
                }}
            ],

            # Geographic distribution
            "geographic_sales": [
                {"$group": {
                    "_id": "$shipping_address.country",
                    "revenue": {"$sum": "$total"},
                    "order_count": {"$sum": 1}
                }},
                {"$sort": {"revenue": -1}}
            ],

            # Overall metrics
            "summary_metrics": [
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$total"},
                    "total_orders": {"$sum": 1},
                    "avg_order_value": {"$avg": "$total"},
                    "unique_customers": {"$addToSet": "$customer_id"}
                }},
                {"$project": {
                    "total_revenue": 1,
                    "total_orders": 1,
                    "avg_order_value": 1,
                    "unique_customers": {"$size": "$unique_customers"}
                }}
            ]
        }}
    ]))

    # Extract dashboard data
    if sales_dashboard:
        dashboard_data = sales_dashboard[0]

        print("=== Sales Dashboard (Last 30 Days) ===")

        # Summary metrics
        summary = dashboard_data['summary_metrics'][0] if dashboard_data['summary_metrics'] else {}
        print(f"Total Revenue: ${summary.get('total_revenue', 0):,.2f}")
        print(f"Total Orders: {summary.get('total_orders', 0):,}")
        print(f"Average Order Value: ${summary.get('avg_order_value', 0):.2f}")
        print(f"Unique Customers: {summary.get('unique_customers', 0):,}")

        # Top customers
        print("\nTop Customers:")
        for customer in dashboard_data['top_customers'][:5]:
            print(f"  {customer['customer_name']}: ${customer['total_spent']:.2f} "
                  f"({customer['order_count']} orders)")

        # Top products
        print("\nTop Products:")
        for product in dashboard_data['product_performance'][:5]:
            print(f"  {product['product_name']}: {product['quantity_sold']} units, "
                  f"${product['revenue']:.2f}")

        # Geographic distribution
        print("\nSales by Country:")
        for geo in dashboard_data['geographic_sales']:
            print(f"  {geo['_id']}: ${geo['revenue']:.2f} ({geo['order_count']} orders)")

    return sales_dashboard

# Execute business intelligence example
bi_results = business_intelligence_example()
```

## Next Steps

After mastering the aggregation framework:

1. **Indexing Strategies**: [Indexing with PyMongo](./02_indexing.md)
2. **Performance Optimization**: [Performance Optimization](./07_performance_optimization.md)
3. **Real-World Applications**: [Complete Examples](../examples/)
4. **Advanced Patterns**: [Advanced Data Patterns](./05_advanced_patterns.md)

## Additional Resources

- [MongoDB Aggregation Framework Documentation](https://docs.mongodb.com/manual/aggregation/)
- [PyMongo Aggregation Examples](https://pymongo.readthedocs.io/en/stable/examples/aggregation.html)
- [Aggregation Pipeline Optimization](https://docs.mongodb.com/manual/core/aggregation-pipeline-optimization/)
- [Aggregation Framework Operators](https://docs.mongodb.com/manual/reference/operator/aggregation/)
