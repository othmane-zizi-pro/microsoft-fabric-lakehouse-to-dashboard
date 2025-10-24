# 🚀 Microsoft Fabric Deployment Guide
## Deploy Your PySpark POC to the Cloud

**You've verified it works locally. Now let's deploy to Azure Fabric!**

---

## 🎯 What You'll Deploy

```
Your Laptop (✅ Working!)          Microsoft Fabric Cloud
─────────────────────               ───────────────────────

Sample CSVs                    →    Lakehouse Storage
PySpark Scripts                →    Fabric Notebooks
Local Processing               →    Spark Compute
Parquet Files                  →    Delta Tables
Local Dashboard                →    SQL Endpoint
                                    (Query from anywhere!)
```

---

## ⏱️ Time Estimate

- **Setup Fabric**: 15 minutes
- **Upload Data**: 5 minutes
- **Run Notebooks**: 10 minutes
- **Query Warehouse**: 5 minutes
- **Total**: ~35 minutes

---

## 📋 Prerequisites

✅ **Microsoft Account** (Outlook, Hotmail, or work account)
✅ **Azure Subscription** (Free tier works!)
✅ **Your working POC** (we just verified this!)

---

## Step 1: Sign Up for Microsoft Fabric (10 min)

### 1.1 Start Free Trial

1. Go to https://app.fabric.microsoft.com
2. Click **Start free trial**
3. Sign in with your Microsoft account
4. Accept terms and conditions
5. Choose **Fabric Trial** (60 days free!)

**You get:**
- F64 Capacity (plenty for learning)
- All Fabric features
- No credit card required
- $0 cost for 60 days

### 1.2 Create Workspace

1. Click **Workspaces** (left sidebar)
2. Click **+ New workspace**
3. Enter name: `AdventureWorks-POC`
4. Click **Apply**

✅ **Checkpoint**: You should see your new workspace!

---

## Step 2: Create Lakehouse (5 min)

### 2.1 Create Lakehouse

1. In your workspace, click **+ New**
2. Select **Lakehouse**
3. Name: `SalesData`
4. Click **Create**

**What is Lakehouse?**
- Storage for your data files
- Like AWS S3 or Azure Data Lake
- Stores both files and tables

### 2.2 Upload Sample Data

1. In Lakehouse, click **Files** (left panel)
2. Click **Upload** → **Upload files**
3. Navigate to: `/Users/othmanezizi/data_warehouse_project/data/poc_sample/raw/`
4. Select all 3 CSV files:
   - `DimProduct.csv`
   - `DimCustomer.csv`
   - `FactInternetSales.csv`
5. Click **Upload**

✅ **Checkpoint**: See 3 CSVs in Files section!

---

## Step 3: Create Your First Fabric Notebook (10 min)

### 3.1 Create Notebook

1. Click **+ New** → **Notebook**
2. Name it: `01_Extract`
3. Select **Lakehouse** → attach `SalesData`

### 3.2 Extract Code (Copy-Paste This)

Click **+Code** to add cells, then paste:

**Cell 1: Load Products**
```python
# Load Products CSV
df_products = spark.read.csv(
    "Files/DimProduct.csv",
    header=True,
    inferSchema=True
)

print(f"✓ Loaded {df_products.count()} products")
df_products.show(5)

# Save as Delta Table (direct path - no catalog needed)
df_products.write.mode("overwrite").format("delta").save("Tables/bronze_products")
print("✓ Saved to bronze_products table")
```

**Cell 2: Load Sales**
```python
# Load Sales CSV
df_sales = spark.read.csv(
    "Files/FactInternetSales.csv",
    header=True,
    inferSchema=True
)

print(f"✓ Loaded {df_sales.count()} sales transactions")
df_sales.show(5)

# Save as Delta Table
df_sales.write.mode("overwrite").format("delta").save("Tables/bronze_sales")
print("✓ Saved to bronze_sales table")
```

**Cell 3: Load Customers**
```python
# Load Customers CSV
df_customers = spark.read.csv(
    "Files/DimCustomer.csv",
    header=True,
    inferSchema=True
)

print(f"✓ Loaded {df_customers.count()} customers")
df_customers.show(5)

# Save as Delta Table
df_customers.write.mode("overwrite").format("delta").save("Tables/bronze_customers")
print("✓ Saved to bronze_customers table")
```

### 3.3 Run the Notebook

1. Click **Run all** (top toolbar)
2. Wait ~1 minute for Spark cluster to start
3. See each cell execute with results

✅ **Checkpoint**: See 3 Delta tables in **Tables** section!

---

## Step 4: Transform Data (10 min)

### 4.1 Create Transform Notebook

1. Click **+ New** → **Notebook**
2. Name: `02_Transform`
3. Attach to `SalesData` Lakehouse

### 4.2 Transform Code

**Cell 1: Load Bronze Tables**
```python
from pyspark.sql import functions as F

# Load bronze tables (use direct paths)
products = spark.read.format("delta").load("Tables/bronze_products")
sales = spark.read.format("delta").load("Tables/bronze_sales")
customers = spark.read.format("delta").load("Tables/bronze_customers")

print(f"✓ Loaded {products.count()} products")
print(f"✓ Loaded {sales.count()} sales")
print(f"✓ Loaded {customers.count()} customers")
```

**Cell 2: Create Sales by Product (Gold Layer)**
```python
# Join sales with products
sales_by_product = sales.join(products, "ProductKey", "left") \
    .groupBy("ProductKey", "ProductName") \
    .agg(
        F.sum("SalesAmount").alias("TotalSales"),
        F.sum("OrderQuantity").alias("TotalQuantity"),
        F.count("SalesOrderNumber").alias("OrderCount")
    ) \
    .orderBy(F.desc("TotalSales"))

# Save as Gold table
sales_by_product.write.mode("overwrite").format("delta").save("Tables/gold_sales_by_product")

print(f"✓ Created Sales by Product: {sales_by_product.count()} products")
sales_by_product.show(10)
```

**Cell 3: Create Sales Trend**
```python
# Sales trend by month
sales_trend = sales \
    .withColumn("YearMonth", F.date_format("OrderDate", "yyyy-MM")) \
    .groupBy("YearMonth") \
    .agg(
        F.sum("SalesAmount").alias("TotalSales"),
        F.count("SalesOrderNumber").alias("OrderCount")
    ) \
    .orderBy("YearMonth")

# Save as Gold table
sales_trend.write.mode("overwrite").format("delta").save("Tables/gold_sales_trend")

print(f"✓ Created Sales Trend: {sales_trend.count()} months")
sales_trend.show()
```

**Cell 4: Create Top Customers**
```python
# Top customers
top_customers = sales.join(customers, "CustomerKey", "left") \
    .withColumn("CustomerName",
                F.concat_ws(" ", F.col("FirstName"), F.col("LastName"))) \
    .groupBy("CustomerKey", "CustomerName", "EmailAddress") \
    .agg(
        F.sum("SalesAmount").alias("TotalPurchases"),
        F.count("SalesOrderNumber").alias("OrderCount")
    ) \
    .orderBy(F.desc("TotalPurchases")) \
    .limit(100)

# Save as Gold table
top_customers.write.mode("overwrite").format("delta").save("Tables/gold_top_customers")

print(f"✓ Created Top 100 Customers")
top_customers.show(10)
```

### 4.3 Run Transform Notebook

1. Click **Run all**
2. Watch the magic happen!

✅ **Checkpoint**: See 3 new `gold_*` tables!

---

## Step 5: Create SQL Warehouse (5 min)

### 5.1 Create Warehouse

1. In workspace, click **+ New** → **Data Warehouse**
2. Name: `SalesWarehouse`
3. Click **Create**

### 5.2 Load Data to Warehouse

**Option A: Via SQL (Easiest)**

In the Warehouse SQL editor, run:

```sql
-- Create tables from Lakehouse (3-part naming)
CREATE TABLE SalesByProduct AS
SELECT * FROM SalesData.dbo.gold_sales_by_product;

CREATE TABLE SalesTrend AS
SELECT * FROM SalesData.dbo.gold_sales_trend;

CREATE TABLE TopCustomers AS
SELECT * FROM SalesData.dbo.gold_top_customers;
```

**Option B: Via Lakehouse**

1. Go back to `SalesData` Lakehouse
2. Right-click `gold_sales_by_product`
3. Select **Copy to** → **Data Warehouse**
4. Choose `SalesWarehouse`
5. Repeat for other gold tables

✅ **Checkpoint**: Query your warehouse!

```sql
SELECT TOP 10
    ProductName,
    TotalSales,
    OrderCount
FROM SalesByProduct
ORDER BY TotalSales DESC;
```

---

## Step 6: Query Your Data (5 min)

### 6.1 Warehouse Queries

Try these queries in the SQL editor:

**Top Products:**
```sql
SELECT
    ProductName,
    CAST(TotalSales AS DECIMAL(18,2)) AS TotalSales,
    TotalQuantity,
    OrderCount
FROM SalesByProduct
ORDER BY TotalSales DESC;
```

**Sales Trend:**
```sql
SELECT
    YearMonth,
    CAST(TotalSales AS DECIMAL(18,2)) AS TotalSales,
    OrderCount,
    CAST(TotalSales / OrderCount AS DECIMAL(18,2)) AS AvgOrderValue
FROM SalesTrend
ORDER BY YearMonth;
```

**VIP Customers:**
```sql
SELECT
    CustomerName,
    EmailAddress,
    CAST(TotalPurchases AS DECIMAL(18,2)) AS TotalPurchases,
    OrderCount
FROM TopCustomers
WHERE TotalPurchases > 10000
ORDER BY TotalPurchases DESC;
```

### 6.2 Get SQL Endpoint

1. Click on your Warehouse
2. Click **Settings** → **Connection strings**
3. Copy the **SQL connection string**

**Format:**
```
[workspace-name].datawarehouse.fabric.microsoft.com
```

Save this! You'll use it to connect from:
- Power Apps
- Power BI
- Excel
- Python
- Any SQL client

---

## Step 7: Visualize in Power BI (10 min)

### 7.1: Create Semantic Model

1. In your SalesWarehouse, click "New Semantic Model"
2. Give it a name: SalesAnalytics
3. Select your tables:
- ✅ SalesByProduct
- ✅ SalesTrend
- ✅ TopCustomers
4. Click "Confirm" or "Create"

### 7.2 Create Report from Semantic Model

After the semantic model is created:

1. You'll see your SalesAnalytics semantic model in your Workspace
2. Click on it to open
3. Now you should see "Autocreate a report" button
4. Click it to open the Power BI report editor


### 7.3 Build Visualizations (optional, if )

Once in the report editor, you'll see:
- Left panel: Visualizations gallery
- Right panel: Fields (your tables and columns)
- Center: Report canvas

Create these visuals:

1. KPI Card - Total Sales

- Click "Card" visual
- Drag SalesByProduct → TotalSales to the field
- Click the visual, then "Format" tab → change title to "Total Revenue"

2. Bar Chart - Top 10 Products

- Click "Clustered Bar Chart"
- Y-axis: SalesByProduct → ProductName
- X-axis: SalesByProduct → TotalSales
- Click the visual → Filters → set ProductName to show "Top 10" by TotalSales

3. Customer Segmentation Scatter Plot

- Click blank space → "Scatter chart"
- Drag fields:
1. TopCustomers → OrderCount → X-axis
2. TopCustomers → TotalPurchases → Y-axis
3. TopCustomers → CustomerName → Tooltops (shows
dots' name on hover)
- Add TotalPurchases to Size to make high-value customers bigger

What you'll see: Clusters showing:
- High frequency buyers (many orders)
- High value buyers (big purchases)
- VIP customers (top-right corner)

4. Table - Top Customers

- Click "Table"
- Add columns:
- TopCustomers → CustomerName
- TopCustomers → TotalPurchases
- TopCustomers → OrderCount

### 7.4 Save and Publish

1. Click "File" → "Save" (or Ctrl+S)
2. Name it: Sales Dashboard
3. It automatically publishes to your workspace

---

## Step 8: Schedule Automation (5 min)

### 8.1 Schedule Extract Notebook

1. Open `01_Extract` notebook
2. Click **Run** → **Schedule**
3. Set:
   - **Frequency**: Daily
   - **Time**: 2:00 AM
   - **Time zone**: Your timezone
4. Click **Apply**

### 8.2 Schedule Transform Notebook

1. Open `02_Transform` notebook
2. Click **Run** → **Schedule**
3. Set:
   - **Frequency**: Daily
   - **Time**: 3:00 AM (after extract)
4. Click **Apply**

✅ **Checkpoint**: Automated pipeline!

Now your data refreshes automatically every day!

---

## 🎉 Success! You've Deployed to Fabric!

### What You Built:

```
┌─────────────────────────────────────────────────────────┐
│             MICROSOFT FABRIC                            │
│                                                          │
│  📁 Lakehouse: SalesData                                │
│     ├─ Files/                                           │
│     │   ├─ DimProduct.csv                               │
│     │   ├─ DimCustomer.csv                              │
│     │   └─ FactInternetSales.csv                        │
│     │                                                    │
│     └─ Tables/                                          │
│         ├─ 🥉 bronze_products                           │
│         ├─ 🥉 bronze_sales                              │
│         ├─ 🥉 bronze_customers                          │
│         ├─ 🥇 gold_sales_by_product                     │
│         ├─ 🥇 gold_sales_trend                          │
│         └─ 🥇 gold_top_customers                        │
│                                                          │
│  🗄️  Data Warehouse: SalesWarehouse                    │
│     ├─ SalesByProduct                                   │
│     ├─ SalesTrend                                       │
│     └─ TopCustomers                                     │
│                                                          │
│  📊 Power BI Report: Sales Dashboard                    │
│     ├─ KPIs                                             │
│     ├─ Charts                                           │
│     └─ Tables                                           │
│                                                          │
│  ⏰ Scheduled Notebooks                                 │
│     ├─ 01_Extract (Daily 2AM)                           │
│     └─ 02_Transform (Daily 3AM)                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Resume Bullet Points

```
• Architected and deployed end-to-end data pipeline on Microsoft
  Fabric, processing 1,000+ sales transactions using PySpark and
  Delta Lake, implementing medallion architecture (bronze/silver/gold)

• Built automated ETL workflow in Fabric Notebooks with scheduled
  execution, transforming raw CSV data into analytics-ready star
  schema in SQL Data Warehouse

• Developed interactive Power BI dashboards querying Fabric SQL
  endpoint, providing real-time sales insights and customer analytics
  to stakeholders

• Demonstrated cloud data engineering skills using modern data stack:
  Microsoft Fabric, Delta Lake, PySpark, SQL Warehouse, and Power BI
```

---

## 🔧 Troubleshooting

**Notebook won't start?**
- Wait 1-2 minutes for Spark cluster to initialize
- Check capacity isn't paused

**Can't see tables?**
- Refresh the Lakehouse view
- Check notebook completed successfully

**SQL queries fail?**
- Verify table names (case-sensitive!)
- Check Lakehouse is attached to Warehouse

**Scheduled runs not working?**
- Verify workspace has capacity assigned
- Check time zone settings

---

## 🚀 Next Steps

Now that you have Fabric working:

1. **Add More Data**
   - Upload real AdventureWorks files
   - Connect to live data sources
   - Set up incremental loads

2. **Build Power Apps**
   - Connect to SQL endpoint
   - Create data entry forms
   - Build approval workflows

3. **Advanced Analytics**
   - Add ML models (Fabric AutoML)
   - Predictive forecasting
   - Anomaly detection

4. **Production Features**
   - Data quality monitoring
   - Alerting on failures
   - Cost optimization

---

## 💰 Cost Management

**Free Tier includes:**
- ✅ 60-day trial
- ✅ F64 capacity
- ✅ All features

**After Trial:**
- Pause capacity when not using
- Use Fabric capacity units
- ~$0.50/hour when active
- $0 when paused

**Best practice:**
- Develop during trial
- Pause nights/weekends
- Schedule notebooks efficiently

---

## 📚 Learn More

- **Fabric Docs**: https://learn.microsoft.com/fabric/
- **Lakehouse Guide**: https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview
- **PySpark on Fabric**: https://learn.microsoft.com/fabric/data-engineering/spark-overview
- **SQL Warehouse**: https://learn.microsoft.com/fabric/data-warehouse/

---

## ✅ Checklist

- [ ] Signed up for Fabric trial
- [ ] Created workspace: AdventureWorks-POC
- [ ] Created Lakehouse: SalesData
- [ ] Uploaded 3 CSV files
- [ ] Ran Extract notebook → 3 bronze tables
- [ ] Ran Transform notebook → 3 gold tables
- [ ] Created Data Warehouse: SalesWarehouse
- [ ] Loaded warehouse tables
- [ ] Ran SQL queries successfully
- [ ] Created Power BI report
- [ ] Scheduled notebooks

**All checked?** 🎉 **You're a Fabric expert now!**

---

**Questions?** Review this guide or check Microsoft Fabric docs!

**Ready to show off?** Take screenshots, update your LinkedIn! 🚀
