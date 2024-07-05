import os
from os.path import isfile, join
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.metrics import silhouette_score
import sys
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import fcluster

import hydra
from omegaconf import DictConfig, OmegaConf

import re
import json
from sklearn.cluster import KMeans
from .utils import *

np.set_printoptions(threshold=sys.maxsize)


def path_factory(study, frequency, method):
    """
    Generates file paths based on study parameters.

    Args:
    - study (str): The name of the study.
    - frequency (str): Data collection frequency.
    - method (str): Methodology for processing data.

    Returns:
    - tuple: Contains paths to interim data, processed data, all features, baseline data, and features configuration.
    """
    with open("config/features.txt") as f:
        features = json.load(f)

    interim_path = f"data/interim/{study}/"
    processed_path = f"data/processed/{study}/"
    feature_path = (
        f"{interim_path}all_participants/{frequency}_{method}_all_features.csv"
    )
    baseline_path = f"{interim_path}all_participants/{frequency}_{method}_baseline.csv"
    f = features[study][frequency]

    return interim_path, processed_path, feature_path, baseline_path, f


def euclidean_similarity(v):
    d = euclidean_distances(v)
    return 1 / (1 + d)


def similarity_against_baseline(
    features_df, baseline_df, method, features
) -> pd.DataFrame():
    if method == "si":
        # Append baseline value to the end of the features frame
        df = pd.concat([features_df, baseline_df], ignore_index=True)

        # Compute euclidean similarity
        baseline_similarity = euclidean_similarity(df[features].values)

        # Get the last row and remove the last indice
        # last row: distance from other days to baseline
        # last indice: distance of baseline against itself
        sim = baseline_similarity[-1][:-1]
        res = features_df.copy()

        res["sim_to_baseline"] = sim

    elif method == "cluster":
        res = pd.DataFrame()
        for cluster in baseline_df["cluster"].unique():
            centroid = baseline_df.query(f"cluster == {cluster}")
            f = features_df.copy().query(f"cluster == {cluster}")

            # Append baseline value to the end of the features frame
            df = pd.concat([f, centroid], ignore_index=True)

            # Compute euclidean similarity
            baseline_similarity = euclidean_similarity(df[features].values)

            # Get the last row and remove the last indice
            # last row: distance from other days to baseline
            # last indice: distance of baseline against itself
            sim = baseline_similarity[-1][:-1]

            f["sim_to_centroid"] = sim
            res = pd.concat([res, f])

    return res


###### OUTLIERS


def outliers_detection(sim_baseline_df, method, outliers_func):
    if method == "si":
        sim_baseline_df["outlier"] = outliers_func(sim_baseline_df["sim_to_baseline"])

    elif method == "cluster":
        # Applying the boxplot function to detect outliers within each cluster
        sim_baseline_df["outlier"] = sim_baseline_df.groupby("cluster")[
            "sim_to_centroid"
        ].transform(outliers_func)

    return sim_baseline_df


def difference_from_baseline(outliers_df, baseline_df, method, features):
    if method == "si":
        res = outliers_df.copy()
        res[features] = outliers_df[features] - baseline_df[features].values

    elif method == "cluster":
        res = pd.DataFrame()
        for cluster in baseline_df["cluster"].unique():
            centroid = baseline_df.query(f"cluster == {cluster}")
            f = outliers_df.copy().query(f"cluster == {cluster}")

            f[features] = outliers_df[features] - centroid[features].values
            res = pd.concat([res, f])

    return res


@hydra.main(version_base=None, config_path="../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg.baseline_rhythm))

    # CONFIG
    study = cfg.outliers.study
    frequency = cfg.outliers.frequency
    method = cfg.outliers.method
    outliers_threshold = cfg.outliers.threshold

    # Function used to detect outliers
    outliers_func = lambda data: std_from_mean(data, threshold=outliers_threshold)

    # momo and corona use different naming convention for user id
    user_id = "subject_id" # if study == "corona" else "user"

    # Get paths and features
    interim_path, processed_path, feature_path, baseline_path, features = path_factory(
        study, frequency, method
    )

    # Load features
    features_df = pd.read_csv(feature_path)
    features_df.dropna(inplace=True, subset=features)

    # Read baseline behaviour of all users
    baseline_df = pd.read_csv(baseline_path)

    # Prepare a df to store difference from baseline
    all_participants_baseline_diff = pd.DataFrame()

    print(features_df.head())
    for uid in features_df[user_id].unique():
        sample = features_df[features_df[user_id] == uid]
        date = features_df[features_df[user_id] == uid]["date"]

        sample_baseline = baseline_df[baseline_df[user_id] == uid]
        sample_baseline_diff = (
            sample.pipe(similarity_against_baseline, sample_baseline, method, features)
            .pipe(outliers_detection, method, outliers_func)
            .pipe(difference_from_baseline, sample_baseline, method, features)
        )

        sample_baseline_diff["date"] = date
        all_participants_baseline_diff = pd.concat(
            [all_participants_baseline_diff, sample_baseline_diff]
        )

    # Save
    all_participants_baseline_diff.to_csv(
        f"{processed_path}{frequency}_{method}_threshold_{outliers_threshold}_diff_baseline.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
