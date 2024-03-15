from .base import BaseCoronaProcessor
from dataclasses import dataclass
import pandas as pd
from ...decorators import save_output_with_freq
from datetime import datetime

DATA_PATH = "data/interim/corona/"


@dataclass
class SleepProcessor(BaseCoronaProcessor):
    def set_datetime_index(self, df):
        df["datetime"] = df["date"] + " " + df["time"]
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Set 'datetime' as the index
        df = df.set_index("datetime")
        return df

    def convert_timezone(self, df):
        # Define a function to convert datetime with error handling
        def convert_datetime(column):
            return pd.to_datetime(column, errors="coerce", utc=True).dt.tz_convert(
                "Europe/Helsinki"
            )

        # Apply the conversion function to the specified columns
        df["sleep_start_time"] = convert_datetime(df["sleep_start_time"])
        df["sleep_end_time"] = convert_datetime(df["sleep_end_time"])

        return df

    def convert_sleepwake_time(self, df):
        def convert_to_proportionate_hour(val):
            if val.hour < 15:
                return round(24 + val.hour + val.minute / 60 + val.second / 3600, 2)
            else:
                return round(val.hour + val.minute / 60 + val.second / 3600, 2)

        df["bedtime"] = df["sleep_start_time"].apply(convert_to_proportionate_hour)
        df["waketime"] = df["sleep_end_time"].apply(convert_to_proportionate_hour)

        return df

    def total_sleep_time(self, df):
        df["tst"] = round(
            df["waketime"] - df["bedtime"] - df["total_interruption_duration"] / 3600, 2
        )
        return df

    def midsleep(self, df):
        df["midsleep"] = round((df["bedtime"] + df["bedtime"] + df["tst"]) / 2, 2)
        return df

    def filter_nights(self, df):
        # Remove artifacts
        df = df[(df["tst"] > 3) & (df["tst"] < 13)]
        return df

    def retain_columns(self, df):
        cols = [
            "subject_id",
            "tst",
            "midsleep",
            "bedtime",
            "waketime",
            "date",
            "total_interruption_duration",
        ]
        df = df[cols]
        return df

    def extract_features(self) -> pd.DataFrame:
        df = (
            self.data.pipe(self.convert_timezone)
            .pipe(self.convert_sleepwake_time)
            .pipe(self.total_sleep_time)
            .pipe(self.midsleep)
            .pipe(self.filter_nights)
            .pipe(self.retain_columns)
        )

        # Roll the dataframe based on frequency
        if self.frequency == "14ds":
            df = df.pipe(self.roll, groupby=["subject_id"], days=14).pipe(
                self.flatten_columns
            )
        elif self.frequency == "7ds":
            df = df.pipe(self.roll, groupby=["subject_id"], days=7).pipe(
                self.flatten_columns
            )

        return df
