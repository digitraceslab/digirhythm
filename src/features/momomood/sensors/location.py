from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.location as location
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/"


@dataclass
class LocationProcessor(BaseProcessor):
    @save_output_with_freq(DATA_PATH + "location_binned.csv", "csv")
    def extract_features(self, time_bin) -> pd.DataFrame:
        """
        time_bin: resampling rate
        """

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
        config["resample_args"] = {"rule": time_bin}

        df = (
            resampled_df.pipe(
                location.extract_features_location,
                features={
                    location.location_distance_features: config,
                    location.location_significant_place_features: config,
                },
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.add_group, self.group)
            .reset_index()
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
            index=["user", "date"],
            columns="hour",
            values=[
                "screen_use_durationtotal",
                "screen_off_durationtotal",
                "screen_on_durationtotal",
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
