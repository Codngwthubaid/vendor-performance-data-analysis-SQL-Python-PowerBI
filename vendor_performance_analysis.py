import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import pymysql
from IPython.display import display
from scipy.stats import ttest_ind #hypothesis testing  
import scipy.stats as stats #statistical analysis
warnings.filterwarnings('ignore')

# helper function 
def format_values(value) : 
    if value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    elif value >= 1000:
        return f"{value/1000:.2f}k"
    else : 
        return str(value)


# creating database connection 
conn = pymysql.connect(
    host = "127.0.0.1",
    user = "root",
    password = "ubaid725061",
    port = 3306,
    database = "vendor_analysis"
)

df = pd.read_sql_query('SELECT * FROM vendor_sales_summary',conn)
# display(df.head())

# summary Statistics 
# display(df.describe().T)

### BEFORE FILTERING
# distribution plots for numerical columns with histogram
numerical_columns = df.select_dtypes(include=np.number).columns

# plt.figure(figsize=(15,10))
# for i, col in enumerate(numerical_columns):
#     plt.subplot(4,4,i+1)
#     sns.histplot(df[col], kde=True, bins=30)
#     plt.title(col)

# plt.tight_layout()
# plt.savefig('images/numerical_distributions.png', dpi=300, bbox_inches='tight') 
# plt.show()

# distribution plots for numerical columns with boxplot
# plt.figure(figsize=(15,10))
# for i, col in enumerate(numerical_columns):
#     plt.subplot(4,4,i+1)
#     sns.boxplot(y=df[col])
#     plt.title(col)

# plt.tight_layout()
# plt.savefig('images/numerical_boxplots.png', dpi=300, bbox_inches='tight') 
# plt.show()


df_1 = pd.read_sql_query('''
    SELECT * 
    FROM vendor_sales_summary 
    WHERE GrossProfit > 0 
    AND ProfitMargin > 0 
    AND TotalSalesQuantity > 0
''',conn)

# display(df_1.describe())


### AFTER FILTERING
numerical_columns_after_filtering = df_1.select_dtypes(include=np.number).columns

# plt.figure(figsize=(15,10))
# for i, col in enumerate(numerical_columns_after_filtering):
#     plt.subplot(4,4,i+1)
#     sns.histplot(df_1[col], kde=True, bins=30)
#     plt.title(col)

# plt.tight_layout()
# plt.savefig('images/numerical_distributions_after_filtering.png', dpi=300, bbox_inches='tight') 
# plt.show()

# distribution plots for numerical columns with boxplot
# plt.figure(figsize=(15,10))
# for i, col in enumerate(numerical_columns_after_filtering):
#     plt.subplot(4,4,i+1)
#     sns.boxplot(y=df_1[col])
#     plt.title(col)

# plt.tight_layout()
# plt.savefig('images/numerical_boxplots_after_filtering.png', dpi=300, bbox_inches='tight') 
# plt.show()


# count plots for categorical columns 
categorical_cols = ['VendorName', 'VendorNumber']

# plt.figure(figsize=(12,5))
# for i, col in enumerate(categorical_cols):
#     plt.subplot(1,2,i+1)
#     sns.countplot(y=df_1[col], order=df_1[col].value_counts().index[:10])
#     plt.title(col)

# plt.tight_layout()
# plt.savefig('images/categorical_countplots.png', dpi=300, bbox_inches='tight') 
# plt.show()


# correlation heatmap on numerical columns
# plt.figure(figsize=(12,10))
# sns.heatmap(df_1[numerical_columns_after_filtering].corr(), annot=True, cmap='coolwarm', fmt='.2f')
# plt.title('Correlation Heatmap')
# plt.savefig('images/correlation_heatmap.png', dpi=300, bbox_inches='tight')
# plt.show()


# QUES :

#####################################################################

# Q1. identify those brands who needs promotional or pricing adjustments which displays lower sales performance but higher profit margin

# step 1 : from this we got the meand of profitmargin and sum of totalsalesdollars
brand_performance = df_1.groupby("Description").agg({
    'TotalSalesDollars' : 'sum',
    'ProfitMargin': 'mean',
}).reset_index()
# display(brand_performance)

# step 2 : set some threshold values
lower_sales_threshold = brand_performance['TotalSalesDollars'].quantile(0.15) # output : 563.53
higher_profit_threshold = brand_performance['ProfitMargin'].quantile(0.85) # output : 0.6340726764137595
# print(lower_sales_threshold,higher_profit_threshold)

# step 3 : filter those brands according to the present condition
target_brands = brand_performance[
    (brand_performance['TotalSalesDollars'] <= lower_sales_threshold) &
    (brand_performance['ProfitMargin'] >= higher_profit_threshold)
]
# print("Brands with lower sales performance but higher profit margins")
# display(target_brands.sort_values('TotalSalesDollars', ascending=True))

brand_performance = brand_performance[brand_performance['TotalSalesDollars'] < 10000] # only for better visualizations

# step 4 : render this data into scatter plot
# plt.figure(figsize=(10,6))
# sns.scatterplot(data = target_brands, x = 'TotalSalesDollars', y = 'ProfitMargin', label = 'Target Brands', color='red')
# sns.scatterplot(data = brand_performance, x = 'TotalSalesDollars', y = 'ProfitMargin', label= "All Brands" , color = 'blue', alpha=0.2)

# plt.axhline(higher_profit_threshold, label="High Profitability",color="black",linestyle="-")
# plt.axvline(lower_sales_threshold, label="Low Sales",color="black",linestyle="-")

# plt.title("Identifying brands with lower sales performance but higher profit margins")
# plt.xlabel("Total Sales Dollars")
# plt.ylabel("Profit Margin")
# plt.legend()
# plt.grid(True)
# plt.savefig('images/brands_with_lower_sales_performance_but_higher_profit_margins.png', dpi=300, bbox_inches='tight')
# plt.show()

#####################################################################

# Q2. Which vendors and brands demonstrate the highest sales performance ?

# step 1 :
top_vendors = df_1.groupby('VendorName')["TotalSalesDollars"].sum().nlargest(10) # top 10 
top_brands = df_1.groupby('Description')['TotalSalesDollars'].sum().nlargest(10) #top 10

# print("Top 10 Vendors by Sales Dollars:")
# print(top_vendors.apply(lambda x : format_values(x)))
# print("\nTop 10 Brands by Sales Dollars:")
# print(top_brands.apply(lambda x : format_values(x)))


#  Step 2 : render on bar plot
# plt.figure(figsize=(15,5))

# plot top vendors
# plt.subplot(1,2,1)
# ax1 = sns.barplot(y=top_vendors.index, x= top_brands.values, palette='Blues_r')
# plt.title("Top 10 vendors by Sales")

# for bar in ax1.patches:
#     ax1.text(bar.get_width() + (bar.get_width() * 0.02), 
#             bar.get_y() + bar.get_height()/2, 
#             format_values(bar.get_width()), 
#             va='center', 
#             ha='left', 
#             fontsize = 10, 
#             color='black')


# plot top brands
# plt.subplot(1,2,2)
# ax2 = sns.barplot(x = top_brands.values, y = top_brands.index.astype(str), palette = 'Reds_r')
# plt.title('Top 10 Brands by Sales')

# for bar in ax2.patches:
#     ax2.text(bar.get_width() + (bar.get_width() * 0.02), 
#             bar.get_y() + bar.get_height()/2, 
#             format_values(bar.get_width()), 
#             va='center', 
#             ha='left', 
#             fontsize = 10, 
#             color='black')

# plt.tight_layout()
# plt.savefig('images/top_10_vendors_and_brands_by_sales.png', dpi=300, bbox_inches='tight')
# plt.show()

#####################################################################

# Q3. Which vendors contribute the most to total purchase dollar ?

# step 1 : check vendors details 
vendor_performance = df_1.groupby("VendorName").agg({
    'TotalPurchasedDollars': 'sum',
    'GrossProfit': 'sum',
    'TotalSalesDollars': 'mean'
}).reset_index()
# print(vendor_performance) #119 

# step 2 : adding a column of PurchaseContribution%
vendor_performance['PurchaseContribution'] = vendor_performance['TotalPurchasedDollars']/vendor_performance['TotalPurchasedDollars'].sum()*100
# print(round(vendor_performance.sort_values('PurchaseContribution', ascending=False), 2))

top_10_vendors = vendor_performance.sort_values('PurchaseContribution', ascending=False).head(10).copy()
top_10_vendors['TotalPurchasedDollars'] = top_10_vendors['TotalPurchasedDollars'].apply(lambda x : format_values(x))
top_10_vendors['GrossProfit'] = top_10_vendors['GrossProfit'].apply(lambda x : format_values(x))
top_10_vendors['TotalSalesDollars'] = top_10_vendors['TotalSalesDollars'].apply(lambda x : format_values(x))
top_10_vendors['CumulativeContribution'] = top_10_vendors['PurchaseContribution'].cumsum()

# print(round(top_10_vendors, 2))
# print(top_10_vendors['PurchaseContribution'].sum()) #0.65
# top 10 vendor contributes : 0.65 and rest of the 109 vendors contributes 0.35

# step 3 : render Bar plot for purchase contribution and Line plot for cumulative contribution 

# fig, ax1 = plt.subplots(figsize=(10,6))
# # Bar plot for purchase contributions
# sns.barplot(x=top_10_vendors['VendorName'], y=top_10_vendors['PurchaseContribution'], palette='mako', ax=ax1)

# # Added rotation=90 and changed vertical alignment to 'top' so it sits neatly inside the bar
# for i, value in enumerate(top_10_vendors['PurchaseContribution']):
#     ax1.text(i, value - 1, f'{value:.2f}%', ha='center', va='top', color='white', fontsize=12, fontweight='bold', rotation=90)

# # line plot for cumulative contribution
# ax2 = ax1.twinx()
# ax2.plot(top_10_vendors['VendorName'], top_10_vendors['CumulativeContribution'], color='red', marker='o', linewidth=2, label="CumulativeContribution", linestyle='--')

# ax1.set_title('Vendor Contribution to Total Purchase')
# ax1.set_xlabel("Top 10 Vendors")
# ax1.set_ylabel("Purchase Contribution (%)", color="blue")
# ax2.set_ylabel("Cumulative Contribution (%)", color="red")

# # Rotates the vendor names on the x-axis vertically
# ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
# ax2.axhline(y=100, color='black', linestyle='--', alpha=0.7)

# ax1.legend(loc='upper left')
# ax2.legend(loc='upper right')
# plt.grid(True)
# plt.savefig('images/vendor_contribution_to_total_purchase.png', dpi=300, bbox_inches='tight')
# plt.show()

#####################################################################

# Q4. How much of total procurement (Sourcing) is dependent on the top vendors ?
# print(f"The purchased contribution of top 10 vendors are :  {round(top_10_vendors['PurchaseContribution'].sum(), 2)}%")

# Step 1 : Preparing data
vendors = list(top_10_vendors['VendorName'].values)
purchase_contributions = list(top_10_vendors['PurchaseContribution'].values)
total_contribution = sum(purchase_contributions)
remaining_contribution = 100 - total_contribution
# print(remaining_contribution)

# append other vendors
# vendors.append("Others Vendors")
# purchase_contributions.append(remaining_contribution)

# step 2 : render a donut chart for purchase contributions
# fig, ax = plt.subplots(figsize=(8,8))
# wedges, labels, autotexts = ax.pie(purchase_contributions, 
#                                   labels = vendors, 
#                                   autopct = '%.1f%%', 
#                                   startangle=140, 
#                                   pctdistance=0.85, 
#                                   colors=plt.cm.Paired.colors)

# center_circle = plt.Circle((0, 0), 0.7, color='white')
# fig.gca().add_artist(center_circle)
# plt.title("Top 10 Vendor's Purchase Contribution")
# plt.text(0,0,f"Total Contribution :\n {round(total_contribution,2)}%", fontsize=14, fontweight='bold', ha='center', va='center')
# plt.savefig('images/vendor_contribution_to_total_purchase.png', dpi=300, bbox_inches='tight')
# plt.show()

#####################################################################

# Q5. Does purchasing in bulk reduce the unit price and what is the optimal purchase volume for cost savings?

df_1['UnitPurchasesPrice'] = df_1['TotalPurchasedDollars'] / df_1['TotalPurchasedQuantity']
df_1['OrderSize'] = pd.qcut(df_1['TotalPurchasedQuantity'], q=3, labels = ['Small','Medium','Large'])
# display(df_1[['OrderSize', 'UnitPurchasesPrice']])

# Step 1 : finding mean for the UnitPurchasedPrice
mean_purchase_by_ordersize = df_1.groupby('OrderSize')['UnitPurchasesPrice'].mean()
# display(mean_purchase_by_ordersize)

# step 2 : render a box plot based on OrderSize
# plt.figure(figsize=(10,6))
# sns.boxplot(x = 'OrderSize', y = 'UnitPurchasesPrice', data = df_1, palette="Set2")
# plt.title("Impact of Bulk Purchasing on Unit Price")
# plt.ylabel("Avg Unit Purchases Price")
# plt.xlabel("Order Size")
# plt.grid(True)
# plt.savefig('images/unit_purchases_price_by_order_size.png', dpi=300, bbox_inches='tight')
# plt.show()

#####################################################################

# Q6. Which vendors have low inventory turnover, indicating excess stock and slow-moving products?
# print(df_1[df_1['StockTurnOver']<1].groupby('VendorName')[['StockTurnOver']].mean().sort_values('StockTurnOver', ascending=True).head(10))    

# Step 1. Prepare data using your logic
# plot_data = (df_1[df_1['StockTurnOver'] < 1]
#              .groupby('VendorName')[['StockTurnOver']]
#              .mean()
#              .sort_values('StockTurnOver', ascending=True)
#              .head(10)
#              .reset_index())

# # Step 2. Set up the plotting environment
# plt.figure(figsize=(10, 6))
# sns.set_theme(style="whitegrid")

# # Step 3. Create a horizontal bar plot (y=VendorName makes it horizontal)
# ax = sns.barplot(
#     x='StockTurnOver', 
#     y='VendorName', 
#     data=plot_data, 
#     palette='Reds_r'
# )

# for container in ax.containers:
#     ax.bar_label(container, fmt='%.2f', padding=5, color='black', weight='bold')

# plt.title('Top 10 Vendors with Lowest Inventory Turnover (< 1.0)', fontsize=14, pad=15, weight='bold')
# plt.xlabel('Average Stock Turnover Rate', fontsize=12, labelpad=10)
# plt.ylabel('Vendor Name', fontsize=12, labelpad=10)
# plt.tight_layout()
# plt.savefig('images/vendors_lowest_inventory_turnover.png', dpi=300, bbox_inches='tight')
# plt.show()

#####################################################################

# Q7. How much capital is locked in unsold inventory per vendor and which vendors contribute the most of it ?
df_1['UnSoldedInventoryValue'] = (df_1['TotalPurchasedQuantity'] - df_1['TotalSalesQuantity']) * df_1['UnitPurchasesPrice']
# display("Total Unsold Capital: ",format_values(df_1['UnSoldedInventoryValue'].sum()))

inventory_value_per_vendor = df_1.groupby('VendorName')['UnSoldedInventoryValue'].sum().reset_index()
top_10_vendors_unsold = inventory_value_per_vendor.sort_values('UnSoldedInventoryValue', ascending=False).head(10)
top_10_vendors_unsold['UnSoldedInventoryValue'] = top_10_vendors_unsold['UnSoldedInventoryValue'].apply(lambda x : format_values(x))
# display(top_10_vendors_unsold)

#####################################################################

# Q8. What is the 95% confidence interval for profit margins of top-performing and low-performing vendors ?
top_threshold = df_1['TotalSalesDollars'].quantile(0.75)
low_threshold = df_1['TotalSalesDollars'].quantile(0.25)
top_performing_vendors = df_1[df_1['TotalSalesDollars'] >= top_threshold]['ProfitMargin'].dropna()
low_performing_vendors = df_1[df_1['TotalSalesDollars'] <= low_threshold]['ProfitMargin'].dropna()
# print(top_performing_vendors, low_performing_vendors)

# Step 1 : finding CI
# def confidence_interval(data, confidence=0.95):
#     mean_value = np.mean(data)
#     std_err = np.std(data, ddof=1) / np.sqrt(len(data))
#     t_critial = stats.t.ppf((1 + confidence)/2, df=len(data) - 1)
#     margin = t_critial * std_err
#     return mean_value, mean_value - margin, mean_value + margin

# top_mean, top_lower, top_upper = confidence_interval(top_performing_vendors)
# low_mean, low_lower, low_upper = confidence_interval(low_performing_vendors)

# display(f"Top Vendor's 95% CI : ({top_lower:.2f} to {top_upper:.2f}) Mean : {top_mean:.2f}")
# display(f"Low Vendor's 95% CI : ({low_lower:.2f} to {low_upper:.2f}) Mean : {low_mean:.2f}")

# Step 2 : render a histogram which shows the top_performing_vendors and low_performing_vendors
# plt.figure(figsize=(12,6))
# sns.histplot(top_performing_vendors, kde=True, color='blue', bins=30,  alpha=0.5, label='Top Vendors')
# plt.axvline(top_mean, color='blue', linestyle='--', linewidth=2, label=f"Top Mean : {top_mean:.2f}")
# plt.axvline(top_lower, color='blue', linestyle='--', linewidth=2, label=f"Top Lower CI : {top_lower:.2f}")
# plt.axvline(top_upper, color='blue', linestyle='--', linewidth=2, label=f"Top Upper CI : {top_upper:.2f}")

# sns.histplot(low_performing_vendors, kde=True, color='red', bins=30,  alpha=0.5, label='Low Vendors')
# plt.axvline(low_mean, color='red', linestyle='--', linewidth=2, label=f"Low Mean : {low_mean:.2f}")
# plt.axvline(low_lower, color='red', linestyle='--', linewidth=2, label=f"Low Lower CI : {low_lower:.2f}")
# plt.axvline(low_upper, color='red', linestyle='--', linewidth=2, label=f"Low Upper CI : {low_upper:.2f}")

# plt.title('Confidence Interval Comparison: Top vs Low Vendors (Profit Margins)')
# plt.xlabel('Profit Margin (%)')
# plt.ylabel('Frequency')
# plt.legend()
# plt.grid(True)
# plt.savefig('images/confidence_interval_comparison.png', dpi=300, bbox_inches='tight')
# plt.show()

#####################################################################

# Q9. Is there a significant difference in profit margin between top-performing and low-performing vendors ? 
top_threshold = df_1['TotalSalesDollars'].quantile(0.75)
low_threshold = df_1['TotalSalesDollars'].quantile(0.25)
top_performing_vendors = df_1[df_1['TotalSalesDollars'] >= top_threshold]['ProfitMargin'].dropna()
low_performing_vendors = df_1[df_1['TotalSalesDollars'] <= low_threshold]['ProfitMargin'].dropna()

# perform two sample t-test
t_stat, p_value = stats.ttest_ind(top_performing_vendors, low_performing_vendors, equal_var=False)

print(f"T-statistic : {t_stat:.4f}, P-value : {p_value:.4f}")
if p_value < 0.5:
    print("Reject hypothesis : there is no significant difference in profit margin between top-performing and low-performing vendors ")
else:
    print("Fail to reject hypothesis : no significant difference in profit margin")


