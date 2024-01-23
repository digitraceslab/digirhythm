from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.location as location
from ....decorators import save_output

DATA_PATH = "data/interim/"


@dataclass
class LocationProcessor(BaseProcessor):
    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.batt_data = niimpy.read_sqlite(
            self.batt_path,
            table="awarebattery",
            tz="Europe/Helsinki",
            add_group=self.group,
        )

    @save_output(DATA_PATH + "location_binned.csv", "csv")
    def extract_features(self, time_bin="15T") -> pd.DataFrame:
        """
        time_bin: resampling rate
        """
        
        config["resample_args"] = {"rule": "1D"}
        # extract only distance related features
        features = {
            location.location_distance_features: {"rule": "1D"}, # arguments,
            location.location_significant_place_features: {"rule": "1D"},
            location.location_number_of_significant_places: {"rule": "1D"}
        }
        
        df = (
            self.data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(
                location.extract_features_location,
                features=wrapper_features,
            )  # call niimpy to extract features with pre-defined time bin
            .pipe(self.add_group, self.group)
            .reset_index()
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
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

    def flatten_columns(self, df):
        df.columns = ["_".join(col).strip() for col in df.columns.values]
        return df
    
    def filter_locations(df, remove_disabled=False, remove_network=True, remove_zeros=True):
        return location.filter_location(
            df,
            remove_disabled=remove_disabled,
            remove_network=remove_network,
            remove_zeros=remove_zeros,
        )
