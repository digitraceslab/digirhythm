from .base import BaseCoronaProcessor
from dataclasses import dataclass
import pandas as pd
from ...decorators import save_output_with_freq
from datetime import datetime

DATA_PATH = "data/interim/corona/"


@dataclass
class HRVProcessor(BaseCoronaProcessor):
    def extract_features(self) -> pd.DataFrame:
        df = self.data.copy()
        
        # Roll the dataframe based on frequency
        if self.frequency == "14ds":
            df = df.pipe(self.roll, groupby=["subject_id"], days=14).pipe(
                self.flatten_columns
            ).pipe(self.normalize_features, ['heart_rate_variability_avg:mean'])
        elif self.frequency == "7ds":
            df = df.pipe(self.roll, groupby=["subject_id"], days=7).pipe(
                self.flatten_columns
            ).pipe(self.normalize_features, ['heart_rate_variability_avg:mean'])
        else:
            df = self.normalize_features(df, ['heart_rate_variability_avg'])
        
        return df
