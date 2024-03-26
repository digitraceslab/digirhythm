import os
from os.path import isfile, join
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import sys
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import fcluster

import hydra
from omegaconf import DictConfig, OmegaConf

import re
import json

np.set_printoptions(threshold=sys.maxsize)


def path_factory(study, frequency):
    
    with open("config/features.txt") as f:
        features = json.load(f)
        
    if study == 'corona':
        sim_path = "data/processed/corona/similarity_matrix/"
        feature_path = f"data/processed/corona/vector_corona_{frequency}.csv"
        f = features[study][frequency]
    elif study == 'momo':
        sim_path = "data/processed/momomood/similarity_matrix/"
        feature_path = f"data/processed/momomood/vector_momo_{frequency}.csv"
        f = features[study][frequency]
    else:
        print("Unrecognize study")
         
    return (sim_path, feature_path, f)
    
def euclidean_similarity(values):
    d = euclidean_distances(values)
    return 1 / (1 + d)


def similarity_matrix(sample, uid):
    """
    Return dictionary of similarity matrix
    """

    # Compute the cosine similarity
    similarity = euclidean_similarity(sample.values)

    # Convert to DataFrame
    similarity_df = pd.DataFrame(similarity)

    return similarity_df


def is_sufficient_data(similarity_matrix, kernel_size):
    return similarity_matrix.shape[0] >= kernel_size * 2


#### STABILITY SCORE
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


def calculate_baseline_si(df, si_max, kernel_size):
    """
    Get the region with highest SI, then average
    """

    region = df.iloc[si_max : si_max + kernel_size]
    baseline = region.mean(axis=0)

    return baseline


#### AVERAGE BASELINE
def calculate_baseline_avg(df):
    """
    Average the aggregate values of all things
    """

    return df.mean(axis=0)


#### CLUSTERING BASELINE
def calculate_baseline_clustering(df):
    res = df.copy()

    # Perform hierarchical clustering
    linked = linkage(res, "ward")

    k = 2
    clusters = fcluster(linked, k, criterion="maxclust")

    # Assign cluster labels to the original dataframe
    res["cluster_label"] = clusters

    # Calculating the centroids
    centroids = res.groupby("cluster_label").mean()

    # Determine the size of each cluster
    cluster_sizes = res["cluster_label"].value_counts()

    # Find the label of the largest cluster
    largest_cluster_label = cluster_sizes.idxmax()

    # Find the centroid of the largest cluster
    baseline = centroids.loc[largest_cluster_label]

    # Remove 'cluster_label' column from the original dataframe
    baseline = baseline.drop(columns=["cluster_label"])

    return baseline


def similarity_against_baseline(features_df, baseline):
    # Append baseline value to the end of the features frame
    df = pd.concat([features_df, pd.DataFrame([baseline])], ignore_index=True)

    # Compute cosine similarity
    baseline_similarity = euclidean_similarity(df.values)

    # Get the last row and remove the last indice
    # last row: distance from other days to baseline
    # last indice: distance of baseline against itself
    res = baseline_similarity[-1][:-1]
    return res



@hydra.main(version_base=None, config_path="../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg.baseline_rhythm))

    # CONFIG
    study = cfg.baseline_rhythm.study
    frequency = cfg.baseline_rhythm.frequency
    method = cfg.baseline_rhythm.method
    kernel_size = cfg.baseline_rhythm.kernel_size
    overlapping_flag = False

    sim_path, feature_path, features = path_factory(study, frequency)

    features_df = pd.read_csv(feature_path)
    features_df.dropna(inplace=True, subset=features)

    res = {}
    for uid in features_df.subject_id.unique():
        sample = features_df[features_df.subject_id == uid][features]

        if overlapping_flag == False:
            if frequency == "7ds":
                sample = sample[0::7]
            if frequency == "14ds":
                sample = sample[0::14]

        # print(sample.shape)
        sm = similarity_matrix(sample, uid)

        if is_sufficient_data(sm, kernel_size) == False:
            continue

        # Save to csv
        sm.to_csv(sim_path + f"{frequency}/similarity_{uid}.csv")

        si_score = stability_score(sm, kernel_size)
        si_max = largest_stability_score(si_score)

        if method == "si":
            baseline = calculate_baseline_si(sample, si_max, kernel_size)
        elif method == "cluster":
            baseline = calculate_baseline_clustering(sample)
        elif method == "average":
            baseline = calculate_baseline_avg(sample)

        similarity_baseline = similarity_against_baseline(sample, baseline)

        res[uid] = similarity_baseline

    # Save to csv
    res_df = pd.DataFrame.from_dict(res, orient="index")
    res_df.to_csv(sim_path + f"/{method}/similarity_baseline_{frequency}.csv")


if __name__ == "__main__":
    main()
