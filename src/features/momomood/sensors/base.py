import sys

sys.path.append("../../../")

import niimpy
import pandas as pd
from dataclasses import dataclass
import numpy as np


@dataclass
class BaseProcessor:

    """
    BaseProcessor is the base class for all sensor processing classes. It provides a structured
    way to handle sensor data processing with support for different frequencies of data
    aggregation and summarization.

    Attributes:
        path (str): The file system path where sensor data files are located.
        table (str): The name of the database table to process.
        group (str): The name of the data grouping to apply, typically based on sensor ID or location.
        data (pd.DataFrame): The data frame containing the sensor data. Defaults to an empty DataFrame.
        frequency (str): Defines the frequency for data aggregation and summarization. It determines
                         how the sensor data is processed and transformed. The possible values are:
            - '4epochs': Divides each day into four time periods (epochs). Each epoch represents
                         a specific part of the day:
                * Night: 00:00 - 05:59
                * Morning: 06:00 - 11:59
                * Afternoon: 12:00 - 17:59
                * Evening: 18:00 - 23:59
                         This is useful for analyzing patterns based on time of day.
            - '7ds': Aggregates data from the past 7 days (one week) from the current date.
            - '14ds': Aggregates data from the past 14 days (two weeks) from the current date.

    """

    sensor_name: str
    path: str
    table: str
    group: str
    frequency: str
    data: pd.DataFrame = pd.DataFrame()

    # Optional var
    batt_path: str = ""
    batt_data: pd.DataFrame = pd.DataFrame()

    def __post_init__(self) -> None:
        self.data = niimpy.read_sqlite(
            self.path, self.table, tz="Europe/Helsinki", add_group=self.group
        )

    def extract_features(self) -> pd.DataFrame:
        """
        Extract features based on the specified frequency.
            pd.DataFrame: A DataFrame containing the extracted features.

        Raises:
            NotImplementedError: This is a placeholder method and should be implemented in child classes.
        """
        raise NotImplementedError("This method should be implemented by child classes.")

    def drop_duplicates_and_sort(self, data: pd.DataFrame) -> pd.DataFrame:
        data.sort_values(by=["user", "datetime"], inplace=True)
        data = data.drop_duplicates(["user", "datetime"])
        return data

    def remove_first_last_day(self, data: pd.DataFrame):
        """
        Remove first and last day of data to avoid incomplete data collection
        """
        grouped = data.groupby(["user", "device", "group"])
        if len(grouped) <= 1:  # If there's only one day of data for the user, remove it
            return pd.DataFrame()
        else:
            res = (
                grouped.apply(
                    lambda x: x[
                        (x.index.date > x.index.min().date())
                        & (x.index.date < x.index.max().date())
                    ]
                )
                .reset_index(drop=True)
                .set_index("datetime")
            )

            return res

    def remove_timezone_info(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.tz_localize(None)
        return df

    def add_group(self, df, group):
        df["group"] = group
        return df

    # Roll over past n days and sum up values
    def roll(self, df, groupby, days):
        # Sort by date first
        df = df.sort_values(["user", "date"])

        df.set_index("date", inplace=True)
        df = (
            df.groupby(groupby)
            .rolling(days)
            .agg(["sum", "min", "max", "mean", "std"])
            .reset_index()
        )

        return df

    def flatten_columns(self, df):
        df.columns = [":".join(col).strip() for col in df.columns.values]
        return df

    def rename_feature_columns(self, df):
        """
        Rename columns from time indicators to parts of the day.

        Parameters:
        - df: pandas.DataFrame with columns to rename.

        Returns:
        - DataFrame with renamed columns.
        """
        # Mapping of time indicators to parts of the day
        segments = {
            ":00": ":night",
            ":06": ":morning",
            ":12": ":afternoon",
            ":18": ":evening",
        }

        # Rename columns based on the mapping
        for time_indicator, segment in segments.items():
            df.columns = [col.replace(time_indicator, segment) for col in df.columns]

        # Append with sensor name
        df.columns = [f"{self.sensor_name}:{col}" for col in df.columns]

        # Append suffix to indicate aggregation freq
        if self.frequency != "4epochs":
            df.columns = [f"{col}:{self.frequency}" for col in df.columns]

        return df

    def normalize_segments(self, df, cols):
        """
        Normalizes specified segment columns within a DataFrame so that the sum of segments equals 1 for each row.

        Parameters:
        - df (pandas.DataFrame): The DataFrame containing the data to be normalized.
        - cols (list of str): A list of base column names to be normalized across specified segments.

        Returns:
        - pandas.DataFrame: The DataFrame with added normalized segment columns and sum columns for each of the base columns.
        """

        # Define the time segments to be normalized
        segments = [":night", ":morning", ":afternoon", ":evening"]

        # Loop through each base column specified in 'cols'
        for col in cols:
            # Create a new column name for storing the sum of segments
            sum_col = f"{col}:sum"

            # Ok, this code is dirty but I'll let it be
            if self.frequency != "4epochs":
                # Generate the full column names for each segment
                segment_cols = [
                    f"{col}{segment}:{self.frequency}" for segment in segments
                ]
                segment_df = (
                    df[segment_cols].xs("sum", axis=1, level=1, drop_level=False).copy()
                )
            else:
                segment_cols = [f"{col}{segment}" for segment in segments]
                segment_df = df[segment_cols].copy()

            # Calculate the sum of segment values for each row and store in the new column
            df[sum_col] = segment_df.sum(axis=1)

            # Generate column names for the normalized values
            segment_cols_norm = [f"{col}:norm" for col in segment_cols]

            # Normalize each segment value by dividing by the sum and store in new normalized columns
            df[segment_cols_norm] = segment_df.div(df[sum_col], axis=0)

            # Replace resulting NaN values with 0
            df[segment_cols_norm] = df[segment_cols_norm].fillna(0)
        return df
