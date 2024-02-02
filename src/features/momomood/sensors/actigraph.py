from .base import BaseProcessor
from dataclasses import dataclass
import niimpy
import pandas as pd
import niimpy.preprocessing.screen as screen
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/"


@dataclass
class ActigraphProcessor(BaseProcessor):
    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)

    @save_output_with_freq(DATA_PATH + "actigraph_binned.csv", "csv")
    def extract_features(self, time_bin="1H") -> pd.DataFrame:
        """
        time_bin: resampling rate
        """

        df = (
            self.data.pipe(self.drop_duplicates_and_sort)
            .pipe(self.remove_first_last_day)
            .pipe(self.remove_timezone_info)
            .pipe(
                lambda x: x.groupby("user").resample(time_bin).agg({"activity": "sum"})
            )
            .reset_index()
            .pipe(self.add_group, self.group)
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .reset_index()
        )

        sleep_df = ()

        return df

    def pivot(self, df):
        """
        Pivot dataframe so that features are spread across columns
        Example: screen_use_00, screen_use_01, ..., screen_use_23
        """

        print(df)
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")
        df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["user", "date", "group"],
            columns="hour",
            values=[
                "activity",
            ],
            fill_value=0,
        )

        return pivoted_df

    def flatten_columns(self, df):
        print(df)
        df.columns = ["_".join(col).strip() for col in df.columns.values]
        return df
