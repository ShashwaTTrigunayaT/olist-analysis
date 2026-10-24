import pandas as pd
import os

RAW_DIR = "data/raw"

files = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

dataframes = {}

for name, filename in files.items():
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(path)
    dataframes[name] = df

    print(f"\n{'='*50}")
    print(f"TABLE: {name}")
    print(f"{'='*50}")
    print(f"Shape: {df.shape}")
    print(f"\nColumns:\n{list(df.columns)}")
    print(f"\nNull counts:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"\nDtypes:\n{df.dtypes}")