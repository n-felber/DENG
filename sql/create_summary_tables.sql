CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.bike_hourly_demand_summary`
AS
SELECT
    hour_of_day,
    AVG(total_rentals) AS avg_total_rentals,
    SUM(total_rentals) AS total_rentals,
    COUNT(*) AS record_count
FROM `{project_id}.{dataset_id}.bike_hour_analytics`
GROUP BY hour_of_day
ORDER BY hour_of_day;


CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.bike_weekday_weekend_summary`
AS
SELECT
    is_weekend,
    CASE
        WHEN is_weekend THEN 'weekend'
        ELSE 'weekday'
    END AS day_type,
    AVG(total_rentals) AS avg_total_rentals,
    SUM(total_rentals) AS total_rentals,
    COUNT(*) AS record_count
FROM `{project_id}.{dataset_id}.bike_day_analytics`
GROUP BY is_weekend
ORDER BY is_weekend;


CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.bike_weather_demand_summary`
AS
SELECT
    weather_situation,
    weather_situation_label,
    AVG(total_rentals) AS avg_total_rentals,
    SUM(total_rentals) AS total_rentals,
    COUNT(*) AS record_count
FROM `{project_id}.{dataset_id}.bike_day_analytics`
GROUP BY weather_situation, weather_situation_label
ORDER BY weather_situation;


CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.bike_daily_trend_summary`
PARTITION BY event_date
AS
SELECT
    event_date,
    day_name,
    month,
    month_name,
    year,
    total_rentals,
    casual,
    registered
FROM `{project_id}.{dataset_id}.bike_day_analytics`;


CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.bike_monthly_trend_summary`
AS
SELECT
    year,
    month,
    month_name,
    SUM(total_rentals) AS total_rentals,
    AVG(total_rentals) AS avg_daily_rentals,
    SUM(casual) AS casual_rentals,
    SUM(registered) AS registered_rentals,
    COUNT(*) AS day_count
FROM `{project_id}.{dataset_id}.bike_day_analytics`
GROUP BY year, month, month_name
ORDER BY year, month;