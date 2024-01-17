import numpy as np
import pandas as pd
from datetime import timedelta
import pytz


class CoronaProcessor:

    """
    Add customized behaviours here as well
    """

    def __init__(self, activity_df, sleep_df):
        self.activity_df = activity_df
        self.sleep_df = sleep_df

    def convert_datetime(self, df):
        datetime_cols = ["date", "sleep_start_time", "sleep_end_time"]

        for col in datetime_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], utc=True)
                df[col] = df[col].dt.tz_convert("Europe/Helsinki")
        return df

    def filter_first_last_day(self, grouped):
        if len(grouped["date"].unique()) > 2:
            return grouped.apply(
                lambda x: x[(x.date > x.date.min()) & (x.date < x.date.max())]
            )

        else:
            return pd.DataFrame()

        return grouped

    def pivot_hourly_value(self, df):
        df["hour"] = "hour_" + pd.to_datetime(df["time"]).dt.strftime("%H")

        # Pivot the table
        pivoted_df = df.pivot_table(
            index=["subject_id", "date"],
            columns="hour",
            values="steps",
            fill_value=0,
        )

        return pivoted_df

    def normalize_activity(self, df):
        """
        Allocate activiy count into bins, then calculate the distribution
        """
        df["steps_sum"] = df.filter(like="hour").sum(axis=1)

        # Select columns starting with 'hour'
        hour_columns = df.columns[df.columns.str.startswith("hour")]

        # Perform the division by 'steps_sum' column and round the result
        normalized_hours = df[hour_columns].div(df["steps_sum"], axis=0).round(3)

        # Update the DataFrame with the normalized and rounded values
        df[hour_columns] = normalized_hours

        return df

    def compute_sleep_var(self, df):
        """
        Compute sleep variables

        """
        df["tib"] = (
            df["sleep_end_time"] - df["sleep_start_time"]
        ).dt.total_seconds() / 3600  # time in bed
        df["tst"] = (
            df["tib"] - df["total_interruption_duration"] / 3600
        )  # sleep time = time in bed - interruption
        df["midsleep"] = (
            df["sleep_start_time"] + (df["sleep_end_time"] - df["sleep_start_time"]) / 2
        )

        # midsleep
        df["sleep_eff"] = round(
            df["tst"] / df["tib"], 3
        )  # sleep efficiency (Tst : Tib)
        return df

    def filter_outlier_tst(self, df, lower=3, upper=13):
        """
        Filter outlier TST (3 < TST < 13)
        """
        df = df[(df["tst"] > lower) & (df["tst"] < upper)]
        return df

    def filter_outlier_midsleep(self, df):
        """
        Filter outlier midsleep (mean_midsleep - 2*std  < mean_midsleep < mean_midsleep + 2*std)
        """
        df["midsleep_hhmm"] = (
            df["midsleep"].dt.hour
            + df["midsleep"].dt.minute / 60
            + np.where(df["midsleep"].dt.hour < 12, 24, 0)
        )
        filter = (
            df["midsleep_hhmm"]
            > df["midsleep_hhmm"].mean() - 2 * df["midsleep_hhmm"].std()
        ) & (
            df["midsleep_hhmm"]
            < df["midsleep_hhmm"].mean() + 2 * df["midsleep_hhmm"].std()
        )
        return df[filter]

    # TODO: Maybe add some preprocess options here
    def run(self):
        processed_activity_df = (
            self.activity_df.pipe(self.convert_datetime)
            .groupby("subject_id")
            .pipe(self.filter_first_last_day)  # remove first and last day of data
            .reset_index(drop=True)
            .pipe(
                self.pivot_hourly_value
            )  # pivot so that hourly step count becomes columns
            .reset_index()
            .pipe(self.normalize_activity)
        )

        processed_sleep_df = (
            self.sleep_df.pipe(self.convert_datetime)
            .groupby("subject_id")
            .pipe(self.filter_first_last_day)  # remove first and last day of data
            .reset_index(drop=True)
            .pipe(self.compute_sleep_var)  # compute tst, sleep_eff, midsleep
            .pipe(self.filter_outlier_tst)  # 3 < tst < 13
            .pipe(self.filter_outlier_midsleep)  # midsleep within 2*std
        )

        return (processed_activity_df, processed_sleep_df)


class VectorizeCorona:
    def __init__(self):
        self.activity_df = pd.DataFrame()
        self.sleep_df = pd.DataFrame()
        self.path = "/m/cs/scratch/corona/data/raw/polar/"

        self._load_data(self.path)

    def _load_data(self, path):
        # For both df, combine orig and backup dataset because the orig data was missing lots of records
        steps_df_orig = pd.read_csv(path + "activity_steps.csv", index_col=0)
        steps_df_restored = pd.read_csv(
            path + "activity_steps_restored.csv", index_col=0
        )
        self.activity_df = (
            pd.concat([steps_df_orig, steps_df_restored])
            .drop_duplicates()
            .reset_index(drop=True)
        )

        raw_sleep = pd.read_csv(self.path + "sleep_summary.csv", index_col=0)
        raw_sleep_backup = pd.read_csv(
            path + "restored_2022-01-30_0015/sleep_summary.csv", index_col=0
        )
        raw_sleep_backup2 = pd.read_csv(
            path + "sleep_summary_jan_to_march_2022.csv", index_col=0
        )
        self.sleep_df = (
            pd.concat([raw_sleep, raw_sleep_backup, raw_sleep_backup2])
            .drop_duplicates()
            .reset_index(drop=True)
        )

    def reindex(self, df):
        """
        Reindex by date users remain in study
        """

        # Sort by user_id and date
        df.sort_values(by=["subject_id", "date"], inplace=True)

        # Assign an index to each date for each user
        df["day_in_study"] = df.groupby("subject_id").cumcount() + 1

        return df

    def filter_insufficient_data(self, df, threshold=14):
        """
        Remove users with insufficient data points (max day in study < threshold)
        """
        df = (
            df.groupby("subject_id")
            .filter(lambda x: x["day_in_study"].max() >= 14)
            .reset_index()
        )
        return df

    def assign_weekday(self, df):
        df["weekday"] = df.date.apply(lambda x: True if x.weekday() < 5 else False)
        return df

    def preprocess(self, processor: CoronaProcessor):
        processed_activity_df, processed_sleep_df = processor.run()

        # Pivot by date column
        # Merge
        merged_df = (
            processed_activity_df.merge(processed_sleep_df, on=["subject_id", "date"])
            .pipe(self.reindex)
            .pipe(
                self.filter_insufficient_data, threshold=14
            )  # filter subjects with at least 14 days of data
            .pipe(self.assign_weekday)
        )

        return merged_df
