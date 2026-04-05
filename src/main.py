import os
import time

import kagglehub
from kagglehub import KaggleDatasetAdapter
from sqlalchemy import create_engine, text


DATABASE_URL = os.environ["DATABASE_URL"]


def wait_for_db(engine, retries=10, delay=2):
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection OK")
            return
        except Exception as exc:
            print(f"Database not ready yet (attempt {attempt}/{retries}): {exc}")
            if attempt == retries:
                raise
            time.sleep(delay)


def main():
    print("--- Started Pipeline ---")

    # If you haven't authenticated yet, uncomment this once:
    # kagglehub.login()

    df_hour = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        "lakshmi25npathi/bike-sharing-dataset",
        "hour.csv",
    )

    df_day = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        "lakshmi25npathi/bike-sharing-dataset",
        "day.csv",
    )

    engine = create_engine(DATABASE_URL)
    wait_for_db(engine)

    with engine.begin() as conn:
        df_hour.to_sql(
            "bike_hour",
            con=conn,
            if_exists="replace",
            index=False,
            chunksize=1000,
            method="multi",
        )

        df_day.to_sql(
            "bike_day",
            con=conn,
            if_exists="replace",
            index=False,
            chunksize=1000,
            method="multi",
        )

    print("Loaded bike_hour:", df_hour.shape)
    print("Loaded bike_day:", df_day.shape)


if __name__ == "__main__":
    main()
