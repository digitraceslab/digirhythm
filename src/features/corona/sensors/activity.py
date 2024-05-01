from .base import BaseCoronaProcessor
from dataclasses import dataclass
import pandas as pd
from ....decorators import save_output_with_freq

DATA_PATH = "data/interim/corona/"


@dataclass
class ActivityProcessor(BaseCoronaProcessor):
    # proper name after
    def set_datetime_index(self, df):
        df["datetime"] = df["date"] + " " + df["time"]
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Set 'datetime' as the index
        df = df.set_index("datetime")
        return df

    def resample(self, df, rule):
        # Group by 'subject_id' and then resample by 6-hour intervals, summing the steps
        resampled_df = (
            df.groupby(["subject_id", "date"])
            .resample("6h")[["steps", "stepsx1000"]]
            .sum()
            .reset_index()
        )

        return resampled_df

    def rescale_steps(self, df):
        df["stepsx1000"] = df["steps"] / 1000
        return df

    def filter_empty_step(self, df):
        print(df)
        return df[df["steps"] > 0]

    def extract_features(self) -> pd.DataFrame:
        # Agg daily events into 6H bins
        rule = "6H"

        df = (
            self.data.pipe(
                self.drop_duplicates_and_sort, by=["subject_id", "date", "time"]
            )
            .pipe(self.remove_first_last_day)
            .pipe(self.set_datetime_index)
            .pipe(self.filter_empty_step)
            .pipe(self.rescale_steps)
            .pipe(self.resample, rule)
            .pipe(self.pivot)
            .pipe(self.flatten_columns)
            .pipe(self.rename_feature_columns)
            .reset_index()
            .pipe(self.roll)
            .pipe(self.normalize_segments, cols=["steps", "stepsx1000"])
            .pipe(
                self.normalize_within_user, cols=["stepsx1000:total", "steps:total"]
            )  # normalize within-user features
            .pipe(
                self.normalize_between_user, cols=["stepsx1000:total", "steps:total"]
            )  # normalize between-user features
            .reset_index()
        )

        return df

    def pivot(self, df):
        df["hour"] = pd.to_datetime(df["datetime"]).dt.strftime("%H")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["subject_id", "date"],
            columns="hour",
            values=["steps", "stepsx1000"],
            fill_value=0,
        )

        return pivoted_df
