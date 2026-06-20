"""
Step 1 — Data Generation & Cleaning
Email Marketing Funnel Analysis

Simulates 10,000 realistic email-marketing records, enforces logical
consistency across the funnel, runs data-quality checks, and exports both
raw and cleaned CSV files.
"""

import os
import numpy as np
import pandas as pd

# Reproducibility
np.random.seed(42)

N_ROWS = 10_000
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def generate_dataset(n=N_ROWS):
    """Simulate the raw email campaign dataset."""

    # ---- Categorical dimensions ----------------------------------------
    campaign_type = np.random.choice(
        ["Welcome", "Promotional", "Newsletter"],
        size=n,
        p=[0.25, 0.45, 0.30],
    )
    subject_line = np.random.choice(["Version_A", "Version_B"], size=n, p=[0.5, 0.5])
    device_type = np.random.choice(
        ["Mobile", "Desktop", "Tablet"], size=n, p=[0.55, 0.35, 0.10]
    )
    region = np.random.choice(["North", "South", "East", "West"], size=n)
    customer_segment = np.random.choice(
        ["New", "Returning", "VIP"], size=n, p=[0.45, 0.40, 0.15]
    )

    # ---- Dates (last 6 months) -----------------------------------------
    end_date = pd.Timestamp("2025-06-15")
    start_date = end_date - pd.Timedelta(days=182)
    random_days = np.random.randint(0, 183, size=n)
    sent_date = start_date + pd.to_timedelta(random_days, unit="D")

    df = pd.DataFrame(
        {
            "email_id": [f"EM{100000 + i}" for i in range(n)],
            "campaign_type": campaign_type,
            "subject_line": subject_line,
            "sent_date": sent_date,
            "device_type": device_type,
            "region": region,
            "customer_segment": customer_segment,
        }
    )

    # ---- Funnel simulation with realistic probabilities ----------------
    # 1) Delivered (95%)
    df["delivered"] = np.random.binomial(1, 0.95, size=n)

    # 2) Opened (28-35% of delivered) — Version_B subject lines perform
    #    slightly better to create a detectable A/B effect.
    base_open = np.where(df["subject_line"] == "Version_B", 0.335, 0.295)
    # Campaign-type modifiers
    camp_open_mod = df["campaign_type"].map(
        {"Welcome": 0.04, "Promotional": -0.01, "Newsletter": 0.0}
    )
    open_prob = np.clip(base_open + camp_open_mod, 0, 1)
    df["opened"] = np.where(
        df["delivered"] == 1, np.random.binomial(1, open_prob), 0
    )

    # 3) Clicked (CTOR roughly 30%, so CTR ~ 8-12% of delivered)
    ctor_prob = 0.30 + df["campaign_type"].map(
        {"Welcome": 0.05, "Promotional": 0.03, "Newsletter": -0.02}
    )
    ctor_prob = np.clip(ctor_prob, 0, 1)
    df["clicked"] = np.where(
        df["opened"] == 1, np.random.binomial(1, ctor_prob), 0
    )

    # 4) Converted (2-5% of delivered => conversion of clickers ~ 25-40%)
    conv_prob = 0.30 + df["device_type"].map(
        {"Desktop": 0.06, "Tablet": 0.0, "Mobile": -0.05}
    )
    conv_prob = conv_prob + df["customer_segment"].map(
        {"VIP": 0.10, "Returning": 0.03, "New": -0.04}
    )
    conv_prob = np.clip(conv_prob, 0, 1)
    df["converted"] = np.where(
        df["clicked"] == 1, np.random.binomial(1, conv_prob), 0
    )

    # 5) Unsubscribed (1-2% of delivered)
    df["unsubscribed"] = np.where(
        df["delivered"] == 1, np.random.binomial(1, 0.015, size=n), 0
    )

    return df


def quality_report(df, label):
    """Print a concise data-quality summary."""
    print(f"\n===== Data Quality Report: {label} =====")
    print(f"Shape: {df.shape}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print(f"Duplicate email_id: {df['email_id'].duplicated().sum()}")
    print("Null counts:")
    print(df.isnull().sum().to_string())
    # Logical consistency violations
    viol_open = ((df["opened"] == 1) & (df["delivered"] == 0)).sum()
    viol_click = ((df["clicked"] == 1) & (df["opened"] == 0)).sum()
    viol_conv = ((df["converted"] == 1) & (df["clicked"] == 0)).sum()
    print(f"Opened but not delivered: {viol_open}")
    print(f"Clicked but not opened : {viol_click}")
    print(f"Converted but not clicked: {viol_conv}")


def clean_dataset(df):
    """Enforce consistency, types, and remove duplicates."""
    df = df.copy()
    # Logical consistency (defensive cascade)
    df.loc[df["delivered"] == 0, ["opened", "clicked", "converted", "unsubscribed"]] = 0
    df.loc[df["opened"] == 0, ["clicked", "converted"]] = 0
    df.loc[df["clicked"] == 0, "converted"] = 0

    # Types
    df["sent_date"] = pd.to_datetime(df["sent_date"])
    flag_cols = ["delivered", "opened", "clicked", "converted", "unsubscribed"]
    df[flag_cols] = df[flag_cols].astype(int)
    cat_cols = ["campaign_type", "subject_line", "device_type", "region", "customer_segment"]
    for c in cat_cols:
        df[c] = df[c].astype("category")

    # De-duplicate
    df = df.drop_duplicates(subset="email_id").reset_index(drop=True)

    # Derived helper columns
    df["bounced"] = (df["delivered"] == 0).astype(int)
    df["sent_week"] = df["sent_date"].dt.to_period("W").dt.start_time
    return df


def main():
    raw = generate_dataset()
    quality_report(raw, "Raw")
    raw_path = os.path.join(DATA_DIR, "raw_email_data.csv")
    raw.to_csv(raw_path, index=False)
    print(f"\nRaw data saved -> {raw_path}")

    cleaned = clean_dataset(raw)
    quality_report(cleaned, "Cleaned")
    clean_path = os.path.join(DATA_DIR, "cleaned_email_data.csv")
    cleaned.to_csv(clean_path, index=False)
    print(f"Cleaned data saved -> {clean_path}")

    # Headline funnel numbers
    print("\n===== Headline Funnel Rates =====")
    sent = len(cleaned)
    delivered = cleaned["delivered"].sum()
    opened = cleaned["opened"].sum()
    clicked = cleaned["clicked"].sum()
    converted = cleaned["converted"].sum()
    print(f"Delivery Rate : {delivered/sent:.1%}")
    print(f"Open Rate     : {opened/delivered:.1%}")
    print(f"CTR           : {clicked/delivered:.1%}")
    print(f"CTOR          : {clicked/opened:.1%}")
    print(f"Conversion    : {converted/clicked:.1%}")
    print(f"Unsub Rate    : {cleaned['unsubscribed'].sum()/delivered:.1%}")


if __name__ == "__main__":
    main()
