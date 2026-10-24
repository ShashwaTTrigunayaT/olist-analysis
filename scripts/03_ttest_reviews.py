"""Welch's t-test: do late deliveries get lower review scores than on-time ones?

Compares review scores for delivered orders that arrived after the estimated
delivery date against those that arrived on or before it.
"""

import json
import os

import pandas as pd
from scipy import stats

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLEAN_DIR = os.path.join(SCRIPT_DIR, "..", "data", "cleaned")
OUTPUT = os.path.join(CLEAN_DIR, "ttest_review_scores.json")


def main():
    orders = pd.read_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"), parse_dates=[
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ])
    reviews = pd.read_csv(os.path.join(CLEAN_DIR, "order_reviews_clean.csv"))

    df = orders.merge(reviews[["order_id", "review_score"]], on="order_id", how="inner")
    df = df[df["is_delivered"] & df["delivery_delay_days"].notna() & df["review_score"].notna()]

    late = df.loc[df["delivery_delay_days"] > 0, "review_score"]
    on_time = df.loc[df["delivery_delay_days"] <= 0, "review_score"]

    t_stat, p_value = stats.ttest_ind(late, on_time, equal_var=False)

    # Cohen's d (pooled standard deviation)
    pooled_sd = ((late.std() ** 2 + on_time.std() ** 2) / 2) ** 0.5
    cohens_d = (late.mean() - on_time.mean()) / pooled_sd if pooled_sd else float("nan")

    result = {
        "late_n": int(late.shape[0]),
        "on_time_n": int(on_time.shape[0]),
        "late_mean_review": round(float(late.mean()), 3),
        "on_time_mean_review": round(float(on_time.mean()), 3),
        "mean_difference": round(float(late.mean() - on_time.mean()), 3),
        "t_statistic": round(float(t_stat), 3),
        "p_value": float(p_value),
        "cohens_d": round(float(cohens_d), 3),
        "test": "Welch's two-sample t-test, two-sided",
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
