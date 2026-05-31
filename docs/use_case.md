# Use Case

## Dataset

This project uses the Kaggle Bike Sharing dataset:

```text
lakshmi25npathi/bike-sharing-dataset
```

Source files:

```text
hour.csv
day.csv
```

The dataset contains historical bike rental records with calendar, weather, and demand fields.

Examples:

* date and hour
* season
* holiday and working day indicators
* weather situation
* temperature
* humidity
* windspeed
* casual rentals
* registered rentals
* total rentals

---

## Analytics use case

The use case is:

**Prepare analytics-ready bike rental data to support demand analysis, operations planning, and service optimization for a bike-sharing provider.**

The pipeline supports questions such as:

* At which hours is rental demand highest?
* How does demand differ between weekdays and weekends?
* How does weather affect bike usage?
* How do casual and registered users differ in behavior?
* Which periods require better bike availability and redistribution planning?

---

## User persona

**Elena Müller — Operations Analyst**

Elena works at a city bike-sharing company. She monitors usage trends and supports operational planning decisions. She needs reliable prepared data to understand demand peaks, weather effects, and rider behavior.

She is comfortable with SQL and dashboards, but she does not want to manually download, clean, and reshape CSV files for every analysis.

---

## Why the user needs a data pipeline

Without a pipeline:

* source files must be downloaded manually
* cleaning and preparation would be repeated for every analysis
* derived fields could be calculated inconsistently
* data refreshes would be harder to reproduce
* analytics outputs would be slower and less reliable

The pipeline solves this by:

* ingesting the dataset in batch mode
* storing raw data locally and in the cloud
* applying consistent transformations
* creating analytics-ready tables
* producing reusable summary tables
* orchestrating repeatable runs with Airflow

---

## Storage and serving layer

The local pipeline serves processed data in PostgreSQL for local inspection and reproducibility.

The cloud pipeline serves processed data in BigQuery for scalable analytics.

This means the end user can query prepared data instead of raw CSV files.

---

## Transformation logic

The transformation creates fields that directly support the use case:

```text
event_date
event_timestamp
hour_of_day
day_name
month_name
is_weekend
weather_situation
weather_situation_label
humidity
total_rentals
casual_share
registered_share
```

It also creates summary tables for:

* average rentals by hour
* weekday vs. weekend demand
* demand by weather situation
* daily rental trends
* monthly rental trends

---

## Why the transformation is necessary

The raw dataset is useful, but not analysis-ready.

The transformation is necessary because:

* raw date and hour fields need to become usable date and timestamp fields
* encoded weather fields need readable labels
* weekend and time-based fields are needed for demand analysis
* casual and registered user shares support rider behavior analysis
* repeated business questions need reusable summary tables

---

## How the transformation supports the use case

The transformed data helps Elena:

* find hourly demand peaks
* compare weekday and weekend demand
* measure the effect of weather on rentals
* compare casual and registered user behavior
* prepare dashboard queries and summary reports
* support planning around bike availability and redistribution

---

## Partitioning and clustering rationale

In BigQuery, the main analytics tables are optimized for the expected questions.

`bike_hour_analytics` is partitioned by date and clustered by:

```text
hour_of_day
is_weekend
weather_situation
```

This supports queries about hourly demand, weekend behavior, and weather effects.

`bike_day_analytics` is partitioned by date and clustered by:

```text
is_weekend
weather_situation
```

This supports daily trend and weather-based analysis.
