from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.screen as screen
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/momo/"


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

    @save_output_with_freq(DATA_PATH + "screen", "csv")
    def extract_features(self) -> pd.DataFrame:
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

        # Normalize segemented features
        df = df.pipe(
            self.normalize_segments,
            cols=[
                "screen:screen_use_durationtotal",
                "screen:screen_off_durationtotal",
                "screen:screen_on_durationtotal",
                "screen:screen_on_count",
                "screen:screen_off_count",
                "screen:screen_use_count",
            ],
        )
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
