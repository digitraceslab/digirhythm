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

    def extract_features(self) -> pd.DataFrame:
        def _convert_timezone(df):
            df.index = df.index.tz_convert("UTC")
            df.index = df.index.tz_convert("Europe/Helsinki")
            return df

        rule = "6H"

        features = {
            app.app_count: {
                "app_column_name": "application_name",
                "screen_column_name": "screen_status",
                "resample_args": {"rule": rule},
            },
            app.app_duration: {
                "app_column_name": "application_name",
                "resample_args": {"rule": rule},
            },
        }

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
            .reset_index()
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

        # Normalize segemented features
        df = df.pipe(
            self.normalize_segments,
            cols=[""],
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
            columns=["app_group", "hour"],
            values=["count", "duration"],
            fill_value=0,
        )

        print(pivoted_df.head(10))

        return pivoted_df
