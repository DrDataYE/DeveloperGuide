# MongoDB Geospatial Queries: Complete Guide

This single guide merges and streamlines the two previous docs. It shows how to model GeoJSON, create 2dsphere indexes, and query with $near, $geoWithin, $geoIntersects, and $centerSphere in mongosh.

## Prerequisites

- MongoDB/mongosh with 2dsphere index support
- GeoJSON coordinates use [longitude, latitude] in WGS84 (EPSG:4326)

## 1) Setup: database, sample data, and 2dsphere index

```javascript
use awesomeplace

// Insert a sample place as a GeoJSON Point
db.places.insertOne({
  name: "California Academy of Sciences",
  location: { type: "Point", coordinates: [-122.4724356, 37.7672544] }
})

// Create a 2dsphere index on the geometry field you query
db.places.createIndex({ location: "2dsphere" })

// Optional inspection
db.places.findOne()
db.places.getIndexes()
```

Notes

- 2dsphere indexes enable spherical calculations on GeoJSON.
- $near and $geoIntersects require a 2dsphere index; $geoWithin benefits from it.

## 2) Find nearest with $near (sorted by distance)

```javascript
// Nearest places to a point (sorted ascending by distance)
db.places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-122.471114, 37.771104] },
    },
  },
});
```

Optional distance bounds (meters):

```javascript
db.places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-122.471114, 37.771104] },
      $maxDistance: 500, // include only within 500 m
      $minDistance: 10, // exclude closer than 10 m
    },
  },
});
```

Tip: return actual distances using $geoNear in an aggregation:

```javascript
db.places.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-122.471114, 37.771104] },
      key: "location",
      spherical: true,
      distanceField: "distanceMeters",
    },
  },
]);
```

If you skipped index creation, MongoDB errors with: "unable to find index for $geoNear query".

## 3) Add more sample points

```javascript
db.places.insertMany([
  {
    name: "Conservatory of Flowers",
    location: { type: "Point", coordinates: [-122.4615748, 37.7701756] },
  },
  {
    name: "Golden Gate Tennis Park",
    location: { type: "Point", coordinates: [-122.4593702, 37.7705046] },
  },
  {
    name: "Nopa",
    location: { type: "Point", coordinates: [-122.4389058, 37.7747415] },
  },
]);

db.places.find();
```

## 4) Containment: $geoWithin with a Polygon

Define polygon corners and close the ring (repeat the first vertex at the end):

```javascript
const p1 = [-122.4547, 37.77473];
const p2 = [-122.45303, 37.76641];
const p3 = [-122.51026, 37.76411];
const p4 = [-122.51088, 37.77131];

// Points fully inside the polygon (boundary included)
db.places.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: [[p1, p2, p3, p4, p1]],
      },
    },
  },
});
```

## 5) Intersections: $geoIntersects with stored areas

Store an area as a Polygon and index it:

```javascript
db.areas.insertOne({
  name: "Golden Gate Park",
  area: { type: "Polygon", coordinates: [[p1, p2, p3, p4, p1]] },
});

// Index required for $geoIntersects queries
db.areas.createIndex({ area: "2dsphere" });
```

Query for areas that intersect a point:

```javascript
db.areas.find({
  area: {
    $geoIntersects: {
      $geometry: { type: "Point", coordinates: [-122.49089, 37.76992] },
    },
  },
});
```

Common pitfall: $geoIntersects must be nested under a field path; it cannot be a top-level operator.

## 6) Circular search: $centerSphere (radius in radians)

```javascript
// ~1 km radius around a center
const radiusKm = 1;
const radiusInRadians = radiusKm / 6378.1; // Earth radius ≈ 6378.1 km

db.places.find({
  location: {
    $geoWithin: {
      $centerSphere: [[-122.46203, 37.77286], radiusInRadians],
    },
  },
});
```

## Cheat sheet

- $near: nearest-first proximity search to a point. Needs 2dsphere index.
- $geoWithin: geometries fully inside a region (index recommended).
- $geoIntersects: geometries that intersect/touch a region. Needs 2dsphere index.
- $centerSphere: spherical circle containment; radius in radians (km / 6378.1).

## Troubleshooting

- "unable to find index for $geoNear query": create 2dsphere on the queried field.
- "unknown top level operator: $geoIntersects": nest under the geometry field.
- Ensure [lon, lat] order and closed polygon rings.
- Keep one consistent GeoJSON field per collection for best index usage.

## References

- https://www.mongodb.com/docs/manual/reference/geojson/
- https://www.mongodb.com/docs/manual/geospatial-queries/
- https://mongoosejs.com/docs/geojson.html
