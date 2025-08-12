# PyMongo Transactions

This comprehensive guide covers MongoDB transactions using PyMongo, including ACID properties, multi-document transactions, and error handling patterns.

## Table of Contents

1. [Transaction Fundamentals](#transaction-fundamentals)
2. [Single Document Transactions](#single-document-transactions)
3. [Multi-Document Transactions](#multi-document-transactions)
4. [Transaction Sessions](#transaction-sessions)
5. [Error Handling and Retry Logic](#error-handling-and-retry-logic)
6. [Performance Considerations](#performance-considerations)
7. [Real-World Examples](#real-world-examples)
8. [Best Practices](#best-practices)

## Transaction Fundamentals

Understanding ACID properties and when to use transactions in MongoDB.

### ACID Properties in MongoDB

```python
from pymongo import MongoClient, WriteConcern, ReadConcern
from pymongo.errors import PyMongoError, OperationFailure
from bson import ObjectId
import time
import threading
from datetime import datetime, timedelta
from decimal import Decimal

# Connect to MongoDB (requires replica set for transactions)
client = MongoClient('mongodb://localhost:27017/?replicaSet=rs0')
db = client.transaction_demo

# Collections for our examples
accounts = db.accounts
orders = db.orders
inventory = db.inventory
audit_log = db.audit_log

def setup_sample_data():
    """Setup sample data for transaction examples"""

    # Clear existing data
    accounts.delete_many({})
    orders.delete_many({})
    inventory.delete_many({})
    audit_log.delete_many({})

    # Sample accounts
    sample_accounts = [
        {
            "_id": ObjectId(),
            "account_id": "ACC001",
            "name": "Alice Johnson",
            "balance": Decimal("1000.00"),
            "currency": "USD",
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "account_id": "ACC002",
            "name": "Bob Smith",
            "balance": Decimal("500.00"),
            "currency": "USD",
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "account_id": "ACC003",
            "name": "Charlie Brown",
            "balance": Decimal("2000.00"),
            "currency": "USD",
            "status": "active",
            "created_at": datetime.utcnow()
        }
    ]

    accounts.insert_many(sample_accounts)
    account_ids = [acc["_id"] for acc in sample_accounts]

    # Sample inventory
    sample_inventory = [
        {
            "_id": ObjectId(),
            "product_id": "PROD001",
            "name": "Laptop Pro",
            "quantity": 50,
            "price": Decimal("999.99"),
            "reserved": 0,
            "last_updated": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "product_id": "PROD002",
            "name": "Wireless Mouse",
            "quantity": 100,
            "price": Decimal("29.99"),
            "reserved": 0,
            "last_updated": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "product_id": "PROD003",
            "name": "USB Cable",
            "quantity": 200,
            "price": Decimal("9.99"),
            "reserved": 0,
            "last_updated": datetime.utcnow()
        }
    ]

    inventory.insert_many(sample_inventory)

    print("✅ Sample data created successfully")
    return account_ids

# Setup data
account_ids = setup_sample_data()
```

### Transaction Requirements and Limitations

```python
def transaction_requirements():
    """Understand transaction requirements and limitations"""

    print("=== MongoDB Transaction Requirements ===")
    print()

    # Check if transactions are supported
    try:
        # Test if we can start a session
        with client.start_session() as session:
            print("✅ Sessions supported")

            # Test if transactions are supported
            with session.start_transaction():
                # Simple operation within transaction
                result = accounts.find_one({"account_id": "ACC001"}, session=session)
                if result:
                    print("✅ Transactions supported")
                else:
                    print("⚠ Test transaction executed but no data found")

    except Exception as e:
        print(f"❌ Transaction support check failed: {e}")
        print("Requirements for transactions:")
        print("  - MongoDB 4.0+ for replica sets")
        print("  - MongoDB 4.2+ for sharded clusters")
        print("  - Replica set deployment (minimum 1 node)")
        return False

    # Transaction limitations
    print("\nTransaction Limitations:")
    print("✅ Can modify multiple documents across multiple collections")
    print("✅ Support read and write operations")
    print("✅ Support aggregation framework")
    print("⚠ Limited to 16MB total transaction size")
    print("⚠ Maximum 60-second transaction lifetime")
    print("⚠ Cannot create collections or indexes within transactions")
    print("❌ No DDL operations (create/drop collections/databases)")
    print("❌ No operations that affect multiple shards (in some cases)")

    return True

# Check transaction support
transaction_support = transaction_requirements()
```

## Single Document Transactions

### Atomic Single Document Operations

```python
def single_document_atomicity():
    """Demonstrate atomic operations on single documents"""

    print("\n=== Single Document Atomicity ===")

    # Single document operations are always atomic in MongoDB
    # No explicit transaction needed

    def atomic_account_update(account_id, amount, transaction_type):
        """Atomically update account balance with audit trail"""

        # This update is atomic - either all fields update or none do
        result = accounts.update_one(
            {"account_id": account_id},
            {
                "$inc": {"balance": amount},
                "$set": {"last_updated": datetime.utcnow()},
                "$push": {
                    "transactions": {
                        "type": transaction_type,
                        "amount": amount,
                        "timestamp": datetime.utcnow(),
                        "transaction_id": str(ObjectId())
                    }
                }
            }
        )

        return result.modified_count > 0

    # Test atomic single document update
    print("Testing atomic single document update...")

    # Get initial balance
    account = accounts.find_one({"account_id": "ACC001"})
    initial_balance = account["balance"] if account else 0

    # Perform atomic update
    success = atomic_account_update("ACC001", Decimal("100.00"), "deposit")

    if success:
        # Verify the update
        updated_account = accounts.find_one({"account_id": "ACC001"})
        new_balance = updated_account["balance"]

        print(f"✅ Atomic update successful")
        print(f"   Initial balance: ${initial_balance}")
        print(f"   New balance: ${new_balance}")
        print(f"   Difference: ${new_balance - initial_balance}")
    else:
        print("❌ Atomic update failed")

    # Demonstrate atomic operations with arrays
    def atomic_inventory_reservation(product_id, quantity):
        """Atomically reserve inventory items"""

        result = inventory.update_one(
            {
                "product_id": product_id,
                "quantity": {"$gte": quantity}  # Ensure sufficient stock
            },
            {
                "$inc": {
                    "quantity": -quantity,
                    "reserved": quantity
                },
                "$set": {"last_updated": datetime.utcnow()}
            }
        )

        return result.modified_count > 0

    # Test inventory reservation
    print("\nTesting atomic inventory reservation...")

    reservation_success = atomic_inventory_reservation("PROD001", 5)

    if reservation_success:
        print("✅ Inventory reservation successful")
        product = inventory.find_one({"product_id": "PROD001"})
        print(f"   Available: {product['quantity']}")
        print(f"   Reserved: {product['reserved']}")
    else:
        print("❌ Inventory reservation failed (insufficient stock)")

    return {
        "account_update": success,
        "inventory_reservation": reservation_success
    }

# Execute single document examples
single_doc_results = single_document_atomicity()
```

## Multi-Document Transactions

### Basic Multi-Document Transactions

```python
def basic_multi_document_transactions():
    """Basic examples of multi-document transactions"""

    print("\n=== Basic Multi-Document Transactions ===")

    def transfer_money(from_account_id, to_account_id, amount):
        """Transfer money between accounts using transaction"""

        with client.start_session() as session:
            try:
                with session.start_transaction():
                    # Check source account balance
                    from_account = accounts.find_one(
                        {"account_id": from_account_id},
                        session=session
                    )

                    if not from_account:
                        raise ValueError(f"Source account {from_account_id} not found")

                    if from_account["balance"] < amount:
                        raise ValueError("Insufficient funds")

                    # Debit from source account
                    debit_result = accounts.update_one(
                        {"account_id": from_account_id},
                        {
                            "$inc": {"balance": -amount},
                            "$set": {"last_updated": datetime.utcnow()}
                        },
                        session=session
                    )

                    if debit_result.modified_count == 0:
                        raise OperationFailure("Failed to debit source account")

                    # Credit to destination account
                    credit_result = accounts.update_one(
                        {"account_id": to_account_id},
                        {
                            "$inc": {"balance": amount},
                            "$set": {"last_updated": datetime.utcnow()}
                        },
                        session=session
                    )

                    if credit_result.modified_count == 0:
                        raise OperationFailure("Failed to credit destination account")

                    # Log the transaction
                    transaction_id = str(ObjectId())
                    audit_log.insert_one({
                        "transaction_id": transaction_id,
                        "type": "transfer",
                        "from_account": from_account_id,
                        "to_account": to_account_id,
                        "amount": amount,
                        "timestamp": datetime.utcnow(),
                        "status": "completed"
                    }, session=session)

                    # If we reach here, all operations succeeded
                    print(f"✅ Transfer completed: ${amount} from {from_account_id} to {to_account_id}")
                    print(f"   Transaction ID: {transaction_id}")

                    return transaction_id

            except Exception as e:
                print(f"❌ Transfer failed: {e}")
                # Transaction will be automatically aborted
                return None

    # Test money transfer
    print("Testing money transfer...")

    # Get initial balances
    acc1 = accounts.find_one({"account_id": "ACC001"})
    acc2 = accounts.find_one({"account_id": "ACC002"})

    print(f"Before transfer:")
    print(f"  ACC001 balance: ${acc1['balance']}")
    print(f"  ACC002 balance: ${acc2['balance']}")

    # Perform transfer
    transfer_id = transfer_money("ACC001", "ACC002", Decimal("250.00"))

    if transfer_id:
        # Check final balances
        acc1_after = accounts.find_one({"account_id": "ACC001"})
        acc2_after = accounts.find_one({"account_id": "ACC002"})

        print(f"After transfer:")
        print(f"  ACC001 balance: ${acc1_after['balance']}")
        print(f"  ACC002 balance: ${acc2_after['balance']}")

        # Verify audit log
        audit_record = audit_log.find_one({"transaction_id": transfer_id})
        print(f"  Audit log created: {audit_record is not None}")

    return transfer_id

# Execute basic transaction examples
basic_transaction_results = basic_multi_document_transactions()
```

### Complex Multi-Collection Transactions

```python
def complex_multi_collection_transactions():
    """Complex transactions involving multiple collections"""

    print("\n=== Complex Multi-Collection Transactions ===")

    def process_order(customer_account_id, order_items):
        """Process an order with inventory reservation and payment"""

        order_id = str(ObjectId())

        with client.start_session() as session:
            try:
                with session.start_transaction():
                    total_amount = Decimal("0.00")
                    reserved_items = []

                    # Step 1: Check and reserve inventory
                    for item in order_items:
                        product_id = item["product_id"]
                        quantity = item["quantity"]

                        # Get product info
                        product = inventory.find_one(
                            {"product_id": product_id},
                            session=session
                        )

                        if not product:
                            raise ValueError(f"Product {product_id} not found")

                        if product["quantity"] < quantity:
                            raise ValueError(f"Insufficient stock for {product_id}")

                        # Reserve inventory
                        reserve_result = inventory.update_one(
                            {"product_id": product_id},
                            {
                                "$inc": {
                                    "quantity": -quantity,
                                    "reserved": quantity
                                },
                                "$set": {"last_updated": datetime.utcnow()}
                            },
                            session=session
                        )

                        if reserve_result.modified_count == 0:
                            raise OperationFailure(f"Failed to reserve {product_id}")

                        item_total = product["price"] * quantity
                        total_amount += item_total

                        reserved_items.append({
                            "product_id": product_id,
                            "product_name": product["name"],
                            "quantity": quantity,
                            "unit_price": product["price"],
                            "total_price": item_total
                        })

                    # Step 2: Check customer account balance
                    customer = accounts.find_one(
                        {"account_id": customer_account_id},
                        session=session
                    )

                    if not customer:
                        raise ValueError(f"Customer account {customer_account_id} not found")

                    if customer["balance"] < total_amount:
                        raise ValueError("Insufficient funds for order")

                    # Step 3: Debit customer account
                    payment_result = accounts.update_one(
                        {"account_id": customer_account_id},
                        {
                            "$inc": {"balance": -total_amount},
                            "$set": {"last_updated": datetime.utcnow()}
                        },
                        session=session
                    )

                    if payment_result.modified_count == 0:
                        raise OperationFailure("Failed to process payment")

                    # Step 4: Create order record
                    order = {
                        "order_id": order_id,
                        "customer_account_id": customer_account_id,
                        "items": reserved_items,
                        "total_amount": total_amount,
                        "status": "confirmed",
                        "created_at": datetime.utcnow(),
                        "payment_status": "paid"
                    }

                    order_result = orders.insert_one(order, session=session)

                    if not order_result.inserted_id:
                        raise OperationFailure("Failed to create order")

                    # Step 5: Log the transaction
                    audit_log.insert_one({
                        "transaction_id": order_id,
                        "type": "order_processing",
                        "customer_account_id": customer_account_id,
                        "total_amount": total_amount,
                        "items_count": len(reserved_items),
                        "timestamp": datetime.utcnow(),
                        "status": "completed"
                    }, session=session)

                    print(f"✅ Order processed successfully")
                    print(f"   Order ID: {order_id}")
                    print(f"   Total amount: ${total_amount}")
                    print(f"   Items: {len(reserved_items)}")

                    return order_id

            except Exception as e:
                print(f"❌ Order processing failed: {e}")
                print("   All changes have been rolled back")
                return None

    # Test complex order processing
    print("Testing complex order processing...")

    order_items = [
        {"product_id": "PROD001", "quantity": 2},  # 2 Laptop Pro
        {"product_id": "PROD002", "quantity": 5}   # 5 Wireless Mouse
    ]

    # Show initial state
    customer = accounts.find_one({"account_id": "ACC003"})
    prod1 = inventory.find_one({"product_id": "PROD001"})
    prod2 = inventory.find_one({"product_id": "PROD002"})

    print(f"Before order:")
    print(f"  Customer balance: ${customer['balance']}")
    print(f"  Laptop Pro stock: {prod1['quantity']}")
    print(f"  Wireless Mouse stock: {prod2['quantity']}")

    # Process order
    order_id = process_order("ACC003", order_items)

    if order_id:
        # Show final state
        customer_after = accounts.find_one({"account_id": "ACC003"})
        prod1_after = inventory.find_one({"product_id": "PROD001"})
        prod2_after = inventory.find_one({"product_id": "PROD002"})

        print(f"After order:")
        print(f"  Customer balance: ${customer_after['balance']}")
        print(f"  Laptop Pro stock: {prod1_after['quantity']} (reserved: {prod1_after['reserved']})")
        print(f"  Wireless Mouse stock: {prod2_after['quantity']} (reserved: {prod2_after['reserved']})")

        # Show order details
        order = orders.find_one({"order_id": order_id})
        print(f"  Order status: {order['status']}")
        print(f"  Payment status: {order['payment_status']}")

    return order_id

# Execute complex transaction examples
complex_transaction_results = complex_multi_collection_transactions()
```

## Transaction Sessions

### Session Management and Options

```python
def transaction_session_management():
    """Advanced session management and transaction options"""

    print("\n=== Transaction Session Management ===")

    # Configure transaction options
    def demonstrate_transaction_options():
        """Demonstrate various transaction configuration options"""

        print("Transaction configuration options:")

        # Read Concern options
        read_concerns = {
            "local": "Default - reads local data",
            "available": "Reads available data (fastest)",
            "majority": "Reads data acknowledged by majority",
            "snapshot": "Provides snapshot isolation"
        }

        # Write Concern options
        write_concerns = {
            "w=1": "Acknowledges write to primary",
            "w='majority'": "Acknowledges write to majority of nodes",
            "j=True": "Acknowledges write to journal"
        }

        print("\nRead Concern options:")
        for concern, description in read_concerns.items():
            print(f"  {concern}: {description}")

        print("\nWrite Concern options:")
        for concern, description in write_concerns.items():
            print(f"  {concern}: {description}")

    def transaction_with_options():
        """Transaction with specific read and write concerns"""

        # Configure session options
        session_options = {
            "causal_consistency": True,  # Ensures causal consistency
            "default_transaction_read_concern": ReadConcern("snapshot"),
            "default_transaction_write_concern": WriteConcern(w="majority", j=True)
        }

        with client.start_session(**session_options) as session:
            try:
                # Start transaction with specific options
                transaction_options = {
                    "read_concern": ReadConcern("snapshot"),
                    "write_concern": WriteConcern(w="majority", j=True, wtimeout=10000),
                    "max_commit_time_ms": 30000  # 30 seconds max commit time
                }

                with session.start_transaction(**transaction_options):
                    # Perform some operations
                    account = accounts.find_one(
                        {"account_id": "ACC001"},
                        session=session
                    )

                    if account:
                        # Update with transaction
                        accounts.update_one(
                            {"account_id": "ACC001"},
                            {"$inc": {"balance": Decimal("10.00")}},
                            session=session
                        )

                        print("✅ Transaction with custom options completed")
                        return True

            except Exception as e:
                print(f"❌ Transaction with options failed: {e}")
                return False

    def manual_transaction_control():
        """Manual transaction control with explicit commit/abort"""

        print("\nTesting manual transaction control...")

        with client.start_session() as session:
            try:
                # Start transaction
                session.start_transaction()

                # Perform operations
                result1 = accounts.update_one(
                    {"account_id": "ACC002"},
                    {"$inc": {"balance": Decimal("50.00")}},
                    session=session
                )

                # Simulate a condition for rollback
                simulate_error = False  # Change to True to test rollback

                if simulate_error:
                    # Manually abort transaction
                    session.abort_transaction()
                    print("✅ Transaction manually aborted")
                    return False
                else:
                    # Manually commit transaction
                    session.commit_transaction()
                    print("✅ Transaction manually committed")
                    return True

            except Exception as e:
                # Transaction will auto-abort on exception
                print(f"❌ Manual transaction failed: {e}")
                return False

    def session_state_tracking():
        """Track session state during transactions"""

        print("\nTracking session state...")

        with client.start_session() as session:
            print(f"Session ID: {session.session_id}")
            print(f"Has ended: {session.has_ended}")
            print(f"In transaction: {session.in_transaction}")

            try:
                with session.start_transaction():
                    print(f"In transaction (after start): {session.in_transaction}")

                    # Get transaction state
                    print(f"Transaction state: {session._transaction.state}")

                    # Perform operation
                    accounts.find_one({"account_id": "ACC001"}, session=session)

                    print("✅ Session state tracking completed")

            except Exception as e:
                print(f"❌ Session state tracking failed: {e}")

            finally:
                print(f"In transaction (after end): {session.in_transaction}")
                print(f"Has ended: {session.has_ended}")

    # Execute session management examples
    demonstrate_transaction_options()
    options_result = transaction_with_options()
    manual_result = manual_transaction_control()
    session_state_tracking()

    return {
        "options_result": options_result,
        "manual_result": manual_result
    }

# Execute session management examples
session_mgmt_results = transaction_session_management()
```

## Error Handling and Retry Logic

### Comprehensive Error Handling

```python
def transaction_error_handling():
    """Comprehensive error handling for transactions"""

    print("\n=== Transaction Error Handling ===")

    def handle_transient_transaction_errors(operation_func, max_retries=3):
        """Handle transient transaction errors with retry logic"""

        for attempt in range(max_retries):
            try:
                with client.start_session() as session:
                    with session.start_transaction():
                        # Execute the operation function
                        result = operation_func(session)
                        return result

            except PyMongoError as e:
                error_labels = getattr(e, 'error_labels', [])

                if "TransientTransactionError" in error_labels:
                    print(f"⚠ Transient error on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        print(f"❌ Max retries ({max_retries}) exceeded for transient error")
                        raise

                elif "UnknownTransactionCommitResult" in error_labels:
                    print(f"⚠ Unknown commit result on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(0.1 * (2 ** attempt))
                        continue
                    else:
                        print(f"❌ Max retries ({max_retries}) exceeded for unknown commit")
                        raise

                else:
                    # Non-transient error, don't retry
                    print(f"❌ Non-transient error: {e}")
                    raise

            except Exception as e:
                # Non-MongoDB error, don't retry
                print(f"❌ Non-MongoDB error: {e}")
                raise

        return None

    def example_operation_with_potential_conflicts(session):
        """Example operation that might have conflicts"""

        # Simulate high contention operation
        account = accounts.find_one({"account_id": "ACC001"}, session=session)

        if not account:
            raise ValueError("Account not found")

        # Add artificial delay to increase chance of conflict
        time.sleep(0.01)

        # Update account
        result = accounts.update_one(
            {"account_id": "ACC001"},
            {
                "$inc": {"balance": Decimal("1.00")},
                "$set": {"last_updated": datetime.utcnow()}
            },
            session=session
        )

        if result.modified_count == 0:
            raise OperationFailure("Failed to update account")

        return result.modified_count

    def test_concurrent_transactions():
        """Test handling of concurrent transaction conflicts"""

        print("Testing concurrent transaction handling...")

        def concurrent_operation(thread_id):
            """Operation to run concurrently"""
            try:
                result = handle_transient_transaction_errors(
                    example_operation_with_potential_conflicts
                )
                print(f"✅ Thread {thread_id}: Transaction completed")
                return True
            except Exception as e:
                print(f"❌ Thread {thread_id}: Transaction failed - {e}")
                return False

        # Start multiple threads to create contention
        threads = []
        results = []

        for i in range(5):
            thread = threading.Thread(
                target=lambda tid=i: results.append(concurrent_operation(tid))
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        successful = sum(1 for r in results if r)
        print(f"Concurrent operations: {successful}/{len(results)} successful")

        return successful

    def handle_specific_transaction_errors():
        """Handle specific types of transaction errors"""

        print("\nTesting specific error handling...")

        def operation_with_insufficient_funds(session):
            """Operation that will fail due to business logic"""

            # Try to transfer more money than available
            account = accounts.find_one({"account_id": "ACC001"}, session=session)

            if account["balance"] < Decimal("10000.00"):  # Intentionally large amount
                raise ValueError("Insufficient funds")

            # This won't be reached
            accounts.update_one(
                {"account_id": "ACC001"},
                {"$inc": {"balance": -Decimal("10000.00")}},
                session=session
            )

            return True

        try:
            result = handle_transient_transaction_errors(operation_with_insufficient_funds)
            print("❌ This should not have succeeded")
        except ValueError as e:
            print(f"✅ Business logic error handled correctly: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    def timeout_handling():
        """Handle transaction timeouts"""

        print("\nTesting timeout handling...")

        def slow_operation(session):
            """Operation that might timeout"""

            # Simulate slow operation
            time.sleep(0.1)

            # Simple update
            result = accounts.update_one(
                {"account_id": "ACC002"},
                {"$inc": {"balance": Decimal("1.00")}},
                session=session
            )

            return result.modified_count

        try:
            # Set a very short timeout to test timeout handling
            with client.start_session() as session:
                with session.start_transaction(
                    write_concern=WriteConcern(w="majority", wtimeout=1)  # 1ms timeout
                ):
                    result = slow_operation(session)
                    print(f"✅ Slow operation completed: {result}")

        except PyMongoError as e:
            if "timeout" in str(e).lower():
                print(f"✅ Timeout handled correctly: {e}")
            else:
                print(f"❌ Unexpected error: {e}")

    # Execute error handling examples
    concurrent_success = test_concurrent_transactions()
    handle_specific_transaction_errors()
    timeout_handling()

    return {
        "concurrent_success": concurrent_success
    }

# Execute error handling examples
error_handling_results = transaction_error_handling()
```

### Retry Patterns and Best Practices

```python
def transaction_retry_patterns():
    """Advanced retry patterns for transactions"""

    print("\n=== Transaction Retry Patterns ===")

    class TransactionRetryHelper:
        """Helper class for transaction retry logic"""

        def __init__(self, max_retries=3, base_delay=0.1, max_delay=2.0):
            self.max_retries = max_retries
            self.base_delay = base_delay
            self.max_delay = max_delay

        def exponential_backoff(self, attempt):
            """Calculate exponential backoff delay"""
            delay = self.base_delay * (2 ** attempt)
            return min(delay, self.max_delay)

        def should_retry_error(self, error):
            """Determine if an error should trigger a retry"""

            if isinstance(error, PyMongoError):
                error_labels = getattr(error, 'error_labels', [])

                # Retry transient errors
                if "TransientTransactionError" in error_labels:
                    return True

                # Retry unknown commit results
                if "UnknownTransactionCommitResult" in error_labels:
                    return True

                # Check for specific error codes that indicate retryable conditions
                error_code = getattr(error, 'code', None)
                retryable_codes = [
                    11601,  # InterruptedAtShutdown
                    11602,  # Interrupted
                    10107,  # NotMaster
                    13435,  # NotMasterNoSlaveOk
                    91,     # ShutdownInProgress
                    189,    # PrimarySteppedDown
                ]

                if error_code in retryable_codes:
                    return True

            return False

        def execute_with_retry(self, operation_func, session_options=None):
            """Execute operation with retry logic"""

            last_error = None

            for attempt in range(self.max_retries):
                try:
                    session_opts = session_options or {}

                    with client.start_session(**session_opts) as session:
                        with session.start_transaction():
                            result = operation_func(session)
                            return result

                except Exception as e:
                    last_error = e

                    if self.should_retry_error(e):
                        if attempt < self.max_retries - 1:
                            delay = self.exponential_backoff(attempt)
                            print(f"⚠ Retryable error on attempt {attempt + 1}, "
                                  f"retrying in {delay:.2f}s: {e}")
                            time.sleep(delay)
                            continue
                        else:
                            print(f"❌ Max retries exceeded: {e}")
                    else:
                        print(f"❌ Non-retryable error: {e}")

                    raise last_error

            # Should not reach here
            raise last_error

    # Test the retry helper
    def test_retry_helper():
        """Test the transaction retry helper"""

        retry_helper = TransactionRetryHelper(max_retries=3)

        def reliable_transfer_operation(session):
            """A transfer operation that might fail transiently"""

            # Simulate occasional transient failures
            import random
            if random.random() < 0.3:  # 30% chance of simulated failure
                # Simulate a transient network error
                error = PyMongoError("Connection lost")
                error.error_labels = ["TransientTransactionError"]
                raise error

            # Perform actual transfer
            from_account = accounts.find_one({"account_id": "ACC001"}, session=session)
            to_account = accounts.find_one({"account_id": "ACC002"}, session=session)

            if not from_account or not to_account:
                raise ValueError("Account not found")

            transfer_amount = Decimal("5.00")

            if from_account["balance"] < transfer_amount:
                raise ValueError("Insufficient funds")

            # Debit and credit
            accounts.update_one(
                {"account_id": "ACC001"},
                {"$inc": {"balance": -transfer_amount}},
                session=session
            )

            accounts.update_one(
                {"account_id": "ACC002"},
                {"$inc": {"balance": transfer_amount}},
                session=session
            )

            return transfer_amount

        print("Testing retry helper with simulated failures...")

        try:
            result = retry_helper.execute_with_retry(reliable_transfer_operation)
            print(f"✅ Transfer completed with retry logic: ${result}")
            return True
        except Exception as e:
            print(f"❌ Transfer failed after retries: {e}")
            return False

    def circuit_breaker_pattern():
        """Implement circuit breaker pattern for transactions"""

        class TransactionCircuitBreaker:
            def __init__(self, failure_threshold=5, recovery_timeout=30):
                self.failure_threshold = failure_threshold
                self.recovery_timeout = recovery_timeout
                self.failure_count = 0
                self.last_failure_time = None
                self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

            def can_execute(self):
                """Check if operation can be executed"""

                if self.state == "CLOSED":
                    return True
                elif self.state == "OPEN":
                    if (datetime.utcnow() - self.last_failure_time).seconds > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                        return True
                    return False
                elif self.state == "HALF_OPEN":
                    return True

                return False

            def record_success(self):
                """Record successful operation"""
                self.failure_count = 0
                self.state = "CLOSED"

            def record_failure(self):
                """Record failed operation"""
                self.failure_count += 1
                self.last_failure_time = datetime.utcnow()

                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    print(f"⚠ Circuit breaker opened after {self.failure_count} failures")

        circuit_breaker = TransactionCircuitBreaker()

        def protected_operation():
            """Operation protected by circuit breaker"""

            if not circuit_breaker.can_execute():
                raise Exception("Circuit breaker is OPEN - operation rejected")

            try:
                # Simulate operation
                with client.start_session() as session:
                    with session.start_transaction():
                        accounts.find_one({"account_id": "ACC001"}, session=session)

                circuit_breaker.record_success()
                return True

            except Exception as e:
                circuit_breaker.record_failure()
                raise

        print("\\nTesting circuit breaker pattern...")

        # Simulate some failures and successes
        for i in range(10):
            try:
                result = protected_operation()
                print(f"✅ Operation {i+1} succeeded")
            except Exception as e:
                print(f"❌ Operation {i+1} failed: {e}")

        return circuit_breaker.state

    # Execute retry pattern examples
    retry_success = test_retry_helper()
    circuit_state = circuit_breaker_pattern()

    return {
        "retry_success": retry_success,
        "circuit_state": circuit_state
    }

# Execute retry pattern examples
retry_results = transaction_retry_patterns()
```

## Performance Considerations

### Transaction Performance Optimization

```python
def transaction_performance_optimization():
    """Optimize transaction performance"""

    print("\n=== Transaction Performance Optimization ===")

    def measure_transaction_performance():
        """Measure and compare transaction performance"""

        def simple_operation():
            """Simple single-document operation"""
            start_time = time.time()

            accounts.update_one(
                {"account_id": "ACC001"},
                {"$inc": {"balance": Decimal("1.00")}}
            )

            return time.time() - start_time

        def transaction_operation():
            """Same operation within transaction"""
            start_time = time.time()

            with client.start_session() as session:
                with session.start_transaction():
                    accounts.update_one(
                        {"account_id": "ACC001"},
                        {"$inc": {"balance": Decimal("1.00")}},
                        session=session
                    )

            return time.time() - start_time

        def batch_operation():
            """Batch multiple operations in single transaction"""
            start_time = time.time()

            with client.start_session() as session:
                with session.start_transaction():
                    for i in range(10):
                        accounts.update_one(
                            {"account_id": "ACC001"},
                            {"$inc": {"balance": Decimal("0.10")}},
                            session=session
                        )

            return time.time() - start_time

        def separate_operations():
            """Same operations separately"""
            start_time = time.time()

            for i in range(10):
                accounts.update_one(
                    {"account_id": "ACC001"},
                    {"$inc": {"balance": Decimal("0.10")}}
                )

            return time.time() - start_time

        # Warm up
        simple_operation()
        transaction_operation()

        # Measure performance
        simple_time = simple_operation()
        transaction_time = transaction_operation()
        batch_time = batch_operation()
        separate_time = separate_operations()

        print("Performance comparison:")
        print(f"  Simple operation: {simple_time*1000:.2f}ms")
        print(f"  Transaction operation: {transaction_time*1000:.2f}ms")
        print(f"  Overhead: {((transaction_time/simple_time)-1)*100:.1f}%")
        print()
        print(f"  Batch in transaction: {batch_time*1000:.2f}ms")
        print(f"  Separate operations: {separate_time*1000:.2f}ms")
        print(f"  Batch efficiency: {((separate_time/batch_time)-1)*100:.1f}% faster")

        return {
            "simple_time": simple_time,
            "transaction_time": transaction_time,
            "batch_time": batch_time,
            "separate_time": separate_time
        }

    def optimization_techniques():
        """Demonstrate transaction optimization techniques"""

        print("\\nTransaction optimization techniques:")

        # 1. Minimize transaction scope
        print("1. ✅ Minimize transaction scope")
        print("   - Keep transactions short")
        print("   - Do preparation work outside transaction")
        print("   - Only include operations that need atomicity")

        # 2. Use appropriate read/write concerns
        print("\\n2. ✅ Use appropriate read/write concerns")
        print("   - Use 'local' read concern for better performance when appropriate")
        print("   - Use w=1 write concern for better performance when appropriate")
        print("   - Balance consistency vs performance needs")

        # 3. Batch operations
        print("\\n3. ✅ Batch operations when possible")
        print("   - Combine multiple operations in single transaction")
        print("   - Use bulk operations where appropriate")
        print("   - Reduce network round trips")

        # 4. Index optimization
        print("\\n4. ✅ Optimize indexes for transaction queries")
        print("   - Ensure queries within transactions use indexes")
        print("   - Monitor query performance with explain()")
        print("   - Consider compound indexes for multi-field queries")

        # 5. Connection pooling
        print("\\n5. ✅ Optimize connection pooling")
        print("   - Use appropriate pool size")
        print("   - Monitor connection usage")
        print("   - Consider separate pools for transactional vs non-transactional operations")

    def anti_patterns():
        """Common transaction anti-patterns to avoid"""

        print("\\nTransaction anti-patterns to avoid:")

        print("❌ Long-running transactions")
        print("   - Avoid operations that take > 60 seconds")
        print("   - Break large operations into smaller transactions")

        print("❌ Unnecessary transactions")
        print("   - Don't use transactions for single document operations")
        print("   - Only use when you need multi-document atomicity")

        print("❌ Hot spotting")
        print("   - Avoid frequent updates to same documents")
        print("   - Distribute load across different documents/shards")

        print("❌ Large transactions")
        print("   - Avoid transactions > 16MB")
        print("   - Monitor transaction size")

        print("❌ DDL operations in transactions")
        print("   - Cannot create/drop collections in transactions")
        print("   - Cannot create indexes in transactions")

    # Execute performance examples
    performance_results = measure_transaction_performance()
    optimization_techniques()
    anti_patterns()

    return performance_results

# Execute performance optimization examples
performance_results = transaction_performance_optimization()
```

## Real-World Examples

### E-commerce Order Processing System

```python
def ecommerce_transaction_system():
    """Complete e-commerce order processing with transactions"""

    print("\n=== E-commerce Transaction System ===")

    class OrderProcessor:
        """Complete order processing system using transactions"""

        def __init__(self, db):
            self.db = db
            self.accounts = db.accounts
            self.inventory = db.inventory
            self.orders = db.orders
            self.audit_log = db.audit_log
            self.promotions = db.promotions

        def validate_order(self, customer_id, items, promotion_code=None):
            """Validate order before processing"""

            validation_errors = []

            # Check customer exists
            customer = self.accounts.find_one({"account_id": customer_id})
            if not customer:
                validation_errors.append(f"Customer {customer_id} not found")

            # Check item availability and calculate total
            total_amount = Decimal("0.00")

            for item in items:
                product = self.inventory.find_one({"product_id": item["product_id"]})

                if not product:
                    validation_errors.append(f"Product {item['product_id']} not found")
                    continue

                if product["quantity"] < item["quantity"]:
                    validation_errors.append(
                        f"Insufficient stock for {item['product_id']} "
                        f"(requested: {item['quantity']}, available: {product['quantity']})"
                    )

                total_amount += product["price"] * item["quantity"]

            # Validate promotion code
            discount_amount = Decimal("0.00")
            if promotion_code:
                promotion = self.promotions.find_one({
                    "code": promotion_code,
                    "active": True,
                    "expires_at": {"$gte": datetime.utcnow()}
                })

                if promotion:
                    if promotion["type"] == "percentage":
                        discount_amount = total_amount * (promotion["value"] / 100)
                    elif promotion["type"] == "fixed":
                        discount_amount = min(promotion["value"], total_amount)
                else:
                    validation_errors.append(f"Invalid or expired promotion code: {promotion_code}")

            final_amount = total_amount - discount_amount

            # Check customer balance
            if customer and customer["balance"] < final_amount:
                validation_errors.append(
                    f"Insufficient funds (balance: ${customer['balance']}, required: ${final_amount})"
                )

            return {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "total_amount": total_amount,
                "discount_amount": discount_amount,
                "final_amount": final_amount
            }

        def process_order_with_retry(self, customer_id, items, promotion_code=None, max_retries=3):
            """Process order with automatic retry logic"""

            # Pre-validate order (outside transaction)
            validation = self.validate_order(customer_id, items, promotion_code)

            if not validation["valid"]:
                raise ValueError(f"Order validation failed: {', '.join(validation['errors'])}")

            # Retry logic for transaction
            for attempt in range(max_retries):
                try:
                    return self._process_order_transaction(
                        customer_id, items, promotion_code, validation
                    )

                except PyMongoError as e:
                    error_labels = getattr(e, 'error_labels', [])

                    if "TransientTransactionError" in error_labels and attempt < max_retries - 1:
                        print(f"⚠ Transient error on attempt {attempt + 1}, retrying...")
                        time.sleep(0.1 * (2 ** attempt))
                        continue
                    else:
                        raise

            raise Exception("Order processing failed after maximum retries")

        def _process_order_transaction(self, customer_id, items, promotion_code, validation):
            """Internal method to process order within transaction"""

            order_id = str(ObjectId())

            with client.start_session() as session:
                with session.start_transaction(
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern(w="majority", j=True)
                ):
                    # Re-validate critical conditions within transaction
                    customer = self.accounts.find_one(
                        {"account_id": customer_id},
                        session=session
                    )

                    if customer["balance"] < validation["final_amount"]:
                        raise ValueError("Insufficient funds (balance changed)")

                    # Reserve inventory
                    reserved_items = []

                    for item in items:
                        product = self.inventory.find_one(
                            {"product_id": item["product_id"]},
                            session=session
                        )

                        if product["quantity"] < item["quantity"]:
                            raise ValueError(f"Insufficient stock for {item['product_id']} (stock changed)")

                        # Reserve inventory
                        reserve_result = self.inventory.update_one(
                            {"product_id": item["product_id"]},
                            {
                                "$inc": {
                                    "quantity": -item["quantity"],
                                    "reserved": item["quantity"]
                                }
                            },
                            session=session
                        )

                        if reserve_result.modified_count == 0:
                            raise OperationFailure(f"Failed to reserve {item['product_id']}")

                        reserved_items.append({
                            "product_id": item["product_id"],
                            "product_name": product["name"],
                            "quantity": item["quantity"],
                            "unit_price": product["price"],
                            "total_price": product["price"] * item["quantity"]
                        })

                    # Process payment
                    payment_result = self.accounts.update_one(
                        {"account_id": customer_id},
                        {
                            "$inc": {"balance": -validation["final_amount"]},
                            "$set": {"last_updated": datetime.utcnow()}
                        },
                        session=session
                    )

                    if payment_result.modified_count == 0:
                        raise OperationFailure("Payment processing failed")

                    # Update promotion usage
                    if promotion_code:
                        self.promotions.update_one(
                            {"code": promotion_code},
                            {"$inc": {"usage_count": 1}},
                            session=session
                        )

                    # Create order record
                    order = {
                        "order_id": order_id,
                        "customer_id": customer_id,
                        "items": reserved_items,
                        "subtotal": validation["total_amount"],
                        "discount": validation["discount_amount"],
                        "total": validation["final_amount"],
                        "promotion_code": promotion_code,
                        "status": "confirmed",
                        "payment_status": "paid",
                        "created_at": datetime.utcnow(),
                        "estimated_delivery": datetime.utcnow() + timedelta(days=3)
                    }

                    order_result = self.orders.insert_one(order, session=session)

                    # Create audit log
                    self.audit_log.insert_one({
                        "transaction_id": order_id,
                        "type": "order_processed",
                        "customer_id": customer_id,
                        "amount": validation["final_amount"],
                        "items_count": len(items),
                        "promotion_used": promotion_code is not None,
                        "timestamp": datetime.utcnow(),
                        "status": "success"
                    }, session=session)

                    print(f"✅ Order {order_id} processed successfully")
                    print(f"   Customer: {customer_id}")
                    print(f"   Total: ${validation['final_amount']}")
                    print(f"   Items: {len(reserved_items)}")

                    return {
                        "order_id": order_id,
                        "status": "success",
                        "total": validation["final_amount"],
                        "items": reserved_items
                    }

    # Setup promotion data
    promotions = db.promotions
    promotions.delete_many({})
    promotions.insert_one({
        "code": "SAVE10",
        "type": "percentage",
        "value": 10,
        "active": True,
        "expires_at": datetime.utcnow() + timedelta(days=30),
        "usage_count": 0
    })

    # Test the order processing system
    processor = OrderProcessor(db)

    # Test successful order
    test_items = [
        {"product_id": "PROD001", "quantity": 1},
        {"product_id": "PROD002", "quantity": 2}
    ]

    try:
        result = processor.process_order_with_retry(
            "ACC003",
            test_items,
            promotion_code="SAVE10"
        )
        print(f"Order processing result: {result['status']}")

    except Exception as e:
        print(f"❌ Order processing failed: {e}")

    # Test order with insufficient funds
    expensive_items = [
        {"product_id": "PROD001", "quantity": 10}  # Too expensive
    ]

    try:
        result = processor.process_order_with_retry("ACC002", expensive_items)
        print("❌ This should have failed")
    except ValueError as e:
        print(f"✅ Order correctly rejected: {e}")

    return processor

# Execute e-commerce example
ecommerce_processor = ecommerce_transaction_system()
```

## Best Practices

### Transaction Best Practices Summary

```python
def transaction_best_practices_summary():
    """Comprehensive transaction best practices"""

    print("\n=== Transaction Best Practices Summary ===")

    best_practices = {
        "design": [
            "Use transactions only when you need multi-document atomicity",
            "Keep transactions as short as possible",
            "Minimize the number of operations in a transaction",
            "Do preparation work outside the transaction",
            "Design for idempotency when possible"
        ],

        "performance": [
            "Use appropriate read and write concerns",
            "Optimize queries with proper indexing",
            "Batch related operations together",
            "Avoid hot spotting on frequently updated documents",
            "Monitor transaction duration and size"
        ],

        "error_handling": [
            "Implement retry logic for transient errors",
            "Use exponential backoff for retries",
            "Handle business logic errors gracefully",
            "Implement circuit breaker patterns for resilience",
            "Log transaction failures for monitoring"
        ],

        "concurrency": [
            "Design to minimize write conflicts",
            "Use optimistic concurrency when appropriate",
            "Consider document design to reduce contention",
            "Implement proper isolation levels",
            "Test under concurrent load"
        ],

        "monitoring": [
            "Monitor transaction success/failure rates",
            "Track transaction duration and size",
            "Set up alerts for transaction failures",
            "Monitor for lock contention",
            "Use profiler to identify slow transactions"
        ]
    }

    for category, practices in best_practices.items():
        print(f"\n{category.upper()} BEST PRACTICES:")
        print("=" * 40)
        for practice in practices:
            print(f"✅ {practice}")

    # Common pitfalls to avoid
    print("\n\nCOMMON PITFALLS TO AVOID:")
    print("=" * 40)
    pitfalls = [
        "Using transactions for single document operations",
        "Creating very long-running transactions",
        "Ignoring transient error retry logic",
        "Not validating business rules within transactions",
        "Performing DDL operations within transactions",
        "Not monitoring transaction performance",
        "Poor error handling and logging",
        "Not testing under concurrent load"
    ]

    for pitfall in pitfalls:
        print(f"❌ {pitfall}")

    # Transaction checklist
    print("\n\nTRANSACTION IMPLEMENTATION CHECKLIST:")
    print("=" * 40)
    checklist = [
        "Identified operations that need atomicity",
        "Designed for minimal transaction scope",
        "Implemented proper error handling",
        "Added retry logic for transient errors",
        "Validated business rules within transactions",
        "Optimized queries with proper indexes",
        "Tested under concurrent load",
        "Set up monitoring and alerting",
        "Documented transaction boundaries",
        "Planned for rollback scenarios"
    ]

    for item in checklist:
        print(f"□ {item}")

    return best_practices

# Execute best practices summary
best_practices = transaction_best_practices_summary()
```

## Summary and Next Steps

This comprehensive guide covered:

1. **Transaction Fundamentals** - ACID properties and requirements
2. **Single Document Transactions** - Atomic operations
3. **Multi-Document Transactions** - Complex multi-collection operations
4. **Session Management** - Advanced session configuration
5. **Error Handling** - Comprehensive error handling and retry patterns
6. **Performance Optimization** - Transaction performance best practices
7. **Real-World Examples** - Complete e-commerce order processing system
8. **Best Practices** - Comprehensive guidelines and checklists

### Key Takeaways

- **Use transactions judiciously** - Only when you need multi-document atomicity
- **Keep transactions short** - Minimize scope and duration
- **Handle errors properly** - Implement retry logic for transient errors
- **Design for concurrency** - Minimize write conflicts and hot spots
- **Monitor performance** - Track transaction metrics and optimize accordingly

### Next Steps

1. **GridFS**: [File Storage with GridFS](./04_gridfs.md)
2. **Text Search**: [Full-Text Search](./05_text_search.md)
3. **Performance Optimization**: [Advanced Performance Tuning](./07_performance_optimization.md)
4. **Monitoring**: [Database Monitoring](./10_monitoring_logging.md)

### Additional Resources

- [MongoDB Transactions Documentation](https://docs.mongodb.com/manual/core/transactions/)
- [PyMongo Transactions Guide](https://pymongo.readthedocs.io/en/stable/api/pymongo/client_session.html)
- [Transaction Best Practices](https://docs.mongodb.com/manual/core/transactions-production-consideration/)
- [ACID Properties in MongoDB](https://docs.mongodb.com/manual/core/write-operations-atomicity/)
