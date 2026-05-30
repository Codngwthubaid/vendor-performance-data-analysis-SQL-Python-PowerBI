import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time 

# Configure Logging
logging.basicConfig(
    filename='logs/insert_data_into_db.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

# MySQL Credentials
host = "127.0.0.1"
user = "root"
password = "ubaid725061"
port = 3306
database = "vendor_analysis"

# Create MySQL Engine
engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
)

# CSV Files Dictionary
files = {
    'begin_inventory': 'data/begin_inventory.csv',
    'end_inventory': 'data/end_inventory.csv',
    'purchases': 'data/purchases.csv',
    'purchase_prices': 'data/purchase_prices.csv',
    'sales': 'data/sales.csv',
    'vendor_invoice': 'data/vendor_invoice.csv'
}

# Insert Data into Database
def insert_data_into_db():
    try:
        start_time = time.time()
        for table_name, file_path in files.items():
            logging.info(f"Starting import for {file_path}")
            print(f"Importing {file_path} into table {table_name}...")

            # Read CSV
            df = pd.read_csv(file_path)

            # Upload to MySQL
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists='replace',
                index=False
            )
            logging.info(f"Successfully imported {table_name} with {len(df)} rows")
            print(f"{table_name} imported successfully!")
        
        end_time = time.time()
        total_time = end_time - start_time
        logging.info(f"Total time taken to import all files: {total_time}")
        print(f"Total time taken to import all files: {total_time}")

    except Exception as e:
        logging.error(f"Error while inserting data: {e}")
        print(f"Error: {e}")


# Read CSV Files Function
def read_csv_files():
    try:
        start_time = time.time()
        logging.info("Reading CSV files started")
        for file in os.listdir('data'):
            if file.endswith('.csv'):
                file_path = f"data/{file}"
                df = pd.read_csv(file_path)
                logging.info(f"{file} loaded successfully with {len(df)} rows")
                print(f"Loaded {file} with {len(df)} rows")
        logging.info("All CSV files read successfully")

        # Call insert function here
        insert_data_into_db()

        end_time = time.time()
        total_time = end_time - start_time
        logging.info(f"Total time taken to read all files: {total_time}")
        print(f"Total time taken to read all files: {total_time}")

    except Exception as e:
        logging.error(f"Error while reading CSV files: {e}")
        print(f"Error: {e}")


# Main Execution
read_csv_files()

print("All files imported successfully.")