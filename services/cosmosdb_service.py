import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from config.settings import COSMOS_DB_ENDPOINT, COSMOS_DB_KEY
# Assuming utils.logger provides a configured logger instance
# If not, we'll need to set up basic logging here or ensure logger is available.
# For now, let's try to import it and handle potential import error if it's not structured as expected.
try:
    from utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO) # Basic config if custom logger not found

# --- Client, Database, and Container Initialization ---
_client = None
DATABASE_NAME = "TradingBotDB"
TRADE_HISTORY_CONTAINER_NAME = "TradeHistory"
# Define the partition key path for the trade history container.
# Each document in this container should have an 'id' field that is unique.
# Or, if you plan to query often by symbol, /symbol might be better.
# For now, using /id assumes each trade document gets a unique GUID or similar as 'id'.
TRADE_HISTORY_PARTITION_KEY_PATH = "/id"

def _get_cosmos_client():
    """Initializes and returns a singleton CosmosClient instance."""
    global _client
    if _client is None:
        if not COSMOS_DB_ENDPOINT or not COSMOS_DB_KEY:
            logger.error("Cosmos DB endpoint or key is not configured. Please check your .env file.")
            raise ValueError("Cosmos DB endpoint or key is not configured.")
        try:
            _client = cosmos_client.CosmosClient(COSMOS_DB_ENDPOINT, {'masterKey': COSMOS_DB_KEY})
            logger.info("Cosmos DB client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB client: {e}")
            raise
    return _client

def get_or_create_database(database_name=DATABASE_NAME):
    """Gets a database by its ID or creates it if it doesn't exist."""
    client = _get_cosmos_client()
    try:
        database = client.get_database_client(database_name)
        database.read() # Check if database exists
        logger.info(f"Database '{database_name}' found.")
        return database
    except exceptions.CosmosResourceNotFoundError:
        logger.info(f"Database '{database_name}' not found. Creating it...")
        try:
            database = client.create_database(database_name)
            logger.info(f"Database '{database_name}' created successfully.")
            return database
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Error creating database '{database_name}': {e.message}")
            raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while getting/creating database '{database_name}': {e}")
        raise

def get_or_create_container(database_client, container_name, partition_key_path):
    """
    Gets a container by its ID within a given database
    or creates it if it doesn't exist.
    """
    try:
        container = database_client.get_container_client(container_name)
        container.read() # Check if container exists
        logger.info(f"Container '{container_name}' found in database '{database_client.id}'.")
        return container
    except exceptions.CosmosResourceNotFoundError:
        logger.info(f"Container '{container_name}' not found in database '{database_client.id}'. Creating it...")
        try:
            container = database_client.create_container(
                id=container_name,
                partition_key=PartitionKey(path=partition_key_path)
            )
            logger.info(f"Container '{container_name}' created successfully in database '{database_client.id}'.")
            return container
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Error creating container '{container_name}': {e.message}")
            raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while getting/creating container '{container_name}': {e}")
        raise

def create_item(container_client, item_document):
    """Creates a new item (document) in the specified container.

    Args:
        container_client: The Cosmos DB container client.
        item_document (dict): The document to be created.
                              It MUST contain a field corresponding to the partition_key_path
                              (e.g., 'id' if partition_key_path is '/id').
    Returns:
        dict: The created item.
    """
    if not isinstance(item_document, dict):
        logger.error("Item document must be a dictionary.")
        raise ValueError("Item document must be a dictionary.")

    # Ensure partition key field exists in the document
    # e.g., if TRADE_HISTORY_PARTITION_KEY_PATH is "/id", item_document must have an "id" key.
    # This check is simplified; a more robust check would parse the path.
    pk_field_name = TRADE_HISTORY_PARTITION_KEY_PATH.lstrip('/')
    if pk_field_name not in item_document:
        logger.error(f"Item document is missing the partition key field '{pk_field_name}'.")
        raise ValueError(f"Item document is missing the partition key field '{pk_field_name}'.")

    try:
        created_item = container_client.create_item(body=item_document)
        logger.info(f"Item created successfully with id '{created_item.get('id', 'N/A')}' in container '{container_client.id}'.")
        return created_item
    except exceptions.CosmosHttpResponseError as e:
        logger.error(f"Error creating item in container '{container_client.id}': {e.message}")
        # Consider if specific error codes need different handling (e.g., 409 Conflict if item with same id already exists)
        raise

def query_items(container_client, query_text, parameters=None, enable_cross_partition_query=True):
    """Queries items in the container using a SQL-like query.

    Args:
        container_client: The Cosmos DB container client.
        query_text (str): The SQL-like query string.
        parameters (list, optional): A list of parameters for parameterized queries. Defaults to None.
        enable_cross_partition_query (bool, optional): Allows queries to span multiple partitions.
                                                     Set to True if your query doesn't filter by the partition key.
                                                     Defaults to True for flexibility, but be mindful of RU consumption.
    Returns:
        list: A list of items matching the query.
    """
    try:
        items = list(container_client.query_items(
            query=query_text,
            parameters=parameters,
            enable_cross_partition_query=enable_cross_partition_query
        ))
        logger.info(f"Query executed successfully in container '{container_client.id}'. Found {len(items)} items.")
        return items
    except exceptions.CosmosHttpResponseError as e:
        logger.error(f"Error querying items in container '{container_client.id}': {e.message}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while querying items: {e}")
        raise

# --- Example Usage / Initialization ---
# You might want a function to initialize and get the specific container for trade history easily.
def get_trade_history_container():
    """Initializes and returns the TradeHistory container client."""
    db_client = get_or_create_database(DATABASE_NAME)
    return get_or_create_container(db_client, TRADE_HISTORY_CONTAINER_NAME, TRADE_HISTORY_PARTITION_KEY_PATH)

if __name__ == '__main__':
    # This is example usage code, primarily for testing this module directly.
    # Ensure your .env file is populated with COSMOS_DB_ENDPOINT and COSMOS_DB_KEY.
    logger.info("Attempting to connect to Cosmos DB and ensure database/container exist...")

    try:
        trade_history_container = get_trade_history_container()
        if trade_history_container:
            logger.info(f"Successfully obtained container client for '{TRADE_HISTORY_CONTAINER_NAME}'.")

            # Example: Create a dummy trade item
            # For this to work, the item_document MUST have an 'id' field because partition_key_path="/id"
            import uuid
            dummy_trade = {
                "id": str(uuid.uuid4()), # This will be the partition key value
                "symbol": "BTC/USDT",
                "timestamp": "2023-10-27T10:00:00Z",
                "type": "buy",
                "price": 34000.00,
                "quantity": 0.001,
                "status": "filled"
            }

            logger.info(f"Attempting to create a dummy trade item: {dummy_trade}")
            # created_item = create_item(trade_history_container, dummy_trade)
            # logger.info(f"Dummy trade item created: {created_item.get('id')}")

            # Example: Query items
            # logger.info("Attempting to query all items...")
            # all_items = query_items(trade_history_container, "SELECT * FROM c")
            # for item in all_items:
            #     logger.info(f"  Item: {item.get('id')}, Symbol: {item.get('symbol')}")

            logger.info("Example operations (commented out by default to prevent accidental writes).")
            logger.info("To test, uncomment the create_item and query_items calls above and run this script directly.")

        else:
            logger.error("Failed to obtain trade history container.")

    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
    except Exception as e:
        logger.error(f"An error occurred during the example usage: {e}", exc_info=True)
