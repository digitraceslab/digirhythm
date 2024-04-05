# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import pandas as pd
import json

def main():
    
    frequency = '7ds'
    study = 'corona'
    overlapping_flag = True
    
    with open("config/features.txt") as f:
        features_dict = json.load(f)
        
    features_set = features_dict[study][f'wellbeing_{frequency}']

    interim_path = f'data/interim/{study}/'
    processed_path = f'data/processed/{study}/'
    
    survey = pd.read_csv(interim_path + f'survey_all.csv', dtype={"subject_id": str})
    features = pd.read_csv(processed_path + f'vector_{study}_{frequency}.csv', 
                           dtype={"subject_id": str})
#    for col in features.columns:
#        print(col)
    # Drop empty features
    df = survey.merge(features, on=['subject_id', 'date'], how='left').dropna(subset=features_set)
    

if __name__ == "__main__":
    main()