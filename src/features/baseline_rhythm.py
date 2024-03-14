import os
from os.path import isfile, join
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys

np.set_printoptions(threshold=sys.maxsize)

KERNEL_SIZE = 7
DATA_PATH = "data/processed/momo/similarity_matrix/"
#dir = "data/processed/momo/similarity_matrix/"
#files = [f for f in os.listdir(dir) if isfile(join(dir, f))]

fp = "data/processed/momo/vector_momo.pkl"
features_df = pd.read_pickle(fp)


FEATURES = [
    # Location
    "location:dist_total:morning",
    "location:dist_total:afternoon",
    "location:dist_total:evening",
    "location:dist_total:night",
    
    "location:n_home:morning",
    "location:n_home:afternoon",
    "location:n_home:evening",
    "location:n_home:night",
    
    "location:n_rare:morning",
    "location:n_rare:afternoon",
    "location:n_rare:evening",
    "location:n_rare:night",
    
]

def similarity_matrix(sample, uid):
    '''
    Return dictionary of similarity matrix
    '''

    # Reindex the DataFrame to include all dates in the range, filling missing ones
    #    date_range = pd.date_range(start=sample.index.min(), end=sample.index.max(), freq='D')
    #    sample = sample.reindex(date_range)

    # Compute the cosine similarity
    similarity = cosine_similarity(sample.values)

    # Convert to DataFrame
    similarity_df = pd.DataFrame(similarity)

    return similarity_df

def is_sufficient_data(similarity_matrix):
    return similarity_matrix.shape[0] >= KERNEL_SIZE * 2

def stability_score(similarity_matrix, kernel_size=7):
    size = similarity_matrix.shape[0] - kernel_size - 1

    # Extract the similarity values of consecutive elements
    consecutive_similarity = np.diag(
        similarity_matrix, k=1
    )  # k=1 for one above the main diagonal

    stability_scores = []
    for i in range(0, size):
        kernel = consecutive_similarity[i : i + kernel_size]
        stability_scores.append(np.median(kernel))
    # Slide
    return stability_scores

def largest_stability_score(stability_score):

    if len(stability_score) == 0:
        return np.nan
    return np.array(stability_score).argmax()

def calculate_baseline(features_df, si_max, kernel_size):

    '''
    Get the region with highest SI, then average
    '''
    
    region = sample.iloc[si_max :  si_max+kernel_size]
    baseline = region.mean(axis=0)
    
    return baseline

def similarity_against_baseline(features_df, baseline):
    
    # Append baseline value to the end of the features frame
    df = pd.concat([features_df, pd.DataFrame([baseline])], ignore_index=True)

    # Compute cosine similarity
    baseline_similarity = cosine_similarity(df.values)

    # Get the last row and remove the last indice 
    # last row: distance from other days to baseline
    # last indice: distance of baseline against itself
    res = baseline_similarity[-1][:-1]
    return res

# Main
res = {}
for uid in features_df.user.unique():
    
    sample = features_df[features_df.user == uid][FEATURES]

    sm = similarity_matrix(sample, uid)

    if is_sufficient_data(sm) == False:
        continue

    # Save to csv
    sm.to_csv(DATA_PATH + f"similarity_{uid}.csv")

    si_score = stability_score(sm, KERNEL_SIZE)
    si_max = largest_stability_score(si_score)

    baseline = calculate_baseline(sample, si_max, KERNEL_SIZE)
    
    similarity_baseline = similarity_against_baseline(sample, baseline)
    
    res[uid] = similarity_baseline

# Save to csv
res_df = pd.DataFrame.from_dict(res, orient='index')
res_df.to_csv(DATA_PATH + f"similarity_baseline.csv")