import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "..", "data", "raw")
CLEAN_DIR = os.path.join(SCRIPT_DIR, "..", "data", "cleaned")
os.makedirs(CLEAN_DIR, exist_ok=True)

# ---- Load ----
customers = pd.read_csv(os.path.join(RAW_DIR, "olist_customers_dataset.csv"))
geolocation = pd.read_csv(os.path.join(RAW_DIR, "olist_geolocation_dataset.csv"))
orders = pd.read_csv(os.path.join(RAW_DIR, "olist_orders_dataset.csv"))
order_items = pd.read_csv(os.path.join(RAW_DIR, "olist_order_items_dataset.csv"))
order_payments = pd.read_csv(os.path.join(RAW_DIR, "olist_order_payments_dataset.csv"))
order_reviews = pd.read_csv(os.path.join(RAW_DIR, "olist_order_reviews_dataset.csv"))
products = pd.read_csv(os.path.join(RAW_DIR, "olist_products_dataset.csv"))
sellers = pd.read_csv(os.path.join(RAW_DIR, "olist_sellers_dataset.csv"))
category_translation = pd.read_csv(os.path.join(RAW_DIR, "product_category_name_translation.csv"))

# ---- 1. Convert date columns in orders from text to real datetime ----
date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

# ---- 2. Flag undelivered orders instead of dropping them ----
orders["is_delivered"] = orders["order_delivered_customer_date"].notnull()

# ---- 3. Calculate delivery delay only where we have real delivery dates ----
orders["delivery_delay_days"] = (
    orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
).dt.days
# Positive number = delivered late, negative = delivered early, NaN = not delivered yet

# ---- 4. Handle missing product categories ----
products["product_category_name"] = products["product_category_name"].fillna("unknown")

# ---- 5. Merge category translation into products (English names) ----
products = products.merge(category_translation, on="product_category_name", how="left")
products["product_category_name_english"] = products["product_category_name_english"].fillna("unknown")

# ---- 6. Missing review comments are NOT errors — just mark clearly ----
order_reviews["review_comment_title"] = order_reviews["review_comment_title"].fillna("No title given")
order_reviews["review_comment_message"] = order_reviews["review_comment_message"].fillna("No comment given")

# ---- 7. Aggregate geolocation: one lat/lng per zip code prefix (average) ----
geolocation_agg = geolocation.groupby("geolocation_zip_code_prefix").agg({
    "geolocation_lat": "mean",
    "geolocation_lng": "mean",
    "geolocation_city": "first",
    "geolocation_state": "first",
}).reset_index()

# ---- Save cleaned files ----
customers.to_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"), index=False)
orders.to_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"), index=False)
order_items.to_csv(os.path.join(CLEAN_DIR, "order_items_clean.csv"), index=False)
order_payments.to_csv(os.path.join(CLEAN_DIR, "order_payments_clean.csv"), index=False)
order_reviews.to_csv(os.path.join(CLEAN_DIR, "order_reviews_clean.csv"), index=False)
products.to_csv(os.path.join(CLEAN_DIR, "products_clean.csv"), index=False)
sellers.to_csv(os.path.join(CLEAN_DIR, "sellers_clean.csv"), index=False)
geolocation_agg.to_csv(os.path.join(CLEAN_DIR, "geolocation_clean.csv"), index=False)

print("Cleaning complete. Summary:")
print(f"Orders: {len(orders)} total, {orders['is_delivered'].sum()} delivered, {(~orders['is_delivered']).sum()} not delivered")
print(f"Products with unknown category: {(products['product_category_name']=='unknown').sum()}")
print(f"Geolocation rows reduced from {len(geolocation)} to {len(geolocation_agg)} (one per zip prefix)")