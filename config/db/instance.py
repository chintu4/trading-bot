import warnings
from urllib3.exceptions import InsecureRequestWarning
import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import time  # Import time module for timestamp

# Suppress insecure HTTPS warnings when using emulator
warnings.simplefilter('ignore', InsecureRequestWarning)

class CosmosDBClient:
    """A client for Azure Cosmos DB operations for the trading platform."""
    
    def __init__(self, endpoint=None, key=None, database_name=None, container_name=None):
        """
        Initialize the Cosmos DB client.
        
        Args:
            endpoint: Cosmos DB endpoint URL
            key: Cosmos DB access key
            database_name: Name of the database to use
            container_name: Name of the container to use
        """
        # Use parameters or fallback to environment variables or defaults
        self.endpoint = endpoint or os.getenv("COSMOS_ENDPOINT", "https://localhost:8081")
        self.key = key or os.getenv("COSMOS_KEY", 
                                   "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==")
        self.database_name = database_name or os.getenv("COSMOS_DB", "trading-bot")
        self.container_name = container_name or os.getenv("COSMOS_CONTAINER", "trading-bot-container")
        
        # Check if using emulator to disable SSL verification
        self.is_emulator = "localhost" in self.endpoint
        self.client = CosmosClient(
            self.endpoint, 
            self.key,
            connection_verify=not self.is_emulator
        )
        
        self.database = None
        self.container = None
        
    def initialize(self, partition_key_path="/id"):
        """
        Initialize database and container.
        
        Args:
            partition_key_path: Path to the partition key in the documents
            
        Returns:
            Container client
        """
        try:
            self.database = self.client.create_database_if_not_exists(id=self.database_name)
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error creating database: {e}")
            self.database = self.client.get_database_client(self.database_name)
            
        try:
            self.container = self.database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path=partition_key_path),
                offer_throughput=400
            )
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error creating container: {e}")
            self.container = self.database.get_container_client(self.container_name)
            
        return self.container
    
    # In the create_item method, add error handling for duplicates
    def create_item(self, item):
        """
        Create a new item in the container.
        
        Args:
            item: Dictionary containing the item to create
            
        Returns:
            Created item or existing item if duplicate
        """
        if not self.container:
            self.initialize()
        
        try:
            return self.container.create_item(body=item)
        except exceptions.CosmosResourceExistsError:
            print(f"Item with ID '{item['id']}' already exists. Retrieving existing item.")
            # Get the existing item using its ID and partition key value
            partition_key_field = self.container.partition_key_path.strip('/')
            return self.get_item(item["id"], item[partition_key_field])
    
    def query_items(self, query, parameters=None, partition_key=None):
        """
        Query items from the container.
        
        Args:
            query: SQL query string
            parameters: List of parameters for the query
            partition_key: Optional partition key value to optimize query
            
        Returns:
            List of items matching the query
        """
        if not self.container:
            self.initialize()
            
        query_options = {
            "enable_cross_partition_query": partition_key is None
        }
        
        if partition_key:
            query_options["partition_key"] = partition_key
        
        return list(self.container.query_items(
            query=query,
            parameters=parameters,
            **query_options
        ))
        
    def get_item(self, item_id, partition_key):
        """
        Get a single item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            partition_key: Partition key value of the item
            
        Returns:
            The item if found, None otherwise
        """
        if not self.container:
            self.initialize()
            
        try:
            return self.container.read_item(item=item_id, partition_key=partition_key)
        except exceptions.CosmosHttpResponseError:
            return None
            
    def update_item(self, item):
        """
        Update an existing item.
        
        Args:
            item: Item with updated values (must include id)
            
        Returns:
            The updated item
        """
        if not self.container:
            self.initialize()
            
        return self.container.replace_item(
            item=item["id"], 
            body=item
        )
    
    def delete_item(self, item_id, partition_key):
        """
        Delete an item from the container.
        
        Args:
            item_id: ID of the item to delete
            partition_key: Partition key value of the item
            
        Returns:
            True if successful, False otherwise
        """
        if not self.container:
            self.initialize()
            
        try:
            self.container.delete_item(item=item_id, partition_key=partition_key)
            return True
        except exceptions.CosmosHttpResponseError:
            return False


# Example usage
if __name__ == "__main__":
    # Create a client
    cosmos_client = CosmosDBClient()
    
    # Initialize with custom partition key path
    cosmos_client.initialize(partition_key_path="/yourPartitionKey")
    
    # Define a test item
    test_item = {
        "id": str(int(time.time())),  # Use timestamp as ID to avoid duplicates
        "yourPartitionKey": "partitionValue",
        "property1": "value1"
    }
    
    # Create the item
    created_item = cosmos_client.create_item(test_item)
    print("Created item:", created_item)
    
    # Query items
    items = cosmos_client.query_items(
        query="SELECT * FROM c WHERE c.yourPartitionKey = @partitionValue",
        parameters=[{"name": "@partitionValue", "value": "partitionValue"}]
    )
    
    print("\nQuery results:")
    for item in items:
        print(item)