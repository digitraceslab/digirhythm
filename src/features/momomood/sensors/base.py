import sys

sys.path.append("../../../")

import niimpy
import pandas as pd
from dataclasses import dataclass


@dataclass
class BaseProcessor:

    """
    This is the base class for all sensor processing classes
    """

    path: str
    table: str
    group: str
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
        This function should be implemented by children classes
        """
        raise NotImplementedError()

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

    def remove_timezone_info(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.tz_localize(None)
        print(data)
        return data

    def add_group(self, df, group):
        df["group"] = group
        return df
