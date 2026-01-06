"""
calendar_integration.py
Fetch Belgian holidays and school vacation periods using Google Calendar API
"""

import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

# For simplicity, we'll use a hardcoded list of Belgian holidays for 2025-2026
# In production, you could use Google Calendar API or a holiday library

BELGIAN_HOLIDAYS_2025_2026 = [
    # 2025
    ("2025-01-01", "New Year's Day"),
    ("2025-04-21", "Easter Monday"),
    ("2025-05-01", "Labour Day"),
    ("2025-05-29", "Ascension Day"),
    ("2025-06-09", "Whit Monday"),
    ("2025-07-21", "Belgian National Day"),
    ("2025-08-15", "Assumption of Mary"),
    ("2025-11-01", "All Saints' Day"),
    ("2025-11-11", "Armistice Day"),
    ("2025-12-25", "Christmas Day"),
    
    # 2026
    ("2026-01-01", "New Year's Day"),
    ("2026-04-06", "Easter Monday"),
    ("2026-05-01", "Labour Day"),
    ("2026-05-14", "Ascension Day"),
    ("2026-05-25", "Whit Monday"),
    ("2026-07-21", "Belgian National Day"),
    ("2026-08-15", "Assumption of Mary"),
    ("2026-11-01", "All Saints' Day"),
    ("2026-11-11", "Armistice Day"),
    ("2026-12-25", "Christmas Day"),
]

# Belgian school vacation periods (Flanders region)
SCHOOL_VACATIONS_2025_2026 = [
    # 2025
    ("2025-02-24", "2025-03-02", "Carnival Break"),
    ("2025-04-14", "2025-04-27", "Easter Break"),
    ("2025-07-01", "2025-08-31", "Summer Break"),
    ("2025-11-03", "2025-11-09", "Autumn Break"),
    ("2025-12-22", "2026-01-05", "Christmas Break"),
    
    # 2026
    ("2026-02-16", "2026-02-22", "Carnival Break"),
    ("2026-04-06", "2026-04-19", "Easter Break"),
    ("2026-07-01", "2026-08-31", "Summer Break"),
]

DATA_DIR = Path("data")
HOLIDAYS_FILE = DATA_DIR / "belgian_holidays.csv"
VACATIONS_FILE = DATA_DIR / "school_vacations.csv"


def create_holidays_dataframe() -> pd.DataFrame:
    """
    Create DataFrame of Belgian public holidays.
    
    Returns:
        DataFrame with date and holiday name
    """
    print("📅 Creating Belgian holidays dataset...")
    
    holidays_data = []
    for date_str, name in BELGIAN_HOLIDAYS_2025_2026:
        holidays_data.append({
            "date": pd.to_datetime(date_str),
            "holiday_name": name,
            "is_holiday": True
        })
    
    df = pd.DataFrame(holidays_data)
    print(f"✅ Created {len(df)} holiday records")
    
    return df


def create_school_vacations_dataframe() -> pd.DataFrame:
    """
    Create DataFrame of Belgian school vacation periods.
    
    Returns:
        DataFrame with vacation periods
    """
    print("🏫 Creating school vacation dataset...")
    
    vacation_data = []
    for start_str, end_str, name in SCHOOL_VACATIONS_2025_2026:
        start = pd.to_datetime(start_str)
        end = pd.to_datetime(end_str)
        
        # Create a row for each day in the vacation period
        current = start
        while current <= end:
            vacation_data.append({
                "date": current,
                "vacation_name": name,
                "is_school_vacation": True
            })
            current += timedelta(days=1)
    
    df = pd.DataFrame(vacation_data)
    print(f"✅ Created {len(df)} vacation day records")
    
    return df


def add_calendar_features_to_traffic(traffic_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add holiday and school vacation flags to traffic data.
    
    Args:
        traffic_df: Traffic data with 'date' column
    
    Returns:
        Traffic data enriched with calendar features
    """
    print("\n📆 Adding calendar features to traffic data...")
    
    # Load or create holiday data
    holidays_df = create_holidays_dataframe()
    vacations_df = create_school_vacations_dataframe()
    
    # Ensure date columns are datetime
    traffic_df["date_only"] = traffic_df["date"].dt.date
    holidays_df["date_only"] = holidays_df["date"].dt.date
    vacations_df["date_only"] = vacations_df["date"].dt.date
    
    # Merge holidays
    traffic_df = traffic_df.merge(
        holidays_df[["date_only", "holiday_name", "is_holiday"]],
        on="date_only",
        how="left"
    )
    
    # Merge vacations
    traffic_df = traffic_df.merge(
        vacations_df[["date_only", "vacation_name", "is_school_vacation"]],
        on="date_only",
        how="left"
    )
    
    # Fill NaN with False/empty
    traffic_df["is_holiday"] = traffic_df["is_holiday"].fillna(False)
    traffic_df["is_school_vacation"] = traffic_df["is_school_vacation"].fillna(False)
    traffic_df["holiday_name"] = traffic_df["holiday_name"].fillna("")
    traffic_df["vacation_name"] = traffic_df["vacation_name"].fillna("")
    
    # Drop temporary column
    traffic_df = traffic_df.drop("date_only", axis=1)
    
    # Summary
    num_holidays = traffic_df["is_holiday"].sum()
    num_vacation_days = traffic_df["is_school_vacation"].sum()
    
    print(f"✅ Added calendar features:")
    print(f"   Holiday records: {num_holidays}")
    print(f"   School vacation records: {num_vacation_days}")
    
    return traffic_df


def main():
    """
    Main execution: Create calendar data and save.
    """
    print("=" * 80)
    print("📅 CALENDAR INTEGRATION")
    print("=" * 80)
    
    # Create datasets
    holidays_df = create_holidays_dataframe()
    vacations_df = create_school_vacations_dataframe()
    
    # Save to CSV
    DATA_DIR.mkdir(exist_ok=True)
    holidays_df.to_csv(HOLIDAYS_FILE, index=False)
    vacations_df.to_csv(VACATIONS_FILE, index=False)
    
    print(f"\n💾 Saved holidays to {HOLIDAYS_FILE}")
    print(f"💾 Saved school vacations to {VACATIONS_FILE}")
    
    print("\n" + "=" * 80)
    print("✅ CALENDAR INTEGRATION COMPLETE")
    print("=" * 80)
    
    return holidays_df, vacations_df


if __name__ == "__main__":
    holidays_df, vacations_df = main()
