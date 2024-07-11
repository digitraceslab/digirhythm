from .base import BaseProcessor
from dataclasses import dataclass, field
import niimpy
import pandas as pd
import niimpy.preprocessing.screen as screen

import polars as pl

import os

path = os.path.abspath(niimpy.__file__)
print(path)


@dataclass
class ScreenProcessor(BaseProcessor):
    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)

    def convert_copenhagen_time(self, df) -> pd.DataFrame():

        # Convert the 'datetime' column from milliseconds to a datetime object
        df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")

        # Set timezone to UTC (assuming the timestamps are in UTC)
        df["datetime"] = df["datetime"].dt.tz_localize("UTC")

        # Convert to Copenhagen time (CET/CEST)
        df["datetime"] = df["datetime"].dt.tz_convert("Europe/Copenhagen")

        return df

    def extract_features(self) -> pd.DataFrame:

        prefixes = ["screen:screen_on_durationtotal", "screen:screen_off_durationtotal"]

        # Agg daily events into 6H bins
        rule = "6H"

        empty_batt_data = pd.DataFrame()

        wrapper_features = {
            screen.screen_duration: {
                "screen_column_name": "screen_status",
                "resample_args": {"rule": rule},
            }
        }

        def head(df):
            return df.head(1000)

        df = (
            self.data.pipe(self.convert_copenhagen_time)
            .pipe(self.set_datetime_index)
            .pipe(self.remove_first_last_day)
            .pipe(self.drop_duplicates_and_sort)
            .pipe(
                screen.extract_features_screen,
                empty_batt_data,
                features=wrapper_features,
            )  # call niimpy to extract features with pre-defined time bin
            .reset_index()
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .pipe(self.rename_segment_columns)
            .pipe(self.sum_segment, prefixes=prefixes)
            .reset_index()
            .pipe(self.roll)
            .pipe(
                self.normalize_within_user, prefixes=prefixes
            )  # normalize within-user features
            .pipe(
                self.normalize_between_user, prefixes=prefixes
            )  # normalize between-user features
            .pipe(self.normalize_segments, cols=prefixes)
        )

        return df

    def pivot(self, df):
        """
        Pivot dataframe so that features are spread across columns
        Example: screen_use_00, screen_use_01, ..., screen_use_23
        """

        print(df.head())
        df.rename(
            columns={"level_0": "device", "level_1": "user", "level_2": "datetime"},
            inplace=True,
        )

        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date"],
            columns="hour",
            values=[
                "screen_on_durationtotal",
                "screen_off_durationtotal",
            ],
            fill_value=0,
        )

        return pivoted_df
