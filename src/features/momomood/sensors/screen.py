from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.screen as screen
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/momo/"

import os

path = os.path.abspath(niimpy.__file__)
print(path)


@dataclass
class ScreenProcessor(BaseProcessor):
    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.batt_data = niimpy.read_sqlite(
            self.batt_path,
            table="awarebattery",
            tz="Europe/Helsinki",
            add_group=self.group,
        )

    def extract_features(self) -> pd.DataFrame:
        prefixes = [
            "screen:screen_use_durationtotal",
            "screen:screen_off_durationtotal",
            "screen:screen_on_durationtotal",
            "screen:screen_on_count",
            "screen:screen_off_count",
            "screen:screen_use_count",
        ]

        # Agg daily events into 6H bins
        rule = "6H"

        wrapper_features = {
            screen.screen_duration: {
                "screen_column_name": "screen_status",
                "resample_args": {"rule": rule},
            },
            screen.screen_count: {
                "screen_column_name": "screen_status",
                "resample_args": {"rule": rule},
            },
        }

        batt_data = (
            self.batt_data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
        )

        df = (
            self.data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(
                screen.extract_features_screen,
                batt_data,
                features=wrapper_features,
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.add_group, self.group)  # re-add user group
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

        df["hour"] = df.index.strftime("%H")
        df["date"] = df.index.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date", "device", "group"],
            columns="hour",
            values=[
                "screen_use_durationtotal",
                "screen_off_durationtotal",
                "screen_on_durationtotal",
                "screen_on_count",
                "screen_off_count",
                "screen_use_count",
            ],
            fill_value=0,
        )

        return pivoted_df
