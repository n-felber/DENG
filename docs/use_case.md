# Use Case

## Dataset

This project uses the **Bike Sharing Dataset** from Kaggle:

- Dataset: `lakshmi25npathi/bike-sharing-dataset`
- Source files:
  - `hour.csv`
  - `day.csv`

The dataset contains historical bike rental records together with calendar and weather-related attributes. It includes variables such as:
- date and hour
- season
- year and month
- holiday / working day indicators
- weather situation
- temperature
- humidity
- windspeed
- casual user count
- registered user count
- total rental count

This combination of operational and contextual variables makes the dataset well suited for demand analytics and pipeline-based processing.

---

## Analytics Use Case

The selected use case is:

**Prepare analytics-ready bike rental data to support demand analysis, operations planning, and service optimization for a bike-sharing provider.**

The pipeline supports questions such as:
- At which hours is rental demand highest?
- How does demand differ between weekdays and weekends?
- How strongly does weather affect bike usage?
- How do casual and registered users differ in behavior?
- Which periods require better bike availability and redistribution planning?

The goal of the project is to transform raw source data into a reproducible, queryable, and analysis-ready dataset stored in PostgreSQL.

---

## User Persona

### Elena Müller — Operations Analyst

Elena Müller is an operations analyst at a city bike-sharing company. Her role is to monitor usage trends and support operational planning decisions. She works closely with operations managers and business stakeholders to improve bike availability, identify demand peaks, and understand how external factors such as weather influence rentals.

Elena is comfortable working with SQL, dashboards, and summary reports, but she does not want to repeatedly clean raw CSV files manually. She needs reliable, structured data that is consistently prepared and easy to query.

---

## Why This User Needs a Data Pipeline

Elena needs a data pipeline because raw source files are not sufficient for repeatable and efficient analysis.

Without a pipeline:
- source files must be downloaded and loaded manually
- cleaning and preparation steps would need to be repeated for every analysis
- derived fields would be calculated inconsistently
- historical data refreshes would be harder to manage
- downstream analytics would be slower and more error-prone

The data pipeline solves this by:
- ingesting the source data in batch mode
- loading it into a local PostgreSQL database
- applying consistent transformation logic
- producing analytics-ready tables
- enabling repeatable scheduled runs through workflow orchestration

This gives Elena a stable data foundation for analysis, reporting, and future extensions such as dashboards or forecasting models.

---

## Problem the User Is Trying to Solve

Elena’s main goal is to understand **bike rental demand patterns** so that the company can make better operational decisions.

The business problems she is trying to solve include:

### 1. Demand visibility
She needs to identify when bike demand is highest and lowest across hours, weekdays, seasons, and weather conditions.

### 2. Operational planning
She needs to help the business decide when more bikes should be available, when redistribution is needed, and when maintenance windows are least disruptive.

### 3. Rider behavior analysis
She wants to compare casual and registered users to understand how customer groups behave differently and how those differences affect planning.

### 4. Reliable analytics inputs
She needs a repeatable and trustworthy dataset in a queryable storage system, rather than raw files that must be reprocessed manually.

The broader question behind the use case is:

**How can historical rental and weather data be transformed into reliable operational insight for a bike-sharing service?**

---

## How the User Uses the Processed Data

After the pipeline runs, Elena uses the processed data in PostgreSQL to:
- analyze hourly and daily rental demand
- compare weekends, weekdays, holidays, and working days
- measure the effect of weather conditions on usage
- identify high-demand and low-demand periods
- prepare dashboard queries and summary reports
- support planning decisions around bike allocation and redistribution

The processed data is therefore intended for direct analytics use and also provides a foundation for future machine learning work such as demand forecasting.

---

## Why PostgreSQL Is the Right Storage Layer

PostgreSQL supports this use case because it allows the team to:
- store raw and transformed data in a structured form
- query the data efficiently with SQL
- separate ingestion from analytics consumption
- support reproducible downstream analysis
- inspect the data through pgAdmin
- build future reporting or BI layers on top of stable tables

For Elena, this is much more practical and scalable than repeatedly working with CSV files alone.

---

## Implemented Transformation Logic

The transformation logic in this project is designed specifically to support Elena’s analytics needs.

After ingesting the raw hourly and daily bike-sharing data, the pipeline creates an analytics-ready transformed layer that improves usability for operational analysis.

The transformation includes:
- column standardization for clearer downstream querying
- creation of a proper date or timestamp structure from source time fields
- derived calendar features such as:
  - `is_weekend`
  - `day_name`
  - `month_name`
- demand-oriented derived metrics such as:
  - `total_rentals`
  - `casual_share`
  - `registered_share`
- aggregated summary data for recurring analytical questions, such as:
  - average rentals by hour of day
  - demand by weekday vs. weekend
  - demand by weather situation
  - daily and monthly rental trends

This transformation layer directly supports the user’s business questions and reduces repeated manual preparation work.

---

## Why the Transformation Is Necessary

The transformation is necessary because the raw dataset is not yet optimized for repeated operational analysis.

The raw source data:
- contains fields that are useful but not yet shaped for stakeholder-friendly querying
- requires repeated interpretation of encoded or split time fields
- does not directly provide the summary metrics most relevant for planning
- is less convenient for recurring SQL analysis and dashboarding

The transformation solves this by converting raw data into a consistent analytics layer with meaningful derived features and summary outputs.

---

## How the Transformation Supports the Use Case

The transformation directly supports Elena’s work in several ways:

- **Time-based features** make it easy to detect demand peaks by hour, weekday, and month.
- **Weekend and working-day indicators** help distinguish commuter usage from leisure usage.
- **User share metrics** make it possible to compare casual and registered rider behavior.
- **Aggregated summary tables** support frequent business questions without requiring repeated manual calculations.
- **Cleaned and standardized schema design** makes SQL analysis and dashboard development easier and more reliable.

This means the transformation is not generic. It is built specifically to support operational demand analysis in the bike-sharing domain.

---

## What Problem the Transformation Solves

The transformation addresses three key problems:

### 1. Raw data is not analysis-ready
The source data is useful, but not ideal for recurring stakeholder analysis without preparation.

### 2. Business questions require derived logic
The most relevant business questions depend on fields such as weekend flags, user shares, grouped timestamps, and demand summaries.

### 3. Reusability and consistency matter
Embedding the transformation into the pipeline ensures that every run produces the same clean and consistent analytics-ready outputs.

This reduces manual effort and improves trust in the data.

---

## Pipeline Output

The pipeline produces:
- raw source tables in PostgreSQL
- transformed analytics-ready tables in PostgreSQL
- queryable data accessible through pgAdmin
- reproducible batch runs managed through workflow orchestration

This ensures that the project is not only a data-loading script, but a complete local data pipeline that supports a real analytics stakeholder.

---

## Summary

This project serves an **operations analyst at a bike-sharing company** who needs reliable and analytics-ready rental data.

The pipeline ingests bike-sharing data in batch mode, stores it in PostgreSQL, applies transformations that support demand analysis, and makes the results available for structured querying and operational insight. The transformation logic is directly tied to the user’s needs: it helps answer questions about demand patterns, rider behavior, and weather effects, enabling better service planning and future analytical extensions.