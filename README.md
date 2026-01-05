# Traffic Analysis – Traffic G3 (Howest CTAI)

This repository contains the Traffic G3 project for the CTAI program at Howest. The project studies traffic around the Howest campus to support better, data‑driven mobility and parking decisions.

## Project Goal
Transform raw traffic sensor data into clear insights, forecasts, and recommendations that answer one central question: how does traffic behave around the campus, and what can Howest do to improve safety, flow, and accessibility?

## Project Trajectory
1. **Data Acquisition & Engineering**
   - Collect hourly Telraam data for key streets near the campus (cars, heavy vehicles, cyclists, pedestrians).
   - Enrich with weather data, holidays, and school periods.
   - Store data in structured files (e.g. CSV/Parquet) and update via repeatable scripts.

2. **Exploratory Data Analysis (EDA)**
   - Visualise daily and weekly patterns, peaks, and anomalies.
   - Compare modes (car, bike, pedestrian) and weekday vs weekend vs holiday behaviour.
   - Identify critical locations and rush‑hour time windows around the campus.

3. **Modelling & Forecasting**
   - Build baseline time‑series models (e.g. ARIMA, Prophet) for short‑term traffic volume prediction.
   - Analyse trends, seasonality, and the effect of holidays and weather.
   - Evaluate models with clear metrics (MAE, RMSE) and residual plots.

4. **Scenario & Insight Generation**
   - Turn model outputs into concrete insights (e.g. impact of more cycling, exam periods, or parking changes).
   - Explore "what‑if" scenarios aligned with realistic policy questions from the client.

5. **Dashboard & Communication**
   - Develop an interactive dashboard (e.g. Streamlit) to:
     - Explore historical traffic by date, time, segment, and mode.
     - Inspect and compare forecasts with actuals.
     - Highlight key indicators and short textual explanations.
     - Provide documentation so non‑technical stakeholders can use the tool.

## Objectives & Success Measures
- **Data quality**: consistent datasets with transparent preprocessing and handling of gaps.
- **Insightfulness**: visualisations and KPIs that directly answer campus mobility questions.
- **Model usefulness**: interpretable, reasonably accurate forecasts that support planning.
- **Usability**: dashboard and docs that a non‑technical client can operate independently.

## Team
Traffic G3 – Howest CTAI:

- Hadi
- Rares
- Hamzzah

## Current Progress (5 January 2026)
Today we set up the foundation of the project and started building the data pipeline.
We created the Git repository, organised the folder structure, and pushed the initial project files so the whole team can collaborate more easily.
We connected to the Telraam API, downloaded the first batches of traffic data for our selected streets, and saved them in structured files for further analysis.
We also updated the scripts to use the correct Telraam start date and refined the README so it clearly explains the project goals and trajectory.
