import unittest
from unittest.mock import patch, MagicMock, ANY
import sys
import os

# Add the project root to the Python path to allow importing project modules
# This might need adjustment based on your exact test execution environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import the modules from the project
# We need to mock settings before importing cosmosdb_service
# as it reads settings upon import for the _client global.
MOCK_SETTINGS = {
    'COSMOS_DB_ENDPOINT': 'mock_endpoint',
    'COSMOS_DB_KEY': 'mock_key'
}

# --- Mock settings module before importing services.cosmosdb_service ---
# This is a common pattern: mock dependencies before the module using them is loaded.
# If services.cosmosdb_service is already loaded elsewhere, this might not work as expected
# without more complex sys.modules manipulation or reloads.

# Option 1: Patch 'config.settings' directly if it's a module.
# This requires 'config' to be a package (have __init__.py) and 'settings.py' to be a module within it.
# Based on the file structure, config/settings.py looks like a module.

mock_config_settings = MagicMock()
mock_config_settings.COSMOS_DB_ENDPOINT = MOCK_SETTINGS['COSMOS_DB_ENDPOINT']
mock_config_settings.COSMOS_DB_KEY = MOCK_SETTINGS['COSMOS_DB_KEY']

# If utils.logger also needs mocking or specific setup for tests, handle it here.
# For now, assume it either works or its absence won't break these specific tests.
mock_utils_logger = MagicMock()
mock_utils_logger.logger = MagicMock()

# Apply patches using a dictionary for sys.modules
# This ensures that when services.cosmosdb_service is imported, it sees our mock.
# This is more robust for modules that might be imported at different times.
with patch.dict(sys.modules, {
    'config.settings': mock_config_settings,
    'utils.logger': mock_utils_logger # Mock out the logger too
}):
    # Import the module to be tested *after* its dependencies are mocked
    import services.cosmosdb_service as cosmosdb_service
    from azure.cosmos import exceptions as cosmos_exceptions # Import exceptions from the actual library

# Reset _client in cosmosdb_service to None before each test
# to ensure client initialization is tested correctly.
def reset_cosmos_client_singleton():
    cosmosdb_service._client = None


class TestCosmosDBService(unittest.TestCase):

    def setUp(self):
        # Reset the singleton client before each test
        reset_cosmos_client_singleton()
        # Clear any previously set mock settings if necessary, though patching usually handles this.
        mock_config_settings.COSMOS_DB_ENDPOINT = MOCK_SETTINGS['COSMOS_DB_ENDPOINT']
        mock_config_settings.COSMOS_DB_KEY = MOCK_SETTINGS['COSMOS_DB_KEY']


    @patch('services.cosmosdb_service.cosmos_client.CosmosClient')
    def test_get_cosmos_client_success(self, mock_cosmos_client_constructor):
        # Ensure global _client is reset
        cosmosdb_service._client = None

        client_instance = mock_cosmos_client_constructor.return_value
        client = cosmosdb_service._get_cosmos_client()

        mock_cosmos_client_constructor.assert_called_once_with(
            MOCK_SETTINGS['COSMOS_DB_ENDPOINT'], {'masterKey': MOCK_SETTINGS['COSMOS_DB_KEY']}
        )
        self.assertEqual(client, client_instance)
        # Test singleton behavior: calling again should return the same instance
        client2 = cosmosdb_service._get_cosmos_client()
        self.assertIs(client, client2)
        mock_cosmos_client_constructor.assert_called_once() # Still called only once


    @patch('services.cosmosdb_service.cosmos_client.CosmosClient')
    def test_get_cosmos_client_missing_credentials(self, mock_cosmos_client_constructor):
        cosmosdb_service._client = None # Ensure client is reset
        mock_config_settings.COSMOS_DB_ENDPOINT = None # Simulate missing endpoint

        with self.assertRaises(ValueError) as context:
            cosmosdb_service._get_cosmos_client()
        self.assertIn("Cosmos DB endpoint or key is not configured", str(context.exception))
        mock_cosmos_client_constructor.assert_not_called()

        # Reset for other tests
        mock_config_settings.COSMOS_DB_ENDPOINT = MOCK_SETTINGS['COSMOS_DB_ENDPOINT']


    @patch('services.cosmosdb_service._get_cosmos_client')
    def test_get_or_create_database_exists(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_db_client = MagicMock()
        mock_client.get_database_client.return_value = mock_db_client

        db = cosmosdb_service.get_or_create_database("TestDB")

        mock_client.get_database_client.assert_called_once_with("TestDB")
        mock_db_client.read.assert_called_once() # Checks if DB exists
        mock_client.create_database.assert_not_called()
        self.assertEqual(db, mock_db_client)

    @patch('services.cosmosdb_service._get_cosmos_client')
    def test_get_or_create_database_creates(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_db_client_existing = MagicMock()
        # Simulate DB not found on first check, then successful creation
        mock_client.get_database_client.return_value = mock_db_client_existing
        mock_db_client_existing.read.side_effect = cosmos_exceptions.CosmosResourceNotFoundError(http_error=MagicMock(status_code=404))

        mock_created_db_client = MagicMock()
        mock_client.create_database.return_value = mock_created_db_client

        db = cosmosdb_service.get_or_create_database("NewDB")

        mock_client.get_database_client.assert_called_once_with("NewDB")
        mock_db_client_existing.read.assert_called_once()
        mock_client.create_database.assert_called_once_with("NewDB")
        self.assertEqual(db, mock_created_db_client)

    @patch('services.cosmosdb_service._get_cosmos_client')
    def test_get_or_create_container_exists(self, mock_get_client):
        mock_db_client = MagicMock() # This is the database client instance
        mock_container_client = MagicMock()
        mock_db_client.get_container_client.return_value = mock_container_client

        container = cosmosdb_service.get_or_create_container(mock_db_client, "TestContainer", "/id")

        mock_db_client.get_container_client.assert_called_once_with("TestContainer")
        mock_container_client.read.assert_called_once() # Checks if container exists
        mock_db_client.create_container.assert_not_called()
        self.assertEqual(container, mock_container_client)

    @patch('services.cosmosdb_service._get_cosmos_client') # Though not directly used by get_or_create_container, it's part of the module
    def test_get_or_create_container_creates(self, mock_get_client_not_used_here):
        mock_db_client = MagicMock() # Database client instance
        mock_container_client_existing = MagicMock()
        mock_db_client.get_container_client.return_value = mock_container_client_existing
        mock_container_client_existing.read.side_effect = cosmos_exceptions.CosmosResourceNotFoundError(http_error=MagicMock(status_code=404))

        mock_created_container_client = MagicMock()
        mock_db_client.create_container.return_value = mock_created_container_client

        container = cosmosdb_service.get_or_create_container(mock_db_client, "NewContainer", "/id")

        mock_db_client.get_container_client.assert_called_once_with("NewContainer")
        mock_container_client_existing.read.assert_called_once()
        mock_db_client.create_container.assert_called_once_with(id="NewContainer", partition_key=ANY) # ANY for PartitionKey object
        self.assertEqual(container, mock_created_container_client)
        # Check partition key path (ANY used because PartitionKey is an object)
        args, kwargs = mock_db_client.create_container.call_args
        self.assertEqual(kwargs['partition_key'].path, "/id")


    def test_create_item_success(self):
        mock_container_client = MagicMock()
        item_doc = {"id": "123", "data": "test"} # 'id' is the partition key field for /id

        # Ensure the partition key path is what we expect for this test
        original_pk_path = cosmosdb_service.TRADE_HISTORY_PARTITION_KEY_PATH
        cosmosdb_service.TRADE_HISTORY_PARTITION_KEY_PATH = "/id"

        cosmosdb_service.create_item(mock_container_client, item_doc)
        mock_container_client.create_item.assert_called_once_with(body=item_doc)

        cosmosdb_service.TRADE_HISTORY_PARTITION_KEY_PATH = original_pk_path # Reset

    def test_create_item_missing_partition_key_field(self):
        mock_container_client = MagicMock()
        item_doc = {"data": "test"} # Missing 'id' field

        original_pk_path = cosmosdb_service.TRADE_HISTORY_PARTITION_KEY_PATH
        cosmosdb_service.TRADE_HISTORY_PARTITION_KEY_PATH = "/id" # PK path is /id

        with self.assertRaises(ValueError) as context:
            cosmosdb_service.create_item(mock_container_client, item_doc)
        self.assertIn("Item document is missing the partition key field 'id'", str(context.exception))

        cosmosdb_service.TRADE_HISTORY_PARTITION_KEY_PATH = original_pk_path # Reset


    def test_query_items_success(self):
        mock_container_client = MagicMock()
        query = "SELECT * FROM c"
        params = [{"name": "@value", "value": "test"}]

        expected_items = [{"id": "1"}, {"id": "2"}]
        mock_container_client.query_items.return_value = iter(expected_items) # query_items returns an iterator

        items = cosmosdb_service.query_items(mock_container_client, query, parameters=params, enable_cross_partition_query=False)

        mock_container_client.query_items.assert_called_once_with(
            query=query, parameters=params, enable_cross_partition_query=False
        )
        self.assertEqual(items, expected_items)

    @patch('services.cosmosdb_service.get_or_create_database')
    @patch('services.cosmosdb_service.get_or_create_container')
    def test_get_trade_history_container(self, mock_get_create_container, mock_get_create_db):
        mock_db = MagicMock()
        mock_container = MagicMock()
        mock_get_create_db.return_value = mock_db
        mock_get_create_container.return_value = mock_container

        # Expected values from cosmosdb_service module
        db_name = cosmosdb_service.DATABASE_NAME
        container_name = cosmosdb_service.TRADE_HISTORY_CONTAINER_NAME
        pk_path = cosmosdb_service.TRADE_HISTORY_PARTITION_KEY_PATH

        container_client = cosmosdb_service.get_trade_history_container()

        mock_get_create_db.assert_called_once_with(db_name)
        mock_get_create_container.assert_called_once_with(mock_db, container_name, pk_path)
        self.assertEqual(container_client, mock_container)


if __name__ == '__main__':
    unittest.main()
