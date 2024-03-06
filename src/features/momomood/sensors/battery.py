from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.battery as battery
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/momo/"


@dataclass
class BatteryProcessor(BaseProcessor):
    def extract_features(self) -> pd.DataFrame:
        # Agg daily events into 6H bins
        rule = "6H"

        wrapper_features = {
            battery.battery_occurrences: {"rule": rule},
            battery.battery_median_level: {"rule": rule},
            battery.battery_mean_level: {"rule": rule},
            battery.battery_std_level: {"rule": rule},
        }

        # self.data.index.name = 'datetime'
        self.data = self.data.sort_index()
        df = (
            self.data.pipe(
                battery.extract_features_battery, features=wrapper_features
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.add_group, self.group)
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .pipe(self.rename_feature_columns)
            .reset_index()
        )

        # Roll the dataframe based on frequency
        if self.frequency == "14ds":
            df = df.pipe(self.roll, groupby=["user", "group"], days=14).pipe(
                self.flatten_columns
            )
        elif self.frequency == "7ds":
            df = df.pipe(self.roll, groupby=["user", "group"], days=7).pipe(
                self.flatten_columns
            )

        return df

    def pivot(self, df):
        """
        Pivot dataframe so that features are spread across columns
        Example: screen_use_00, screen_use_01, ..., screen_use_23
        """
        df["hour"] = df.index.strftime("%H")
        df["date"] = df.index.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date", "group"],
            columns="hour",
            values=[
                "occurrences",
                "battery_std_level",
                "battery_mean_level",
                "battery_median_level",
            ],
            fill_value=0,
        )

        return pivoted_df
