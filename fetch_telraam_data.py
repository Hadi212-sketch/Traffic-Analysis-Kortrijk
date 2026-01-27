import os
import time
from datetime import datetime, timedelta, timezone

import requests
import pandas as pd

API_KEY = "whtPSh8eE81VkAOCeVo1e6qitCNy33ev9hEQRMoC"
URL = "https://telraam-api.net/v1/reports/traffic"

SEGMENTS = {
    "9000008372": "sintmartenslatemlaan",
    "9000009940": "graaf_karel_de_goedelaan",
}

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

PROJECT_START = datetime(2025, 11,1 , 0, 0, tzinfo=timezone.utc)
TS_COL = "date"  # time column in your CSVs

def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%SZ")

def get_existing_df(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def get_time_window(existing_df: pd.DataFrame):
    if existing_df.empty or TS_COL not in existing_df.columns:
        start = PROJECT_START
    else:
        last_ts = pd.to_datetime(existing_df[TS_COL]).max()
        start = last_ts.to_pydatetime() + timedelta(hours=1)

    now_utc = datetime.now(timezone.utc)
    end = now_utc.replace(minute=0, second=0, microsecond=0)
    if end <= start:
        return None, None
    return start, end

def fetch_segment(segment_id: str, start_dt: datetime, end_dt: datetime, max_retries: int = 3) -> pd.DataFrame:
    body = {
        "id": segment_id,
        "time_start": iso(start_dt),
        "time_end": iso(end_dt),
        "level": "segments",
        "format": "per-hour",
    }
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json",
    }

    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(URL, headers=headers, json=body)
            if r.status_code == 429:
                wait = 5 * attempt
                print(f"429 rate limit, wait {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json().get("report", [])
            if not data:
                return pd.DataFrame()
            return pd.DataFrame(data)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def update_segment(segment_id: str, name: str):
    path = os.path.join(DATA_DIR, f"{name}_per-hour.csv")
    existing = get_existing_df(path)

    start, end = get_time_window(existing)
    if start is None:
        print(f"[{name}] no new hours to fetch.")
        return

    print(f"[{name}] fetching from {iso(start)} to {iso(end)}")
    new_df = fetch_segment(segment_id, start, end)
    if new_df.empty:
        print(f"[{name}] no new data returned.")
        return

    combined = pd.concat([existing, new_df], ignore_index=True)
    if TS_COL in combined.columns:
        combined.drop_duplicates(subset=[TS_COL], inplace=True)
        combined.sort_values(TS_COL, inplace=True)

    combined.to_csv(path, index=False)
    print(f"[{name}] updated: {len(new_df)} new rows, total {len(combined)} rows")

def combine_raw_data():
    """Combine both street CSV files into traffic_two_streets_raw.csv"""
    print("\n[Combining] Creating traffic_two_streets_raw.csv...")
    
    dfs = []
    for seg_name in SEGMENTS.values():
        path = os.path.join(DATA_DIR, f"{seg_name}_per-hour.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['street_name'] = seg_name.replace('_', ' ').title()
            dfs.append(df)
            print(f"  ✓ Loaded {len(df)} rows from {seg_name}")
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        combined.sort_values('date', inplace=True)
        
        output_path = os.path.join(DATA_DIR, "traffic_two_streets_raw.csv")
        combined.to_csv(output_path, index=False)
        print(f"  ✓ Combined file saved: {len(combined)} total rows")
        print(f"  ✓ Output: {output_path}")
    else:
        print("  ⚠ No street data files found to combine")

def main():
    for seg_id, seg_name in SEGMENTS.items():
        update_segment(seg_id, seg_name)
        time.sleep(2)
    
    # Combine both streets into raw CSV
    combine_raw_data()

if __name__ == "__main__":
    main()
