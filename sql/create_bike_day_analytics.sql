CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.bike_day_analytics`
PARTITION BY event_date
CLUSTER BY is_weekend, weather_situation
AS
SELECT
    *,
    CAST(dteday AS DATE) AS event_date,

    2011 + CAST(yr AS INT64) AS year,
    CAST(mnth AS INT64) AS month,

    FORMAT_DATE('%A', CAST(dteday AS DATE)) AS day_name,
    FORMAT_DATE('%B', CAST(dteday AS DATE)) AS month_name,

    CASE
        WHEN CAST(weekday AS INT64) IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS is_weekend,

    CAST(weathersit AS INT64) AS weather_situation,

    CASE
        WHEN CAST(weathersit AS INT64) = 1 THEN 'Clear/Partly cloudy'
        WHEN CAST(weathersit AS INT64) = 2 THEN 'Mist/Cloudy'
        WHEN CAST(weathersit AS INT64) = 3 THEN 'Light rain/snow'
        WHEN CAST(weathersit AS INT64) = 4 THEN 'Heavy rain/snow'
        ELSE 'Unknown'
    END AS weather_situation_label,

    CAST(hum AS FLOAT64) AS humidity,

    CAST(cnt AS INT64) AS total_rentals,

    COALESCE(
        SAFE_DIVIDE(CAST(casual AS FLOAT64), NULLIF(CAST(cnt AS FLOAT64), 0)),
        0
    ) AS casual_share,

    COALESCE(
        SAFE_DIVIDE(CAST(registered AS FLOAT64), NULLIF(CAST(cnt AS FLOAT64), 0)),
        0
    ) AS registered_share

FROM `{project_id}.{dataset_id}.bike_day_raw`;