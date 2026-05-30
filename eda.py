import pandas as pd
import pymysql
from sqlalchemy import create_engine
from IPython.display import display
import time

# creating mysql database connection 
conn = pymysql.connect(
    host = "127.0.0.1",
    user = "root",
    password = "ubaid725061",
    port = 3306,
    database = "vendor_analysis"
)

engine = create_engine(
    f"mysql+pymysql://root:ubaid725061@127.0.0.1:3306/vendor_analysis"
)

# checking all the tables which are present in the database
tables_df = pd.read_sql("show tables", conn)

# Extract the column name dynamically (usually 'Tables_in_vendor_analysis')
column_name = tables_df.columns[0] 

# Loop through the actual table names in that column
for table in tables_df[column_name]:
    # print('-'*10, f'{table}', '-'*10)
    
    # Get record count
    count_df = pd.read_sql(f'select count(*) as count from `{table}`', conn)
    # print('Count of records:', count_df['count'].values[0])
    
    # Display top 5 rows
    # display(pd.read_sql(f'select * from `{table}` limit 5', conn))


# Get more better details for a specifc vendor 
purchases = pd.read_sql('select * from purchases where VendorNumber = 4466', conn)
purchase_prices = pd.read_sql('select * from purchase_prices where VendorNumber = 4466', conn)
# display(purchases.groupby(['Brand', 'PurchasePrice'])[['Quantity', 'Dollars']].sum())


vendor_invoice = pd.read_sql('select * from vendor_invoice where VendorNumber = 4466', conn)
freight_summary = pd.read_sql_query("select VendorNumber, SUM(Freight) as Total_Freight from vendor_invoice group by VendorNumber", conn)
sales = pd.read_sql("SELECT * FROM sales where VendorNo = 4466", conn)
# print(sales.columns) 

# getting colums 
# print(purchase_prices.columns)
# print(purchases.columns)
# print(sales.columns)

# now we merge colums of tables (purchase_prices and purchases) based on BRAND, by writing a SQL query
# print(pd.read_sql_query(
#     """SELECT
# 	COUNT(p.VendorNumber),
#     p.VendorNumber,
#     p.VendorName,
#     p.Brand,
#     p.PurchasePrice,
#     pp.Volume,
#     pp.Price AS Actual_Price,
#     SUM(p.Quantity) AS TotalPurchasedQuantity,
#     ROUND(SUM(p.Dollars),2)  AS TotalPurchasedDollars
# FROM purchases p
# JOIN purchase_prices pp 
#     ON p.Brand = pp.Brand  
#     WHERE p.PurchasePrice > 0
# GROUP BY 
#     p.VendorNumber,
#     p.VendorName,
#     p.Brand,
#     p.PurchasePrice,
#     pp.Volume,
#     pp.Price
# ORDER BY 
#     TotalPurchasedDollars;
#     """
#     , conn)
# )

# sales = pd.read_sql("SELECT * FROM sales where VendorNo = 4466", conn)
# Index(['InventoryId', 'Store', 'Brand', 'Description', 'Size', 'SalesQuantity',
#        'SalesDollars', 'SalesPrice', 'SalesDate', 'Volume', 'Classification',
#        'ExciseTax', 'VendorNo', 'VendorName'],

# print(pd.read_sql_query("""
#   SELECT 
# 	    VendorNumber, 
#       ROUND(SUM(Freight),2) AS Total_Freight 
#   FROM vendor_invoice 
#   GROUP BY VendorNumber;
# """, conn))

# print(pd.read_sql_query("""
# SELECT
#     pp.VendorNumber,
#     pp.VendorName,
#     pp.Brand,
#     pp.PurchasePrice,
#     pp.Price AS Actual_Price,
#     SUM(vi.Quantity) AS TotalPurchasedQuantity,
#     ROUND(SUM(vi.Dollars),2)  AS TotalPurchasedDollars,
#     ROUND(SUM(vi.Freight),2) as TotalFreightCost,
#     SUM(s.SalesQuantity) AS TotalSalesQuantity, 
# 	ROUND(SUM(s.SalesDollars),2) AS TotalSalesDollars, 
# 	ROUND(SUM(s.SalesPrice),2) AS TotalSalesPrice, 
# 	ROUND(SUM(s.ExciseTax),2) AS TotalExciseTax 
# FROM purchase_prices pp 
# JOIN sales s
#     ON pp.Brand = s.Brand  
#     AND pp.VendorNumber = s.VendorNo
# JOIN vendor_invoice vi
# 	ON pp.VendorNumber = vi.VendorNumber
# GROUP BY 
#     pp.VendorNumber,
#     pp.VendorName,
#     pp.Brand,
#     pp.PurchasePrice,
# 	pp.Price;
# """), conn)


start_time = time.time()
print(start_time)
vendor_sales_summary = pd.read_sql_query("""
WITH FreightSummary AS (
	SELECT 
		VendorNumber, 
		ROUND(SUM(Freight),2) AS FreightCost 
	FROM vendor_invoice  
	GROUP BY VendorNumber
),

PurchaseSummary AS (
	SELECT
		p.VendorNumber,
		p.VendorName,
		p.Brand,
		p.PurchasePrice,
		pp.Volume,
		pp.Price AS Actual_Price,
		SUM(p.Quantity) AS TotalPurchasedQuantity,
		ROUND(SUM(p.Dollars),2)  AS TotalPurchasedDollars
	FROM purchases p
	JOIN purchase_prices pp 
     ON p.Brand = pp.Brand  
     WHERE p.PurchasePrice > 0
	GROUP BY 
     p.VendorNumber,
     p.VendorName,
     p.Brand,
     p.PurchasePrice,
     pp.Volume,
     pp.Price
),

SalesSummary AS (
	SELECT
     VendorNo, 
     Brand, 
	 SUM(SalesQuantity) AS TotalSalesQuantity, 
     ROUND(SUM(SalesDollars),2) AS TotalSalesDollars, 
     ROUND(SUM(SalesPrice),2) AS TotalSalesPrice, 
     ROUND(SUM(ExciseTax),2) AS TotalExciseTax 
	FROM sales 
	GROUP BY 
     VendorNo, 
     Brand 
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
""", conn)

end_time = time.time()
print(end_time)
print(f"Total time taken to read all files: {end_time - start_time}")
# display(vendor_sales_summary)

# removing inconsistencies from vendor names
vendor_sales_summary['VendorName'] = vendor_sales_summary['VendorName'].str.strip()
vendor_sales_summary['Volume'] = vendor_sales_summary['Volume'].astype('float64')
vendor_sales_summary.fillna(1, inplace= True)

# rename this "Actual_Price" with ActualPrice (column name)
vendor_sales_summary['ActualPrice'] = vendor_sales_summary['Actual_Price']
vendor_sales_summary.drop('Actual_Price', axis = 1, inplace = True)

# Creating some new columns for better analysis
vendor_sales_summary['GrossProfit'] = vendor_sales_summary['TotalSalesDollars'] - vendor_sales_summary['TotalPurchasedDollars']
vendor_sales_summary['ProfitMargin'] = vendor_sales_summary['GrossProfit'] / vendor_sales_summary['TotalSalesDollars']
vendor_sales_summary['StockTurnOver'] = vendor_sales_summary['TotalSalesQuantity'] / vendor_sales_summary['TotalPurchasedQuantity']
vendor_sales_summary['SalesToPurchaseRatio'] = vendor_sales_summary['TotalSalesQuantity'] / vendor_sales_summary['TotalPurchasedQuantity']


# saving vendor_sales_summary table into DB 
# creating a cursor 
# cursor = conn.cursor()
# cursor.execute("""
#     CREATE TABLE vendor_sales_summary (
#         VendorNumber INT,
#         VendorName VARCHAR(100),
#         Brand VARCHAR(100),
#         PurchasePrice DECIMAL(10,2),
#         ActualPrice DECIMAL(10,2),
#         Volume FLOAT,
#         TotalPurchasedQuantity INT,
#         TotalPurchasedDollars DECIMAL(10,2),
#         TotalSalesQuantity INT,
#         TotalSalesDollars DECIMAL(10,2),
#         TotalSalesPrice DECIMAL(10,2),
#         TotalExciseTax DECIMAL(10,2),
#         FreightCost DECIMAL(10,2),
#         GrossProfit DECIMAL(10,2),
#         ProfitMargin FLOAT,
#         StockTurnOver FLOAT,
#         SalesToPurchaseRatio FLOAT, 
#         PRIMARY KEY (VendorNumber, Brand)
#     );
# """)


# print(pd.read_sql_query("SELECT * FROM vendor_sales_summary", conn))
# print(vendor_sales_summary.to_sql("vendor_sales_summary", engine, if_exists = 'replace', index= False))