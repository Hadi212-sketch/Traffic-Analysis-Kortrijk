import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML imports for clustering
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest
    sklearn_available = True
except ImportError:
    sklearn_available = False

# Configure Streamlit
st.set_page_config(
    page_title="Sint-Martens-Latemlaan Traffic Analysis",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stSelectbox label, .stSlider label, .stDateInput label {
        font-weight: bold;
        color: #2E86AB;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
    }
    .sidebar .sidebar-content {
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# Cache functions for loading data and models
@st.cache_data
def load_data():
    """Load the preprocessed dataframe"""
    # Try parquet first, then CSV as fallback
    try:
        df = pd.read_parquet("../models/df_model.parquet")
        df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
        return df
    except (FileNotFoundError, OSError) as e:
        # If parquet fails, try CSV
        try:
            df = pd.read_csv("../models/df_model.csv", parse_dates=['datetime'])
            df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
            return df
        except FileNotFoundError:
            st.error("❌ Data file not found. Please run the export code in the notebook first.")
            st.error("The notebook should export df_model to ../models/df_model.parquet or df_model.csv")
            st.stop()

@st.cache_data
def load_holidays():
    """Load holiday data"""
    try:
        holidays = pd.read_csv("../data/belgian_holidays.csv")
        holidays['date'] = pd.to_datetime(holidays['date']).dt.date
        holidays['is_holiday'] = 1
        return holidays
    except FileNotFoundError:
        st.warning("⚠️ Holiday data not found. Using default holiday logic.")
        return pd.DataFrame(columns=['date', 'is_holiday'])

@st.cache_data
def load_vacations():
    """Load school vacation data"""
    try:
        vac = pd.read_csv("../data/school_vacations.csv")
        vac['date'] = pd.to_datetime(vac['date']).dt.date
        vac['is_school_vacation'] = 1
        return vac
    except FileNotFoundError:
        st.warning("⚠️ School vacation data not found. Using default vacation logic.")
        return pd.DataFrame(columns=['date', 'is_school_vacation'])

@st.cache_resource
def load_models():
    """Load trained models and metadata"""
    try:
        models = joblib.load("../models/models.pkl")
        targets = joblib.load("../models/targets.pkl")
        feature_cols = joblib.load("../models/feature_cols.pkl")
        return models, targets, feature_cols
    except FileNotFoundError:
        st.error("❌ Model files not found. Please run the export code in the notebook first.")
        st.stop()

# Holiday and vacation logic functions
def add_calendar_features(df, holidays, vacations):
    """Add holiday and school vacation flags to dataframe"""
    df = df.copy()
    df['date_only'] = pd.to_datetime(df['datetime']).dt.date
    
    # Merge holidays
    df = df.merge(holidays[['date', 'is_holiday']], 
                  left_on='date_only', right_on='date', how='left')
    df['is_holiday'] = df['is_holiday'].fillna(0).astype(int)
    
    # Merge vacations
    df = df.merge(vacations[['date', 'is_school_vacation']], 
                  left_on='date_only', right_on='date', how='left')
    df['is_school_vacation'] = df['is_school_vacation'].fillna(0).astype(int)
    
    return df.drop(columns=['date'], errors='ignore')

def apply_weather_scenario(future_df, scenario, historical_data):
    """Apply weather conditions based on scenario"""
    future_df = future_df.copy()
    
    if scenario == "normal":
        # Use median values from historical data
        weather_cols = ["temperature_c", "precipitation_mm", "cloud_cover_pct", "wind_speed_kmh"]
        for col in weather_cols:
            future_df[col] = historical_data[col].median()
    
    elif scenario == "rainy_morning_rush":
        # High precipitation and clouds during 7-9 AM, normal otherwise
        future_df["temperature_c"] = historical_data["temperature_c"].quantile(0.25)
        future_df["wind_speed_kmh"] = historical_data["wind_speed_kmh"].median()
        
        # Apply rain conditions during rush hours (7-9 AM)
        rush_hours = future_df['hour'].isin([7, 8, 9])
        future_df.loc[rush_hours, "precipitation_mm"] = historical_data["precipitation_mm"].quantile(0.9)
        future_df.loc[rush_hours, "cloud_cover_pct"] = 95
        future_df.loc[~rush_hours, "precipitation_mm"] = historical_data["precipitation_mm"].median()
        future_df.loc[~rush_hours, "cloud_cover_pct"] = historical_data["cloud_cover_pct"].median()
    
    elif scenario == "cloudy_windy":
        # High clouds and wind, low precipitation
        future_df["temperature_c"] = historical_data["temperature_c"].median()
        future_df["precipitation_mm"] = 0
        future_df["cloud_cover_pct"] = 95
        future_df["wind_speed_kmh"] = historical_data["wind_speed_kmh"].quantile(0.9)
    
    return future_df

def adjust_for_parking_scenario(predictions_df, scenario):
    """Adjust predictions based on parking scenario"""
    adjusted = predictions_df.copy()
    
    if scenario == "closed":
        # Parking closed: reduce cars, increase bikes and pedestrians
        adjusted["car"] *= 0.5
        adjusted["bike"] *= 1.2
        adjusted["pedestrian"] *= 1.2
        # Heavy vehicles unchanged
    elif scenario == "paid":
        # Paid parking: moderate reduction in cars
        adjusted["car"] *= 0.75
        adjusted["bike"] *= 1.1
        adjusted["pedestrian"] *= 1.1
        # Heavy vehicles unchanged
    # "open" scenario: no changes
    
    # Recalculate total people
    adjusted["total_people"] = (
        adjusted["car"] + adjusted["bike"] + 
        adjusted["pedestrian"] + adjusted["heavy"]
    )
    
    return adjusted

def create_future_dataframe(last_datetime, weeks_ahead, street_code, holidays, vacations, vacation_scenario):
    """Create future dataframe with proper features"""
    
    # Generate future time index
    future_hours = 24 * 7 * weeks_ahead
    future_index = pd.date_range(
        start=last_datetime + pd.Timedelta(hours=1),
        periods=future_hours,
        freq="H"
    )
    
    # Create base dataframe
    future = pd.DataFrame({"datetime": future_index})
    future["hour"] = future["datetime"].dt.hour
    future["dayofweek"] = future["datetime"].dt.dayofweek
    future["is_weekend"] = future["dayofweek"].isin([5, 6]).astype(int)
    
    # Add calendar features based on scenario
    if vacation_scenario == "calendar":
        future = add_calendar_features(future, holidays, vacations)
    elif vacation_scenario == "force_vacation":
        future["is_holiday"] = 0
        future["is_school_vacation"] = 1
    elif vacation_scenario == "force_no_vacation":
        future["is_holiday"] = 0
        future["is_school_vacation"] = 0
    
    # Add street code for Sint-Martens-Latemlaan
    future["street_code"] = street_code
    
    return future

# Load data and models
df_model = load_data()
holidays = load_holidays()
vacations = load_vacations()
models, targets, feature_cols = load_models()

# Get street code for Sint-Martens-Latemlaan
sint_martens_code = df_model[df_model["street_name"] == "Sintmartenslatemlaan"]["street_code"].iloc[0]

# Main app
st.markdown("<h1 style='text-align: center; font-size: 3.5rem; margin-bottom: 0.5rem;'>🚗 Traffic Analysis & Prediction</h1>", unsafe_allow_html=True)
st.markdown("Interactive analysis and forecasting of traffic patterns around Howest Campus")

# Sidebar controls
st.sidebar.header("📊 Analysis Parameters")

# Historical analysis date range
st.sidebar.subheader("Historical Period")
date_min = df_model['datetime'].min().date()
date_max = df_model['datetime'].max().date()

start_date = st.sidebar.date_input(
    "Start Date",
    value=date_min,
    min_value=date_min,
    max_value=date_max
)

end_date = st.sidebar.date_input(
    "End Date", 
    value=date_max,
    min_value=date_min,
    max_value=date_max
)

# Forecast parameters
st.sidebar.subheader("Forecast Parameters")
weeks_ahead = st.sidebar.slider("Weeks ahead to forecast", 1, 13, 4)

parking_scenario = st.sidebar.selectbox(
    "Parking Scenario",
    ["open", "closed", "paid"],
    help="Open: current situation, Closed: no parking allowed, Paid: parking fees applied"
)

weather_scenario = st.sidebar.selectbox(
    "Weather Scenario",
    ["normal", "rainy_morning_rush", "cloudy_windy"],
    help="Normal: typical weather, Rainy rush: rain during 7-9 AM, Cloudy windy: high clouds and wind"
)

vacation_scenario = st.sidebar.selectbox(
    "School Vacation Scenario",
    ["calendar", "force_vacation", "force_no_vacation"],
    help="Calendar: use real calendar, Force vacation: all days as vacation, Force no vacation: no vacation days"
)

run_forecast = st.sidebar.button("🔮 Run Forecast", type="primary", use_container_width=True)

# Main content with custom CSS for larger tabs
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.4rem;
        font-weight: 600;
        padding: 14px 28px;
    }
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Historical Analysis", "🔮 Future Forecast", "📊 Scenario Comparison", "📋 Raw Data", "🎯 Clustering & Anomalies"])

with tab1:
    st.header("Historical Traffic Analysis")
    
    # Filter historical data  
    start_dt = pd.to_datetime(start_date).tz_localize(None)
    end_dt = pd.to_datetime(end_date).tz_localize(None) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    mask = (df_model['datetime'] >= start_dt) & (df_model['datetime'] <= end_dt)
    filtered_data = df_model[mask]
    
    if len(filtered_data) == 0:
        st.warning("No data available for selected date range")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Records", 
                f"{len(filtered_data):,}",
                help="Number of hourly observations"
            )
        with col2:
            st.metric(
                "Avg Daily Traffic", 
                f"{filtered_data['total_people'].mean():.1f}",
                help="Average people per hour"
            )
        with col3:
            st.metric(
                "Peak Hour Traffic", 
                f"{filtered_data['total_people'].max():.0f}",
                help="Maximum people in any hour"
            )
        with col4:
            st.metric(
                "Days Analyzed", 
                f"{filtered_data['datetime'].dt.date.nunique()}",
                help="Number of unique days"
            )
        
        # Hourly traffic pattern
        st.subheader("Average Hourly Traffic Pattern")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # By transportation mode
        modes = ["car", "bike", "pedestrian", "heavy"]
        mode_colors = {'car': '#E63946', 'bike': '#06A77D', 'pedestrian': '#F18F01', 'heavy': '#6A4C93'}
        
        hourly_by_mode = filtered_data.groupby('hour')[modes].mean()
        
        for mode in modes:
            ax1.plot(hourly_by_mode.index, hourly_by_mode[mode], 
                    marker='o', linewidth=2.5, label=mode.capitalize(), 
                    color=mode_colors[mode], markersize=6)
        
        ax1.set_xlabel('Hour of Day', fontweight='bold')
        ax1.set_ylabel('Average Count per Hour', fontweight='bold')
        ax1.set_title('Hourly Pattern by Transportation Mode', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(range(0, 24, 2))
        
        # Total people by hour
        hourly_total = filtered_data.groupby('hour')['total_people'].mean()
        ax2.plot(hourly_total.index, hourly_total.values, 
                marker='o', linewidth=3, color='#2E86AB', markersize=8)
        ax2.set_xlabel('Hour of Day', fontweight='bold')
        ax2.set_ylabel('Average Total People per Hour', fontweight='bold')
        ax2.set_title('Total Hourly Traffic Pattern', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(range(0, 24, 2))
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Weekly pattern
        st.subheader("Weekly Traffic Pattern")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        weekly_avg = filtered_data.groupby('dayofweek')['total_people'].mean()
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Create full week data with zeros for missing days
        full_week = pd.Series(0, index=range(7))
        full_week[weekly_avg.index] = weekly_avg.values
        
        bars = ax.bar(range(7), full_week.values, 
                     color=['#2E86AB' if i < 5 else '#F18F01' for i in range(7)],
                     edgecolor='white', linewidth=2)
        
        ax.set_xticks(range(7))
        ax.set_xticklabels(day_names, rotation=45)
        ax.set_ylabel('Average People per Hour', fontweight='bold')
        ax.set_title('Weekly Traffic Pattern', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, full_week.values):
            height = bar.get_height()
            if value > 0:  # Only show label if there's data
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)

with tab2:
    st.header("Future Traffic Forecast")
    
    if run_forecast:
        with st.spinner("🔄 Generating forecast..."):
            # Use the selected end date as the starting point for forecast
            last_dt = pd.to_datetime(end_date).tz_localize(None)
            
            # Create future dataframe
            future = create_future_dataframe(
                last_dt, weeks_ahead, sint_martens_code, 
                holidays, vacations, vacation_scenario
            )
            
            # Apply weather scenario
            future = apply_weather_scenario(future, weather_scenario, df_model)
            
            # Generate predictions for all targets
            predictions = {}
            for target in targets:
                model = models[target]
                predictions[f"pred_{target}"] = model.predict(future[feature_cols])
            
            # Create predictions dataframe
            future_preds = pd.DataFrame(predictions)
            future_preds['datetime'] = future['datetime']
            
            # Rename columns for consistency
            pred_cols = {}
            for target in targets:
                pred_cols[f"pred_{target}"] = target
            future_preds = future_preds.rename(columns=pred_cols)
            
            # Apply parking scenario adjustments
            future_adj = adjust_for_parking_scenario(future_preds, parking_scenario)
            future_open = adjust_for_parking_scenario(future_preds, "open")  # baseline
            
            # Display forecast summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Forecast Period",
                    f"{weeks_ahead} weeks",
                    help="Number of weeks forecasted"
                )
            with col2:
                avg_total = future_adj['total_people'].mean()
                baseline_avg = future_open['total_people'].mean()
                delta = avg_total - baseline_avg
                st.metric(
                    "Avg Hourly Traffic",
                    f"{avg_total:.1f}",
                    delta=f"{delta:+.1f} vs open",
                    help="Average people per hour under selected scenario"
                )
            with col3:
                total_week = future_adj['total_people'].sum()
                st.metric(
                    f"Total {weeks_ahead}-Week Traffic",
                    f"{total_week:,.0f}",
                    help="Total predicted people over forecast period"
                )
            
            # Enhanced visualization section
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h2 style='font-size: 2.2rem;'>📈 Traffic Forecast Overview</h2>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Daily Average Comparison (Bar Chart) - Full Width
            st.markdown("### 📊 Daily Average Comparison by Day")
            daily_open = future_open.groupby(future_open['datetime'].dt.date)['total_people'].mean()
            daily_adj = future_adj.groupby(future_adj['datetime'].dt.date)['total_people'].mean()
            
            fig, ax = plt.subplots(figsize=(16, 6))
            x = np.arange(len(daily_open))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, daily_open.values, width, 
                          label='Open Parking', color='#4CAF50', alpha=0.8)
            bars2 = ax.bar(x + width/2, daily_adj.values, width,
                          label=f'{parking_scenario.capitalize()} Parking',
                          color='#F44336' if parking_scenario == "closed" else '#FF9800',
                          alpha=0.8)
            
            # Add value labels on bars - only if not too many days to avoid overlap
            if len(daily_open) <= 21:  # Only show labels for 3 weeks or less
                label_fontsize = 10 if len(daily_open) <= 14 else 8
                for bars in [bars1, bars2]:
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{height:.0f}', ha='center', va='bottom', 
                               fontweight='bold', fontsize=label_fontsize)
            
            ax.set_xlabel('Date', fontweight='bold', fontsize=13)
            ax.set_ylabel('Average People per Hour', fontweight='bold', fontsize=13)
            ax.set_title('Daily Traffic Averages', fontweight='bold', fontsize=15)
            ax.set_xticks(x)
            # Format dates as MM/DD
            date_labels = [date.strftime('%m/%d') for date in daily_open.index]
            ax.set_xticklabels(date_labels, fontsize=10, rotation=45, ha='right')
            ax.legend(fontsize=12, loc='upper right')
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            
            # Add some spacing
            st.markdown("---")
            
            # Mode Distribution Pie Chart - Centered
            st.markdown("### 🚗 Traffic Mode Distribution")
            mode_totals = {
                'Car': future_adj['car'].sum(),
                'Bike': future_adj['bike'].sum(), 
                'Pedestrian': future_adj['pedestrian'].sum(),
                'Heavy': future_adj['heavy'].sum()
            }
            
            # Center the pie chart
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                fig, ax = plt.subplots(figsize=(10, 10))
                colors = ['#E63946', '#06A77D', '#F18F01', '#6A4C93']
                wedges, texts, autotexts = ax.pie(mode_totals.values(), 
                                                 labels=mode_totals.keys(),
                                                 colors=colors,
                                                 autopct='%1.1f%%',
                                                 startangle=90,
                                                 explode=(0.05, 0.05, 0.05, 0.05))
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(13)
                
                for text in texts:
                    text.set_fontsize(13)
                    text.set_fontweight('bold')
                
                ax.set_title(f'Mode Share - {parking_scenario.capitalize()} Scenario', 
                           fontweight='bold', fontsize=16, pad=20)
                plt.tight_layout()
                st.pyplot(fig)
            
            # Hourly Pattern Heatmap
            st.markdown("**📅 Hourly Traffic Patterns**")
            future_adj['hour'] = future_adj['datetime'].dt.hour
            future_adj['day'] = future_adj['datetime'].dt.day_name()
            
            heatmap_data = future_adj.pivot_table(
                values='total_people',
                index='hour',
                columns='day',
                aggfunc='mean'
            )
            
            # Reorder columns to show proper weekday order
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex(columns=[d for d in day_order if d in heatmap_data.columns])
            
            fig, ax = plt.subplots(figsize=(12, 8))
            im = ax.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
            
            # Set ticks and labels
            ax.set_xticks(range(len(heatmap_data.columns)))
            ax.set_xticklabels(heatmap_data.columns)
            ax.set_yticks(range(len(heatmap_data.index)))
            ax.set_yticklabels(heatmap_data.index)
            
            # Add text annotations
            for i in range(len(heatmap_data.index)):
                for j in range(len(heatmap_data.columns)):
                    value = heatmap_data.iloc[i, j]
                    if not pd.isna(value):
                        ax.text(j, i, f'{value:.0f}', ha='center', va='center',
                               color='white' if value > heatmap_data.values.max()*0.6 else 'black',
                               fontweight='bold')
            
            ax.set_xlabel('Day of Week', fontweight='bold')
            ax.set_ylabel('Hour of Day', fontweight='bold')
            ax.set_title(f'Traffic Intensity Heatmap - {parking_scenario.capitalize()} Scenario',
                        fontweight='bold', fontsize=14, pad=20)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('People per Hour', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Time Series with Trend
            st.markdown("**📈 Detailed Time Series Forecast**")
            fig, ax = plt.subplots(figsize=(16, 8))
            
            # Plot with filled areas
            ax.fill_between(future_open['datetime'], future_open['total_people'],
                           alpha=0.3, color='#4CAF50', label='Open Parking (Range)')
            ax.plot(future_open['datetime'], future_open['total_people'],
                   color='#4CAF50', linewidth=3, label='Open Parking', marker='o', markersize=4)
            
            ax.fill_between(future_adj['datetime'], future_adj['total_people'],
                           alpha=0.3, color='#F44336' if parking_scenario == "closed" else '#FF9800',
                           label=f'{parking_scenario.capitalize()} Parking (Range)')
            ax.plot(future_adj['datetime'], future_adj['total_people'],
                   color='#F44336' if parking_scenario == "closed" else '#FF9800',
                   linewidth=3, linestyle='--', 
                   label=f'{parking_scenario.capitalize()} Parking', marker='s', markersize=4)
            
            # Highlight rush hours
            if weather_scenario == "rainy_morning_rush":
                rush_mask = future['hour'].isin([7, 8, 9])
                rush_times = future[rush_mask]['datetime']
                for rush_time in rush_times:
                    ax.axvspan(rush_time - pd.Timedelta(minutes=30), 
                             rush_time + pd.Timedelta(minutes=30),
                             alpha=0.2, color='lightblue', zorder=0)
                ax.text(0.02, 0.98, '🌧️ Rainy Rush Hours Highlighted', 
                       transform=ax.transAxes, fontsize=10, 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7),
                       verticalalignment='top')
            
            # Add weekend shading
            for dt in pd.date_range(future_adj['datetime'].min(), future_adj['datetime'].max(), freq='D'):
                if dt.dayofweek >= 5:  # Saturday and Sunday
                    ax.axvspan(dt, dt + pd.Timedelta(days=1), alpha=0.1, color='gray', zorder=0)
            
            ax.set_xlabel('Date & Time', fontweight='bold', fontsize=12)
            ax.set_ylabel('People per Hour', fontweight='bold', fontsize=12)
            ax.set_title(f'Comprehensive Traffic Forecast\n{weather_scenario.replace("_", " ").title()} Weather | {vacation_scenario.replace("_", " ").title()} Vacation', 
                        fontweight='bold', fontsize=14, pad=20)
            ax.legend(fontsize=11, loc='upper right')
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Better date formatting - adjust based on forecast period length
            import matplotlib.dates as mdates
            forecast_days = (future_adj['datetime'].max() - future_adj['datetime'].min()).days
            
            if forecast_days <= 7:
                # Short period: show daily with hours
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            elif forecast_days <= 28:
                # Medium period: show every few days
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, forecast_days//7)))
            else:
                # Long period: show weekly
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=max(1, forecast_days//30)))
                
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Mode-specific forecasts
            st.subheader("🚗 Forecast by Transportation Mode")
            
            modes = ["car", "bike", "pedestrian", "heavy"]
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            axes = axes.ravel()
            
            for ax, mode in zip(axes, modes):
                ax.plot(future_open['datetime'], future_open[mode],
                       label='Open Parking', color='#4CAF50', linewidth=2.5, alpha=0.9)
                ax.plot(future_adj['datetime'], future_adj[mode],
                       label=f'{parking_scenario.capitalize()} Parking',
                       color='#F44336' if parking_scenario == "closed" else '#FF9800',
                       linewidth=2.5, linestyle='--', alpha=0.9)
                
                ax.set_title(f'{mode.capitalize()} Traffic', fontweight='bold')
                ax.set_ylabel('Count per Hour', fontweight='bold')
                ax.legend(fontsize=9)
                ax.grid(True, alpha=0.3)
                ax.tick_params(axis='x', rotation=45)
            
            axes[2].set_xlabel('Date/Time', fontweight='bold')
            axes[3].set_xlabel('Date/Time', fontweight='bold')
            
            plt.suptitle(f'Mode-Specific Forecasts ({parking_scenario.capitalize()} vs Open Parking)',
                        fontsize=14, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
            
            # Key Insights Summary
            st.subheader("🎯 Key Forecast Insights")
            
            # Calculate impact metrics
            total_change = ((future_adj['total_people'].sum() - future_open['total_people'].sum()) / future_open['total_people'].sum()) * 100
            car_change = ((future_adj['car'].sum() - future_open['car'].sum()) / future_open['car'].sum()) * 100
            bike_change = ((future_adj['bike'].sum() - future_open['bike'].sum()) / future_open['bike'].sum()) * 100
            ped_change = ((future_adj['pedestrian'].sum() - future_open['pedestrian'].sum()) / future_open['pedestrian'].sum()) * 100
            
            # Display metrics in columns
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                st.metric(
                    label="🚗 Car Traffic",
                    value=f"{future_adj['car'].mean():.1f}/hr",
                    delta=f"{car_change:+.1f}%"
                )
                
            with metric_cols[1]:
                st.metric(
                    label="🚲 Bike Traffic", 
                    value=f"{future_adj['bike'].mean():.1f}/hr",
                    delta=f"{bike_change:+.1f}%"
                )
                
            with metric_cols[2]:
                st.metric(
                    label="🚶‍♂️ Pedestrians",
                    value=f"{future_adj['pedestrian'].mean():.1f}/hr", 
                    delta=f"{ped_change:+.1f}%"
                )
                
            with metric_cols[3]:
                st.metric(
                    label="👥 Total Traffic",
                    value=f"{future_adj['total_people'].mean():.1f}/hr",
                    delta=f"{total_change:+.1f}%"
                )
            
            # Mode Comparison Chart (Enhanced Bar Chart)
            st.markdown("**📊 Transportation Mode Impact Analysis**")
            
            # Prepare data for comparison
            modes = ["car", "bike", "pedestrian", "heavy"]
            open_totals = [future_open[m].sum() for m in modes]
            adj_totals = [future_adj[m].sum() for m in modes]
            mode_names = ['Car', 'Bike', 'Pedestrian', 'Heavy']
            
            x = np.arange(len(modes))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            bars1 = ax.bar(x - width/2, open_totals, width, 
                          label='Open Parking', color='#4CAF50', alpha=0.8,
                          edgecolor='white', linewidth=2)
            bars2 = ax.bar(x + width/2, adj_totals, width,
                          label=f'{parking_scenario.capitalize()} Parking',
                          color='#F44336' if parking_scenario == "closed" else '#FF9800',
                          alpha=0.8, edgecolor='white', linewidth=2)
            
            # Add value labels and percentage change
            for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
                h1, h2 = bar1.get_height(), bar2.get_height()
                
                # Value labels
                ax.text(bar1.get_x() + bar1.get_width()/2., h1,
                       f'{h1:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
                ax.text(bar2.get_x() + bar2.get_width()/2., h2,
                       f'{h2:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
                
                # Percentage change arrow
                change_pct = ((h2 - h1) / h1) * 100
                arrow_color = 'green' if change_pct > 0 else 'red'
                arrow = '↗️' if change_pct > 0 else '↘️'
                ax.text(i, max(h1, h2) * 1.15, f'{arrow} {abs(change_pct):.1f}%',
                       ha='center', va='center', fontweight='bold', 
                       color=arrow_color, fontsize=12,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            
            ax.set_xlabel('Transportation Mode', fontweight='bold', fontsize=12)
            ax.set_ylabel('Total Count (Forecast Period)', fontweight='bold', fontsize=12)
            ax.set_title(f'Traffic Volume Impact by Mode\n{parking_scenario.capitalize()} vs Open Parking', 
                        fontweight='bold', fontsize=14, pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(mode_names, fontsize=11)
            ax.legend(fontsize=11, framealpha=0.95)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Summary insights text
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<h2 style='font-size: 2.2rem;'>📋 Forecast Summary</h2>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            impact_level = "High" if abs(total_change) > 15 else "Medium" if abs(total_change) > 5 else "Low"
            impact_color = "🔴" if abs(total_change) > 15 else "🟡" if abs(total_change) > 5 else "🟢"
            
            # Create interactive metric cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🚗 Cars Impact",
                    value=f"{future_adj['car'].sum():.0f}",
                    delta=f"{car_change:+.1f}%"
                )
            
            with col2:
                st.metric(
                    label="🚴 Bikes Impact",
                    value=f"{future_adj['bike'].sum():.0f}",
                    delta=f"{bike_change:+.1f}%"
                )
            
            with col3:
                st.metric(
                    label="🚶 Pedestrians Impact",
                    value=f"{future_adj['pedestrian'].sum():.0f}",
                    delta=f"{ped_change:+.1f}%"
                )
            
            with col4:
                st.metric(
                    label="📏 Total Impact",
                    value=f"{future_adj['total_people'].sum():.0f}",
                    delta=f"{total_change:+.1f}%"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Summary box with better contrast
            st.markdown(f"""
            <div style='background-color: #e8f4f8; padding: 2rem; border-radius: 10px; border-left: 5px solid #2E86AB;'>
                <h3 style='margin-top: 0; font-size: 1.5rem; color: #1a1a1a;'>{impact_color} Parking Policy Impact: <strong>{impact_level}</strong> ({total_change:+.1f}% total change)</h3>
                <h4 style='font-size: 1.3rem; margin-top: 1.5rem; color: #2a2a2a;'>🔑 Key Insights:</h4>
                <ul style='font-size: 1.1rem; line-height: 2; color: #2a2a2a;'>
                    <li><strong>Baseline vs Scenario:</strong> {future_open['total_people'].sum():.0f} → {future_adj['total_people'].sum():.0f} total people</li>
                    <li><strong>Peak Traffic Hours:</strong> {future_adj.groupby(future_adj['datetime'].dt.hour)['total_people'].mean().idxmax()}:00 - {future_adj.groupby(future_adj['datetime'].dt.hour)['total_people'].mean().idxmax()+2}:00</li>
                    <li><strong>Daily Average:</strong> {future_adj['total_people'].mean():.0f} people per hour</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Weather impact note
            if weather_scenario == "rainy_morning_rush":
                st.info("🌧️ **Weather Note:** Rainy conditions during morning rush hours may further reduce bike traffic and increase car dependency.")
            elif weather_scenario == "sunny_weekend":
                st.info("☀️ **Weather Note:** Sunny weekend conditions typically increase bike and pedestrian traffic.")
            
            # Store results in session state for comparison tab
            st.session_state.forecast_results = {
                'future_open': future_open,
                'future_adj': future_adj,
                'parking_scenario': parking_scenario,
                'weather_scenario': weather_scenario,
                'vacation_scenario': vacation_scenario,
                'weeks_ahead': weeks_ahead
            }
            
    else:
        st.info("👈 Configure your parameters and click 'Run Forecast' to generate predictions")

with tab3:
    st.header("Scenario Impact Comparison")
    
    if 'forecast_results' in st.session_state:
        results = st.session_state.forecast_results
        future_open = results['future_open']
        future_adj = results['future_adj']
        scenario = results['parking_scenario']
        
        # Calculate percentage changes
        modes = ["car", "bike", "pedestrian", "heavy", "total_people"]
        
        changes = {}
        for mode in modes:
            open_avg = future_open[mode].mean()
            adj_avg = future_adj[mode].mean()
            pct_change = ((adj_avg - open_avg) / open_avg) * 100 if open_avg > 0 else 0
            changes[mode] = {
                'open': open_avg,
                'adjusted': adj_avg,
                'absolute_change': adj_avg - open_avg,
                'percent_change': pct_change
            }
        
        # Display impact metrics
        st.subheader(f"📊 Impact of {scenario.capitalize()} Parking Policy")
        
        cols = st.columns(len(modes))
        for i, mode in enumerate(modes):
            with cols[i]:
                change = changes[mode]
                st.metric(
                    mode.replace('_', ' ').title(),
                    f"{change['adjusted']:.1f}",
                    delta=f"{change['absolute_change']:+.1f} ({change['percent_change']:+.1f}%)",
                    delta_color="inverse" if mode == "car" and change['percent_change'] < 0 else "normal"
                )
        
        # Impact visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Absolute changes
        mode_names = [m.replace('_', ' ').title() for m in modes]
        changes_abs = [changes[m]['absolute_change'] for m in modes]
        colors = ['#E63946', '#06A77D', '#F18F01', '#6A4C93', '#2E86AB']
        
        bars1 = ax1.bar(mode_names, changes_abs, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        ax1.axhline(0, color='black', linewidth=1)
        ax1.set_ylabel('Change in Count per Hour', fontweight='bold')
        ax1.set_title(f'{scenario.capitalize()} vs Open Parking\n(Absolute Change)', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, value in zip(bars1, changes_abs):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:+.1f}', ha='center', 
                    va='bottom' if height >= 0 else 'top', fontweight='bold')
        
        # Percentage changes
        changes_pct = [changes[m]['percent_change'] for m in modes]
        bars2 = ax2.bar(mode_names, changes_pct, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        ax2.axhline(0, color='black', linewidth=1)
        ax2.set_ylabel('Percentage Change (%)', fontweight='bold')
        ax2.set_title(f'{scenario.capitalize()} vs Open Parking\n(Percentage Change)', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, value in zip(bars2, changes_pct):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:+.1f}%', ha='center', 
                    va='bottom' if height >= 0 else 'top', fontweight='bold')
        
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
        
        # Weekly distribution comparison
        st.subheader("📅 Weekly Traffic Distribution")
        
        # Add day names to forecast data
        future_open_weekly = future_open.copy()
        future_adj_weekly = future_adj.copy()
        future_open_weekly['dayofweek'] = future_open_weekly['datetime'].dt.dayofweek
        future_adj_weekly['dayofweek'] = future_adj_weekly['datetime'].dt.dayofweek
        
        weekly_open = future_open_weekly.groupby('dayofweek')['total_people'].mean()
        weekly_adj = future_adj_weekly.groupby('dayofweek')['total_people'].mean()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(7)
        width = 0.35
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        bars1 = ax.bar(x - width/2, weekly_open.values, width, label='Open Parking', 
                      color='#4CAF50', alpha=0.8, edgecolor='white', linewidth=2)
        bars2 = ax.bar(x + width/2, weekly_adj.values, width, 
                      label=f'{scenario.capitalize()} Parking',
                      color='#F44336' if scenario == "closed" else '#FF9800',
                      alpha=0.8, edgecolor='white', linewidth=2)
        
        ax.set_xlabel('Day of Week', fontweight='bold')
        ax.set_ylabel('Average People per Hour', fontweight='bold')
        ax.set_title('Weekly Traffic Distribution Comparison', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(day_names)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        
    else:
        st.info("👈 Run a forecast first to see scenario comparisons")

with tab4:
    st.header("📋 Raw Data Explorer")
    
    # Data filtering options
    st.subheader("🔍 Data Filters")
    
    col1, col2 = st.columns(2)
    with col1:
        available_streets = df_model['street_name'].unique()
        selected_street = st.selectbox("Select Street", available_streets)
        
    with col2:
        # Date range for raw data
        raw_start = st.date_input("From Date", value=date_min, key="raw_start")
        raw_end = st.date_input("To Date", value=date_max, key="raw_end")
    
    # Filter data based on selections
    raw_start_dt = pd.to_datetime(raw_start).tz_localize(None)
    raw_end_dt = pd.to_datetime(raw_end).tz_localize(None) + pd.Timedelta(days=1)
    
    raw_filtered = df_model[
        (df_model['street_name'] == selected_street) &
        (df_model['datetime'] >= raw_start_dt) &
        (df_model['datetime'] <= raw_end_dt)
    ].copy()
    
    st.subheader(f"📊 Data Summary - {selected_street}")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", f"{len(raw_filtered):,}")
    with col2:
        st.metric("Date Range", f"{(raw_end_dt - raw_start_dt).days} days")
    with col3:
        st.metric("Avg Hourly Traffic", f"{raw_filtered['total_people'].mean():.1f}")
    with col4:
        st.metric("Peak Hour Traffic", f"{raw_filtered['total_people'].max():.0f}")
    
    # Data preview
    st.subheader("📋 Data Preview")
    
    # Select columns to display
    display_columns = [
        'datetime', 'street_name', 'hour', 'dayofweek', 'is_weekend',
        'car', 'bike', 'pedestrian', 'heavy', 'total_people',
        'temperature_c', 'precipitation_mm', 'cloud_cover_pct', 'wind_speed_kmh',
        'is_holiday', 'is_school_vacation'
    ]
    
    # Show data with search/filter
    if len(raw_filtered) > 0:
        # Add sorting option
        sort_col = st.selectbox("Sort by", display_columns, index=0)
        sort_order = st.radio("Sort order", ["Ascending", "Descending"], horizontal=True)
        
        if sort_order == "Descending":
            raw_display = raw_filtered[display_columns].sort_values(sort_col, ascending=False)
        else:
            raw_display = raw_filtered[display_columns].sort_values(sort_col, ascending=True)
        
        # Display data
        st.dataframe(raw_display, use_container_width=True, height=400)
        
        # Download button
        csv_data = raw_display.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name=f"traffic_data_{selected_street}_{raw_start}_{raw_end}.csv",
            mime="text/csv",
            help="Download filtered data as CSV file"
        )
        
        # Statistical summary
        st.subheader("📈 Statistical Summary")
        
        numeric_cols = ['car', 'bike', 'pedestrian', 'heavy', 'total_people', 
                       'temperature_c', 'precipitation_mm', 'cloud_cover_pct', 'wind_speed_kmh']
        
        summary_stats = raw_filtered[numeric_cols].describe()
        st.dataframe(summary_stats, use_container_width=True)
        
    else:
        st.warning("No data found for selected filters.")

with tab5:
    st.header("🎯 Clustering & Anomaly Detection")
    st.markdown("Analysis of cyclist traffic patterns and anomaly detection on both key campus streets.")
    
    # Load clustering data
    @st.cache_data
    def load_clustering_data():
        try:
            df_full = pd.read_csv("../data/traffic_weather_merged.csv", parse_dates=['date'])
            return df_full
        except FileNotFoundError:
            st.error("❌ Traffic weather data file not found.")
            return None
    
    clustering_data = load_clustering_data()
    
    if clustering_data is not None:
        # Apply date filters from sidebar
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)
        
        # Remove timezone info from clustering data for comparison
        if clustering_data['date'].dt.tz is not None:
            clustering_data['date'] = clustering_data['date'].dt.tz_localize(None)
        
        # Filter data based on selected dates
        mask = (clustering_data['date'] >= start_dt) & (clustering_data['date'] < end_dt)
        clustering_data = clustering_data[mask].copy()
        
        if len(clustering_data) == 0:
            st.warning("⚠️ No data available for the selected date range. Please adjust the date filters.")
            st.stop()
        
        # Focus on cyclist data for both key streets
        df_two_streets = clustering_data[clustering_data['street_name'].isin([
            'Sintmartenslatemlaan',
            'Graaf Karel de Goedelaan'
        ])].copy()
        
        if len(df_two_streets) == 0:
            st.warning("⚠️ No data available for the selected streets in this date range.")
            st.stop()
        
        # Feature engineering
        df_two_streets['hour'] = df_two_streets['date'].dt.hour
        df_two_streets['dayofweek'] = df_two_streets['date'].dt.dayofweek
        df_two_streets['is_weekend'] = (df_two_streets['dayofweek'] >= 5).astype(int)
        df_two_streets['street_id'] = df_two_streets['street_name'].astype('category').cat.codes
        df_two_streets['target_count'] = df_two_streets['bike']  # Focus on cyclists
        
        # Clustering controls
        st.subheader("🔧 Analysis Parameters")
        col1, col2 = st.columns(2)
        
        with col1:
            n_clusters = st.slider("Number of Clusters", 2, 4, 3)
            contamination_rate = st.slider("Anomaly Detection Rate (%)", 1, 5, 2) / 100
        
        with col2:
            focus_street = st.selectbox("Focus Street for Details", 
                                       ['Both Streets', 'Sintmartenslatemlaan', 'Graaf Karel de Goedelaan'])
        
        if st.button("🔄 Run Clustering Analysis", type="primary"):
            if not sklearn_available:
                st.error("❌ Scikit-learn not available. Please install it to use clustering features.")
                st.stop()
                
            from sklearn.preprocessing import StandardScaler
            from sklearn.cluster import KMeans
            from sklearn.ensemble import IsolationForest
            
            # Prepare features
            feature_cols_clustering = [
                'hour', 'dayofweek', 'is_weekend', 'street_id',
                'temperature_c', 'precipitation_mm', 'cloud_cover_pct',
                'target_count'
            ]
            
            df_features = df_two_streets[feature_cols_clustering].fillna(0)
            
            # Standardize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(df_features)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            df_two_streets['cluster'] = kmeans.fit_predict(features_scaled)
            
            # Perform anomaly detection
            iso_forest = IsolationForest(contamination=contamination_rate, random_state=42)
            anomaly_predictions = iso_forest.fit_predict(features_scaled)
            df_two_streets['is_anomaly'] = (anomaly_predictions == -1)
            
            # Display results
            st.subheader("📊 Clustering Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Data Points", f"{len(df_two_streets):,}")
            with col2:
                st.metric("Clusters Found", n_clusters)
            with col3:
                anomaly_count = df_two_streets['is_anomaly'].sum()
                st.metric("Anomalies Detected", f"{anomaly_count} ({anomaly_count/len(df_two_streets)*100:.1f}%)")
            
            # Cluster distribution
            st.subheader("🎯 Cluster Distribution")
            cluster_dist = df_two_streets.groupby(['street_name', 'cluster']).size().unstack(fill_value=0)
            st.dataframe(cluster_dist, use_container_width=True)
            
            # Visualization: Hourly patterns by cluster
            st.subheader("📈 Hourly Traffic Patterns by Cluster")
            
            streets_to_plot = ['Graaf Karel de Goedelaan', 'Sintmartenslatemlaan'] if focus_street == 'Both Streets' else [focus_street]
            
            if focus_street == 'Both Streets':
                fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
            else:
                fig, axes = plt.subplots(1, 1, figsize=(12, 6))
                axes = [axes]
            
            for idx, street in enumerate(streets_to_plot):
                street_data = df_two_streets[df_two_streets['street_name'] == street]
                cluster_hourly = street_data.groupby(['cluster', 'hour'])['target_count'].mean().reset_index()
                
                ax = axes[idx] if len(axes) > 1 else axes[0]
                colors = plt.cm.Set3(np.linspace(0, 1, n_clusters))
                
                for cluster in range(n_clusters):
                    data = cluster_hourly[cluster_hourly['cluster'] == cluster]
                    ax.plot(data['hour'], data['target_count'], 
                           marker='o', label=f'Cluster {cluster}', 
                           linewidth=2, color=colors[cluster])
                
                ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
                ax.set_ylabel('Average Cyclist Count', fontsize=12, fontweight='bold')
                ax.set_title(f'{street}', fontsize=13, fontweight='bold')
                ax.legend(title='Cluster', fontsize=9)
                ax.grid(alpha=0.3)
                ax.set_xticks(range(0, 24, 2))
            
            plt.suptitle('Cyclist Traffic Clusters - Hourly Patterns', fontsize=14, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
            
            # Anomaly visualization
            st.subheader("⚠️ Anomaly Detection Results")
            
            # Summary of anomalies
            anomaly_summary = df_two_streets[df_two_streets['is_anomaly']].groupby('street_name').agg({
                'target_count': ['count', 'mean', 'min', 'max'],
                'temperature_c': 'mean',
                'precipitation_mm': 'mean'
            }).round(2)
            
            anomaly_summary.columns = ['Count', 'Avg_Cyclists', 'Min_Cyclists', 'Max_Cyclists', 'Avg_Temp', 'Avg_Rain']
            st.dataframe(anomaly_summary, use_container_width=True)
            
            # Scatter plot: Temperature vs Cyclist count with anomalies
            fig, axes = plt.subplots(1, 2, figsize=(16, 6))
            
            for idx, street in enumerate(['Graaf Karel de Goedelaan', 'Sintmartenslatemlaan']):
                street_data = df_two_streets[df_two_streets['street_name'] == street]
                normal = street_data[~street_data['is_anomaly']]
                anomaly = street_data[street_data['is_anomaly']]
                
                ax = axes[idx]
                ax.scatter(normal['temperature_c'], normal['target_count'], 
                          alpha=0.4, s=20, c='blue', label='Normal')
                ax.scatter(anomaly['temperature_c'], anomaly['target_count'], 
                          alpha=0.8, s=60, c='red', marker='X', label='Anomaly')
                
                ax.set_xlabel('Temperature (°C)', fontsize=12, fontweight='bold')
                ax.set_ylabel('Cyclist Count', fontsize=12, fontweight='bold')
                ax.set_title(f'{street}', fontsize=13, fontweight='bold')
                ax.legend()
                ax.grid(alpha=0.3)
            
            plt.suptitle('Cyclist Count vs Temperature (Anomalies Highlighted)', fontsize=14, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
        
        else:
            st.info("👆 Click 'Run Clustering Analysis' to see results")
            
    else:
        st.error("Cannot load clustering data. Please ensure the traffic_weather_merged.csv file exists.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Sint-Martens-Latemlaan Traffic Analysis Dashboard</strong></p>
    <p>Built with Streamlit • Data from Howest Campus Traffic Study • Team G3: Hadi, Rares, Hamzzah</p>
</div>
""", unsafe_allow_html=True)
