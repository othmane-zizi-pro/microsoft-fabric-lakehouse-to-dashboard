"""
Create clean sample data for POC demo
This bypasses the AdventureWorks CSV encoding issues
"""
import pandas as pd
from pathlib import Path
import random
from datetime import datetime, timedelta

print("="*70)
print("Creating Sample Data for POC")
print("="*70)

# Create directories
Path("data/poc_sample/raw").mkdir(parents=True, exist_ok=True)

# ============================================================================
# 1. DimProduct - 50 products
# ============================================================================
print("\n📦 Creating Products...")
products_data = []
bike_types = ['Road', 'Mountain', 'Touring', 'Hybrid']
colors = ['Red', 'Black', 'Silver', 'Blue', 'Yellow']

for i in range(1, 51):
    bike_type = random.choice(bike_types)
    color = random.choice(colors)
    products_data.append({
        'ProductKey': i,
        'ProductName': f"{bike_type} Bike {color} {i}",
        'Color': color,
        'StandardCost': random.randint(200, 800),
        'ListPrice': random.randint(500, 2000),
        'ProductSubcategoryKey': random.randint(1, 5)
    })

df_products = pd.DataFrame(products_data)
df_products.to_csv('data/poc_sample/raw/DimProduct.csv', index=False)
print(f"✓ Created {len(df_products)} products")

# ============================================================================
# 2. DimCustomer - 200 customers
# ============================================================================
print("\n👥 Creating Customers...")
first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa', 'Tom', 'Anna']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']

customers_data = []
for i in range(1, 201):
    first = random.choice(first_names)
    last = random.choice(last_names)
    customers_data.append({
        'CustomerKey': i,
        'FirstName': first,
        'LastName': last,
        'EmailAddress': f"{first.lower()}.{last.lower()}{i}@email.com",
        'YearlyIncome': random.randint(30000, 150000),
        'TotalChildren': random.randint(0, 4),
        'Education': random.choice(['High School', 'Bachelors', 'Graduate Degree']),
        'Occupation': random.choice(['Professional', 'Skilled Manual', 'Clerical', 'Management']),
        'GeographyKey': random.randint(1, 10)
    })

df_customers = pd.DataFrame(customers_data)
df_customers.to_csv('data/poc_sample/raw/DimCustomer.csv', index=False)
print(f"✓ Created {len(df_customers)} customers")

# ============================================================================
# 3. FactInternetSales - 1000 sales transactions
# ============================================================================
print("\n💰 Creating Sales Transactions...")
sales_data = []
start_date = datetime(2023, 1, 1)

for i in range(1, 1001):
    order_date = start_date + timedelta(days=random.randint(0, 365))
    product_key = random.randint(1, 50)
    customer_key = random.randint(1, 200)
    quantity = random.randint(1, 3)
    unit_price = random.randint(500, 2000)
    sales_amount = quantity * unit_price

    sales_data.append({
        'SalesOrderNumber': f'SO{i:05d}',
        'SalesOrderLineNumber': 1,
        'OrderDate': order_date.strftime('%Y-%m-%d'),
        'ProductKey': product_key,
        'CustomerKey': customer_key,
        'OrderQuantity': quantity,
        'UnitPrice': unit_price,
        'SalesAmount': sales_amount,
        'TaxAmt': sales_amount * 0.08,
        'Freight': random.randint(10, 50)
    })

df_sales = pd.DataFrame(sales_data)
df_sales.to_csv('data/poc_sample/raw/FactInternetSales.csv', index=False)
print(f"✓ Created {len(df_sales)} sales transactions")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*70)
print("✅ Sample Data Created Successfully!")
print("="*70)
print(f"\nData location: data/poc_sample/raw/")
print(f"  • DimProduct.csv ({len(df_products)} rows)")
print(f"  • DimCustomer.csv ({len(df_customers)} rows)")
print(f"  • FactInternetSales.csv ({len(df_sales)} rows)")
print(f"\nTotal Sales: ${df_sales['SalesAmount'].sum():,.2f}")
print(f"Date Range: {df_sales['OrderDate'].min()} to {df_sales['OrderDate'].max()}")
print("\nNext: Run 01_extract_simple.py with sample data path")
print("="*70 + "\n")
