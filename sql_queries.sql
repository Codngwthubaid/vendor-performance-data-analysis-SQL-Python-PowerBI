USE vendor_analysis;

select COUNT(Description) from vendor_sales_summary;


-- SELECT 
-- 	VendorNumber, 
--     ROUND(SUM(Freight),2) AS Total_Freight 
-- FROM vendor_invoice 
-- GROUP BY VendorNumber;

-- SELECT
--     p.VendorNumber,
--     p.VendorName,
--     p.Brand,
--     p.PurchasePrice,
--     pp.Volume,
--     pp.Price AS Actual_Price,
--     SUM(p.Quantity) AS TotalPurchasedQuantity,
--     ROUND(SUM(p.Dollars),2)  AS TotalPurchasedDollars
-- FROM purchases p
-- JOIN purchase_prices pp 
--     ON p.Brand = pp.Brand  
--     WHERE p.PurchasePrice > 0
-- GROUP BY 
--     p.VendorNumber,
--     p.VendorName,
--     p.Brand,
--     p.PurchasePrice,
--     pp.Volume,
--     pp.Price
-- ORDER BY 
--     TotalPurchasedDollars;


-- SELECT 
--     VendorNo, 
--     Brand, 
-- 	   SUM(SalesQuantity) AS TotalSalesQuantity, 
--     ROUND(SUM(SalesDollars),2) AS TotalSalesDollars, 
--     ROUND(SUM(SalesPrice),2) AS TotalSalesPrice, 
--     ROUND(SUM(ExciseTax),2) AS TotalExciseTax 
-- FROM sales 
-- GROUP BY 
--     VendorNo, 
--     Brand 
-- ORDER BY 
--     TotalSalesDollars DESC;

-- SELECT
--     pp.VendorNumber,
--     pp.VendorName,
--     pp.Brand,
--     pp.PurchasePrice,
--     pp.Price AS Actual_Price,
--     SUM(vi.Quantity) AS TotalPurchasedQuantity,
--     ROUND(SUM(vi.Dollars),2)  AS TotalPurchasedDollars,
--     ROUND(SUM(vi.Freight),2) as TotalFreightCost,
--     SUM(s.SalesQuantity) AS TotalSalesQuantity, 
-- 	ROUND(SUM(s.SalesDollars),2) AS TotalSalesDollars, 
-- 	ROUND(SUM(s.SalesPrice),2) AS TotalSalesPrice, 
-- 	ROUND(SUM(s.ExciseTax),2) AS TotalExciseTax 
-- FROM purchase_prices pp 
-- JOIN sales s
--     ON pp.Brand = s.Brand  
--     AND pp.VendorNumber = s.VendorNo
-- JOIN vendor_invoice vi
-- 	ON pp.VendorNumber = vi.VendorNumber
-- GROUP BY 
--     pp.VendorNumber,
--     pp.VendorName,
--     pp.Brand,
--     pp.PurchasePrice,
-- 	pp.Price;


-- optimized query  : BUT EXCIDE THE 30 SECS TIME LIMIT
-- WITH FreightSummary AS (
-- 	SELECT 
-- 		VendorNumber, 
-- 		ROUND(SUM(Freight),2) AS FreightCost 
-- 	FROM vendor_invoice  
-- 	GROUP BY VendorNumber
-- ),

-- PurchaseSummary AS (
-- 	SELECT
-- 		p.VendorNumber,
-- 		p.VendorName,
-- 		p.Brand,
-- 		p.PurchasePrice,
-- 		pp.Volume,
-- 		pp.Price AS Actual_Price,
-- 		SUM(p.Quantity) AS TotalPurchasedQuantity,
-- 		ROUND(SUM(p.Dollars),2)  AS TotalPurchasedDollars
-- 	FROM purchases p
-- 	JOIN purchase_prices pp 
--      ON p.Brand = pp.Brand  
--      WHERE p.PurchasePrice > 0
-- 	GROUP BY 
--      p.VendorNumber,
--      p.VendorName,
--      p.Brand,
--      p.PurchasePrice,
--      pp.Volume,
--      pp.Price
-- ),

-- SalesSummary AS (
-- 	SELECT
--      VendorNo, 
--      Brand, 
-- 	 SUM(SalesQuantity) AS TotalSalesQuantity, 
--      ROUND(SUM(SalesDollars),2) AS TotalSalesDollars, 
--      ROUND(SUM(SalesPrice),2) AS TotalSalesPrice, 
--      ROUND(SUM(ExciseTax),2) AS TotalExciseTax 
-- 	FROM sales 
-- 	GROUP BY 
--      VendorNo, 
--      Brand 
-- )


-- SELECT 
-- 	ps.VendorNumber,
-- 	ps.VendorName,
-- 	ps.Brand,
--     ps.PurchasePrice,
--     ps.Actual_Price,
--     ps.Volume,
--     ps.TotalPurchasedQuantity,
--     ps.TotalPurchasedDollars,
--     ss.TotalSalesQuantity,
--     ss.TotalSalesDollars,
--     ss.TotalSalesPrice,
--     ss.TotalExciseTax,
--     fs.FreightCost
-- FROM PurchaseSummary ps
-- LEFT JOIN SalesSummary ss
-- 	ON ps.VendorNumber = ss.VendorNo
--     AND ps.Brand = ss.Brand
-- LEFT JOIN FreightSummary fs
-- 	ON ps.VendorNumber = fs.VendorNumber
-- ORDER BY ps.TotalPurchasedDollars DESC;






-- 1. Aggregate Freight exactly as before
WITH FreightSummary AS (
	SELECT 
		VendorNumber, 
		ROUND(SUM(Freight), 2) AS FreightCost 
	FROM vendor_invoice  
	GROUP BY VendorNumber
),

-- 2. Aggregate Purchases FIRST to prevent Many-to-Many data explosion
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

-- 3. Join the prices cleanly now that the rows are condensed
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

-- 4. Aggregate Sales exactly as before
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

-- 5. Combine everything in the final rapid output
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




