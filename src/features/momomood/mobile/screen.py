import sys

sys.path.insert(0, "../../..")

from base import BaseProcessor
from dataclasses import dataclass
import niimpy 
import pandas as pd
import niimpy.preprocessing.screen as screen

@dataclass
class ScreenProcessor(BaseProcessor):

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.batt_data = niimpy.read_sqlite(self.batt_path, table='awarebattery',  tz="Europe/Helsinki", add_group=self.group)


    def extract_features(self, time_bin='15T') -> pd.DataFrame:
        '''
        time_bin: resampling rate
        '''
        wrapper_features = {
            screen.screen_duration: {
                "screen_column_name": "screen_status",
                "resample_args": {"rule": time_bin},
            },
            screen.screen_count: {
                "screen_column_name": "screen_status",
                "resample_args": {"rule": time_bin},
            },
        }

        
        df = (
            self.data
            .pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(
                screen.extract_features_screen, self.batt_data, features=wrapper_features
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.add_group, self.group)
            .reset_index()
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
        )

        return df

    def pivot(self, df):

        '''
        Pivot dataframe so that features are spread across columns
        Example: screen_use_00, screen_use_01, ..., screen_use_23
        '''
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date"],
            columns="hour",
            values=["incoming_count", "outgoing_count",
                   "incoming_duration_total", "outgoing_duration_total"],
            fill_value=0,
        )

        return pivoted_df
    
    def flatten_columns(self, df):
    
        df.columns = ['_'.join(col).strip() for col in df.columns.values]
        return df
