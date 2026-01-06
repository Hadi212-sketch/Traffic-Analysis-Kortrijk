"""
weather_integration.py
Fetches weather data from Open-Meteo API and merges with Telraam traffic data
"""

import pandas as pd
import requests
from datetime import datetime, timezone
import pytz
import time
from pathlib import Path

# Configuration
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
KORTRIJK_LAT = 50.8279
KORTRIJK_LON = 3.2651
TIMEZONE = "Europe/Brussels"

# Data paths
DATA_DIR = Path("data")
TRAFFIC_FILE = DATA_DIR / "sintmartenslatemlaan_per-hour.csv"
WEATHER_FILE = DATA_DIR / "weather_kortrijk.csv"
MERGED_FILE = DATA_DIR / "traffic_weather_merged.csv"


def fetch_weather_data(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical weather data from Open-Meteo API for Kortrijk.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        DataFrame with hourly weather data
    """
    params = {
        "latitude": KORTRIJK_LAT,
        "longitude": KORTRIJK_LON,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": [
            "temperature_2m",
            "precipitation",
            "rain",
            "snowfall",
            "cloudcover",
            "windspeed_10m",
            "sunshine_duration"
        ],
        "timezone": TIMEZONE
    }
    
    print(f"📡 Fetching weather data from {start_date} to {end_date}...")
    
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Convert to DataFrame
        hourly = data["hourly"]
        df = pd.DataFrame({
            "date": pd.to_datetime(hourly["time"]),
            "temperature_c": hourly["temperature_2m"],
            "precipitation_mm": hourly["precipitation"],
            "rain_mm": hourly["rain"],
            "snowfall_cm": hourly["snowfall"],
            "cloud_cover_pct": hourly["cloudcover"],
            "wind_speed_kmh": hourly["windspeed_10m"],
            "sunshine_duration_s": hourly["sunshine_duration"]
        })
        
        print(f"✅ Fetched {len(df)} weather records")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        raise
    except KeyError as e:
        print(f"❌ Data Error: Missing key {e}")
        raise


def load_traffic_data() -> pd.DataFrame:
    """
    Load Telraam traffic data from CSV.
    
    Returns:
        DataFrame with traffic data
    """
    print(f"📂 Loading traffic data from {TRAFFIC_FILE}...")
    
    if not TRAFFIC_FILE.exists():
        raise FileNotFoundError(f"Traffic file not found: {TRAFFIC_FILE}")
    
    df = pd.read_csv(TRAFFIC_FILE)
    df["date"] = pd.to_datetime(df["date"])
    
    print(f"✅ Loaded {len(df)} traffic records")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    
    return df


def merge_traffic_weather(traffic_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge traffic and weather data by timestamp.
    
    Args:
        traffic_df: Telraam traffic DataFrame
        weather_df: Open-Meteo weather DataFrame
    
    Returns:
        Merged DataFrame
    """
    print("\n🔗 Merging traffic and weather data...")
    
    # Ensure both have timezone-aware datetime
    if traffic_df["date"].dt.tz is None:
        traffic_df["date"] = traffic_df["date"].dt.tz_localize("UTC")
    
    if weather_df["date"].dt.tz is None:
        weather_df["date"] = weather_df["date"].dt.tz_localize(TIMEZONE)
    
    # Convert both to same timezone (Europe/Brussels)
    traffic_df["date"] = traffic_df["date"].dt.tz_convert(TIMEZONE)
    weather_df["date"] = weather_df["date"].dt.tz_convert(TIMEZONE)
    
    # Merge on date (hour-level alignment)
    merged = pd.merge(
        traffic_df,
        weather_df,
        on="date",
        how="left",
        validate="1:1"
    )
    
    # Validation
    missing_weather = merged["temperature_c"].isna().sum()
    if missing_weather > 0:
        print(f"⚠️  Warning: {missing_weather} records without weather data")
    
    print(f"✅ Merged dataset: {len(merged)} records")
    print(f"   Columns: {list(merged.columns)}")
    
    return merged


def validate_merged_data(df: pd.DataFrame) -> dict:
    """
    Validate the merged dataset for quality issues.
    
    Returns:
        Dictionary with validation metrics
    """
    print("\n🔍 Validating merged dataset...")
    
    validation = {
        "total_records": len(df),
        "date_range": (df["date"].min(), df["date"].max()),
        "missing_weather": df["temperature_c"].isna().sum(),
        "missing_traffic": df["car"].isna().sum(),
        "duplicate_dates": df.duplicated(subset=["date"]).sum(),
        "temperature_range": (df["temperature_c"].min(), df["temperature_c"].max()),
        "precipitation_days": (df["precipitation_mm"] > 0).sum(),
    }
    
    print(f"   Total records: {validation['total_records']}")
    print(f"   Date range: {validation['date_range'][0]} to {validation['date_range'][1]}")
    print(f"   Missing weather: {validation['missing_weather']}")
    print(f"   Missing traffic: {validation['missing_traffic']}")
    print(f"   Duplicate dates: {validation['duplicate_dates']}")
    print(f"   Temperature range: {validation['temperature_range'][0]:.1f}°C to {validation['temperature_range'][1]:.1f}°C")
    print(f"   Days with precipitation: {validation['precipitation_days']}")
    
    if validation["duplicate_dates"] > 0:
        print("⚠️  Warning: Duplicate timestamps detected!")
    
    if validation["missing_weather"] > 0:
        print("⚠️  Warning: Some records missing weather data")
    
    return validation


def main():
    """
    Main execution: Fetch weather, load traffic, merge, validate, save.
    """
    print("=" * 80)
    print("🌦️  WEATHER INTEGRATION - W1.3")
    print("=" * 80)
    
    # Step 1: Load traffic data
    traffic_df = load_traffic_data()
    
    # Step 2: Determine date range for weather API
    start_date = traffic_df["date"].min().strftime("%Y-%m-%d")
    end_date = traffic_df["date"].max().strftime("%Y-%m-%d")
    
    # Step 3: Fetch weather data
    weather_df = fetch_weather_data(start_date, end_date)
    
    # Step 4: Save raw weather data
    DATA_DIR.mkdir(exist_ok=True)
    weather_df.to_csv(WEATHER_FILE, index=False)
    print(f"💾 Saved weather data to {WEATHER_FILE}")
    
    # Step 5: Merge datasets
    merged_df = merge_traffic_weather(traffic_df, weather_df)
    
    # Step 6: Validate
    validation = validate_merged_data(merged_df)
    
    # Step 7: Save merged dataset
    merged_df.to_csv(MERGED_FILE, index=False)
    print(f"\n💾 Saved merged dataset to {MERGED_FILE}")
    
    print("\n" + "=" * 80)
    print("✅ W1.3 COMPLETE - Weather integration successful!")
    print("=" * 80)
    
    return merged_df, validation


if __name__ == "__main__":
    merged_df, validation = main()

from calendar_integration import add_calendar_features_to_traffic

def main():
    """
    Main execution: Fetch weather, load traffic, merge, add calendar, validate, save.
    """
    print("=" * 80)
    print("🌦️  COMPLETE DATA INTEGRATION - W1.3")
    print("=" * 80)
    
    # Step 1: Load traffic data
    traffic_df = load_traffic_data()
    
    # Step 2: Determine date range for weather API
    start_date = traffic_df["date"].min().strftime("%Y-%m-%d")
    end_date = traffic_df["date"].max().strftime("%Y-%m-%d")
    
    # Step 3: Fetch weather data
    weather_df = fetch_weather_data(start_date, end_date)
    
    # Step 4: Save raw weather data
    DATA_DIR.mkdir(exist_ok=True)
    weather_df.to_csv(WEATHER_FILE, index=False)
    print(f"💾 Saved weather data to {WEATHER_FILE}")
    
    # Step 5: Merge traffic + weather
    merged_df = merge_traffic_weather(traffic_df, weather_df)
    
    # Step 6: Add calendar features (holidays + school vacations)
    merged_df = add_calendar_features_to_traffic(merged_df)
    
    # Step 7: Validate
    validation = validate_merged_data(merged_df)
    
    # Step 8: Save final integrated dataset
    FINAL_FILE = DATA_DIR / "traffic_weather_calendar_integrated.csv"
    merged_df.to_csv(FINAL_FILE, index=False)
    print(f"\n💾 Saved FINAL integrated dataset to {FINAL_FILE}")
    
    print("\n" + "=" * 80)
    print("✅ W1.3 COMPLETE - Full integration successful!")
    print(f"   Dataset includes: Traffic + Weather + Holidays + School Vacations")
    print("=" * 80)
    
    return merged_df, validation
