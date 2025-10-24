# Microsoft Fabric Lakehouse to Dashboard

> **A production-ready data pipeline demonstrating PySpark ETL, Medallion architecture, and Delta Lake on Microsoft Fabric**

[![Microsoft Fabric](https://img.shields.io/badge/Microsoft-Fabric-blue.svg)](https://www.microsoft.com/fabric)
[![PySpark](https://img.shields.io/badge/PySpark-3.4+-orange.svg)](https://spark.apache.org/)
[![Delta Lake](https://img.shields.io/badge/Delta-Lake-00ADD4.svg)](https://delta.io/)

## Overview

This project provides **ready-to-deploy Fabric Notebooks** implementing an end-to-end data engineering pipeline using **Microsoft Fabric Lakehouse**. It processes 1,000+ sales transactions across 50 products and 200 customers, demonstrating enterprise data engineering patterns using the **Medallion Architecture** (Bronze/Silver/Gold).

**Key Technologies:** Microsoft Fabric | PySpark | Delta Lake | SQL Data Warehouse | Power BI

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              MICROSOFT FABRIC LAKEHOUSE                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  📁 Files/                                                    │
│     └─ Raw CSV uploads (DimProduct, DimCustomer, Sales)      │
│                                                               │
│  📊 Tables/                                                   │
│     ├─ 🥉 BRONZE LAYER (Delta Tables)                        │
│     │   └─ Raw data ingestion from CSV files                 │
│     │      • bronze_products, bronze_sales, bronze_customers │
│     │                                                         │
│     ├─ 🥈 SILVER LAYER (Delta Tables) - OPTIONAL             │
│     │   └─ Cleaned & validated data                          │
│     │                                                         │
│     └─ 🥇 GOLD LAYER (Delta Tables)                          │
│         └─ Business-ready analytics                          │
│            • gold_sales_by_product                           │
│            • gold_sales_trend                                │
│            • gold_top_customers                              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                   SQL DATA WAREHOUSE                          │
│     • Load Gold tables for BI consumption                     │
│     • Power BI integration via semantic model                 │
│     • Real-time analytics via SQL endpoint                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- **Microsoft Account** (Outlook, Hotmail, or work/school account)
- **Microsoft Fabric Free Trial** (60 days, no credit card required)
- **Python 3.8+** (to generate sample data)

### Step 1: Generate Sample Data

```bash
# Clone the repository
git clone https://github.com/othmanezizi/microsoft-fabric-lakehouse-to-dashboard.git
cd microsoft-fabric-lakehouse-to-dashboard

# Install dependencies (only for data generation)
pip install pandas

# Generate sample CSV files
python 00_create_sample_data.py
```

This creates three CSV files in `data/poc_sample/raw/`:
- `DimProduct.csv` (50 products)
- `DimCustomer.csv` (200 customers)
- `FactInternetSales.csv` (1,000 sales transactions)

### Step 2: Deploy to Microsoft Fabric

Follow the comprehensive deployment guide:

📖 **[FABRIC_DEPLOYMENT_GUIDE.md](FABRIC_DEPLOYMENT_GUIDE.md)** (~35 minutes)

**Quick Summary:**
1. Sign up for Fabric trial at https://app.fabric.microsoft.com
2. Create Lakehouse and upload CSV files
3. Upload `01_Extract.ipynb` and `02_Transform.ipynb` notebooks
4. Run notebooks to create Delta tables
5. Create SQL Warehouse and Power BI dashboard

---

## Project Structure

```
.
├── 00_create_sample_data.py      # Generate sample CSV data
├── 01_Extract.ipynb              # Fabric Notebook: CSV → Bronze Delta tables
├── 02_Transform.ipynb            # Fabric Notebook: Bronze → Gold Delta tables
├── FABRIC_DEPLOYMENT_GUIDE.md    # Step-by-step Fabric deployment guide
├── README.md                     # This file
├── requirements.txt              # Python dependencies (pandas only)
│
└── data/
    └── poc_sample/raw/           # Sample CSV files to upload to Fabric
        ├── DimProduct.csv
        ├── DimCustomer.csv
        └── FactInternetSales.csv
```

---

## Data Pipeline Details

### Sample Data
- **50 Products**: Road, Mountain, Touring, Hybrid bikes
- **200 Customers**: Realistic names, emails, demographics
- **1,000 Sales**: $2.5M+ total sales across 2023
- **13 Months** of transaction history

### Fabric Notebooks

**01_Extract.ipynb - Bronze Layer**
```python
# Load CSVs from Lakehouse Files and save as Delta tables
df_products = spark.read.csv("Files/DimProduct.csv", header=True, inferSchema=True)
df_products.write.mode("overwrite").format("delta").save("Tables/bronze_products")

df_sales = spark.read.csv("Files/FactInternetSales.csv", header=True, inferSchema=True)
df_sales.write.mode("overwrite").format("delta").save("Tables/bronze_sales")

df_customers = spark.read.csv("Files/DimCustomer.csv", header=True, inferSchema=True)
df_customers.write.mode("overwrite").format("delta").save("Tables/bronze_customers")
```

**02_Transform.ipynb - Gold Layer**
```python
from pyspark.sql import functions as F

# Load Bronze tables
products = spark.read.format("delta").load("Tables/bronze_products")
sales = spark.read.format("delta").load("Tables/bronze_sales")
customers = spark.read.format("delta").load("Tables/bronze_customers")

# Create Gold analytics tables
sales_by_product = sales.join(products, "ProductKey") \
    .groupBy("ProductKey", "ProductName") \
    .agg(
        F.sum("SalesAmount").alias("TotalSales"),
        F.sum("OrderQuantity").alias("TotalQuantity"),
        F.count("SalesOrderNumber").alias("OrderCount")
    ) \
    .orderBy(F.desc("TotalSales"))

sales_by_product.write.mode("overwrite").format("delta").save("Tables/gold_sales_by_product")
```

---

## Microsoft Fabric Deployment

### Why Fabric?
- **60-day free trial** (no credit card required)
- **Unified platform**: Lakehouse + Warehouse + Notebooks + Power BI all in one
- **Delta Lake** support built-in (ACID transactions, time travel)
- **Auto-scaling** managed Spark clusters
- **SQL endpoint** for instant querying
- **Power BI integration** for dashboards

### Deployment Workflow
1. **Generate data** → Run `00_create_sample_data.py` locally
2. **Sign up** → https://app.fabric.microsoft.com (free trial)
3. **Create Lakehouse** → Upload CSV files to Files/
4. **Upload notebooks** → Import `01_Extract.ipynb` and `02_Transform.ipynb`
5. **Run notebooks** → Execute to create Delta tables
6. **Create Warehouse** → Load Gold tables for BI
7. **Build dashboard** → Use Power BI semantic model

**Full step-by-step guide:** [FABRIC_DEPLOYMENT_GUIDE.md](FABRIC_DEPLOYMENT_GUIDE.md) (~35 minutes)

### Expected Results in Fabric

After running both notebooks, you'll have:

**Bronze Delta Tables:**
- `bronze_products` (50 rows)
- `bronze_sales` (1,000 rows)
- `bronze_customers` (200 rows)

**Gold Delta Tables:**
- `gold_sales_by_product` (top products by revenue)
- `gold_sales_trend` (monthly sales over time)
- `gold_top_customers` (top 100 customers by spend)

---

## Key Features

✅ **Medallion Architecture**: Industry-standard Bronze/Silver/Gold pattern using Delta Lake
✅ **Production-Ready Notebooks**: Upload directly to Fabric, no copy-paste needed
✅ **Delta Lake**: ACID transactions, time travel, and schema evolution
✅ **PySpark on Fabric**: Managed Spark clusters with auto-scaling
✅ **SQL Queryable**: Direct SQL access via Lakehouse SQL endpoint
✅ **Power BI Ready**: Seamless integration for dashboards and reports
✅ **Sample Data Included**: Generate realistic test data with one command

---

## Learning Outcomes

After completing this project, you'll understand:

**Microsoft Fabric**
- Lakehouse architecture and capabilities
- Uploading and managing notebooks
- Working with Delta tables
- SQL endpoint for querying
- Power BI semantic model creation

**PySpark on Fabric**
- DataFrame API and transformations
- Reading CSVs and writing Delta tables
- Joins, aggregations, and window functions
- Spark session management in Fabric notebooks

**Data Engineering Patterns**
- Medallion architecture (Bronze/Silver/Gold layers)
- Delta Lake ACID transactions and versioning
- Star schema design (fact + dimension tables)
- Building analytics-ready gold tables

**Cloud Data Warehousing**
- Lakehouse vs Data Warehouse differences
- Loading tables from Lakehouse to Warehouse
- BI integration and reporting patterns

---

## Resume-Ready Bullet Points

```
• Architected end-to-end data pipeline on Microsoft Fabric Lakehouse,
  processing 1,000+ sales transactions using PySpark and Delta Lake,
  implementing medallion architecture (Bronze/Silver/Gold layers)

• Developed production-ready Fabric notebooks transforming raw CSV data
  into analytics-ready Delta tables with ACID compliance, enabling
  business intelligence and reporting capabilities

• Deployed data warehouse on Microsoft Fabric with SQL endpoint and
  Power BI integration, providing real-time sales insights and customer
  analytics through interactive dashboards

• Demonstrated enterprise data engineering patterns including star schema
  design, scheduled notebook execution, and cloud-native data processing
  on Microsoft Fabric platform
```

---

## Troubleshooting

**Can't generate sample data?**
```bash
# Ensure pandas is installed
pip install pandas

# Run the data generation script
python 00_create_sample_data.py

# Verify CSVs were created
ls data/poc_sample/raw/  # Should see 3 CSV files
```

**Notebook won't start in Fabric?**
- Wait 1-2 minutes for Spark cluster to initialize on first run
- Check that your Fabric workspace has an active capacity assigned
- Verify you're not in a paused capacity state

**Can't see tables after running notebooks?**
- Refresh the Lakehouse view (click refresh icon)
- Check that notebook cells executed successfully (no errors)
- Verify files are in the correct location (Files/ for CSVs, Tables/ for Delta)

**SQL queries fail in Warehouse?**
- Verify table names match exactly (case-sensitive)
- Ensure Lakehouse is properly linked to the Warehouse
- Check that Gold tables were created successfully in the Lakehouse

**Power BI can't find tables?**
- Create a Semantic Model from the Warehouse first
- Ensure tables are loaded into the Warehouse (not just Lakehouse)
- Refresh the semantic model after loading new data

---

## Next Steps

**Expand Your Fabric Pipeline:**
- Add real AdventureWorks database (16+ tables)
- Implement incremental loading patterns
- Add Silver layer with data quality checks
- Create additional Gold analytics tables

**Power BI Enhancements:**
- Build comprehensive dashboard with KPIs
- Add customer segmentation analysis
- Create sales forecasting visuals
- Implement row-level security (RLS)

**Production Features:**
- Schedule notebook execution (automated daily runs)
- Add data quality monitoring and alerts
- Implement Delta Lake time travel for auditing
- Set up Fabric deployment pipelines (CI/CD)

**Advanced Analytics:**
- Add Fabric ML models for prediction
- Implement real-time streaming with Event Streams
- Connect live data sources (Azure SQL, APIs)
- Build data science notebooks with AutoML

---

## Resources

**Microsoft Fabric:**
- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Fabric Lakehouse Overview](https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview)
- [PySpark on Fabric](https://learn.microsoft.com/fabric/data-engineering/spark-overview)
- [Fabric Data Warehouse](https://learn.microsoft.com/fabric/data-warehouse/)
- [Power BI in Fabric](https://learn.microsoft.com/fabric/get-started/end-to-end-tutorials)

**Data Engineering Concepts:**
- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- [Delta Lake Documentation](https://docs.delta.io/latest/index.html)
- [PySpark API Reference](https://spark.apache.org/docs/latest/api/python/)

---

## License

MIT License - feel free to use this project for learning and portfolio purposes.

---

**Built with ❤️ for data engineering learners**

*Questions or feedback? Open an issue or connect with me on [LinkedIn](https://www.linkedin.com/in/othmanezizi/)!*
