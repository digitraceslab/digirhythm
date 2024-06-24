import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, euclidean_distances
from sklearn.preprocessing import StandardScaler

import hydra
from omegaconf import DictConfig, OmegaConf


def path_factory(study, frequency):
    with open("config/features.txt") as f:
        features = json.load(f)

    interim_path = f"data/interim/{study}/"
    sim_path = f"data/processed/{study}/similarity_matrix/"
    feature_path = f"data/processed/{study}/all_features_{frequency}.csv"
    f = features[study][frequency]

    return (interim_path, sim_path, feature_path, f)


def euclidean_similarity(values):
    d = euclidean_distances(values)
    return 1 / (1 + d)


###################SI BASELINE ###################
def similarity_matrix(sample, uid):
    """
    Return dictionary of similarity matrix
    """

    # Compute the cosine similarity
    similarity = euclidean_similarity(sample.values)

    # Convert to DataFrame
    similarity_df = pd.DataFrame(similarity)

    return similarity_df


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


################### AVERAGE BASELINE ###################
def calculate_baseline_avg(df):
    """
    Average the aggregate values of all things
    """

    return df.mean(axis=0)


################### CLUSTERING BASELINE ###################
def calculate_baseline_clustering(df):
    res = df.copy()

    # Function to calculate K-means with silhouette score for cluster validation
    def calculate_kmeans(data, max_k=5):
        scores = []
        models = []

        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=4, n_init=10)
            labels = kmeans.fit_predict(data)

            # Choose optimal num cluster
            score = silhouette_score(data, labels)
            scores.append(score)
            models.append(kmeans)

        # Select the model with the highest silhouette score
        best_idx = np.argmax(scores)
        best_kmeans = models[best_idx]
        return best_kmeans

    # Calculate the best K-means model
    best_kmeans = calculate_kmeans(res)
    cluster_centers = best_kmeans.cluster_centers_
    labels = best_kmeans.labels_
    return labels, cluster_centers


@hydra.main(version_base=None, config_path="../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg.baseline_rhythm))

    # CONFIG
    study = cfg.baseline_rhythm.study
    frequency = cfg.baseline_rhythm.frequency
    method = cfg.baseline_rhythm.method
    kernel_size = cfg.baseline_rhythm.kernel_size
    overlapping_flag = False
    min_sample = cfg.baseline_rhythm.min_sample

    # momo and corona use different naming convention for user id
    user_id = "subject_id" if study == "corona" else "user"

    # Get paths and features
    interim_path, sim_path, feature_path, features = path_factory(study, frequency)

    # Load features vector
    features_df = pd.read_csv(feature_path)

    print("Feature null percentage", features_df[features].isnull().mean())
    features_df.dropna(inplace=True, subset=features)

    # Init result data frame
    all_participants_baseline_df = pd.DataFrame()
    all_features_df = pd.DataFrame()

    for uid in features_df[user_id].unique():
        # Log
        print(f"Processing {uid}...")
        # Create a user folder under interim
        path = f"{interim_path}{uid}"
        if not os.path.exists(path):
            os.makedirs(path)

        # Get features from each user
        sample = features_df[features_df[user_id] == uid][features]
        date = features_df[features_df[user_id] == uid]["date"]

        # Stop if user does not have enough data
        if len(sample) < min_sample:
            continue

        # Retain date
        date = features_df[features_df[user_id] == uid]["date"]

        if overlapping_flag == False:
            if frequency == "7ds":
                sample = sample[0::7]
                date = date[0::7]
            if frequency == "14ds":
                sample = sample[0::14]
                date = date[0::14]

        # Compute baseline based on method
        if method == "si":
            # Compute similarity matrix
            sm = similarity_matrix(sample, uid)

            # Save to csv
            sm.to_csv(sim_path + f"{frequency}/similarity_{uid}.csv")

            # Compute SI score and get max SI region
            si_score = stability_score(sm, kernel_size)
            si_max = largest_stability_score(si_score)

            baseline = calculate_baseline_si(sample, si_max, kernel_size)

            ###### Save baseline behaviour ######
            baseline_df = pd.DataFrame(baseline).transpose()

        elif method == "cluster":
            # Return cluster labels and possibly multiple baseline
            labels, baseline = calculate_baseline_clustering(sample)
            baseline_df = pd.DataFrame(baseline, columns=features)
            baseline_df["cluster"] = range(len(baseline_df))

            # Store feature cluster
            sample["cluster"] = labels
            sample.to_csv(
                f"{path}/all_features_cluster.csv",
                index=False,
            )
        elif method == "average":
            baseline = calculate_baseline_avg(sample)
            baseline_df = pd.DataFrame(baseline)

        baseline_df["subject_id"] = uid
        all_participants_baseline_df = pd.concat(
            [all_participants_baseline_df, baseline_df]
        )

        sample["subject_id"] = uid
        sample["date"] = date
        all_features_df = pd.concat([all_features_df, sample])

    # Save all features
    all_features_df.to_csv(
        interim_path + f"all_participants/{frequency}_{method}_all_features.csv",
        index=False,
    )

    # Save all baseline
    all_participants_baseline_df.to_csv(
        interim_path + f"all_participants/{frequency}_{method}_baseline.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
