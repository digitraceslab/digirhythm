# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import pandas as pd
import json

def main():
    
    frequency = '14ds'
    study = 'corona'

    with open("config/features.txt") as f:
        features_dict = json.load(f)
        
    features_set = features_dict[study][f'wellbeing_{frequency}']

    interim_path = f'data/interim/{study}/'
    processed_path = f'data/processed/{study}/'
    
    # Survey and processed features

    survey = pd.read_csv(interim_path + f'survey_all.csv', dtype={"subject_id": str})
    features = pd.read_csv(processed_path + f'vector_{study}_{frequency}.csv', 
                           dtype={"subject_id": str})

    res = survey.merge(features, on=['subject_id', 'date'],
                       how='left').dropna(subset=features_set)
    uids = res['subject_id'].unique()
    
    
    # Load similarity to baseline
    # Iterate through user id under study
    similarity_baseline_df = pd.DataFrame()
    for uid in uids:
        path = f'{interim_path}{uid}/'
        df = pd.read_csv(path + '4epochs_si_baseline_similarity.csv')
        df['subject_id'] = uid
        similarity_baseline_df = pd.concat([similarity_baseline_df, df])
        
        dfam = df.groupby(['subject_id', 'date']).size().reset_index()
        
        dfam = dfam[dfam[0] > 1][0:3]
        
    if frequency == '7ds':
        # Sort by date first
        similarity_baseline_df = similarity_baseline_df.sort_values(["subject_id", "date"])
        similarity_baseline_df.set_index("date", inplace=True)
        similarity_baseline_df = similarity_baseline_df.groupby('subject_id').rolling(7).agg('median').reset_index().dropna()
    elif frequency == '14ds':
        similarity_baseline_df = similarity_baseline_df.sort_values(["subject_id", "date"])
        similarity_baseline_df.set_index("date", inplace=True)
        similarity_baseline_df = similarity_baseline_df.groupby('subject_id').rolling(14).agg('median').reset_index().dropna()
        

    features_set.append('baseline_similarity')
    res = res.merge(similarity_baseline_df, on=['subject_id', 'date'], how='left')[features_set]

    # Remove non-binary
    res = res[res['gender'] != 'non-binary']
    
    # NOrmalize age
    # Assuming df is your DataFrame and 'age' is the column you want to normalize
    res['age:norm'] = (res['age'] - res['age'].min()) / (res['age'].max() - res['age'].min())
    res.to_csv(processed_path + f'{frequency}_regularity_wellbeing.csv', index=False)
    
if __name__ == "__main__":
    main()