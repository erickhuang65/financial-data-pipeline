import logging
import os
from google.cloud import bigquery
from google.api_core import exceptions
from google.api_core.exceptions import GoogleAPIError
import pandas as pd

class BigQueryConnector:
    
    def __init__(self, 
                 project_id: str, 
                 credentials_path: str):
        """
        Initialize BigQuery client with project ID and optional credentials path.
        
        Args:
            project_id (str): Google Cloud Project ID
            credentials_path (str, optional): Path to service account JSON file.
            If None, uses GOOGLE_APPLICATION_CREDENTIALS env var.
        """
        
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)
        
        # checks with path to credential is valid
        if credentials_path is None:
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if not credentials_path:
            self.logger.error("Google credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS or provide credentials_path")
            raise ValueError("Google credentials not found")
            
        if not os.path.exists(credentials_path):
            self.logger.error(f"Credential file not found at {credentials_path}")
            raise FileNotFoundError(f"Credential file not found at {credentials_path}")

        try:
            #self.client = bigquery.Client()
            self.client = bigquery.Client.from_service_account_json(
                credentials_path, 
                project=project_id
            )
            self.logger.info(f"BigQuery client initialized for project: {project_id}")
        except GoogleAPIError as e:
            self.logger.error(f"Failed to initialize BigQuery client: {str(e)}")
            raise
        
# 1. Setup: 

    def create_dataset(
            self,
            dataset_id: str, 
            location: str = "US",
            exists_ok: bool = True):
        """
        Creates a BigQuery dataset if the table doesn't exist.
        Args:
            dataset_id: Dataset ID (e.g., stock_market_data)
            location: Geographic location to default US
            exists_ok: 
        """
        dataset_ref = f"{self.project_id}.{dataset_id}"
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        try:
            dataset = self.client.create_dataset(dataset, exists_ok=exists_ok)
            self.logger.info(f"Dataset {dataset_id} created or already exists")
            return dataset
        except GoogleAPIError as e:
            self.logger.error(f"Error creating dataset {dataset_id}: {e}")
            raise
        
# 2. Data Loading Operations
    # load pandas DataFrame to table
    def load_dataframe(self, 
                       df: pd.DataFrame, 
                       destination:str, 
                       job_config=None):
        """
        Load dataframe from ETL Transformer to BigQuery project
        Args:
            data (obj): Pandas DataFrame with stock data
            destination (str): Table reference (e.g., raw_stock_price)
            job_config (optional): LoadJobConfig object
            
        Returns:
            a LoadJob Object
        """ 
        # if df is None:
        #     self.logger.error(f"DataFrame cannot be None")
        #     return False

        if df.empty:
            self.logger.error(f"DataFrame is empty")
            raise ValueError(f"Cannot load empty DataFrame")
        
        if not destination:
            self.logger.error(f"Missing destination table")
            raise ValueError(f"Destination table required")
        
        if job_config is None: 
            job_config = bigquery.LoadJobConfig()
            job_config.write_disposition = 'WRITE_APPEND'

            # Use CSV format as fallback if pyarrow has issues
            try:
                import pyarrow
            except ImportError:
                job_config.source_format = bigquery.SourceFormat.CSV
                self.logger.warning("PyArrow not installed, using CSV format")
        
        try:
            job = self.client.load_table_from_dataframe(
                dataframe = df,
                destination = destination, 
                job_config = job_config)
            job.result()

        except GoogleAPIError as e:
            self.logger.error(f"Error loading dataframe to BigQuery Client: {e}")

    # insert data in batches for efficiency
    def batch_insert(self, df, destination, job_config=None):
        pass 
    
    # update existing records or insert new ones
    def upsert_data(self):
        pass  

# 3. Query Operations

# execute_query() - run SQL queries
# get_table_info() - check table schemas, row counts
# check_data_freshness() - validate when data was last updated

# 4. Table Management

# truncate_table() - clear table data
# drop_table() - delete tables
# list_tables() - see what tables exist

# 5. Data Validation

# validate_schema() - ensure data matches expected table structure
# check_duplicates() - find duplicate records
# get_row_count() - verify data loaded correctly