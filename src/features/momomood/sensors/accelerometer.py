from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import numpy as np
import niimpy.preprocessing.battery as battery
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/momo/"


@dataclass
class AccelerometerProcessor(BaseProcessor):
    def resample_data(self, df, rule="5H", agg_func="mean"):
        """
        Resample the DataFrame based on a given rule and aggregation function.

        Parameters:
        - df: pandas DataFrame to resample.
        - rule: resampling frequency (e.g., 'D' for daily, 'M' for monthly).
        - agg_func: aggregation function to use (e.g., 'mean', 'sum').

        Returns:
        - Resampled pandas DataFrame.
        """

        return df.groupby(["user", "device", "group"]).resample(rule).apply(agg_func)

    def rename_cols(self, df):
        df.rename(
            columns={
                "double_values_0": "x",
                "double_values_1": "y",
                "double_values_2": "z",
            },
            errors="raise",
            inplace=True,
        )
        return df

    def magnitude(self, df):
        df["magnitude"] = np.sqrt(df["x"] ** 2 + df["y"] ** 2 + df["z"] ** 2)
        return df

    def extract_features(self) -> pd.DataFrame:
        # Agg daily events into 6H bins
        rule = "6H"

        # self.data.index.name = 'datetime'
        self.data = self.data.sort_index()
        df = (
            self.data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(self.rename_cols)
            .pipe(self.magnitude)
            .pipe(self.resample_data, rule, "mean")
            .reset_index()
            .pipe(self.add_group, self.group)
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .pipe(self.rename_feature_columns)
            .reset_index()
        )

        # Roll the dataframe based on frequency
        if self.frequency == "14ds":
            df = df.pipe(self.roll, groupby=["user", "group"], days=14)
        elif self.frequency == "7ds":
            df = df.pipe(self.roll, groupby=["user", "group"], days=7)

        return df

    def pivot(self, df):
        """
        Pivot dataframe so that features are spread across columns
        Example: screen_use_00, screen_use_01, ..., screen_use_23
        """
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date", "group"],
            columns="hour",
            values=["magnitude"],
            fill_value=0,
        )

        return pivoted_df
