# PyMongo Data Modeling

This comprehensive guide covers MongoDB data modeling principles, patterns, and best practices using PyMongo, including schema design, relationships, and optimization strategies.

## Table of Contents

1. [Data Modeling Overview](#data-modeling-overview)
2. [Schema Design Principles](#schema-design-principles)
3. [Embedded vs Referenced Data](#embedded-vs-referenced-data)
4. [Relationship Patterns](#relationship-patterns)
5. [Schema Validation](#schema-validation)
6. [Common Modeling Patterns](#common-modeling-patterns)
7. [Performance Considerations](#performance-considerations)
8. [Migration and Evolution](#migration-and-evolution)
9. [Real-World Examples](#real-world-examples)
10. [Best Practices](#best-practices)

## Data Modeling Overview

MongoDB's flexible document model allows for rich data structures, but effective modeling requires understanding how your application will use the data.

### Document Structure Basics

```python
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.data_modeling_guide

def document_structure_examples():
    """Examples of different document structures"""

    # Simple flat document
    simple_user = {
        "_id": ObjectId(),
        "username": "john_doe",
        "email": "john@example.com",
        "age": 28,
        "created_at": datetime.utcnow()
    }

    # Nested document with embedded objects
    detailed_user = {
        "_id": ObjectId(),
        "username": "jane_smith",
        "email": "jane@example.com",
        "profile": {
            "first_name": "Jane",
            "last_name": "Smith",
            "age": 32,
            "bio": "Software engineer with 10 years experience",
            "location": {
                "city": "San Francisco",
                "state": "CA",
                "country": "USA",
                "coordinates": [-122.4194, 37.7749]
            }
        },
        "preferences": {
            "theme": "dark",
            "language": "en",
            "notifications": {
                "email": True,
                "push": False,
                "sms": True
            }
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Document with arrays
    user_with_arrays = {
        "_id": ObjectId(),
        "username": "developer_bob",
        "email": "bob@example.com",
        "skills": ["Python", "JavaScript", "MongoDB", "React"],
        "projects": [
            {
                "name": "E-commerce Platform",
                "role": "Backend Developer",
                "technologies": ["Python", "Django", "PostgreSQL"],
                "start_date": datetime(2023, 1, 15),
                "end_date": datetime(2023, 6, 30),
                "status": "completed"
            },
            {
                "name": "Data Analytics Tool",
                "role": "Full Stack Developer",
                "technologies": ["Python", "React", "MongoDB"],
                "start_date": datetime(2023, 7, 1),
                "end_date": None,
                "status": "in_progress"
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "Tech University",
                "year": 2018
            }
        ],
        "contact_methods": [
            {"type": "email", "value": "bob@example.com", "primary": True},
            {"type": "phone", "value": "+1-555-0123", "primary": False},
            {"type": "linkedin", "value": "linkedin.com/in/devbob", "primary": False}
        ]
    }

    return simple_user, detailed_user, user_with_arrays

# Example usage
simple, detailed, with_arrays = document_structure_examples()
```

### BSON Data Types and Usage

```python
def bson_data_types_examples():
    """Examples of different BSON data types in documents"""

    from bson import Binary, Code, Decimal128, Int64, Regex
    from bson.codec_options import CodecOptions
    from decimal import Decimal

    comprehensive_document = {
        # Basic types
        "_id": ObjectId(),
        "string_field": "Hello MongoDB",
        "integer_field": 42,
        "float_field": 3.14159,
        "boolean_field": True,
        "null_field": None,

        # Date and time
        "date_field": datetime.utcnow(),
        "timestamp_field": datetime.now(),

        # Binary data
        "binary_field": Binary(b"binary data example", 0),

        # Decimal for precise calculations
        "decimal_field": Decimal128(Decimal("123.456789")),

        # Large integers
        "long_field": Int64(9223372036854775807),

        # Regular expressions
        "regex_field": Regex("^[a-zA-Z0-9]+$", "i"),

        # JavaScript code
        "code_field": Code("function() { return this.value * 2; }"),

        # Arrays of mixed types
        "mixed_array": [
            "string",
            123,
            True,
            datetime.utcnow(),
            {"nested": "object"}
        ],

        # Nested documents
        "nested_document": {
            "level_1": {
                "level_2": {
                    "deep_value": "nested data"
                }
            }
        },

        # Array of documents
        "document_array": [
            {"name": "Item 1", "value": 100},
            {"name": "Item 2", "value": 200}
        ]
    }

    return comprehensive_document

# Example usage
comprehensive_doc = bson_data_types_examples()
```

## Schema Design Principles

### Designing for Your Application

```python
def schema_design_principles():
    """Demonstrate key schema design principles"""

    # Principle 1: Design for your application patterns
    def design_for_queries():
        """Design schema based on query patterns"""

        # Bad: Requires multiple queries and joins
        # users collection: {_id, username, email}
        # profiles collection: {_id, user_id, bio, location}
        # preferences collection: {_id, user_id, theme, language}

        # Good: Single document for common queries
        user_optimized = {
            "_id": ObjectId(),
            "username": "john_doe",
            "email": "john@example.com",
            "profile": {
                "bio": "Software engineer",
                "location": "San Francisco, CA"
            },
            "preferences": {
                "theme": "dark",
                "language": "en"
            },
            # Keep frequently accessed data together
            "last_login": datetime.utcnow(),
            "is_active": True,
            "created_at": datetime.utcnow()
        }

        return user_optimized

    # Principle 2: Consider data growth
    def design_for_growth():
        """Consider how data will grow over time"""

        # Bad: Unbounded arrays that grow indefinitely
        bad_design = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "all_page_views": [  # This could grow to millions of entries!
                {"page": "/home", "timestamp": datetime.utcnow()},
                {"page": "/products", "timestamp": datetime.utcnow()},
                # ... potentially millions more
            ]
        }

        # Good: Separate collection for high-volume data
        user_session = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "session_start": datetime.utcnow(),
            "session_end": None,
            "page_count": 0,
            "last_activity": datetime.utcnow()
        }

        page_view = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "session_id": ObjectId(),
            "page": "/products",
            "timestamp": datetime.utcnow(),
            "duration": 45.5  # seconds
        }

        return user_session, page_view

    # Principle 3: Balance embedding vs referencing
    def embedding_vs_referencing():
        """Balance between embedding and referencing"""

        # Embed when:
        # - Data is accessed together
        # - Data doesn't change often
        # - Related data is small

        blog_post_embedded = {
            "_id": ObjectId(),
            "title": "MongoDB Data Modeling",
            "content": "Long blog post content...",
            "author": {  # Embed author info (relatively static)
                "name": "John Doe",
                "bio": "MongoDB expert",
                "avatar_url": "https://example.com/avatar.jpg"
            },
            "tags": ["mongodb", "database", "nosql"],  # Embed tags (small, accessed together)
            "metadata": {
                "word_count": 1250,
                "reading_time": 5,
                "difficulty": "intermediate"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Reference when:
        # - Data is large
        # - Data changes frequently
        # - Need to avoid duplication

        blog_post_referenced = {
            "_id": ObjectId(),
            "title": "MongoDB Data Modeling",
            "content": "Long blog post content...",
            "author_id": ObjectId(),  # Reference to user collection
            "category_id": ObjectId(),  # Reference to category collection
            "comments": [  # Reference to comments (could be many)
                ObjectId("comment_1"),
                ObjectId("comment_2")
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        return blog_post_embedded, blog_post_referenced

    optimized_user = design_for_queries()
    session_design = design_for_growth()
    embedding_example = embedding_vs_referencing()

    return optimized_user, session_design, embedding_example

# Example usage
design_examples = schema_design_principles()
```

### Document Size Considerations

```python
def document_size_considerations():
    """Understand document size limits and optimization"""

    def calculate_document_size():
        """Calculate and optimize document size"""

        import sys
        import bson

        # Large document example
        large_document = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "large_text_field": "A" * 1000000,  # 1MB of text
            "large_array": [{"item": i, "data": "x" * 1000} for i in range(1000)],
            "created_at": datetime.utcnow()
        }

        # Calculate BSON size
        bson_size = len(bson.encode(large_document))
        print(f"Large document BSON size: {bson_size:,} bytes ({bson_size / (1024*1024):.2f} MB)")

        # Optimized version
        optimized_document = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "summary": "Document summary",  # Keep only essential data
            "metadata": {
                "item_count": 1000,
                "total_size": bson_size,
                "external_data_ref": "file_storage_id_12345"  # Reference to external storage
            },
            "created_at": datetime.utcnow()
        }

        optimized_size = len(bson.encode(optimized_document))
        print(f"Optimized document BSON size: {optimized_size:,} bytes")

        return large_document, optimized_document

    def document_size_best_practices():
        """Best practices for document size management"""

        # Keep documents under 16MB (MongoDB limit)
        # Aim for documents under 1MB for best performance

        # Strategy 1: Pagination within documents
        paginated_comments = {
            "_id": ObjectId(),
            "post_id": ObjectId(),
            "page": 1,
            "total_pages": 5,
            "comments": [
                {
                    "author": "user1",
                    "text": "Great post!",
                    "timestamp": datetime.utcnow()
                }
                # ... up to 50 comments per page
            ],
            "created_at": datetime.utcnow()
        }

        # Strategy 2: Separate large fields
        post_metadata = {
            "_id": ObjectId(),
            "title": "My Blog Post",
            "author_id": ObjectId(),
            "summary": "Post summary",
            "word_count": 2500,
            "content_ref": ObjectId(),  # References full content document
            "created_at": datetime.utcnow()
        }

        post_content = {
            "_id": ObjectId(),  # Same as content_ref above
            "full_content": "Very long blog post content...",
            "formatted_content": "<html>...</html>",
            "raw_markdown": "# Title\n\nContent..."
        }

        return paginated_comments, post_metadata, post_content

    large_doc, optimized_doc = calculate_document_size()
    best_practices_examples = document_size_best_practices()

    return large_doc, optimized_doc, best_practices_examples

# Example usage
size_examples = document_size_considerations()
```

## Embedded vs Referenced Data

### When to Embed

```python
def when_to_embed():
    """Examples of when embedding is appropriate"""

    # 1. One-to-one relationships (user profile)
    user_with_profile = {
        "_id": ObjectId(),
        "username": "john_doe",
        "email": "john@example.com",
        "profile": {  # Embed profile (1:1, accessed together)
            "first_name": "John",
            "last_name": "Doe",
            "age": 28,
            "bio": "Software developer",
            "avatar_url": "https://example.com/avatar.jpg",
            "social_links": {
                "linkedin": "linkedin.com/in/johndoe",
                "github": "github.com/johndoe",
                "twitter": "@johndoe"
            }
        },
        "created_at": datetime.utcnow()
    }

    # 2. One-to-few relationships (contact methods)
    user_with_contacts = {
        "_id": ObjectId(),
        "username": "jane_smith",
        "email": "jane@example.com",
        "contact_methods": [  # Embed contact methods (few, accessed together)
            {
                "type": "email",
                "value": "jane@example.com",
                "primary": True,
                "verified": True
            },
            {
                "type": "phone",
                "value": "+1-555-0123",
                "primary": False,
                "verified": False
            },
            {
                "type": "slack",
                "value": "@jane.smith",
                "primary": False,
                "verified": True
            }
        ]
    }

    # 3. Configuration and settings
    application_config = {
        "_id": ObjectId(),
        "app_name": "My Application",
        "version": "1.2.3",
        "settings": {  # Embed settings (accessed together, small)
            "database": {
                "host": "localhost",
                "port": 27017,
                "name": "myapp"
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            },
            "email": {
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "use_tls": True
            }
        },
        "feature_flags": {  # Embed feature flags (small, accessed frequently)
            "new_ui": True,
            "beta_features": False,
            "analytics": True
        }
    }

    # 4. Address information
    customer_with_address = {
        "_id": ObjectId(),
        "customer_id": "CUST_12345",
        "name": "Acme Corporation",
        "billing_address": {  # Embed billing address
            "street": "123 Business St",
            "suite": "Suite 100",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94105",
            "country": "USA"
        },
        "shipping_address": {  # Embed shipping address
            "street": "456 Warehouse Ave",
            "city": "Oakland",
            "state": "CA",
            "zip": "94607",
            "country": "USA"
        }
    }

    return user_with_profile, user_with_contacts, application_config, customer_with_address

# Example usage
embedding_examples = when_to_embed()
```

### When to Reference

```python
def when_to_reference():
    """Examples of when referencing is appropriate"""

    # 1. One-to-many with many being large
    def blog_system():
        """Blog system with referenced comments"""

        # Blog post document
        blog_post = {
            "_id": ObjectId(),
            "title": "Understanding MongoDB References",
            "slug": "understanding-mongodb-references",
            "author_id": ObjectId(),  # Reference to user
            "content": "Long blog post content...",
            "tags": ["mongodb", "database", "references"],
            "comment_count": 150,  # Denormalized count for performance
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Comments in separate collection (could be thousands)
        comment = {
            "_id": ObjectId(),
            "post_id": blog_post["_id"],  # Reference to blog post
            "author_id": ObjectId(),  # Reference to user
            "content": "Great explanation of references!",
            "likes": 15,
            "reply_to": None,  # Reference to parent comment (for threading)
            "created_at": datetime.utcnow()
        }

        return blog_post, comment

    # 2. Many-to-many relationships
    def course_enrollment_system():
        """Course enrollment with many-to-many relationships"""

        # Student document
        student = {
            "_id": ObjectId(),
            "student_id": "STU_12345",
            "name": "Alice Johnson",
            "email": "alice@university.edu",
            "major": "Computer Science",
            "year": 3,
            "gpa": 3.75
        }

        # Course document
        course = {
            "_id": ObjectId(),
            "course_code": "CS101",
            "title": "Introduction to Computer Science",
            "credits": 3,
            "instructor_id": ObjectId(),  # Reference to instructor
            "max_enrollment": 50,
            "current_enrollment": 35
        }

        # Enrollment (junction document)
        enrollment = {
            "_id": ObjectId(),
            "student_id": student["_id"],  # Reference to student
            "course_id": course["_id"],  # Reference to course
            "semester": "Fall 2023",
            "grade": None,  # Will be updated later
            "enrollment_date": datetime.utcnow(),
            "status": "enrolled"
        }

        return student, course, enrollment

    # 3. Frequently changing data
    def product_inventory_system():
        """Product system with separate inventory tracking"""

        # Product document (relatively static)
        product = {
            "_id": ObjectId(),
            "sku": "LAPTOP_001",
            "name": "Gaming Laptop Pro",
            "description": "High-performance gaming laptop",
            "category": "Electronics",
            "brand": "TechBrand",
            "specifications": {
                "cpu": "Intel i7-12700H",
                "ram": "32GB DDR4",
                "storage": "1TB NVMe SSD",
                "gpu": "RTX 3070"
            },
            "created_at": datetime.utcnow()
        }

        # Inventory document (frequently updated)
        inventory = {
            "_id": ObjectId(),
            "product_id": product["_id"],  # Reference to product
            "warehouse_id": ObjectId(),
            "quantity_available": 15,
            "quantity_reserved": 3,
            "reorder_point": 5,
            "last_restocked": datetime(2023, 10, 15),
            "updated_at": datetime.utcnow()
        }

        # Price history (separate for tracking changes)
        price_history = {
            "_id": ObjectId(),
            "product_id": product["_id"],  # Reference to product
            "price": 1299.99,
            "currency": "USD",
            "effective_date": datetime.utcnow(),
            "reason": "seasonal_discount"
        }

        return product, inventory, price_history

    # 4. Shared data across multiple documents
    def user_role_system():
        """User role system with referenced roles"""

        # Role document (shared across many users)
        role = {
            "_id": ObjectId(),
            "name": "admin",
            "display_name": "Administrator",
            "permissions": [
                "user.create",
                "user.read",
                "user.update",
                "user.delete",
                "system.configure",
                "reports.view"
            ],
            "created_at": datetime.utcnow()
        }

        # User document with role reference
        user = {
            "_id": ObjectId(),
            "username": "admin_user",
            "email": "admin@company.com",
            "role_ids": [role["_id"]],  # Array of role references
            "department": "IT",
            "created_at": datetime.utcnow()
        }

        return role, user

    # Execute examples
    blog_examples = blog_system()
    course_examples = course_enrollment_system()
    inventory_examples = product_inventory_system()
    role_examples = user_role_system()

    return {
        "blog": blog_examples,
        "course": course_examples,
        "inventory": inventory_examples,
        "roles": role_examples
    }

# Example usage
reference_examples = when_to_reference()
```

### Hybrid Approaches

```python
def hybrid_approaches():
    """Examples of combining embedding and referencing"""

    # 1. Embedding with selective referencing
    def social_media_post():
        """Social media post with hybrid approach"""

        post = {
            "_id": ObjectId(),
            "author": {  # Embed author summary (for display)
                "user_id": ObjectId(),
                "username": "john_doe",
                "display_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "verified": True
            },
            "content": "Just learned about MongoDB data modeling! #mongodb #database",
            "media": [
                {
                    "type": "image",
                    "url": "https://example.com/image.jpg",
                    "alt_text": "MongoDB logo"
                }
            ],
            "hashtags": ["mongodb", "database"],
            "mentions": [
                {
                    "user_id": ObjectId(),
                    "username": "mongodb_official",
                    "display_name": "MongoDB"
                }
            ],
            "stats": {  # Embed for quick access
                "likes": 42,
                "shares": 8,
                "comments": 15
            },
            "engagement_summary": {
                "recent_likes": [  # Embed recent engagement (limited)
                    {
                        "user_id": ObjectId(),
                        "username": "friend1",
                        "timestamp": datetime.utcnow()
                    }
                ],
                "total_engagement": 65
            },
            "created_at": datetime.utcnow()
        }

        # Detailed engagement in separate collection
        engagement = {
            "_id": ObjectId(),
            "post_id": post["_id"],
            "user_id": ObjectId(),
            "type": "like",  # like, share, comment
            "timestamp": datetime.utcnow()
        }

        return post, engagement

    # 2. Denormalization with references
    def order_system():
        """Order system with denormalized data and references"""

        order = {
            "_id": ObjectId(),
            "order_number": "ORD_20231015_001",
            "customer": {  # Embed customer summary (snapshot at order time)
                "customer_id": ObjectId(),
                "name": "Jane Smith",
                "email": "jane@example.com",
                "membership_level": "gold"
            },
            "items": [
                {
                    "product_id": ObjectId(),  # Reference for detailed product info
                    "sku": "LAPTOP_001",
                    "name": "Gaming Laptop",  # Denormalized for quick access
                    "price": 1299.99,  # Price at time of order
                    "quantity": 1,
                    "total": 1299.99
                }
            ],
            "shipping_address": {  # Embed address (snapshot)
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94105",
                "country": "USA"
            },
            "payment": {
                "method": "credit_card",
                "last_four": "1234",
                "transaction_id": "TXN_123456"
            },
            "totals": {
                "subtotal": 1299.99,
                "tax": 104.00,
                "shipping": 15.99,
                "total": 1419.98
            },
            "status": "processing",
            "order_date": datetime.utcnow(),
            "estimated_delivery": datetime.utcnow() + timedelta(days=3)
        }

        return order

    # 3. Cached references
    def user_activity_feed():
        """Activity feed with cached user data"""

        activity = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "type": "post_created",
            "target_type": "blog_post",
            "target_id": ObjectId(),
            "user_snapshot": {  # Cached user data for feed display
                "username": "content_creator",
                "display_name": "Content Creator",
                "avatar_url": "https://example.com/avatar.jpg",
                "cached_at": datetime.utcnow()
            },
            "content_preview": {  # Cached content for quick display
                "title": "My Latest Blog Post",
                "excerpt": "This is an excerpt of the blog post...",
                "image_url": "https://example.com/preview.jpg"
            },
            "metadata": {
                "visibility": "public",
                "engagement_count": 0
            },
            "created_at": datetime.utcnow()
        }

        return activity

    # Execute examples
    social_examples = social_media_post()
    order_example = order_system()
    activity_example = user_activity_feed()

    return {
        "social": social_examples,
        "order": order_example,
        "activity": activity_example
    }

# Example usage
hybrid_examples = hybrid_approaches()
```

## Relationship Patterns

### One-to-One Relationships

```python
def one_to_one_patterns():
    """Examples of one-to-one relationship patterns"""

    # Pattern 1: Embedded document (most common)
    user_with_profile_embedded = {
        "_id": ObjectId(),
        "username": "john_doe",
        "email": "john@example.com",
        "profile": {  # 1:1 embedded
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": datetime(1990, 5, 15),
            "bio": "Software engineer passionate about databases",
            "location": "San Francisco, CA",
            "website": "https://johndoe.dev"
        },
        "preferences": {  # 1:1 embedded
            "theme": "dark",
            "language": "en",
            "timezone": "America/Los_Angeles",
            "notifications": {
                "email": True,
                "push": False,
                "sms": True
            }
        },
        "created_at": datetime.utcnow()
    }

    # Pattern 2: Referenced document (when profile is large or sensitive)
    user_with_profile_referenced = {
        "_id": ObjectId(),
        "username": "jane_doe",
        "email": "jane@example.com",
        "profile_id": ObjectId(),  # Reference to profile document
        "status": "active",
        "created_at": datetime.utcnow()
    }

    user_profile_document = {
        "_id": ObjectId(),  # Same as profile_id above
        "user_id": ObjectId(),  # Back-reference (optional)
        "personal_info": {
            "full_name": "Jane Doe",
            "date_of_birth": datetime(1985, 3, 20),
            "ssn": "***-**-1234",  # Sensitive data
            "emergency_contact": {
                "name": "John Doe",
                "phone": "+1-555-0123",
                "relationship": "spouse"
            }
        },
        "professional_info": {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "experience_years": 10,
            "resume_url": "https://storage.example.com/resumes/jane_doe.pdf"
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    return user_with_profile_embedded, user_with_profile_referenced, user_profile_document

# Example usage
one_to_one_examples = one_to_one_patterns()
```

### One-to-Many Relationships

```python
def one_to_many_patterns():
    """Examples of one-to-many relationship patterns"""

    # Pattern 1: Embedded documents (for small, bounded sets)
    blog_post_with_embedded_comments = {
        "_id": ObjectId(),
        "title": "Understanding MongoDB Relationships",
        "author_id": ObjectId(),
        "content": "Blog post content...",
        "comments": [  # Embed comments (if limited in number)
            {
                "comment_id": ObjectId(),
                "author": "commenter1",
                "content": "Great post!",
                "created_at": datetime.utcnow(),
                "likes": 5
            },
            {
                "comment_id": ObjectId(),
                "author": "commenter2",
                "content": "Very informative.",
                "created_at": datetime.utcnow(),
                "likes": 3
            }
        ],
        "tags": ["mongodb", "database", "relationships"],  # Embedded array
        "created_at": datetime.utcnow()
    }

    # Pattern 2: Referenced documents (for large or unbounded sets)
    blog_post_with_referenced_comments = {
        "_id": ObjectId(),
        "title": "Advanced MongoDB Patterns",
        "author_id": ObjectId(),
        "content": "Blog post content...",
        "comment_count": 150,  # Denormalized count
        "latest_comments": [  # Cache recent comments for quick display
            {
                "comment_id": ObjectId(),
                "author": "recent_commenter",
                "content": "Latest comment...",
                "created_at": datetime.utcnow()
            }
        ],
        "created_at": datetime.utcnow()
    }

    # Comments in separate collection
    comment_document = {
        "_id": ObjectId(),
        "post_id": blog_post_with_referenced_comments["_id"],  # Parent reference
        "author_id": ObjectId(),
        "content": "This is a detailed comment with lots of text...",
        "replies": [  # Nested comments
            {
                "reply_id": ObjectId(),
                "author_id": ObjectId(),
                "content": "Reply to the comment",
                "created_at": datetime.utcnow()
            }
        ],
        "likes": 25,
        "created_at": datetime.utcnow()
    }

    # Pattern 3: Array of references (parent holds references to children)
    user_with_order_references = {
        "_id": ObjectId(),
        "username": "customer123",
        "email": "customer@example.com",
        "order_ids": [  # Array of order references
            ObjectId("order1"),
            ObjectId("order2"),
            ObjectId("order3")
        ],
        "order_count": 3,  # Denormalized count
        "last_order_date": datetime.utcnow()
    }

    order_document = {
        "_id": ObjectId("order1"),
        "customer_id": user_with_order_references["_id"],  # Back-reference
        "order_number": "ORD_001",
        "items": [
            {
                "product_id": ObjectId(),
                "quantity": 2,
                "price": 29.99
            }
        ],
        "total": 59.98,
        "status": "shipped",
        "created_at": datetime.utcnow()
    }

    return (blog_post_with_embedded_comments,
            blog_post_with_referenced_comments,
            comment_document,
            user_with_order_references,
            order_document)

# Example usage
one_to_many_examples = one_to_many_patterns()
```

### Many-to-Many Relationships

```python
def many_to_many_patterns():
    """Examples of many-to-many relationship patterns"""

    # Pattern 1: Array of references (simple many-to-many)
    def simple_many_to_many():
        """Simple many-to-many with arrays of references"""

        # User with skills
        user = {
            "_id": ObjectId(),
            "username": "developer123",
            "email": "dev@example.com",
            "skill_ids": [  # Array of skill references
                ObjectId("skill_python"),
                ObjectId("skill_mongodb"),
                ObjectId("skill_react")
            ]
        }

        # Skill document
        skill = {
            "_id": ObjectId("skill_python"),
            "name": "Python",
            "category": "Programming Language",
            "description": "High-level programming language",
            "user_ids": [  # Back-references to users with this skill
                user["_id"],
                ObjectId("other_user_1"),
                ObjectId("other_user_2")
            ],
            "user_count": 3  # Denormalized count
        }

        return user, skill

    # Pattern 2: Junction collection (complex many-to-many)
    def complex_many_to_many():
        """Complex many-to-many with junction collection"""

        # Student document
        student = {
            "_id": ObjectId(),
            "student_id": "STU_12345",
            "name": "Alice Johnson",
            "email": "alice@university.edu",
            "major": "Computer Science",
            "enrollment_count": 4
        }

        # Course document
        course = {
            "_id": ObjectId(),
            "course_code": "CS101",
            "title": "Introduction to Computer Science",
            "credits": 3,
            "instructor_id": ObjectId(),
            "enrollment_count": 25
        }

        # Enrollment junction document
        enrollment = {
            "_id": ObjectId(),
            "student_id": student["_id"],
            "course_id": course["_id"],
            "semester": "Fall 2023",
            "grade": "A",
            "enrollment_date": datetime(2023, 8, 15),
            "completion_date": datetime(2023, 12, 15),
            "credits_earned": 3,
            "status": "completed",
            "metadata": {
                "attendance_rate": 0.95,
                "participation_score": 8.5,
                "final_project_score": 92
            }
        }

        return student, course, enrollment

    # Pattern 3: Embedded junction data
    def embedded_many_to_many():
        """Many-to-many with embedded junction data"""

        # Project with team members
        project = {
            "_id": ObjectId(),
            "name": "E-commerce Platform",
            "description": "Building a modern e-commerce platform",
            "team_members": [  # Embedded junction data
                {
                    "user_id": ObjectId(),
                    "username": "project_lead",
                    "role": "Project Manager",
                    "join_date": datetime(2023, 1, 1),
                    "permissions": ["admin", "write", "read"],
                    "contribution_hours": 320
                },
                {
                    "user_id": ObjectId(),
                    "username": "backend_dev",
                    "role": "Backend Developer",
                    "join_date": datetime(2023, 1, 15),
                    "permissions": ["write", "read"],
                    "contribution_hours": 280
                },
                {
                    "user_id": ObjectId(),
                    "username": "frontend_dev",
                    "role": "Frontend Developer",
                    "join_date": datetime(2023, 2, 1),
                    "permissions": ["write", "read"],
                    "contribution_hours": 260
                }
            ],
            "status": "in_progress",
            "created_at": datetime(2023, 1, 1),
            "deadline": datetime(2023, 12, 31)
        }

        # User document with project references
        user = {
            "_id": ObjectId(),
            "username": "project_lead",
            "email": "lead@company.com",
            "current_projects": [  # Simple references to projects
                {
                    "project_id": project["_id"],
                    "role": "Project Manager",
                    "status": "active"
                }
            ],
            "total_projects": 15,
            "total_hours": 2400
        }

        return project, user

    # Execute patterns
    simple_user, simple_skill = simple_many_to_many()
    complex_student, complex_course, complex_enrollment = complex_many_to_many()
    embedded_project, embedded_user = embedded_many_to_many()

    return {
        "simple": (simple_user, simple_skill),
        "complex": (complex_student, complex_course, complex_enrollment),
        "embedded": (embedded_project, embedded_user)
    }

# Example usage
many_to_many_examples = many_to_many_patterns()
```

## Schema Validation

### Document Validation with PyMongo

```python
def schema_validation_examples():
    """Examples of schema validation in PyMongo"""

    # Create collections with validation
    def create_validated_collections():
        """Create collections with schema validation"""

        # User collection validation
        user_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["username", "email", "created_at"],
                "properties": {
                    "username": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9_]{3,20}$",
                        "description": "Username must be 3-20 characters, alphanumeric and underscore only"
                    },
                    "email": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                        "description": "Must be a valid email address"
                    },
                    "age": {
                        "bsonType": "int",
                        "minimum": 13,
                        "maximum": 120,
                        "description": "Age must be between 13 and 120"
                    },
                    "profile": {
                        "bsonType": "object",
                        "properties": {
                            "first_name": {"bsonType": "string", "maxLength": 50},
                            "last_name": {"bsonType": "string", "maxLength": 50},
                            "bio": {"bsonType": "string", "maxLength": 500}
                        }
                    },
                    "preferences": {
                        "bsonType": "object",
                        "properties": {
                            "theme": {"enum": ["light", "dark", "auto"]},
                            "language": {"bsonType": "string", "pattern": "^[a-z]{2}$"},
                            "notifications": {
                                "bsonType": "object",
                                "properties": {
                                    "email": {"bsonType": "bool"},
                                    "push": {"bsonType": "bool"},
                                    "sms": {"bsonType": "bool"}
                                }
                            }
                        }
                    },
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }

        # Create collection with validation
        try:
            db.create_collection(
                "validated_users",
                validator=user_validator,
                validationLevel="strict",  # strict, moderate
                validationAction="error"   # error, warn
            )
            print("✅ User collection created with validation")
        except Exception as e:
            print(f"User collection validation: {e}")

        # Product collection validation
        product_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "price", "category", "active"],
                "properties": {
                    "name": {
                        "bsonType": "string",
                        "minLength": 1,
                        "maxLength": 200
                    },
                    "price": {
                        "bsonType": "number",
                        "minimum": 0,
                        "description": "Price must be a positive number"
                    },
                    "category": {
                        "enum": ["Electronics", "Clothing", "Books", "Home", "Sports", "Other"]
                    },
                    "tags": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "maxItems": 10
                    },
                    "specifications": {
                        "bsonType": "object",
                        "description": "Product specifications can be any object"
                    },
                    "active": {"bsonType": "bool"},
                    "stock": {
                        "bsonType": "int",
                        "minimum": 0
                    },
                    "rating": {
                        "bsonType": "number",
                        "minimum": 0,
                        "maximum": 5
                    }
                }
            }
        }

        try:
            db.create_collection(
                "validated_products",
                validator=product_validator,
                validationLevel="strict",
                validationAction="error"
            )
            print("✅ Product collection created with validation")
        except Exception as e:
            print(f"Product collection validation: {e}")

    # Test validation
    def test_validation():
        """Test schema validation with valid and invalid documents"""

        users_collection = db.validated_users
        products_collection = db.validated_products

        # Valid user document
        valid_user = {
            "username": "john_doe",
            "email": "john@example.com",
            "age": 28,
            "profile": {
                "first_name": "John",
                "last_name": "Doe",
                "bio": "Software engineer"
            },
            "preferences": {
                "theme": "dark",
                "language": "en",
                "notifications": {
                    "email": True,
                    "push": False,
                    "sms": True
                }
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        try:
            result = users_collection.insert_one(valid_user)
            print(f"✅ Valid user inserted: {result.inserted_id}")
        except Exception as e:
            print(f"❌ Valid user insertion failed: {e}")

        # Invalid user document (missing required field)
        invalid_user = {
            "username": "jane_doe",
            # Missing required email field
            "age": 25,
            "created_at": datetime.utcnow()
        }

        try:
            result = users_collection.insert_one(invalid_user)
            print(f"❌ Invalid user should not have been inserted: {result.inserted_id}")
        except Exception as e:
            print(f"✅ Invalid user correctly rejected: {e}")

        # Valid product document
        valid_product = {
            "name": "Laptop Pro",
            "price": 1299.99,
            "category": "Electronics",
            "tags": ["laptop", "computer", "portable"],
            "specifications": {
                "cpu": "Intel i7",
                "ram": "16GB",
                "storage": "512GB SSD"
            },
            "active": True,
            "stock": 10,
            "rating": 4.5
        }

        try:
            result = products_collection.insert_one(valid_product)
            print(f"✅ Valid product inserted: {result.inserted_id}")
        except Exception as e:
            print(f"❌ Valid product insertion failed: {e}")

        # Invalid product document (invalid category)
        invalid_product = {
            "name": "Invalid Product",
            "price": 99.99,
            "category": "InvalidCategory",  # Not in enum
            "active": True
        }

        try:
            result = products_collection.insert_one(invalid_product)
            print(f"❌ Invalid product should not have been inserted: {result.inserted_id}")
        except Exception as e:
            print(f"✅ Invalid product correctly rejected: {e}")

    # Modify validation rules
    def modify_validation():
        """Modify existing validation rules"""

        # Update validation for users collection
        updated_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["username", "email", "created_at", "status"],  # Added status
                "properties": {
                    "username": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9_]{3,30}$",  # Increased max length
                        "description": "Username must be 3-30 characters"
                    },
                    "email": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                    },
                    "status": {  # New required field
                        "enum": ["active", "inactive", "suspended", "pending"]
                    },
                    "age": {
                        "bsonType": "int",
                        "minimum": 13,
                        "maximum": 120
                    },
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }

        try:
            db.command({
                "collMod": "validated_users",
                "validator": updated_validator,
                "validationLevel": "moderate"  # Allow existing docs that don't match
            })
            print("✅ User validation rules updated")
        except Exception as e:
            print(f"❌ Failed to update validation: {e}")

    # Execute validation examples
    create_validated_collections()
    test_validation()
    modify_validation()

# Example usage
schema_validation_examples()
```

### Custom Validation Functions

```python
def custom_validation_patterns():
    """Examples of custom validation patterns"""

    def validate_user_data(user_data):
        """Custom validation function for user data"""
        errors = []

        # Required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                errors.append(f"Missing required field: {field}")

        # Username validation
        if 'username' in user_data:
            username = user_data['username']
            if len(username) < 3 or len(username) > 20:
                errors.append("Username must be 3-20 characters")
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                errors.append("Username can only contain alphanumeric characters and underscore")

        # Email validation
        if 'email' in user_data:
            email = user_data['email']
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append("Invalid email format")

        # Password validation
        if 'password' in user_data:
            password = user_data['password']
            if len(password) < 8:
                errors.append("Password must be at least 8 characters")
            if not re.search(r'[A-Z]', password):
                errors.append("Password must contain at least one uppercase letter")
            if not re.search(r'[a-z]', password):
                errors.append("Password must contain at least one lowercase letter")
            if not re.search(r'\d', password):
                errors.append("Password must contain at least one digit")

        # Age validation
        if 'age' in user_data:
            age = user_data['age']
            if not isinstance(age, int) or age < 13 or age > 120:
                errors.append("Age must be an integer between 13 and 120")

        # Profile validation
        if 'profile' in user_data:
            profile = user_data['profile']
            if not isinstance(profile, dict):
                errors.append("Profile must be an object")
            else:
                if 'bio' in profile and len(profile['bio']) > 500:
                    errors.append("Bio must be 500 characters or less")

        return errors

    def validate_product_data(product_data):
        """Custom validation function for product data"""
        errors = []

        # Required fields
        required_fields = ['name', 'price', 'category']
        for field in required_fields:
            if field not in product_data or product_data[field] is None:
                errors.append(f"Missing required field: {field}")

        # Name validation
        if 'name' in product_data:
            name = product_data['name']
            if not isinstance(name, str) or len(name.strip()) == 0:
                errors.append("Product name cannot be empty")
            elif len(name) > 200:
                errors.append("Product name must be 200 characters or less")

        # Price validation
        if 'price' in product_data:
            price = product_data['price']
            if not isinstance(price, (int, float)) or price < 0:
                errors.append("Price must be a non-negative number")
            elif price > 1000000:
                errors.append("Price cannot exceed $1,000,000")

        # Category validation
        if 'category' in product_data:
            valid_categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Other']
            if product_data['category'] not in valid_categories:
                errors.append(f"Category must be one of: {', '.join(valid_categories)}")

        # Stock validation
        if 'stock' in product_data:
            stock = product_data['stock']
            if not isinstance(stock, int) or stock < 0:
                errors.append("Stock must be a non-negative integer")

        # Rating validation
        if 'rating' in product_data:
            rating = product_data['rating']
            if not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
                errors.append("Rating must be a number between 0 and 5")

        # Tags validation
        if 'tags' in product_data:
            tags = product_data['tags']
            if not isinstance(tags, list):
                errors.append("Tags must be an array")
            elif len(tags) > 10:
                errors.append("Cannot have more than 10 tags")
            else:
                for tag in tags:
                    if not isinstance(tag, str) or len(tag.strip()) == 0:
                        errors.append("All tags must be non-empty strings")
                        break

        return errors

    def safe_insert_with_validation(collection, document, validation_func):
        """Insert document with custom validation"""

        # Validate document
        errors = validation_func(document)
        if errors:
            error_message = f"Validation failed: {'; '.join(errors)}"
            print(f"❌ {error_message}")
            raise ValueError(error_message)

        # Add timestamps
        document['created_at'] = datetime.utcnow()
        document['updated_at'] = datetime.utcnow()

        try:
            result = collection.insert_one(document)
            print(f"✅ Document inserted successfully: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"❌ Database insertion failed: {e}")
            raise

    def safe_update_with_validation(collection, filter_dict, update_data, validation_func):
        """Update document with custom validation"""

        # Get current document
        current_doc = collection.find_one(filter_dict)
        if not current_doc:
            raise ValueError("Document not found")

        # Merge update with current document for validation
        merged_doc = current_doc.copy()
        if '$set' in update_data:
            merged_doc.update(update_data['$set'])

        # Validate merged document
        errors = validation_func(merged_doc)
        if errors:
            error_message = f"Validation failed: {'; '.join(errors)}"
            print(f"❌ {error_message}")
            raise ValueError(error_message)

        # Add updated timestamp
        if '$set' not in update_data:
            update_data['$set'] = {}
        update_data['$set']['updated_at'] = datetime.utcnow()

        try:
            result = collection.update_one(filter_dict, update_data)
            print(f"✅ Document updated successfully")
            return result
        except Exception as e:
            print(f"❌ Database update failed: {e}")
            raise

    # Test custom validation
    def test_custom_validation():
        """Test custom validation functions"""

        users_collection = db.custom_validated_users
        products_collection = db.custom_validated_products

        # Test valid user
        valid_user = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "SecurePass123",
            "age": 25,
            "profile": {
                "bio": "I'm a software developer"
            }
        }

        try:
            user_id = safe_insert_with_validation(users_collection, valid_user, validate_user_data)
        except ValueError as e:
            print(f"User validation error: {e}")

        # Test invalid user
        invalid_user = {
            "username": "x",  # Too short
            "email": "invalid-email",  # Invalid format
            "password": "weak",  # Too weak
            "age": 150  # Too old
        }

        try:
            safe_insert_with_validation(users_collection, invalid_user, validate_user_data)
        except ValueError as e:
            print(f"Expected validation error: {e}")

        # Test valid product
        valid_product = {
            "name": "Test Product",
            "price": 99.99,
            "category": "Electronics",
            "stock": 10,
            "rating": 4.5,
            "tags": ["test", "product"]
        }

        try:
            product_id = safe_insert_with_validation(products_collection, valid_product, validate_product_data)
        except ValueError as e:
            print(f"Product validation error: {e}")

        # Test invalid product
        invalid_product = {
            "name": "",  # Empty name
            "price": -10,  # Negative price
            "category": "InvalidCategory",  # Invalid category
            "tags": ["tag"] * 15  # Too many tags
        }

        try:
            safe_insert_with_validation(products_collection, invalid_product, validate_product_data)
        except ValueError as e:
            print(f"Expected product validation error: {e}")

    test_custom_validation()
    return validate_user_data, validate_product_data

# Example usage
validation_functions = custom_validation_patterns()
```

## Next Steps

After mastering data modeling:

1. **Advanced Patterns**: [Advanced Data Patterns](../advanced/05_advanced_patterns.md)
2. **Performance Optimization**: [Performance and Optimization](../advanced/04_performance_optimization.md)
3. **Aggregation**: [Aggregation Framework](../advanced/01_aggregation_framework.md)
4. **Real-World Examples**: [Complete Application Examples](../examples/)

## Additional Resources

- [MongoDB Data Modeling Guide](https://docs.mongodb.com/manual/core/data-modeling-introduction/)
- [Schema Design Patterns](https://docs.mongodb.com/manual/applications/data-models/)
- [Schema Validation](https://docs.mongodb.com/manual/core/schema-validation/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/)
