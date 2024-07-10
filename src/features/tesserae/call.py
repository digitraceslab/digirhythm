from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.communication as comm

DATA_PATH = "data/interim/momo/"


@dataclass
class CallProcessor(BaseProcessor):

    def compute_total_call(self, df) -> pd.DataFrame:
        print(df.columns)
        df['total_count'] = df['outgoing_count'] + df['incoming_count']
        df['total_duration'] = df['outgoing_duration_total'] + df['incoming_duration_total']
        return df
        
    def extract_features(self) -> pd.DataFrame:
        prefixes = [
            "call:incoming_count",
            "call:outgoing_count",
            "call:incoming_duration_total",
            "call:outgoing_duration_total",
            "call:total_count",
            "call:total_duration"
        ]

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
            self.data.pipe(self.set_datetime_index)
            .pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(
                comm.extract_features_comms, features=wrapper_features
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.compute_total_call)
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

        df["datetime"] = df["index"]
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
                "total_count",
                "total_duration"
            ],
            fill_value=0,
        )

        return pivoted_df
