# PyMongo GridFS - File Storage

This comprehensive guide covers MongoDB GridFS using PyMongo for storing and retrieving large files that exceed the BSON document size limit.

## Table of Contents

1. [GridFS Overview](#gridfs-overview)
2. [Basic File Operations](#basic-file-operations)
3. [Advanced GridFS Operations](#advanced-gridfs-operations)
4. [File Metadata and Indexing](#file-metadata-and-indexing)
5. [Streaming and Large Files](#streaming-and-large-files)
6. [GridFS Performance Optimization](#gridfs-performance-optimization)
7. [Real-World Examples](#real-world-examples)
8. [Best Practices](#best-practices)

## GridFS Overview

GridFS is a specification for storing and retrieving files that exceed the BSON document size limit of 16MB. It divides files into chunks and stores them in two collections.

### GridFS Architecture

```python
from pymongo import MongoClient
import gridfs
from gridfs import GridFS
from bson import ObjectId
import io
import os
from PIL import Image
import json
from datetime import datetime, timedelta
import hashlib

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.gridfs_demo

# Initialize GridFS
fs = GridFS(db)

def gridfs_overview():
    """Understanding GridFS architecture and components"""

    print("=== GridFS Architecture ===")
    print()

    # GridFS uses two collections:
    print("GridFS Collections:")
    print("1. fs.files - stores file metadata")
    print("2. fs.chunks - stores file data in chunks")
    print()

    # Default chunk size
    print(f"Default chunk size: {gridfs.DEFAULT_CHUNK_SIZE} bytes ({gridfs.DEFAULT_CHUNK_SIZE // 1024} KB)")
    print()

    # When to use GridFS
    print("When to use GridFS:")
    print("✅ Files larger than 16MB")
    print("✅ Need to store large amounts of binary data")
    print("✅ Want to access file metadata separately")
    print("✅ Need to stream large files")
    print("✅ Want atomic file operations")
    print()

    # When NOT to use GridFS
    print("When NOT to use GridFS:")
    print("❌ Files smaller than 16MB (use regular documents)")
    print("❌ Need frequent updates to file content")
    print("❌ Simple file storage (consider cloud storage)")
    print("❌ Need POSIX file system features")
    print()

    # GridFS benefits
    print("GridFS Benefits:")
    print("✅ No file size limits")
    print("✅ Automatic chunking")
    print("✅ Atomic operations")
    print("✅ Metadata storage")
    print("✅ Range queries")
    print("✅ Replication and sharding support")

# Execute overview
gridfs_overview()
```

### GridFS Collections Structure

```python
def examine_gridfs_collections():
    """Examine the structure of GridFS collections"""

    print("\n=== GridFS Collections Structure ===")

    # Clear existing data for clean examples
    db.fs.files.delete_many({})
    db.fs.chunks.delete_many({})

    # Store a sample file to examine structure
    sample_data = b"Hello, GridFS! This is a sample file content for demonstration."

    # Store file with metadata
    file_id = fs.put(
        sample_data,
        filename="sample.txt",
        content_type="text/plain",
        metadata={
            "author": "Demo User",
            "department": "Engineering",
            "tags": ["demo", "sample", "text"]
        }
    )

    print(f"Stored file with ID: {file_id}")

    # Examine fs.files collection
    file_doc = db.fs.files.find_one({"_id": file_id})
    print("\nfs.files document structure:")
    print(f"  _id: {file_doc['_id']}")
    print(f"  filename: {file_doc['filename']}")
    print(f"  length: {file_doc['length']} bytes")
    print(f"  chunkSize: {file_doc['chunkSize']} bytes")
    print(f"  uploadDate: {file_doc['uploadDate']}")
    print(f"  md5: {file_doc['md5']}")
    print(f"  contentType: {file_doc.get('contentType', 'Not set')}")
    print(f"  metadata: {file_doc.get('metadata', 'None')}")

    # Examine fs.chunks collection
    chunks = list(db.fs.chunks.find({"files_id": file_id}))
    print(f"\nfs.chunks documents: {len(chunks)} chunk(s)")

    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}:")
        print(f"    _id: {chunk['_id']}")
        print(f"    files_id: {chunk['files_id']}")
        print(f"    n: {chunk['n']} (chunk number)")
        print(f"    data size: {len(chunk['data'])} bytes")

    return file_id

# Execute collection examination
sample_file_id = examine_gridfs_collections()
```

## Basic File Operations

### Storing Files

```python
def basic_file_storage():
    """Basic file storage operations with GridFS"""

    print("\n=== Basic File Storage ===")

    # Method 1: Store data directly
    def store_data_directly():
        """Store binary data directly"""

        data = b"Direct binary data storage example"

        file_id = fs.put(
            data,
            filename="direct_data.bin",
            content_type="application/octet-stream"
        )

        print(f"✅ Stored data directly: {file_id}")
        return file_id

    # Method 2: Store from file-like object
    def store_from_file_object():
        """Store from file-like object"""

        # Create in-memory file
        file_obj = io.BytesIO(b"File-like object data content")

        file_id = fs.put(
            file_obj,
            filename="from_fileobj.txt",
            content_type="text/plain"
        )

        print(f"✅ Stored from file object: {file_id}")
        return file_id

    # Method 3: Store actual file
    def store_actual_file():
        """Store an actual file from disk"""

        # Create a temporary file
        temp_filename = "temp_demo_file.txt"
        temp_content = "This is a temporary file for GridFS demo.\n" * 100

        try:
            # Write temporary file
            with open(temp_filename, 'w') as f:
                f.write(temp_content)

            # Store in GridFS
            with open(temp_filename, 'rb') as f:
                file_id = fs.put(
                    f,
                    filename="stored_file.txt",
                    content_type="text/plain",
                    metadata={
                        "source": "disk",
                        "original_name": temp_filename,
                        "size_kb": len(temp_content) // 1024
                    }
                )

            print(f"✅ Stored actual file: {file_id}")
            return file_id

        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    # Method 4: Store with custom chunk size
    def store_with_custom_chunk_size():
        """Store file with custom chunk size"""

        # Large data to demonstrate chunking
        large_data = b"X" * (1024 * 1024)  # 1MB of data

        # Custom GridFS with smaller chunk size
        custom_fs = GridFS(db, collection="custom")

        file_id = custom_fs.put(
            large_data,
            filename="large_file.bin",
            chunk_size=64 * 1024,  # 64KB chunks instead of default 256KB
            metadata={"type": "large_binary", "custom_chunks": True}
        )

        print(f"✅ Stored with custom chunk size: {file_id}")

        # Check chunking
        chunks = list(db.custom.chunks.find({"files_id": file_id}))
        print(f"   Created {len(chunks)} chunks of ~64KB each")

        return file_id

    # Execute all storage methods
    direct_id = store_data_directly()
    fileobj_id = store_from_file_object()
    actual_id = store_actual_file()
    custom_id = store_with_custom_chunk_size()

    return {
        "direct": direct_id,
        "fileobj": fileobj_id,
        "actual": actual_id,
        "custom": custom_id
    }

# Execute file storage examples
storage_results = basic_file_storage()
```

### Retrieving Files

```python
def basic_file_retrieval():
    """Basic file retrieval operations"""

    print("\n=== Basic File Retrieval ===")

    # Method 1: Get file by ID
    def retrieve_by_id(file_id):
        """Retrieve file by ObjectId"""

        try:
            grid_out = fs.get(file_id)

            print(f"Retrieved file by ID: {file_id}")
            print(f"  Filename: {grid_out.filename}")
            print(f"  Content type: {grid_out.content_type}")
            print(f"  Length: {grid_out.length} bytes")
            print(f"  Upload date: {grid_out.upload_date}")
            print(f"  MD5: {grid_out.md5}")

            # Read content
            content = grid_out.read()
            print(f"  Content preview: {content[:50]}...")

            return content

        except gridfs.NoFile:
            print(f"❌ File with ID {file_id} not found")
            return None

    # Method 2: Get file by filename (latest version)
    def retrieve_by_filename(filename):
        """Retrieve latest file by filename"""

        try:
            grid_out = fs.get_last_version(filename)

            print(f"Retrieved latest version of: {filename}")
            print(f"  File ID: {grid_out._id}")
            print(f"  Length: {grid_out.length} bytes")

            content = grid_out.read()
            return content

        except gridfs.NoFile:
            print(f"❌ File '{filename}' not found")
            return None

    # Method 3: Streaming retrieval
    def retrieve_streaming(file_id):
        """Retrieve file with streaming"""

        try:
            grid_out = fs.get(file_id)

            print(f"Streaming file: {grid_out.filename}")

            # Read in chunks
            chunk_size = 1024
            total_read = 0

            while True:
                chunk = grid_out.read(chunk_size)
                if not chunk:
                    break

                total_read += len(chunk)
                # Process chunk here
                print(f"  Read chunk: {len(chunk)} bytes")

            print(f"  Total read: {total_read} bytes")

            return total_read

        except gridfs.NoFile:
            print(f"❌ File with ID {file_id} not found")
            return 0

    # Method 4: Retrieve to file
    def retrieve_to_file(file_id, output_filename):
        """Retrieve file and save to disk"""

        try:
            grid_out = fs.get(file_id)

            with open(output_filename, 'wb') as f:
                f.write(grid_out.read())

            print(f"✅ File saved to: {output_filename}")
            print(f"   Size: {os.path.getsize(output_filename)} bytes")

            # Clean up
            os.remove(output_filename)

            return True

        except gridfs.NoFile:
            print(f"❌ File with ID {file_id} not found")
            return False
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False

    # Test retrieval methods using stored files
    if storage_results["direct"]:
        content1 = retrieve_by_id(storage_results["direct"])
        content2 = retrieve_by_filename("direct_data.bin")
        streamed = retrieve_streaming(storage_results["direct"])
        saved = retrieve_to_file(storage_results["direct"], "output_test.bin")

    return {
        "by_id": content1 is not None,
        "by_filename": content2 is not None,
        "streamed": streamed > 0,
        "saved": saved
    }

# Execute retrieval examples
retrieval_results = basic_file_retrieval()
```

### File Management Operations

```python
def file_management_operations():
    """File management operations - list, delete, update"""

    print("\n=== File Management Operations ===")

    # List files
    def list_files():
        """List all files in GridFS"""

        files = fs.list()
        print(f"Files in GridFS: {len(files)}")

        for filename in files:
            print(f"  - {filename}")

        return files

    # Find files with criteria
    def find_files_with_criteria():
        """Find files matching specific criteria"""

        # Find by metadata
        files_by_metadata = db.fs.files.find({
            "metadata.author": "Demo User"
        })

        print("Files by author 'Demo User':")
        for file_doc in files_by_metadata:
            print(f"  - {file_doc['filename']} (ID: {file_doc['_id']})")

        # Find by content type
        text_files = db.fs.files.find({
            "contentType": "text/plain"
        })

        print("Text files:")
        for file_doc in text_files:
            print(f"  - {file_doc['filename']} ({file_doc['length']} bytes)")

        # Find by size range
        large_files = db.fs.files.find({
            "length": {"$gte": 1000}
        })

        print("Files >= 1000 bytes:")
        for file_doc in large_files:
            print(f"  - {file_doc['filename']} ({file_doc['length']} bytes)")

    # Delete files
    def delete_files():
        """Delete files from GridFS"""

        # Create a test file to delete
        test_data = b"This file will be deleted"
        test_id = fs.put(test_data, filename="to_delete.txt")

        print(f"Created test file for deletion: {test_id}")

        # Verify file exists
        if fs.exists(test_id):
            print("✅ File exists before deletion")

        # Delete by ID
        fs.delete(test_id)
        print("🗑️ File deleted")

        # Verify deletion
        if not fs.exists(test_id):
            print("✅ File successfully deleted")
        else:
            print("❌ File deletion failed")

        # Delete by filename (all versions)
        # First create multiple versions
        fs.put(b"Version 1", filename="versioned.txt")
        fs.put(b"Version 2", filename="versioned.txt")
        fs.put(b"Version 3", filename="versioned.txt")

        print("Created multiple versions of 'versioned.txt'")

        # Count versions before deletion
        versions_before = db.fs.files.count_documents({"filename": "versioned.txt"})
        print(f"Versions before deletion: {versions_before}")

        # Delete all versions
        for grid_out in fs.find({"filename": "versioned.txt"}):
            fs.delete(grid_out._id)

        versions_after = db.fs.files.count_documents({"filename": "versioned.txt"})
        print(f"Versions after deletion: {versions_after}")

    # Check file existence
    def check_file_existence():
        """Check if files exist"""

        # Check existing file
        if storage_results["direct"]:
            exists = fs.exists(storage_results["direct"])
            print(f"File {storage_results['direct']} exists: {exists}")

        # Check non-existent file
        fake_id = ObjectId()
        exists = fs.exists(fake_id)
        print(f"Fake file {fake_id} exists: {exists}")

        # Check by filename
        exists = fs.exists(filename="direct_data.bin")
        print(f"File 'direct_data.bin' exists: {exists}")

    # Execute management operations
    files = list_files()
    find_files_with_criteria()
    delete_files()
    check_file_existence()

    return files

# Execute file management examples
management_results = file_management_operations()
```

## Advanced GridFS Operations

### Working with File Versions

```python
def file_versioning():
    """Handle file versions in GridFS"""

    print("\n=== File Versioning ===")

    # Create multiple versions of the same file
    def create_file_versions():
        """Create multiple versions of a file"""

        filename = "document.txt"
        versions = []

        for i in range(1, 4):
            content = f"This is version {i} of the document.\nContent updated at {datetime.utcnow()}"

            file_id = fs.put(
                content.encode(),
                filename=filename,
                metadata={
                    "version": i,
                    "author": f"User{i}",
                    "created_at": datetime.utcnow()
                }
            )

            versions.append(file_id)
            print(f"✅ Created version {i}: {file_id}")

        return versions

    # Retrieve specific versions
    def retrieve_versions(filename):
        """Retrieve all versions of a file"""

        # Get all versions (sorted by upload date)
        all_versions = list(fs.find({"filename": filename}).sort("uploadDate", 1))

        print(f"All versions of '{filename}':")
        for i, version in enumerate(all_versions):
            metadata = version.metadata or {}
            print(f"  Version {i+1}: ID {version._id}")
            print(f"    Upload date: {version.upload_date}")
            print(f"    Metadata: {metadata}")
            print(f"    Content preview: {version.read(50)}...")
            print()

        # Get latest version
        latest = fs.get_last_version(filename)
        print(f"Latest version ID: {latest._id}")

        return all_versions

    # Version comparison
    def compare_versions(filename):
        """Compare different versions of a file"""

        versions = list(fs.find({"filename": filename}).sort("uploadDate", 1))

        if len(versions) < 2:
            print("Need at least 2 versions to compare")
            return

        print(f"Comparing versions of '{filename}':")

        for i in range(len(versions) - 1):
            current = versions[i]
            next_version = versions[i + 1]

            current_content = current.read()
            next_content = next_version.read()

            print(f"Version {i+1} vs Version {i+2}:")
            print(f"  Size change: {len(current_content)} -> {len(next_content)} bytes")
            print(f"  Content changed: {current_content != next_content}")

            # Reset read position
            current.seek(0)
            next_version.seek(0)

    # Execute versioning examples
    versions = create_file_versions()
    all_versions = retrieve_versions("document.txt")
    compare_versions("document.txt")

    return versions

# Execute versioning examples
versioning_results = file_versioning()
```

### File Metadata and Custom Attributes

```python
def advanced_metadata_operations():
    """Advanced metadata and custom attribute operations"""

    print("\n=== Advanced Metadata Operations ===")

    # Store files with rich metadata
    def store_with_rich_metadata():
        """Store files with comprehensive metadata"""

        # Document file
        doc_content = b"Important business document content..."
        doc_id = fs.put(
            doc_content,
            filename="business_report.pdf",
            content_type="application/pdf",
            metadata={
                "document_type": "report",
                "department": "finance",
                "author": "John Doe",
                "created_by": "user123",
                "tags": ["quarterly", "revenue", "analysis"],
                "security_level": "confidential",
                "version": "1.0",
                "approved_by": "manager456",
                "expiry_date": datetime.utcnow() + timedelta(days=365),
                "file_hash": hashlib.md5(doc_content).hexdigest(),
                "custom_fields": {
                    "project_id": "PROJ-2023-001",
                    "cost_center": "CC-FIN-001",
                    "approval_required": True
                }
            }
        )

        # Image file
        image_content = b"Fake image data..."
        image_id = fs.put(
            image_content,
            filename="product_photo.jpg",
            content_type="image/jpeg",
            metadata={
                "file_type": "image",
                "category": "product",
                "product_id": "PROD-001",
                "photographer": "Jane Smith",
                "camera_settings": {
                    "iso": 400,
                    "aperture": "f/2.8",
                    "shutter_speed": "1/125",
                    "focal_length": "50mm"
                },
                "dimensions": {"width": 1920, "height": 1080},
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "city": "New York"
                },
                "processing": {
                    "color_corrected": True,
                    "cropped": False,
                    "watermarked": True
                }
            }
        )

        print(f"✅ Stored document with metadata: {doc_id}")
        print(f"✅ Stored image with metadata: {image_id}")

        return doc_id, image_id

    # Query by metadata
    def query_by_metadata():
        """Query files using metadata criteria"""

        print("Querying files by metadata...")

        # Find files by department
        finance_files = db.fs.files.find({
            "metadata.department": "finance"
        })

        print("Finance department files:")
        for file_doc in finance_files:
            print(f"  - {file_doc['filename']} ({file_doc['contentType']})")

        # Find files by tags (array contains)
        quarterly_files = db.fs.files.find({
            "metadata.tags": "quarterly"
        })

        print("Files tagged 'quarterly':")
        for file_doc in quarterly_files:
            print(f"  - {file_doc['filename']}")

        # Find files by date range
        recent_files = db.fs.files.find({
            "uploadDate": {"$gte": datetime.utcnow() - timedelta(hours=1)}
        })

        print("Files uploaded in last hour:")
        for file_doc in recent_files:
            print(f"  - {file_doc['filename']} ({file_doc['uploadDate']})")

        # Complex metadata query
        complex_query = db.fs.files.find({
            "$and": [
                {"metadata.security_level": {"$in": ["confidential", "secret"]}},
                {"metadata.custom_fields.approval_required": True},
                {"length": {"$gte": 100}}
            ]
        })

        print("Files requiring approval (confidential/secret, >100 bytes):")
        for file_doc in complex_query:
            metadata = file_doc.get('metadata', {})
            print(f"  - {file_doc['filename']}")
            print(f"    Security: {metadata.get('security_level')}")
            print(f"    Size: {file_doc['length']} bytes")

    # Update metadata
    def update_file_metadata():
        """Update file metadata after storage"""

        # Find a file to update
        file_doc = db.fs.files.find_one({"filename": "business_report.pdf"})

        if file_doc:
            file_id = file_doc["_id"]

            # Update metadata
            update_result = db.fs.files.update_one(
                {"_id": file_id},
                {
                    "$set": {
                        "metadata.status": "reviewed",
                        "metadata.reviewed_by": "supervisor789",
                        "metadata.review_date": datetime.utcnow(),
                        "metadata.version": "1.1"
                    },
                    "$push": {
                        "metadata.tags": "reviewed"
                    }
                }
            )

            print(f"✅ Updated metadata for {file_doc['filename']}")
            print(f"   Modified count: {update_result.modified_count}")

            # Verify update
            updated_doc = db.fs.files.find_one({"_id": file_id})
            metadata = updated_doc.get('metadata', {})
            print(f"   New status: {metadata.get('status')}")
            print(f"   Updated tags: {metadata.get('tags')}")

    # Metadata aggregation
    def metadata_aggregation():
        """Aggregate metadata for reporting"""

        # File type distribution
        type_distribution = list(db.fs.files.aggregate([
            {"$group": {
                "_id": "$contentType",
                "count": {"$sum": 1},
                "total_size": {"$sum": "$length"}
            }},
            {"$sort": {"count": -1}}
        ]))

        print("File type distribution:")
        for dist in type_distribution:
            print(f"  {dist['_id']}: {dist['count']} files, {dist['total_size']} bytes")

        # Department file analysis
        dept_analysis = list(db.fs.files.aggregate([
            {"$match": {"metadata.department": {"$exists": True}}},
            {"$group": {
                "_id": "$metadata.department",
                "file_count": {"$sum": 1},
                "avg_size": {"$avg": "$length"},
                "total_size": {"$sum": "$length"}
            }}
        ]))

        print("Department file analysis:")
        for dept in dept_analysis:
            print(f"  {dept['_id']}: {dept['file_count']} files")
            print(f"    Average size: {dept['avg_size']:.0f} bytes")
            print(f"    Total size: {dept['total_size']} bytes")

    # Execute metadata operations
    doc_id, image_id = store_with_rich_metadata()
    query_by_metadata()
    update_file_metadata()
    metadata_aggregation()

    return doc_id, image_id

# Execute metadata examples
metadata_results = advanced_metadata_operations()
```

## Streaming and Large Files

### Efficient Streaming Operations

```python
def streaming_operations():
    """Efficient streaming operations for large files"""

    print("\n=== Streaming Operations ===")

    # Create large file for streaming tests
    def create_large_file():
        """Create a large file for streaming demonstrations"""

        # Generate large content (5MB)
        chunk_data = b"A" * 1024  # 1KB chunk
        large_content = chunk_data * 5120  # 5MB total

        file_id = fs.put(
            large_content,
            filename="large_stream_test.bin",
            content_type="application/octet-stream",
            metadata={
                "type": "streaming_test",
                "size_mb": 5,
                "created_for": "streaming_demo"
            }
        )

        print(f"✅ Created large file (5MB): {file_id}")
        return file_id

    # Streaming read
    def streaming_read(file_id):
        """Read file in streaming fashion"""

        print(f"Streaming read of file: {file_id}")

        grid_out = fs.get(file_id)

        chunk_size = 64 * 1024  # 64KB chunks
        bytes_read = 0
        chunk_count = 0

        start_time = datetime.utcnow()

        while True:
            chunk = grid_out.read(chunk_size)
            if not chunk:
                break

            bytes_read += len(chunk)
            chunk_count += 1

            # Simulate processing
            if chunk_count % 10 == 0:
                print(f"  Processed {chunk_count} chunks, {bytes_read} bytes")

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        print(f"✅ Streaming read completed:")
        print(f"   Total bytes: {bytes_read}")
        print(f"   Chunks processed: {chunk_count}")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Throughput: {bytes_read / duration / 1024 / 1024:.2f} MB/s")

        return bytes_read

    # Streaming write
    def streaming_write():
        """Write large file using streaming"""

        print("Streaming write of large file...")

        # Use GridIn for streaming writes
        grid_in = fs.new_file(
            filename="streamed_large.bin",
            content_type="application/octet-stream",
            metadata={"created_via": "streaming_write"}
        )

        chunk_size = 64 * 1024  # 64KB chunks
        total_chunks = 100  # Total ~6.4MB

        start_time = datetime.utcnow()

        try:
            for i in range(total_chunks):
                # Generate chunk data
                chunk_data = f"Chunk {i:04d} ".encode() + b"X" * (chunk_size - 12)

                # Write chunk
                grid_in.write(chunk_data)

                if (i + 1) % 20 == 0:
                    print(f"  Written {i + 1} chunks")

            # Finalize the file
            grid_in.close()

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            total_bytes = total_chunks * chunk_size

            print(f"✅ Streaming write completed:")
            print(f"   File ID: {grid_in._id}")
            print(f"   Total bytes: {total_bytes}")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"   Throughput: {total_bytes / duration / 1024 / 1024:.2f} MB/s")

            return grid_in._id

        except Exception as e:
            print(f"❌ Streaming write failed: {e}")
            grid_in.abort()
            return None

    # Partial reads (range requests)
    def partial_read(file_id, start_byte, end_byte):
        """Read specific byte range from file"""

        print(f"Partial read: bytes {start_byte}-{end_byte}")

        grid_out = fs.get(file_id)

        # Seek to start position
        grid_out.seek(start_byte)

        # Read specified range
        read_size = end_byte - start_byte + 1
        data = grid_out.read(read_size)

        print(f"✅ Read {len(data)} bytes from position {start_byte}")
        print(f"   Content preview: {data[:50]}...")

        return data

    # Progress tracking for large operations
    def progress_tracking_example(file_id):
        """Demonstrate progress tracking for large file operations"""

        print("Progress tracking example...")

        grid_out = fs.get(file_id)
        total_size = grid_out.length

        chunk_size = 32 * 1024  # 32KB chunks
        bytes_processed = 0

        start_time = datetime.utcnow()
        last_progress_time = start_time

        while True:
            chunk = grid_out.read(chunk_size)
            if not chunk:
                break

            bytes_processed += len(chunk)

            # Update progress every second
            current_time = datetime.utcnow()
            if (current_time - last_progress_time).total_seconds() >= 1.0:
                progress_pct = (bytes_processed / total_size) * 100
                elapsed = (current_time - start_time).total_seconds()
                rate = bytes_processed / elapsed / 1024 / 1024  # MB/s

                print(f"  Progress: {progress_pct:.1f}% ({bytes_processed}/{total_size} bytes) @ {rate:.2f} MB/s")
                last_progress_time = current_time

        total_time = (datetime.utcnow() - start_time).total_seconds()
        avg_rate = bytes_processed / total_time / 1024 / 1024

        print(f"✅ Processing completed in {total_time:.2f}s @ {avg_rate:.2f} MB/s")

    # Execute streaming operations
    large_file_id = create_large_file()

    if large_file_id:
        bytes_read = streaming_read(large_file_id)
        streamed_file_id = streaming_write()

        # Test partial reads
        partial_data = partial_read(large_file_id, 1000, 2000)

        # Progress tracking
        progress_tracking_example(large_file_id)

    return {
        "large_file_id": large_file_id,
        "streamed_file_id": streamed_file_id
    }

# Execute streaming examples
streaming_results = streaming_operations()
```

## GridFS Performance Optimization

### Performance Best Practices

```python
def gridfs_performance_optimization():
    """GridFS performance optimization techniques"""

    print("\n=== GridFS Performance Optimization ===")

    # Optimize chunk size
    def optimize_chunk_size():
        """Demonstrate chunk size optimization"""

        test_data = b"X" * (1024 * 1024)  # 1MB test data

        chunk_sizes = [64*1024, 256*1024, 512*1024, 1024*1024]  # 64KB to 1MB

        print("Chunk size performance comparison:")

        for chunk_size in chunk_sizes:
            # Create custom GridFS with specific chunk size
            test_fs = GridFS(db, collection=f"test_{chunk_size}")

            start_time = datetime.utcnow()

            # Store file
            file_id = test_fs.put(
                test_data,
                filename=f"test_{chunk_size}.bin",
                chunk_size=chunk_size
            )

            store_time = (datetime.utcnow() - start_time).total_seconds()

            # Retrieve file
            start_time = datetime.utcnow()
            retrieved = test_fs.get(file_id).read()
            retrieve_time = (datetime.utcnow() - start_time).total_seconds()

            # Count chunks
            chunk_count = db[f"test_{chunk_size}"].chunks.count_documents({"files_id": file_id})

            print(f"  Chunk size {chunk_size//1024}KB:")
            print(f"    Store time: {store_time:.3f}s")
            print(f"    Retrieve time: {retrieve_time:.3f}s")
            print(f"    Chunks created: {chunk_count}")
            print(f"    Total time: {store_time + retrieve_time:.3f}s")
            print()

    # Index optimization
    def optimize_indexes():
        """Optimize GridFS indexes for better performance"""

        print("GridFS index optimization...")

        # Default indexes
        print("Default GridFS indexes:")
        files_indexes = list(db.fs.files.list_indexes())
        chunks_indexes = list(db.fs.chunks.list_indexes())

        print("fs.files indexes:")
        for idx in files_indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")

        print("fs.chunks indexes:")
        for idx in chunks_indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")

        # Create additional performance indexes
        try:
            # Index for filename queries
            db.fs.files.create_index([("filename", 1), ("uploadDate", -1)])
            print("✅ Created filename + uploadDate index")

            # Index for metadata queries
            db.fs.files.create_index("metadata.department")
            print("✅ Created metadata.department index")

            # Index for content type queries
            db.fs.files.create_index("contentType")
            print("✅ Created contentType index")

            # Compound index for complex queries
            db.fs.files.create_index([
                ("metadata.department", 1),
                ("contentType", 1),
                ("uploadDate", -1)
            ])
            print("✅ Created compound metadata index")

        except Exception as e:
            print(f"Index creation note: {e}")

    # Query optimization
    def optimize_queries():
        """Optimize GridFS queries for better performance"""

        print("Query optimization examples...")

        # Bad query (no index usage)
        def bad_query_example():
            start_time = datetime.utcnow()

            # This query doesn't use indexes efficiently
            result = list(db.fs.files.find({
                "length": {"$gte": 1000}
            }).limit(10))

            duration = (datetime.utcnow() - start_time).total_seconds()
            print(f"❌ Unoptimized query: {duration:.3f}s, {len(result)} results")

        # Good query (uses indexes)
        def good_query_example():
            start_time = datetime.utcnow()

            # This query uses the contentType index
            result = list(db.fs.files.find({
                "contentType": "text/plain"
            }).limit(10))

            duration = (datetime.utcnow() - start_time).total_seconds()
            print(f"✅ Optimized query: {duration:.3f}s, {len(result)} results")

        # Query with projection
        def projected_query_example():
            start_time = datetime.utcnow()

            # Only retrieve needed fields
            result = list(db.fs.files.find(
                {"contentType": "text/plain"},
                {"filename": 1, "length": 1, "uploadDate": 1}
            ).limit(10))

            duration = (datetime.utcnow() - start_time).total_seconds()
            print(f"✅ Projected query: {duration:.3f}s, {len(result)} results")

        bad_query_example()
        good_query_example()
        projected_query_example()

    # Connection optimization
    def connection_optimization():
        """Connection and client optimization for GridFS"""

        print("Connection optimization recommendations:")
        print("✅ Use connection pooling")
        print("✅ Set appropriate maxPoolSize")
        print("✅ Use read preferences for read-heavy workloads")
        print("✅ Consider write concern for consistency vs performance")
        print("✅ Use compression for network optimization")

        # Example optimized client configuration
        optimized_config = {
            "maxPoolSize": 100,
            "minPoolSize": 10,
            "maxIdleTimeMS": 30000,
            "waitQueueTimeoutMS": 10000,
            "compressors": ["zstd", "zlib", "snappy"],
            "zlibCompressionLevel": 6
        }

        print(f"Recommended client configuration: {optimized_config}")

    # Monitoring and profiling
    def monitoring_performance():
        """Monitor GridFS performance"""

        print("Performance monitoring recommendations:")

        # Collection statistics
        files_stats = db.command("collStats", "fs.files")
        chunks_stats = db.command("collStats", "fs.chunks")

        print(f"fs.files collection:")
        print(f"  Documents: {files_stats.get('count', 0):,}")
        print(f"  Size: {files_stats.get('size', 0):,} bytes")
        print(f"  Average document size: {files_stats.get('avgObjSize', 0):,} bytes")

        print(f"fs.chunks collection:")
        print(f"  Documents: {chunks_stats.get('count', 0):,}")
        print(f"  Size: {chunks_stats.get('size', 0):,} bytes")
        print(f"  Average document size: {chunks_stats.get('avgObjSize', 0):,} bytes")

        # Performance metrics to monitor
        print("Key metrics to monitor:")
        print("✅ Average file size vs chunk size ratio")
        print("✅ Number of chunks per file")
        print("✅ Query response times")
        print("✅ Index usage statistics")
        print("✅ Storage efficiency")

    # Execute optimization examples
    optimize_chunk_size()
    optimize_indexes()
    optimize_queries()
    connection_optimization()
    monitoring_performance()

# Execute performance optimization
gridfs_performance_optimization()
```

## Real-World Examples

### Document Management System

```python
def document_management_system():
    """Complete document management system using GridFS"""

    print("\n=== Document Management System ===")

    class DocumentManager:
        """Complete document management system"""

        def __init__(self, db):
            self.db = db
            self.fs = GridFS(db, collection="documents")
            self.setup_indexes()

        def setup_indexes(self):
            """Setup optimized indexes for document management"""

            try:
                # Document metadata indexes
                self.db.documents.files.create_index([
                    ("metadata.document_type", 1),
                    ("metadata.department", 1),
                    ("uploadDate", -1)
                ])

                self.db.documents.files.create_index("metadata.tags")
                self.db.documents.files.create_index("metadata.author")
                self.db.documents.files.create_index("metadata.security_level")

                print("✅ Document management indexes created")

            except Exception as e:
                print(f"Index setup: {e}")

        def upload_document(self, file_data, filename, document_info):
            """Upload a document with comprehensive metadata"""

            # Validate input
            if not file_data:
                raise ValueError("File data is required")

            if not filename:
                raise ValueError("Filename is required")

            # Generate document metadata
            metadata = {
                "document_type": document_info.get("type", "general"),
                "department": document_info.get("department", "unknown"),
                "author": document_info.get("author", "anonymous"),
                "tags": document_info.get("tags", []),
                "security_level": document_info.get("security_level", "public"),
                "description": document_info.get("description", ""),
                "project_id": document_info.get("project_id"),
                "version": document_info.get("version", "1.0"),
                "upload_timestamp": datetime.utcnow(),
                "file_hash": hashlib.sha256(file_data).hexdigest(),
                "uploaded_by": document_info.get("uploaded_by", "system"),
                "approval_status": "pending",
                "retention_period": document_info.get("retention_days", 365)
            }

            # Determine content type
            content_type = document_info.get("content_type")
            if not content_type:
                if filename.lower().endswith('.pdf'):
                    content_type = "application/pdf"
                elif filename.lower().endswith(('.doc', '.docx')):
                    content_type = "application/msword"
                elif filename.lower().endswith(('.jpg', '.jpeg')):
                    content_type = "image/jpeg"
                elif filename.lower().endswith('.png'):
                    content_type = "image/png"
                else:
                    content_type = "application/octet-stream"

            # Store document
            file_id = self.fs.put(
                file_data,
                filename=filename,
                content_type=content_type,
                metadata=metadata
            )

            print(f"✅ Document uploaded: {filename} (ID: {file_id})")
            return file_id

        def search_documents(self, search_criteria):
            """Search documents by various criteria"""

            query = {}

            # Build query from criteria
            if search_criteria.get("department"):
                query["metadata.department"] = search_criteria["department"]

            if search_criteria.get("document_type"):
                query["metadata.document_type"] = search_criteria["document_type"]

            if search_criteria.get("author"):
                query["metadata.author"] = {"$regex": search_criteria["author"], "$options": "i"}

            if search_criteria.get("tags"):
                query["metadata.tags"] = {"$in": search_criteria["tags"]}

            if search_criteria.get("security_level"):
                query["metadata.security_level"] = search_criteria["security_level"]

            if search_criteria.get("date_from"):
                query["uploadDate"] = {"$gte": search_criteria["date_from"]}

            if search_criteria.get("date_to"):
                if "uploadDate" in query:
                    query["uploadDate"]["$lte"] = search_criteria["date_to"]
                else:
                    query["uploadDate"] = {"$lte": search_criteria["date_to"]}

            # Execute search
            results = list(self.db.documents.files.find(query).sort("uploadDate", -1))

            print(f"Search found {len(results)} documents")
            return results

        def get_document(self, file_id):
            """Retrieve document by ID"""

            try:
                return self.fs.get(file_id)
            except gridfs.NoFile:
                print(f"Document {file_id} not found")
                return None

        def update_document_metadata(self, file_id, updates):
            """Update document metadata"""

            update_ops = {}

            for key, value in updates.items():
                update_ops[f"metadata.{key}"] = value

            # Add modification timestamp
            update_ops["metadata.last_modified"] = datetime.utcnow()

            result = self.db.documents.files.update_one(
                {"_id": file_id},
                {"$set": update_ops}
            )

            if result.modified_count > 0:
                print(f"✅ Document metadata updated: {file_id}")
                return True
            else:
                print(f"❌ Failed to update document: {file_id}")
                return False

        def approve_document(self, file_id, approver):
            """Approve a document"""

            return self.update_document_metadata(file_id, {
                "approval_status": "approved",
                "approved_by": approver,
                "approval_date": datetime.utcnow()
            })

        def delete_document(self, file_id, reason=""):
            """Delete a document with audit trail"""

            # Get document info before deletion
            doc_info = self.db.documents.files.find_one({"_id": file_id})

            if not doc_info:
                print(f"Document {file_id} not found")
                return False

            # Create audit record
            audit_record = {
                "action": "delete",
                "file_id": file_id,
                "filename": doc_info["filename"],
                "deleted_at": datetime.utcnow(),
                "reason": reason,
                "original_metadata": doc_info.get("metadata", {})
            }

            self.db.document_audit.insert_one(audit_record)

            # Delete the document
            self.fs.delete(file_id)

            print(f"✅ Document deleted: {doc_info['filename']}")
            return True

        def generate_report(self):
            """Generate document management report"""

            print("Document Management Report:")
            print("=" * 50)

            # Total statistics
            total_docs = self.db.documents.files.count_documents({})
            total_size = list(self.db.documents.files.aggregate([
                {"$group": {"_id": None, "total": {"$sum": "$length"}}}
            ]))

            total_size_bytes = total_size[0]["total"] if total_size else 0

            print(f"Total Documents: {total_docs:,}")
            print(f"Total Size: {total_size_bytes:,} bytes ({total_size_bytes/1024/1024:.2f} MB)")

            # By department
            dept_stats = list(self.db.documents.files.aggregate([
                {"$group": {
                    "_id": "$metadata.department",
                    "count": {"$sum": 1},
                    "size": {"$sum": "$length"}
                }},
                {"$sort": {"count": -1}}
            ]))

            print("\nBy Department:")
            for stat in dept_stats:
                print(f"  {stat['_id']}: {stat['count']} docs, {stat['size']:,} bytes")

            # By document type
            type_stats = list(self.db.documents.files.aggregate([
                {"$group": {
                    "_id": "$metadata.document_type",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]))

            print("\nBy Document Type:")
            for stat in type_stats:
                print(f"  {stat['_id']}: {stat['count']} documents")

            # Approval status
            approval_stats = list(self.db.documents.files.aggregate([
                {"$group": {
                    "_id": "$metadata.approval_status",
                    "count": {"$sum": 1}
                }}
            ]))

            print("\nApproval Status:")
            for stat in approval_stats:
                print(f"  {stat['_id']}: {stat['count']} documents")

    # Test the document management system
    doc_manager = DocumentManager(db)

    # Upload sample documents
    sample_docs = [
        {
            "data": b"Sample business proposal content...",
            "filename": "business_proposal.pdf",
            "info": {
                "type": "proposal",
                "department": "sales",
                "author": "John Doe",
                "tags": ["business", "proposal", "Q4"],
                "security_level": "confidential"
            }
        },
        {
            "data": b"Employee handbook content...",
            "filename": "employee_handbook.pdf",
            "info": {
                "type": "policy",
                "department": "hr",
                "author": "HR Team",
                "tags": ["policy", "handbook", "employees"],
                "security_level": "internal"
            }
        }
    ]

    uploaded_ids = []
    for doc in sample_docs:
        file_id = doc_manager.upload_document(
            doc["data"],
            doc["filename"],
            doc["info"]
        )
        uploaded_ids.append(file_id)

    # Search documents
    search_results = doc_manager.search_documents({
        "department": "sales",
        "tags": ["business"]
    })

    # Approve a document
    if uploaded_ids:
        doc_manager.approve_document(uploaded_ids[0], "manager123")

    # Generate report
    doc_manager.generate_report()

    return doc_manager

# Execute document management example
doc_manager = document_management_system()
```

## Best Practices

### GridFS Best Practices Summary

```python
def gridfs_best_practices():
    """Comprehensive GridFS best practices"""

    print("\n=== GridFS Best Practices ===")

    best_practices = {
        "when_to_use": [
            "Files larger than 16MB",
            "Need to store binary data with metadata",
            "Want atomic file operations",
            "Need to stream large files",
            "Require file versioning"
        ],

        "when_not_to_use": [
            "Files smaller than 16MB (use regular documents)",
            "Frequent file modifications",
            "Simple file storage needs",
            "Need POSIX file system features"
        ],

        "performance": [
            "Choose appropriate chunk size (256KB default is often good)",
            "Create indexes on frequently queried metadata fields",
            "Use projection to limit returned fields",
            "Consider read preferences for read-heavy workloads",
            "Use streaming for large files"
        ],

        "security": [
            "Store sensitive metadata separately if needed",
            "Implement proper access controls",
            "Consider encryption for sensitive files",
            "Audit file access and modifications",
            "Validate file content and metadata"
        ],

        "maintenance": [
            "Monitor collection sizes and growth",
            "Implement file lifecycle management",
            "Regular backup of both files and chunks collections",
            "Clean up orphaned chunks if any",
            "Monitor index usage and performance"
        ]
    }

    for category, practices in best_practices.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        print("=" * 40)
        for practice in practices:
            print(f"✅ {practice}")

    # Common pitfalls
    print("\nCOMMON PITFALLS TO AVOID:")
    print("=" * 40)
    pitfalls = [
        "Using GridFS for small files",
        "Not optimizing chunk size for your use case",
        "Missing indexes on metadata fields",
        "Not handling GridFS exceptions properly",
        "Storing frequently changing files",
        "Not monitoring storage growth",
        "Forgetting to clean up temporary files"
    ]

    for pitfall in pitfalls:
        print(f"❌ {pitfall}")

    # Implementation checklist
    print("\nGRIDFS IMPLEMENTATION CHECKLIST:")
    print("=" * 40)
    checklist = [
        "Analyzed file size and access patterns",
        "Chosen appropriate chunk size",
        "Designed metadata schema",
        "Created necessary indexes",
        "Implemented error handling",
        "Added file lifecycle management",
        "Set up monitoring and alerting",
        "Planned backup strategy",
        "Tested with realistic data volumes",
        "Documented usage patterns"
    ]

    for item in checklist:
        print(f"□ {item}")

    return best_practices

# Execute best practices summary
best_practices = gridfs_best_practices()
```

## Summary and Next Steps

This comprehensive guide covered:

1. **GridFS Overview** - Architecture and when to use GridFS
2. **Basic File Operations** - Storing, retrieving, and managing files
3. **Advanced Operations** - Versioning, metadata, and custom attributes
4. **Streaming Operations** - Efficient handling of large files
5. **Performance Optimization** - Chunk sizes, indexes, and query optimization
6. **Real-World Examples** - Complete document management system
7. **Best Practices** - Comprehensive guidelines and recommendations

### Key Takeaways

- **Use GridFS judiciously** - Only for files > 16MB or when you need special features
- **Optimize chunk size** - Balance between number of chunks and performance
- **Index metadata fields** - Essential for query performance
- **Handle large files efficiently** - Use streaming for better memory usage
- **Plan for growth** - Monitor storage and implement lifecycle management

### Next Steps

1. **Text Search**: [Full-Text Search with MongoDB](./05_text_search.md)
2. **Geospatial Queries**: [Location-Based Operations](./06_geospatial_queries.md)
3. **Performance Optimization**: [Advanced Performance Tuning](./07_performance_optimization.md)
4. **Monitoring**: [Database Monitoring](./10_monitoring_profiling.md)

### Additional Resources

- [MongoDB GridFS Documentation](https://docs.mongodb.com/manual/core/gridfs/)
- [PyMongo GridFS API](https://pymongo.readthedocs.io/en/stable/api/gridfs/)
- [GridFS Best Practices](https://docs.mongodb.com/manual/core/gridfs/#when-to-use-gridfs)
- [File Storage Alternatives](https://docs.mongodb.com/manual/core/gridfs/#alternatives-to-gridfs)
