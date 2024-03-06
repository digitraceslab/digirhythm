from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.location as location
from ....decorators import save_output_with_freq


@dataclass
class LocationProcessor(BaseProcessor):
    def extract_features(self) -> pd.DataFrame:
        rule = "6H"

        # Preprocess pipeline
        df = (
            self.data.pipe(
                self.converter, types={"accuracy": float}
            )  # Convert column type
            .pipe(self.remove_first_last_day)  # Remove first and last day for each user
            .pipe(
                self.remove_timezone_info
            )  # Remove timezone-specific, return naive-timezone timestamp
            .pipe(
                location.filter_location,
                remove_disabled=True,
                remove_network=True,
                remove_zeros=True,
            )  # Filter disabled and network location
        )

        # Resample into 5-min bins
        resampled_df = (
            (
                df.groupby(["user", "device", "group"])[
                    ["double_latitude", "double_longitude", "double_speed"]
                ]
                .resample("5T")
                .median()
                .reset_index()
            )
            .set_index("datetime")
            .dropna()
        )

        config = {}
        config["resample_args"] = {"rule": rule}

        df = (
            resampled_df.pipe(
                location.extract_features_location,
                features={
                    location.location_distance_features: config,
                    location.location_significant_place_features: config,
                },
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
            df = df.pipe(self.roll, groupby=["user", "group"], days=14).pipe(self.flatten_columns)
        elif self.frequency == "7ds":
            df = df.pipe(self.roll, groupby=["user", "group"], days=7).pipe(self.flatten_columns)

        return df

    def pivot(self, df):
        """
        Pivot dataframe so that features are spread across columns
        Example: screen_use_00, screen_use_01, ..., screen_use_23
        """
        print(df.columns)
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date", "group"],
            columns="hour",
            values=[
                "dist_total",
                "n_bins",
                "speed_average",
                "speed_variance",
                "speed_max",
                "variance",
                "log_variance",
                "n_sps",
                "n_static",
                "n_moving",
                "n_rare",
                "n_home",
                "max_dist_home",
                "n_transitions",
                "n_top1",
                "n_top2",
                "n_top3",
                "n_top4",
                "n_top5",
                "entropy",
                "normalized_entropy",
            ],
            fill_value=0,
        )

        return pivoted_df

    def converter(self, df, types):
        """
        Convert column data types
        """
        df = df.astype(types)
        return df

    def filter_locations(
        self, df, remove_disabled=False, remove_network=True, remove_zeros=True
    ):
        return location.filter_location(
            df,
            remove_disabled=remove_disabled,
            remove_network=remove_network,
            remove_zeros=remove_zeros,
        )
