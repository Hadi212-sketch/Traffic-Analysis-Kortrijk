# Traffic Analysis Dashboard - User Manual
**Version 1.0 | January 2026**  
**Developed by Traffic G3 - Howest CTAI**  
*Hadi, Rares, Hamzzah*

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [Dashboard Overview](#3-dashboard-overview)
4. [Feature Guide](#4-feature-guide)
   - [4.1 Historical Analysis](#41-historical-analysis-tab)
   - [4.2 Future Forecast](#42-future-forecast-tab)
   - [4.3 Scenario Comparison](#43-scenario-comparison-tab)
   - [4.4 Roadblock Simulation](#44-roadblock-simulation-tab)
   - [4.5 Raw Data Explorer](#45-raw-data-explorer-tab)
   - [4.6 Clustering & Anomalies](#46-clustering--anomalies-tab)
5. [Use Cases & Examples](#5-use-cases--examples)
6. [Tips & Best Practices](#6-tips--best-practices)
7. [Troubleshooting](#7-troubleshooting)
8. [Technical Information](#8-technical-information)

---

## 1. Introduction

### 1.1 Purpose of the Dashboard

The Traffic Analysis Dashboard is an interactive web-based tool designed to help campus administrators, urban planners, and decision-makers understand and predict traffic patterns around Howest Campus in Kortrijk. The dashboard transforms raw traffic sensor data into actionable insights through visualizations, forecasts, and scenario simulations.

### 1.2 What Can You Do?

With this dashboard, you can:

- **Analyze historical traffic patterns** to understand peak hours, weekly trends, and seasonal variations
- **Forecast future traffic** up to 13 weeks ahead with customizable scenarios
- **Compare policy scenarios** to see the impact of parking changes, weather conditions, or school vacations
- **Simulate roadblocks** to assess disruption and plan traffic management
- **Explore raw data** with filtering and download capabilities
- **Detect anomalies** in cyclist traffic patterns for safety insights

### 1.3 Data Sources

The dashboard analyzes data from:
- **Telraam traffic sensors** on two key streets near campus:
  - Sintmartenslatemlaan
  - Graaf Karel de Goedelaan
- **Weather data** (temperature, precipitation, cloud cover, wind speed)
- **Calendar data** (Belgian holidays and school vacation periods)
- **Traffic modes tracked**: Cars, bikes, pedestrians, heavy vehicles

---

## 2. Getting Started

### 2.1 Accessing the Dashboard

**Online Access (Recommended):**
1. Open your web browser (Chrome, Firefox, Safari, or Edge)
2. Navigate to: [Your Streamlit Cloud URL]
3. Wait 10-15 seconds for the dashboard to load
4. No login required - the dashboard is publicly accessible

**Local Access (For Developers):**
```bash
cd Traffic-Analysis-Kortrijk
streamlit run dashboard/app.py
```

### 2.2 System Requirements

- **Web Browser**: Modern browser with JavaScript enabled
- **Internet Connection**: Required for online access
- **Screen Resolution**: Minimum 1366x768 (desktop recommended)
- **No Installation Required**: Runs entirely in your browser

### 2.3 First-Time Navigation

When you first open the dashboard, you'll see:

1. **Title and Description** at the top
2. **Sidebar on the left** with date selectors and scenario controls
3. **Six tabs** across the main area:
   - 📈 Historical Analysis
   - 🔮 Future Forecast
   - 📊 Scenario Comparison
   - 🚧 Roadblock Simulation
   - 📋 Raw Data
   - 🎯 Clustering & Anomalies

---

## 3. Dashboard Overview

### 3.1 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│          Traffic Analysis & Prediction                  │
│    Interactive analysis around Howest Campus            │
├──────────────┬──────────────────────────────────────────┤
│   SIDEBAR    │              MAIN CONTENT                │
│              │                                           │
│ Date Range   │   [Tabs: Historical | Forecast | ...]   │
│              │                                           │
│ Forecast     │   [Charts and Visualizations]            │
│ Parameters   │                                           │
│              │   [Metrics and Insights]                 │
│ Scenarios    │                                           │
│              │                                           │
└──────────────┴──────────────────────────────────────────┘
```

### 3.2 Sidebar Controls

The sidebar contains all the configuration options you'll need:

**Historical Period Section:**
- **Start Date**: Select beginning of analysis period
- **End Date**: Select end of analysis period
- Default range: Full dataset (November 2025 onwards)

**Forecast Parameters Section:**
- **Weeks ahead to forecast**: Slider from 1-13 weeks
- **Parking Scenario**: Dropdown menu
  - Open (current situation)
  - Closed (no parking allowed)
  - Paid (parking fees applied)
- **Weather Scenario**: Dropdown menu
  - Normal (typical conditions)
  - Rainy morning rush (7-9 AM precipitation)
  - Cloudy windy (high clouds and wind)
- **School Vacation Scenario**: Dropdown menu
  - Calendar (uses actual vacation dates)
  - Force vacation (all days as vacation)
  - Force no vacation (no vacation days)

**Run Forecast Button:**
- Primary action button to generate predictions
- Clicking this processes your selected scenarios

### 3.3 Color Coding

The dashboard uses consistent colors throughout:
- 🔵 **Blue** (#3498DB) - Cars
- 🟢 **Green** (#27AE60) - Bikes
- 🟠 **Orange** (#E67E22) - Pedestrians
- 🟣 **Purple** (#9B59B6) - Heavy vehicles
- 🔴 **Red** (#E63946) - Alerts/reductions
- 🟡 **Yellow** - Warnings/medium impact

---

## 4. Feature Guide

### 4.1 Historical Analysis Tab

**Purpose**: Understand past traffic patterns and trends.

#### What You'll See:

1. **Summary Metrics (Top Row)**
   - Total Records: Number of hourly observations
   - Avg Daily Traffic: Average people per hour
   - Peak Hour Traffic: Maximum in any single hour
   - Days Analyzed: Number of unique days

2. **Hourly Traffic Pattern Chart**
   - Two side-by-side plots:
     - Left: Traffic by mode (car, bike, pedestrian, heavy)
     - Right: Total people per hour
   - X-axis: Hour of day (0-23)
   - Y-axis: Average count
   - **Interpretation**: Identify morning/evening rush hours and quiet periods

3. **Weekly Traffic Pattern Chart**
   - Bar chart showing average traffic by day of week
   - Monday through Sunday
   - **Interpretation**: Compare weekday vs. weekend patterns

4. **Mode Distribution Chart**
   - Horizontal bar chart showing total counts
   - Compare relative usage of each transportation mode
   - **Interpretation**: See which modes dominate

#### How to Use:

**Example 1: Analyze a Specific Week**
1. In sidebar, set Start Date to Monday of your target week
2. Set End Date to Sunday of the same week
3. View the hourly pattern to identify peak hours
4. Check weekly distribution to see if weekend differs from weekdays

**Example 2: Compare Two Months**
1. First, set dates for Month 1
2. Note the peak hour traffic metric
3. Then, change dates to Month 2
4. Compare the peak hour traffic change

**Key Insights You Can Find:**
- Peak traffic hours (typically 7-9 AM and 4-6 PM)
- Weekend vs. weekday differences
- Seasonal trends (comparing months)
- Mode share (how many use bikes vs. cars)

---

### 4.2 Future Forecast Tab

**Purpose**: Predict traffic for upcoming weeks under different scenarios.

#### Step-by-Step Usage:

**Step 1: Configure Your Forecast**
1. Open the **Forecast Parameters** section in sidebar
2. Select **Weeks ahead** (1-13 weeks)
   - Short-term (1-2 weeks): Most accurate
   - Medium-term (3-6 weeks): Good for planning
   - Long-term (7-13 weeks): Strategic decisions
3. Choose **Parking Scenario**:
   - **Open**: Current situation (baseline)
   - **Closed**: No parking allowed (expect -50% cars, +20% bikes/pedestrians)
   - **Paid**: Parking fees applied (expect -25% cars, +10% bikes/pedestrians)
4. Choose **Weather Scenario**:
   - **Normal**: Median historical weather
   - **Rainy morning rush**: Heavy rain 7-9 AM (expect -20% bikes)
   - **Cloudy windy**: High clouds/wind (expect -10% bikes)
5. Choose **School Vacation Scenario**:
   - **Calendar**: Uses real Belgian school vacation dates
   - **Force vacation**: Treats all days as vacation (lower traffic)
   - **Force no vacation**: No vacation periods (higher traffic)
6. Click **🔮 Run Forecast** button

**Step 2: Interpret Results**

Once processing completes (5-10 seconds), you'll see:

1. **Summary Metrics (Top)**
   - Forecast Period: Confirms weeks ahead
   - Avg Hourly Traffic: Mean people per hour
   - Total Week Traffic: Sum over forecast period

2. **Traffic Forecast Overview Chart**
   - Line chart showing hourly predictions
   - Red line: Your selected scenario
   - Blue line: Baseline (open parking, normal weather)
   - **Interpretation**: See where scenarios diverge

3. **Forecast by Transportation Mode (2x2 Grid)**
   - Four separate charts for car, bike, pedestrian, heavy
   - Each shows scenario vs. baseline
   - **Interpretation**: Understand mode-specific impacts

4. **Key Forecast Insights (Metrics Row)**
   - 🚗 Car Traffic: Average per hour with % change
   - 🚲 Bike Traffic: Average per hour with % change
   - 🚶 Pedestrians: Average per hour with % change
   - 👥 Total Traffic: Average per hour with % change

5. **Transportation Mode Impact Analysis (Bar Chart)**
   - Side-by-side bars comparing baseline vs. scenario
   - Shows absolute counts for forecast period
   - **Interpretation**: Visual comparison of policy impact

6. **Daily Average Comparison (Bar Chart)**
   - Daily traffic averages across forecast period
   - Compare scenario (red) vs. baseline (green)
   - **Interpretation**: Day-to-day variations

7. **Traffic Mode Distribution (Pie Chart)**
   - Shows percentage share of each mode
   - **Interpretation**: Overall mode split under scenario

8. **Hourly Traffic Patterns (Heatmap)**
   - Rows: Hours (0-23)
   - Columns: Days of week
   - Colors: Traffic intensity (yellow=low, red=high)
   - **Interpretation**: Identify peak times by day

#### Practical Examples:

**Example 1: Plan for Closed Parking Day**
```
Scenario:
- Weeks ahead: 1
- Parking: Closed
- Weather: Normal
- Vacation: Calendar

Expected Result:
- Cars: -50% (e.g., 100 → 50 per hour)
- Bikes: +20% (e.g., 30 → 36 per hour)
- Pedestrians: +20% (e.g., 15 → 18 per hour)
- Total: Reduced by ~40%

Use Case: Assess if alternative transport can absorb car traffic
```

**Example 2: Rainy Week Forecast**
```
Scenario:
- Weeks ahead: 2
- Parking: Open
- Weather: Rainy morning rush
- Vacation: Calendar

Expected Result:
- Bikes: -20% during morning (7-9 AM)
- Cars: Slightly higher (+5%)
- Pedestrians: -10%

Use Case: Plan for increased parking demand on rainy days
```

**Example 3: Summer Vacation Impact**
```
Scenario:
- Weeks ahead: 4
- Parking: Open
- Weather: Normal
- Vacation: Force vacation

Expected Result:
- All modes: -30% to -50%
- Campus traffic significantly reduced

Use Case: Schedule maintenance or construction work
```

---

### 4.3 Scenario Comparison Tab

**Purpose**: Compare the impact of different policies side-by-side.

#### How It Works:

This tab automatically populates after you run a forecast in Tab 2. It shows:

1. **Impact Metrics (Top Row)**
   - 🚗 Cars Impact: Total count and % change
   - 🚴 Bikes Impact: Total count and % change
   - 🚶 Pedestrians Impact: Total count and % change
   - 👥 Total Impact: Overall % change

2. **Scenario Impact Charts (2 Charts)**
   - Left: Absolute change (people count)
   - Right: Percentage change (%)
   - **Interpretation**: See which modes are most affected

3. **Weekly Distribution Comparison**
   - Compare baseline vs. scenario by day of week
   - **Interpretation**: See if impacts vary by weekday

#### Use Cases:

**Compare Parking Policies**
1. Run forecast with "Closed" parking
2. View Scenario Comparison tab
3. Note the impact metrics
4. Return to Forecast tab, change to "Paid" parking
5. Run forecast again
6. Compare the two sets of results

**Example Output:**
```
Closed Parking:
- Cars: -50% (-30 per hour)
- Bikes: +20% (+6 per hour)
- Total: -40%

Paid Parking:
- Cars: -25% (-15 per hour)
- Bikes: +10% (+3 per hour)
- Total: -20%

Decision: Paid parking is less disruptive while still reducing cars
```

---

### 4.4 Roadblock Simulation Tab

**Purpose**: Assess the impact of a roadblock on a specific street and date.

#### Step-by-Step Usage:

**Step 1: Configure Roadblock**

1. **Select Street** (left column):
   - Sintmartenslatemlaan
   - Graaf Karel de Goedelaan
   - Choose the street where roadblock will occur

2. **Select Date**:
   - Pick any date within dataset range or future
   - Use calendar picker
   - Consider weekday vs. weekend

3. **Set Time Window** (right column):
   - **Start Hour**: When roadblock begins (0-23)
   - **End Hour**: When roadblock ends (0-23)
   - Example: 7 AM to 9 AM for morning rush

**Step 2: Run Simulation**

4. Click **🚧 Simulate Roadblock** button
5. Wait 3-5 seconds for processing

**Step 3: Interpret Results**

You'll see:

1. **Quick Impact Summary (4 Metrics)**
   - Peak Without Roadblock: Max people/hour (normal)
   - Peak With Roadblock: Max people/hour (reduced)
   - Car Traffic Reduction: Percentage drop
   - Bike Traffic Reduction: Percentage drop

2. **Total Traffic Impact Chart (Large)**
   - Blue line: Normal day (without roadblock)
   - Red line: With roadblock
   - Gray shaded area: Roadblock period
   - Annotation box: Peak reduction percentage
   - **Interpretation**: See overall traffic suppression

3. **Impact by Transportation Mode (2x2 Grid)**
   - Four charts: Car, Bike, Pedestrian, Heavy
   - Each shows normal vs. roadblock
   - Colored boxes show average drop percentage
   - **Interpretation**: Understand mode-specific impacts

4. **Roadblock Impact Analysis (Text Insights)**
   - Peak Hour Impact: Peak reduction stats
   - Full Day Impact: Total daily reduction
   - Mode-specific changes: Detailed breakdown
   - Summary: Key takeaway message

#### Roadblock Impact Model:

The simulation applies these reductions during the roadblock period:

| Mode        | Reduction | Reason                           |
|-------------|-----------|----------------------------------|
| Cars        | -90%      | Cannot access due to closure     |
| Heavy       | -80%      | Trucks rerouted                  |
| Bikes       | -20%      | Some cyclists avoid area         |
| Pedestrians | -10%      | Some pedestrians avoid area      |

#### Practical Examples:

**Example 1: Morning Road Construction**
```
Configuration:
- Street: Sintmartenslatemlaan
- Date: Monday, February 3, 2026
- Time: 7:00 - 9:00 (morning rush)

Results:
- Peak traffic: 120 → 25 people/hour (-79%)
- Car reduction: -90% (100 → 10 cars/hour)
- Bike reduction: -20% (15 → 12 bikes/hour)
- Daily impact: -30% overall

Use Case: 
- Plan detour signage
- Notify campus community
- Schedule extra bike parking
```

**Example 2: Afternoon Event Setup**
```
Configuration:
- Street: Graaf Karel de Goedelaan
- Date: Friday, March 20, 2026
- Time: 14:00 - 18:00 (afternoon)

Results:
- Peak traffic: 80 → 18 people/hour (-78%)
- Car reduction: -90% (65 → 7 cars/hour)
- Minimal bike impact (off-peak hours)
- Daily impact: -22%

Use Case:
- Safe event setup window
- Reduced disruption to morning/evening commutes
```

**Example 3: Weekend Maintenance**
```
Configuration:
- Street: Sintmartenslatemlaan
- Date: Saturday, February 15, 2026
- Time: 8:00 - 12:00 (morning)

Results:
- Much lower baseline traffic (weekends are quieter)
- Peak traffic: 40 → 10 people/hour
- Daily impact: -15%

Use Case:
- Ideal time for maintenance
- Minimal disruption to campus users
```

---

### 4.5 Raw Data Explorer Tab

**Purpose**: Access, filter, and download the underlying traffic data.

#### Features:

1. **Data Filters**
   - **Select Street**: Choose Sintmartenslatemlaan or Graaf Karel de Goedelaan
   - **From Date**: Start of data range
   - **To Date**: End of data range

2. **Data Summary (4 Metrics)**
   - Total Records: Number of hourly observations
   - Date Range: Days covered
   - Avg Hourly Traffic: Mean people per hour
   - Peak Hour Traffic: Maximum in any hour

3. **Data Preview Table**
   - Columns:
     - datetime: Date and time
     - street_name: Street identifier
     - hour: Hour of day (0-23)
     - dayofweek: Day number (0=Monday)
     - is_weekend: 1 if weekend, 0 if weekday
     - car, bike, pedestrian, heavy: Counts by mode
     - total_people: Sum of all modes
     - temperature_c, precipitation_mm, cloud_cover_pct, wind_speed_kmh: Weather
     - is_holiday, is_school_vacation: Calendar flags
   - **Sort by**: Select any column
   - **Sort order**: Ascending or Descending
   - **Scrollable**: Explore 400 rows at a time

4. **Download as CSV Button**
   - Downloads filtered data to your computer
   - Filename: traffic_data_{street}_{start}_{end}.csv
   - Open in Excel, Google Sheets, or Python

5. **Statistical Summary**
   - Descriptive statistics for all numeric columns
   - Count, mean, std, min, 25%, 50%, 75%, max
   - **Interpretation**: Understand data distribution

#### Use Cases:

**Example 1: Export Data for External Analysis**
1. Select street: Sintmartenslatemlaan
2. Set date range: December 1-31, 2025
3. Click "📥 Download as CSV"
4. Open in Excel for custom analysis

**Example 2: Find Specific High-Traffic Days**
1. Select street and full date range
2. Sort by: total_people
3. Sort order: Descending
4. Scroll through top records
5. Identify dates with unusually high traffic
6. Cross-reference with holiday/event calendars

**Example 3: Analyze Weather Correlations**
1. Download full dataset
2. In Excel, create scatter plot:
   - X-axis: temperature_c
   - Y-axis: bike
3. Observe correlation (warmer = more bikes)

---

### 4.6 Clustering & Anomalies Tab

**Purpose**: Discover hidden patterns in cyclist traffic and identify unusual events.

#### What is Clustering?

Clustering groups similar traffic patterns together. For example:
- **Cluster 1**: Weekday morning rush (high cyclists, warm, dry)
- **Cluster 2**: Weekend leisure (moderate cyclists, any weather)
- **Cluster 3**: Rainy days (low cyclists, high precipitation)

#### What is Anomaly Detection?

Anomaly detection identifies unusual traffic conditions that don't fit normal patterns. For example:
- Unexpected cyclist surge during exam periods
- Traffic drop during unscheduled events
- Weather-related anomalies

#### Step-by-Step Usage:

**Step 1: Configure Analysis**

1. **Analysis Parameters**:
   - **Number of Clusters**: 2-4 (start with 3)
     - Fewer clusters = broader categories
     - More clusters = finer distinctions
   - **Anomaly Detection Rate**: 1-5% (start with 2%)
     - Lower % = only extreme outliers
     - Higher % = includes more unusual events

2. **Focus Street**:
   - Both Streets (compare patterns)
   - Sintmartenslatemlaan only
   - Graaf Karel de Goedelaan only

**Step 2: Run Analysis**

3. Click **🔄 Run Clustering Analysis**
4. Wait 5-10 seconds for machine learning processing

**Step 3: Interpret Results**

1. **Clustering Results (3 Metrics)**
   - Total Data Points: Observations analyzed
   - Clusters Found: Number of pattern groups
   - Anomalies Detected: Count and percentage

2. **Cluster Distribution Table**
   - Shows how many observations in each cluster per street
   - **Interpretation**: Are clusters evenly distributed or imbalanced?

3. **Hourly Traffic Patterns by Cluster**
   - Line charts showing average cyclist count by hour
   - Different color per cluster
   - **Interpretation**: Each cluster represents a different daily pattern

4. **Anomaly Detection Results**
   - Summary table: Count, avg cyclists, temp, rain for anomalies
   - **Interpretation**: What conditions produce anomalies?

5. **Temperature vs Cyclist Count (Scatter Plot)**
   - Each point is one observation
   - Normal points in blue
   - Anomalies in red
   - **Interpretation**: Do anomalies occur at extreme temperatures?

#### Practical Examples:

**Example 1: Understand Cyclist Patterns**
```
Configuration:
- Clusters: 3
- Anomaly rate: 2%
- Focus: Both streets

Results:
- Cluster 0: Weekday rush (high cyclists, morning/evening)
- Cluster 1: Weekend/vacation (moderate cyclists, midday)
- Cluster 2: Bad weather (low cyclists, rainy/cold)

Insight: Most variation driven by day-of-week and weather
```

**Example 2: Investigate Anomalies**
```
Results:
- 48 anomalies detected (2% of data)
- Anomaly characteristics:
  - Average cyclists: 45 (vs. normal 25)
  - Average temp: 22°C (warm days)
  - Average rain: 0mm (dry days)

Insight: Anomalies are unusually high cyclist counts on warm, dry days
Action: Possibly special events or exam periods - plan extra bike parking
```

**Example 3: Compare Two Streets**
```
Cluster Distribution:
                     Cluster 0  Cluster 1  Cluster 2
Sintmartenslatemlaan      450        320        180
Graaf Karel de Goedelaan  380        410        160

Insight: Sintmartenslatemlaan has more Cluster 0 (rush hour pattern)
        Graaf Karel de Goedelaan more balanced

Action: Prioritize cyclist infrastructure on Sintmartenslatemlaan
```

---

## 5. Use Cases & Examples

### 5.1 Campus Parking Policy Decision

**Question**: Should we close campus parking or implement paid parking?

**Steps**:
1. Go to **Future Forecast** tab
2. Run forecast with "Closed" parking for 4 weeks
3. Note: Cars -50%, Bikes +20%, Total -40%
4. Return, change to "Paid" parking, run again
5. Note: Cars -25%, Bikes +10%, Total -20%
6. Go to **Scenario Comparison** tab
7. Compare impacts side-by-side

**Decision Framework**:
- If goal is maximum car reduction: Choose "Closed"
- If goal is balanced approach: Choose "Paid"
- If concern about total traffic loss: "Paid" is less disruptive

---

### 5.2 Infrastructure Planning

**Question**: Where should we add bike lanes?

**Steps**:
1. Go to **Historical Analysis** tab
2. Set full date range
3. Check Mode Distribution chart
4. Note bike percentage: ~15-20% of traffic
5. Go to **Clustering & Anomalies** tab
6. Compare Sintmartenslatemlaan vs. Graaf Karel de Goedelaan
7. Check which street has more cyclist-heavy clusters

**Decision**:
- Street with higher bike usage gets priority for bike lane
- Use anomaly detection to identify peak demand periods
- Plan bike parking based on forecast growth

---

### 5.3 Event Planning

**Question**: When can we safely close a street for an event?

**Steps**:
1. Go to **Roadblock Simulation** tab
2. Test different dates:
   - Weekday: High traffic disruption
   - Weekend: Lower baseline traffic
3. Test different times:
   - Morning rush (7-9 AM): Maximum disruption
   - Afternoon (2-5 PM): Moderate disruption
   - Evening (6-9 PM): Lower disruption
4. Compare results

**Decision**:
- Weekend afternoon has lowest impact
- If weekday required, avoid morning rush
- Plan detour routes based on mode-specific impacts

---

### 5.4 Seasonal Planning

**Question**: How will traffic change during summer vacation?

**Steps**:
1. Go to **Future Forecast** tab
2. Set weeks ahead: 8 (summer period)
3. Parking: Open
4. Weather: Normal
5. Vacation: Force vacation
6. Run forecast
7. Compare "Total Week Traffic" to non-vacation baseline

**Expected Result**:
- 30-50% reduction in all traffic modes
- Even larger reduction in morning rush hours
- More leisure-time traffic (midday, weekends)

**Planning Actions**:
- Schedule maintenance during low-traffic weeks
- Reduce parking attendant hours
- Plan construction projects

---

### 5.5 Weather-Responsive Operations

**Question**: How should we prepare for rainy weeks?

**Steps**:
1. Go to **Future Forecast** tab
2. Set weeks ahead: 1
3. Weather: Rainy morning rush
4. Run forecast
5. Note bike reduction (-20%) and car increase (+5%)

**Planning Actions**:
- Increase parking availability
- Clear bike shelters for reduced bikes
- Plan indoor routes/covered walkways
- Communicate alternative transport options

---

## 6. Tips & Best Practices

### 6.1 Forecasting Tips

**Accuracy Considerations**:
- ✅ **Short-term forecasts (1-2 weeks)**: Most reliable
- ⚠️ **Medium-term (3-6 weeks)**: Good for planning, some uncertainty
- ⚠️ **Long-term (7-13 weeks)**: Strategic only, higher uncertainty

**Scenario Selection**:
- Always compare to baseline (open parking, normal weather)
- Test extreme scenarios (closed + rainy) for worst-case planning
- Use calendar scenario for realistic forecasts

### 6.2 Data Interpretation

**Understanding Metrics**:
- **Average** = typical conditions (use for general planning)
- **Peak** = maximum observed (use for capacity planning)
- **Total** = sum over period (use for budget/resource allocation)

**Percentage Changes**:
- Green ↑ positive change (good if goal is more bikes/pedestrians)
- Red ↓ negative change (concerning if total traffic drops too much)
- Context matters: -50% cars may be desired policy outcome

### 6.3 Common Pitfalls

❌ **Don't**:
- Forecast beyond 13 weeks (too uncertain)
- Ignore weather effects (major impact on bikes)
- Compare weekday to weekend directly (different patterns)
- Assume one-size-fits-all solutions (streets differ)

✅ **Do**:
- Use multiple tabs for comprehensive analysis
- Cross-reference historical patterns with forecasts
- Consider multiple scenarios before decisions
- Download raw data for detailed investigation

### 6.4 Performance Tips

**Dashboard Responsiveness**:
- First load takes 10-15 seconds (loading data)
- Forecasts take 5-10 seconds (model computation)
- Use cached results when possible (no need to re-run)
- If dashboard freezes, refresh browser

**Browser Recommendations**:
- Chrome: Best performance
- Firefox: Good performance
- Safari: Good on Mac
- Edge: Good on Windows
- Avoid Internet Explorer (not supported)

---

## 7. Troubleshooting

### 7.1 Common Issues

**Dashboard Won't Load**
- **Symptom**: Blank page or spinning icon
- **Solution**: 
  - Wait 30 seconds
  - Refresh browser (F5 or Ctrl+R)
  - Check internet connection
  - Try different browser

**Forecast Button Not Working**
- **Symptom**: Nothing happens when clicking "Run Forecast"
- **Solution**:
  - Check that end date ≥ start date
  - Ensure dates are within data range
  - Refresh page and try again

**Charts Not Displaying**
- **Symptom**: Empty spaces where charts should be
- **Solution**:
  - Scroll down (charts may be loading)
  - Refresh browser
  - Check that date range has data
  - Try wider date range

**Download CSV Fails**
- **Symptom**: No file downloads
- **Solution**:
  - Check browser download settings
  - Allow downloads from the site
  - Ensure popup blocker is off
  - Try right-click → Save as

### 7.2 Data Questions

**Why are there gaps in the data?**
- Telraam sensors occasionally go offline
- Weather API may have missing data
- This is normal; gaps are handled automatically

**Why do numbers seem low?**
- Data represents **per hour** averages
- Multiply by hours for daily totals
- Compare to baseline, not absolute expectations

**Why do forecasts differ from historical?**
- Forecasts include scenario adjustments
- Weather assumptions affect results
- Future is uncertain; forecasts are estimates

### 7.3 Getting Help

**For Technical Issues**:
- Contact Traffic G3 team:
  - Email: [your-team-email@howest.be]
  - Teams: Traffic G3 channel

**For Data Questions**:
- Consult this user manual first
- Check the "Raw Data" tab for source data
- Review the Telraam sensor documentation

**For Policy Questions**:
- Use the dashboard insights as input
- Consult with campus administration
- Consider multiple scenarios

---

## 8. Technical Information

### 8.1 Data Collection

**Telraam Sensors**:
- Location: Two streets near Howest Campus
- Frequency: Hourly measurements
- Modes tracked: Car, bike, pedestrian, heavy vehicle
- Data quality: ~95% uptime

**Weather Data**:
- Source: Open-Meteo API
- Metrics: Temperature, precipitation, cloud cover, wind speed
- Frequency: Hourly
- Historical range: November 2025 onwards

**Calendar Data**:
- Belgian national holidays
- Flemish school vacation periods
- Updated annually

### 8.2 Forecasting Model

**Algorithm**:
- Random Forest Regressor
- Trained on historical data (Nov 2025 - Jan 2026)
- Features: Hour, day of week, weather, calendar, street
- Targets: Car, bike, pedestrian, heavy, total people

**Accuracy**:
- 1-week forecast: ±15% typical error
- 4-week forecast: ±25% typical error
- 13-week forecast: ±40% typical error

**Limitations**:
- Cannot predict unexpected events (accidents, road closures)
- Weather scenarios are simplified
- Assumes policy changes have immediate full effect

### 8.3 Privacy & Data

**Privacy Compliance**:
- Telraam sensors are GDPR-compliant
- No personal identification of individuals
- Only aggregate counts collected
- No video or photo storage

**Data Retention**:
- Historical data: Stored indefinitely
- Forecasts: Generated on-demand, not stored
- User interactions: Not tracked

### 8.4 Updates & Maintenance

**Data Updates**:
- Manual refresh required for new Telraam data
- Weather data fetched as needed
- Calendar data updated annually

**Dashboard Updates**:
- Version history maintained on GitHub
- Updates deployed to Streamlit Cloud
- No user action required for updates

---

## Appendix: Quick Reference

### Transportation Mode Icons
- 🚗 Cars
- 🚲 Bikes
- 🚶 Pedestrians
- 🚚 Heavy Vehicles
- 👥 Total People

### Scenario Impacts (Typical)

**Parking Scenarios**:
| Scenario | Cars   | Bikes  | Pedestrians | Total  |
|----------|--------|--------|-------------|--------|
| Open     | 0%     | 0%     | 0%          | 0%     |
| Closed   | -50%   | +20%   | +20%        | -40%   |
| Paid     | -25%   | +10%   | +10%        | -20%   |

**Weather Scenarios**:
| Scenario           | Cars | Bikes  | Pedestrians | Total |
|--------------------|------|--------|-------------|-------|
| Normal             | 0%   | 0%     | 0%          | 0%    |
| Rainy morning rush | +5%  | -20%   | -10%        | -5%   |
| Cloudy windy       | +2%  | -10%   | -5%         | -2%   |

**Roadblock Impacts** (during closure period):
| Mode        | Reduction |
|-------------|-----------|
| Cars        | -90%      |
| Heavy       | -80%      |
| Bikes       | -20%      |
| Pedestrians | -10%      |

### Keyboard Shortcuts
- F5 or Ctrl+R: Refresh dashboard
- Ctrl+F: Find text on page
- Ctrl+ (plus): Zoom in
- Ctrl- (minus): Zoom out
- Ctrl+0 (zero): Reset zoom

---

## Document Information

**Version**: 1.0  
**Date**: January 2026  
**Authors**: Traffic G3 - Hadi, Rares, Hamzzah  
**Institution**: Howest - Kortrijk Campus  
**Project**: Traffic Analysis Dashboard  
**Contact**: [team-email@howest.be]

**Document License**: Internal use for Howest Campus administration and stakeholders

---

*End of User Manual*
