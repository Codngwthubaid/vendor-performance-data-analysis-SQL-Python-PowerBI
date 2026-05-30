import pandas as pd
import pymysql
from sqlalchemy import create_engine
import logging
import time
from datetime import datetime

logging.basicConfig(
    filename='logs/vendor_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "ubaid725061",
    "port": 3306,
    "database": "vendor_analysis"
}


def get_connection():
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"]
    )
    engine = create_engine(
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return conn, engine


def create_vendor_summary(conn):
    query = """
    WITH FreightSummary AS (
        SELECT
            VendorNumber,
            ROUND(SUM(Freight), 2) AS FreightCost
        FROM vendor_invoice
        GROUP BY VendorNumber
    ),

    AggregatedPurchases AS (
        SELECT
            VendorNumber,
            VendorName,
            Brand,
            PurchasePrice,
            SUM(Quantity) AS TotalPurchasedQuantity,
            ROUND(SUM(Dollars), 2) AS TotalPurchasedDollars
        FROM purchases
        WHERE PurchasePrice > 0
        GROUP BY VendorNumber, VendorName, Brand, PurchasePrice
    ),

    PurchaseSummary AS (
        SELECT
            ap.VendorNumber,
            ap.VendorName,
            ap.Brand,
            ap.PurchasePrice,
            pp.Volume,
            pp.Price AS Actual_Price,
            ap.TotalPurchasedQuantity,
            ap.TotalPurchasedDollars
        FROM AggregatedPurchases ap
        LEFT JOIN purchase_prices pp
            ON ap.Brand = pp.Brand
    ),

    SalesSummary AS (
        SELECT
            VendorNo,
            Brand,
            SUM(SalesQuantity) AS TotalSalesQuantity,
            ROUND(SUM(SalesDollars), 2) AS TotalSalesDollars,
            ROUND(SUM(SalesPrice), 2) AS TotalSalesPrice,
            ROUND(SUM(ExciseTax), 2) AS TotalExciseTax
        FROM sales
        GROUP BY VendorNo, Brand
    )

    SELECT
        ps.VendorNumber,
        ps.VendorName,
        ps.Brand,
        ps.PurchasePrice,
        ps.Actual_Price,
        ps.Volume,
        ps.TotalPurchasedQuantity,
        ps.TotalPurchasedDollars,
        ss.TotalSalesQuantity,
        ss.TotalSalesDollars,
        ss.TotalSalesPrice,
        ss.TotalExciseTax,
        fs.FreightCost
    FROM PurchaseSummary ps
    LEFT JOIN SalesSummary ss
        ON ps.VendorNumber = ss.VendorNo
        AND ps.Brand = ss.Brand
    LEFT JOIN FreightSummary fs
        ON ps.VendorNumber = fs.VendorNumber
    ORDER BY ps.TotalPurchasedDollars DESC;
    """
    logging.info("Executing vendor_sales_summary query")
    df = pd.read_sql_query(query, conn)
    logging.info(f"Query returned {len(df)} rows")
    return df


def clean_data(df):
    logging.info("Starting data cleaning")

    df['VendorName'] = df['VendorName'].str.strip()

    sales_null_cols = ['TotalSalesQuantity', 'TotalSalesDollars',
                       'TotalSalesPrice', 'TotalExciseTax']
    for col in sales_null_cols:
        null_count = df[col].isna().sum()
        if null_count > 0:
            logging.warning(f"{col}: {null_count} null values filled with 0")
    df[sales_null_cols] = df[sales_null_cols].fillna(0)

    df['FreightCost'] = df['FreightCost'].fillna(0)

    df['Volume'] = df['Volume'].fillna(1).astype('float64')

    df.rename(columns={'Actual_Price': 'ActualPrice'}, inplace=True)

    logging.info("Creating derived columns")
    df['GrossProfit'] = df['TotalSalesDollars'] - df['TotalPurchasedDollars']
    df['ProfitMargin'] = df['GrossProfit'] / df['TotalSalesDollars'].replace(0, pd.NA)
    df['StockTurnOver'] = df['TotalSalesQuantity'] / df['TotalPurchasedQuantity'].replace(0, pd.NA)
    df['SalesToPurchaseRatio'] = df['TotalSalesQuantity'] / df['TotalPurchasedQuantity'].replace(0, pd.NA)

    df = df.round(2)

    logging.info("Data cleaning completed")
    return df


def run_pipeline():
    start_time = time.time()
    start_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"{'='*60}")
    logging.info(f"Pipeline started at {start_dt}")
    print(f"[{start_dt}] Pipeline started")

    try:
        logging.info("Creating database connection")
        conn, engine = get_connection()
        print("Database connection established")

        df = create_vendor_summary(conn)
        print(f"vendor_sales_summary query executed: {len(df)} rows returned")

        df = clean_data(df)

        logging.info("Saving vendor_sales_summary to database")
        df.to_sql("vendor_sales_summary", engine, if_exists='replace', index=False)
        logging.info(f"Saved {len(df)} rows to vendor_sales_summary table")
        print(f"Saved {len(df)} rows to vendor_sales_summary table")

        conn.close()

        end_time = time.time()
        end_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elapsed = round(end_time - start_time, 2)
        logging.info(f"Pipeline ended at {end_dt} | Total time: {elapsed}s")
        logging.info(f"{'='*60}")
        print(f"[{end_dt}] Pipeline completed successfully in {elapsed}s")

    except Exception as e:
        end_time = time.time()
        elapsed = round(end_time - start_time, 2)
        logging.error(f"Pipeline failed at {elapsed}s: {e}", exc_info=True)
        print(f"Pipeline failed after {elapsed}s: {e}")


if __name__ == "__main__":
    run_pipeline()
