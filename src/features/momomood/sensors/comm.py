from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.communication as comm
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/"


@dataclass
class CallProcessor(BaseProcessor):
    
    @save_output_with_freq(DATA_PATH + f"calls", "csv")
    def extract_features(self) -> pd.DataFrame:
        if self.frequency == "4epochs":
            rule = "6H"
        else:
            rule = "1D"

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
            .reset_index()
            .pipe(self.add_group, self.group)
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .reset_index()
        )

        # Slice the dataframe based on frequency
        if self.frequency == '2wks':
            df = df.pipe(self.roll, groupby=['user', 'group'], days=14)
        
        return df

    def pivot(self, df):
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date", "group"],
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

    @save_output_with_freq(DATA_PATH + "sms", "csv")
    def extract_features(self, time_bin="15T") -> pd.DataFrame:
        wrapper_features = {comm.sms_count: {"resample_args": {"rule": time_bin}}}

        df = (
            self.data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(
                comm.extract_features_comms, features=wrapper_features
            )  # call niimpy to extract features with pre-defined time bin
            .reset_index()
            .pipe(self.add_group, self.group)
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .reset_index()
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

        return pivoted_df

