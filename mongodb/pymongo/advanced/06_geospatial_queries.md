# PyMongo Geospatial Queries

A concise guide to geospatial and location-based queries in MongoDB using PyMongo.

## Basics

```python
from pymongo import MongoClient, GEO2D, GEOSPHERE
import math

# Connection
client = MongoClient('mongodb://localhost:27017/')
db = client.geo_demo
collection = db.locations

# Clear previous data
collection.drop()
```

## Setting up Geospatial Data

```python
def setup_geospatial_data():
    """Setup sample geospatial data"""

    # Locations in different cities
    locations = [
        {
            "name": "Cairo Tower",
            "type": "landmark",
            "location": {
                "type": "Point",
                "coordinates": [31.2241, 30.0461]  # [longitude, latitude]
            }
        },
        {
            "name": "Pyramids of Giza",
            "type": "landmark",
            "location": {
                "type": "Point",
                "coordinates": [31.1313, 29.9792]
            }
        },
        {
            "name": "Alexandria Library",
            "type": "library",
            "location": {
                "type": "Point",
                "coordinates": [29.9097, 31.2156]
            }
        {
            "name": "Red Sea Resort",
            "type": "hotel",
            "location": {
                "type": "Point",
                "coordinates": [34.3300, 27.2579]
            }
        }
    ]

    # Insert data
    collection.insert_many(locations)

    # Create 2dsphere geospatial index
    collection.create_index([("location", GEOSPHERE)])

    print("✅ Geospatial data and index created")
    print(f"Inserted {len(locations)} locations")

setup_geospatial_data()
```

## Basic Geospatial Queries

```python
def basic_geospatial_queries():
    """Basic geospatial queries"""

    # Near search from a point
    cairo_center = [31.2357, 30.0444]  # Cairo center

    near_cairo = collection.find({
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": cairo_center
                },
                "$maxDistance": 50000  # 50 kilometers
            }
        }
    })

    print("Locations near Cairo (50 km):")
    for loc in near_cairo:
        print(f"  - {loc['name']} ({loc['type']})")

    # Search within a geographic polygon
    egypt_polygon = {
        "type": "Polygon",
        "coordinates": [[
            [24.0, 22.0],  # Southwest
            [37.0, 22.0],  # Southeast
            [37.0, 32.0],  # Northeast
            [24.0, 32.0],  # Northwest
            [24.0, 22.0]   # Close polygon
        ]]
    }

    within_egypt = collection.find({
        "location": {
            "$geoWithin": {
                "$geometry": egypt_polygon
            }
        }
    })

    print("\nLocations within Egypt:")
    for loc in within_egypt:
        print(f"  - {loc['name']}")

basic_geospatial_queries()
```

## Advanced Queries

```python
def advanced_geospatial_queries():
    """Advanced geospatial queries"""

    # Search with distance calculation
    results = collection.aggregate([
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [31.2357, 30.0444]  # Cairo
                },
                "distanceField": "distance",
                "maxDistance": 100000,  # 100 km
                "spherical": True
            }
        },
        {
            "$project": {
                "name": 1,
                "type": 1,
                "distance_km": {"$divide": ["$distance", 1000]}
            }
        }
    ])

    print("Locations with distance from Cairo:")
    for loc in results:
        print(f"  - {loc['name']}: {loc['distance_km']:.1f} km")

    # Search with variable radius
    def find_nearby_by_type(location_type, center, radius_km):
        """Search for locations within radius"""

        results = collection.find({
            "type": location_type,
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": center
                    },
                    "$maxDistance": radius_km * 1000
                }
            }
        })

        return list(results)

    # Search for nearby hotels
    hotels = find_nearby_by_type("hotel", [31.2357, 30.0444], 500)
    print(f"\nHotels within 500 km: {len(hotels)}")

    # Search for nearby landmarks
    landmarks = find_nearby_by_type("landmark", [31.2357, 30.0444], 100)
    print(f"Landmarks within 100 km: {len(landmarks)}")

advanced_geospatial_queries()
```

## Geographic Operations

```python
def geospatial_operations():
    """Useful geographic operations"""

    # Calculate distance between two points
    def calculate_distance(point1, point2):
        """Calculate distance between two points (Haversine)"""

        lat1, lon1 = math.radians(point1[1]), math.radians(point1[0])
        lat2, lon2 = math.radians(point2[1]), math.radians(point2[0])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth radius in kilometers

        return c * r

    # Find nearest locations
    def find_closest_locations(target_point, limit=3):
        """Find nearest locations to a specific point"""

        results = collection.aggregate([
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": target_point
                    },
                    "distanceField": "distance",
                    "spherical": True,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "name": 1,
                    "type": 1,
                    "distance_km": {"$divide": ["$distance", 1000]}
                }
            }
        ])

        return list(results)

    # Test operations
    cairo = [31.2357, 30.0444]
    alex = [29.9097, 31.2156]

    distance = calculate_distance(cairo, alex)
    print(f"Distance between Cairo and Alexandria: {distance:.1f} km")

    closest = find_closest_locations(cairo, 2)
    print("\nClosest two locations to Cairo:")
    for loc in closest:
        print(f"  - {loc['name']}: {loc['distance_km']:.1f} km")

geospatial_operations()
```

## Practical Applications

```python
def practical_geospatial_examples():
    """Practical examples for geospatial queries"""

    # Food delivery system
    def delivery_system_example():
        """Example of food delivery system"""

        # Add restaurants
        restaurants = [
            {
                "name": "Pizza Palace",
                "cuisine": "Italian",
                "delivery_radius": 5000,  # 5 km
                "location": {
                    "type": "Point",
                    "coordinates": [31.2400, 30.0500]
                }
            },
            {
                "name": "Burger House",
                "cuisine": "American",
                "delivery_radius": 3000,  # 3 km
                "location": {
                    "type": "Point",
                    "coordinates": [31.2300, 30.0400]
                }
            }
        ]

        restaurants_collection = db.restaurants
        restaurants_collection.drop()
        restaurants_collection.insert_many(restaurants)
        restaurants_collection.create_index([("location", GEOSPHERE)])

        # Search for restaurants delivering to specific address
        customer_location = [31.2350, 30.0450]

        available_restaurants = restaurants_collection.find({
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": customer_location
                    },
                    "$maxDistance": 5000
                }
            }
        })

        print("Available restaurants for delivery:")
        for restaurant in available_restaurants:
            print(f"  - {restaurant['name']} ({restaurant['cuisine']})")

    # Taxi system
    def taxi_system_example():
        """Example of a taxi system"""

        # Available drivers
        drivers = [
            {
                "name": "Ahmed",
                "status": "available",
                "location": {
                    "type": "Point",
                    "coordinates": [31.2380, 30.0480]
                }
            },
            {
                "name": "Mohamed",
                "status": "available",
                "location": {
                    "type": "Point",
                    "coordinates": [31.2320, 30.0420]
                }
            }
        ]

        drivers_collection = db.drivers
        drivers_collection.drop()
        drivers_collection.insert_many(drivers)
        drivers_collection.create_index([("location", GEOSPHERE)])

        # Find the nearest available driver
        pickup_location = [31.2350, 30.0450]

        nearest_driver = drivers_collection.find_one({
            "status": "available",
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": pickup_location
                    }
                }
            }
        })

        if nearest_driver:
            print(f"Nearest available driver: {nearest_driver['name']}")

    delivery_system_example()
    taxi_system_example()

practical_geospatial_examples()
```

## Best Practices

```python
def geospatial_best_practices():
    """Best practices for geospatial queries"""

    practices = {
        "Index Design": [
            "Use 2dsphere for geospatial coordinates",
            "Create compound indexes for complex queries",
            "Monitor the size and performance of geospatial indexes"
        ],
        "Query Optimization": [
            "Use reasonable distance limits",
            "Combine geospatial queries with other filters",
            "Use projection to reduce data transfer"
        ],
        "Data Structure": [
            "Use GeoJSON for better compatibility",
            "Store coordinates in order [longitude, latitude]",
            "Validate geospatial data"
        ]
    }

    for category, items in practices.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ✅ {item}")

    # Examples of common errors
    print("\nCommon errors:")
    errors = [
        "Reversing latitude/longitude order",
        "Using incorrect indexes for the required type",
        "Not specifying reasonable distance limits",
        "Ignoring coordinate validation"
    ]

    for error in errors:
        print(f"  ❌ {error}")

geospatial_best_practices()
```

## Summary

Key Features:

- Geospatial Indexing: create_index([("location", GEOSPHERE)])
- Near Search: {"$near": {"$geometry": point, "$maxDistance": distance}}
- Search Within Area: {"$geoWithin": {"$geometry": polygon}}
- Distance Calculation: $geoNear in aggregation
- GeoJSON Support: for complex shapes

Useful Queries:

- Search for nearest locations
- Locate places within radius
- Calculate distances and directions
- Complex geospatial operations

Best Practices:

- Use appropriate 2dsphere indexes
- Store coordinates in correct order [longitude, latitude]
- Use reasonable distance limits
- Combine geospatial queries with other filters

### Next: [performance optimization](./07_performance_optimization.md)
