from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.application as app
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/momo/"

import warnings

warnings.filterwarnings("ignore")


@dataclass
class EigenbehavProcessor:
    path: str
    table: str
    group: str
    rule: str
    data: pd.DataFrame = pd.DataFrame()

    # Optional var
    batt_path: str = ""
    batt_data: pd.DataFrame = pd.DataFrame()
    screen_path: str = ""
    screen_data: pd.DataFrame = pd.DataFrame()

    def __post_init__(self, *args, **kwargs):
        self.data = niimpy.read_sqlite(
            self.path, self.table, tz="Europe/Helsinki", add_group=self.group
        )

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

    def drop_duplicates_and_sort(self, data: pd.DataFrame) -> pd.DataFrame:
        data.sort_values(by=["user", "datetime"], inplace=True)
        data = data.drop_duplicates(["user", "datetime"])
        return data

    def remove_first_last_day(self, df):
        # Function to filter out the first and last day for each group
        def filter_days(group):
            # Determine the first and last day
            first_day = group.index.min().floor("D")
            last_day = group.index.max().floor("D")

            # Exclude rows from the first and last day
            return group[
                (group.index.floor("D") > first_day)
                & (group.index.floor("D") < last_day)
            ]

        # Group by 'user' and 'device' and apply the filter_days function
        return df.groupby(["user", "device", "group"], group_keys=False).apply(
            filter_days
        )

    def add_group(self, df, group):
        group_dict = {
            "mmm-bd": "bd",
            "mmm-mdd": "mdd",
            "mmm-bpd": "bpd",
            "mmm-control": "control",
        }
        df["group"] = group_dict[group]
        return df

    def pivot(self, df):
        """
        Pivot dataframe so that features are spread across columns
        Example: screen_use_00, screen_use_01, ..., screen_use_23
        """

        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)

        if self.rule == "5T":
            df["hour"] = df["datetime"].dt.strftime("%H%M")
            df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")

            # Pivot the table
            pivoted_df = df.pivot_table(
                index=["user", "date", "group"],
                columns=["app_group", "hour"],
                values=["count", "duration"],
                fill_value=0,
            )

        elif self.rule == "1H":
            df["hour"] = df["datetime"].dt.strftime("%H")
            df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")

            # Pivot the table
            pivoted_df = df.pivot_table(
                index=["user", "date", "group"],
                columns=["app_group", "hour"],
                values=["count", "duration"],
                fill_value=0,
            )

        return pivoted_df

    def flatten_columns(self, df):
        """
        Flatten columns if they are 2-level
        """

        df.columns = [":".join(col).strip() for col in df.columns.values]

        return df

    def extract_features(self) -> pd.DataFrame:
        features = {
            app.app_count: {
                "app_column_name": "application_name",
                "screen_column_name": "screen_status",
                "resample_args": {"rule": self.rule},
            },
            app.app_duration: {
                "app_column_name": "application_name",
                "screen_column_name": "screen_status",
                "resample_args": {"rule": self.rule},
            },
        }

        self.batt_data = self.batt_data.pipe(self.remove_first_last_day).pipe(
            self.remove_timezone_info
        )

        self.screen_data = self.screen_data.pipe(self.remove_first_last_day).pipe(
            self.remove_timezone_info
        )

        self.data = self.data.pipe(self.remove_first_last_day).pipe(
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
            .reset_index()
            .pipe(self.add_group, self.group)
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .reset_index()
        )

        return df
