from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.application as app
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/momo/"

import warnings

warnings.filterwarnings("ignore")


@dataclass
class ApplicationProcessor(BaseProcessor):
    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.batt_data = niimpy.read_sqlite(
            self.batt_path,
            table="awarebattery",
            tz="Europe/Helsinki",
            add_group=self.group,
        )
        self.screen_data = niimpy.read_sqlite(
            self.screen_path,
            table="awarescreen",
            tz="Europe/Helsinki",
            add_group=self.group,
        )

    def remove_timezone_info(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.tz_localize(None)
        df["datetime"] = df["datetime"].dt.tz_localize(None)
        return df

    def extract_features(self) -> pd.DataFrame:
        rule = "6H"

        prefixes = [
            "application:count:news",
            "application:duration:news",
            "application:count:games",
            "application:duration:games",
            "application:count:comm",
            "application:duration:comm",
            "application:count:leisure",
            "application:duration:leisure",
            "application:count:socialmedia",
            "application:duration:socialmedia",
            "application:count:off",
            "application:duration:off",
        ]

        features = {
            app.app_count: {
                "app_column_name": "application_name",
                "screen_column_name": "screen_status",
                "resample_args": {"rule": rule},
            },
            app.app_duration: {
                "app_column_name": "application_name",
                "screen_column_name": "screen_status",
                "resample_args": {"rule": rule},
            },
        }

        self.batt_data = self.batt_data.pipe(self.remove_first_last_day).pipe(
            self.remove_timezone_info
        )

        self.screen_data = self.screen_data.pipe(self.remove_first_last_day).pipe(
            self.remove_timezone_info
        )

        df = (
            self.data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(
                app.extract_features_app,
                self.batt_data,
                self.screen_data,
                features=features,
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.add_group, self.group)
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

        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)
        df["hour"] = df["datetime"].dt.strftime("%H")
        df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date", "device", "group"],
            columns=["app_group", "hour"],
            values=["count", "duration"],
            fill_value=0,
        )

        return pivoted_df
