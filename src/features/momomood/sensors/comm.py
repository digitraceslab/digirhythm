from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.communication as comm
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/momo/"


@dataclass
class CallProcessor(BaseProcessor):
    def extract_features(self) -> pd.DataFrame:
        # Agg daily events into 6H bins
        rule = "6H"

        wrapper_features = {
            comm.call_count: {
                "communication_column_name": "call_duration",
                "resample_args": {"rule": rule},
            },
            comm.call_duration_total: {
                "communication_column_name": "call_duration",
                "resample_args": {"rule": rule},
            },
        }

        df = (
            self.data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(
                comm.extract_features_comms, features=wrapper_features
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.add_group, self.group)
            .pipe(self.normalize_numerical)
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .pipe(self.rename_feature_columns)
            .reset_index()
            .pipe(self.roll)
            .pipe(
                self.normalize_segments,
                cols=[
                    "call:incoming_count",
                    "call:outgoing_count",
                    "call:incoming_duration_total",
                    "call:outgoing_duration_total",
                ],
            )
        )

        return df

    def pivot(self, df):
        df["datetime"] = df.index
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date", "group", "device"],
            columns="hour",
            values=[
                "incoming_count",
                "outgoing_count",
                "incoming_duration_total",
                "outgoing_duration_total",
            ],
            fill_value=0,
        )

        return pivoted_df


class SmsProcessor(BaseProcessor):
    #    @save_output_with_freq(DATA_PATH + "sms", "csv")
    def extract_features(self) -> pd.DataFrame:
        # Agg daily events into 6H bins
        rule = "6H"
        wrapper_features = {comm.sms_count: {"resample_args": {"rule": rule}}}

        df = (
            self.data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(
                comm.extract_features_comms, features=wrapper_features
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.add_group, self.group)
            .pipe(self.normalize_numerical)
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .pipe(self.rename_feature_columns)
            .reset_index()
            .pipe(self.roll)
            .pipe(
                self.normalize_segments,
                cols=["sms:incoming_count", "sms:outgoing_count"],
            )
        )
        return df

    def pivot(self, df):
        df["datetime"] = df.index
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date", "group", "device"],
            columns="hour",
            values=["incoming_count", "outgoing_count"],
            fill_value=0,
        )

        return pivoted_df
