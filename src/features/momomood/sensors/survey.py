from .base import BaseProcessor
from dataclasses import dataclass
from .util_questionnaire_mapper import BG_ANSWER_MAP
import niimpy
import pandas as pd

DATA_PATH = "data/interim/momo/"

@dataclass
class SurveyProcessor(BaseProcessor):
    
    groupby_col = ['user', 'device', 'datetime', 'group']
    
    def pivot(self, df): 
        return df.pivot(index=['user', 'device', 'datetime', 'group'], columns='id', values='answer')
    
    def transform_cols(self, df):

        res = df.rename(columns={'x': 'sleep_alone'})
        return res
    

    def convert_to_binary_answer(self, df):
    
        for key in BG_ANSWER_MAP.keys():
            df[key] = df[key].replace(BG_ANSWER_MAP[key])
            
        return df
    
    def extract_features(self) -> pd.DataFrame:        
        
        # Pivot
        pivot_df = self.data.pipe(self.pivot).pipe(self.transform_cols).pipe(self.convert_to_binary_answer)
        
        return pivot_df