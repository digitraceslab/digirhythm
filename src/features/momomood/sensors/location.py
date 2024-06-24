from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.location as location
from ....decorators import save_output_with_freq
import inspect


@dataclass
class LocationProcessor(BaseProcessor):

    def rename_feature_columns(self, df):
        df.columns = [
            (
                f"{self.sensor_name}:{col}"
                if col not in ["user", "date", "device", "group"]
                else col
            )
            for col in df.columns
        ]

        return df

    def rename_features_columns(self, df, prefixes):
        """
        Rename columns from time indicators to parts of the day.

        Parameters:
        - df: pandas.DataFrame with columns to rename.

        Returns:
        - DataFrame with renamed columns.
        """

        # Append with sensor name

        df.columns = [
            (
                f"{self.sensor_name}:{col}{self.col_suffix}"
                if col not in ["user", "device", "group", "date"]
                else col
            )
            for col in df.columns
        ]

        return df

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

    def resample(self, df):

        # Agg to 5 mins
        agg_data = (
            df.pipe(self.converter, types={"accuracy": float})  # Convert column type
            .pipe(
                location.filter_location,
                remove_disabled=True,
                remove_network=False,
                remove_zeros=True,
            )  # Filter disabled and network location
            .groupby(self.groupby_cols)
            .resample("5T")
            .median(numeric_only=True)
            .reset_index()
        )

        return agg_data

    def extract_features(self) -> pd.DataFrame:
        rule = "1D"

        # Agg to 5 mins
        agg_data = self.resample(self.data)

        # Rename
        agg_data.rename(columns={"level_2": "datetime"}, inplace=True)

        # Set datetime index
        # agg_data.set_index('datetime', inplace=True)

        config = {}
        config["resample_args"] = {"rule": rule}

        prefixes = [
            "location:dist_total",
            "location:n_bins",
            "location:speed_average",
            "location:speed_variance",
            "location:speed_max",
            "location:variance",
            "location:log_variance",
            "location:n_sps",
            "location:n_static",
            "location:n_moving",
            "location:n_rare",
            "location:n_home",
            "location:max_dist_home",
            "location:n_transitions",
            "location:n_top1",
            "location:n_top2",
            "location:n_top3",
            "location:n_top4",
            "location:n_top5",
            "location:entropy",
            "location:normalized_entropy",
        ]

        df = (
            agg_data.pipe(self.drop_duplicates_and_sort)
            .set_index("datetime")
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .dropna(subset=["double_longitude", "double_latitude"])
            .pipe(
                location.extract_features_location,
                features={
                    location.location_distance_features: config,
                    location.location_significant_place_features: config,
                },
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(
                lambda x: x.assign(location_proportion_home=x["n_home"] / x["n_static"])
            )
            .pipe(self.add_group, self.group)  # re-add user group
            .pipe(self.rename_features_columns, prefixes)  # re-add user group
            .reset_index()
            .pipe(
                lambda df: df.rename(columns={"datetime": "date"})
            )  # add formatted date
            .pipe(self.roll)
            .pipe(
                self.normalize_within_user, prefixes=prefixes
            )  # normalize within-user features
            .pipe(
                self.normalize_between_user, prefixes=prefixes
            )  # normalize between-user features
        )

        return df

    def pivot(self, df):
        """
        Pivot dataframe so that features are spread across columns
        Example: screen_use_00, screen_use_01, ..., screen_use_23
        """

        df["date"] = pd.to_datetime(df.index).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "device", "group"],
            columns="date",
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
