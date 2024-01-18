from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.communication as comm

@dataclass
class CallProcessor(BaseProcessor):
    def extract_features(self, time_bin="15T") -> pd.DataFrame:
        wrapper_features = {
            comm.call_count: {
                "communication_column_name": "call_duration",
                "resample_args": {"rule": time_bin},
            },
            comm.call_duration_total: {
                "communication_column_name": "call_duration",
                "resample_args": {"rule": time_bin},
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
            .reset_index()
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
        )

        return df

    def pivot(self, df):
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date"],
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

    def flatten_columns(self, df):
        df.columns = ["_".join(col).strip() for col in df.columns.values]
        return df


class SmsProcessor(BaseProcessor):
    def extract_features(self, time_bin="15T") -> pd.DataFrame:
        wrapper_features = {comm.sms_count: {"resample_args": {"rule": time_bin}}}

        df = (
            self.data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(
                comm.extract_features_comms, features=wrapper_features
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.add_group, self.group)
            .reset_index()
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
        )

        return df

    def pivot(self, df):
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date"],
            columns="hour",
            values=["incoming_count", "outgoing_count"],
            fill_value=0,
        )
        print(pivoted_df)
        return pivoted_df

    def flatten_columns(self, df):
        df.columns = ["_".join(col).strip() for col in df.columns.values]
        return df
