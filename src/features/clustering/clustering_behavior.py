import numpy as np
import pandas as pd
from sklearn.cluster import OPTICS, cluster_optics_dbscan, HDBSCAN, DBSCAN
import os
import sys
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import hydra
from omegaconf import DictConfig, OmegaConf

from sklearn.decomposition import PCA
import umap
import json

from sklearn.cluster import KMeans
from sklearn.metrics import euclidean_distances, silhouette_score


np.set_printoptions(threshold=sys.maxsize)


def path_factory(study, frequency):
    with open("config/features.txt") as f:
        features = json.load(f)

    if study == "corona":
        interim_path = "data/interim/corona/"
        sim_path = "data/processed/corona/similarity_matrix/"
        feature_path = f"data/processed/corona/corona_all_features_{frequency}.csv"
        f = features[study][frequency]
    elif study == "momo":
        interim_path = "data/interim/momo/"
        sim_path = "data/processed/momo/similarity_matrix/"
        feature_path = f"data/processed/momo/vector_momo_{frequency}.csv"
        f = features[study][frequency]
    else:
        print("Unrecognize study")

    return (interim_path, sim_path, feature_path, f)


@hydra.main(version_base=None, config_path="../../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg.clustering))

    # CONFIG
    study = cfg.clustering.study
    frequency = cfg.clustering.frequency
    min_samples = cfg.clustering.min_samples

    # momo and corona use different naming convention for user id
    user_id = "subject_id" if study == "corona" else "user"

    # Get paths and features
    interim_path, sim_path, feature_path, features = path_factory(study, frequency)

    features_df = pd.read_csv(feature_path)

    features_df.dropna(inplace=True, subset=features)
    features_df.sort_values(by=["subject_id"], inplace=True)

    res = {}
    all_participants_baseline = {}

    for uid in features_df[user_id].unique():
        print(f"Processing {uid}")
        # Create a user folder under interim
        path = f"{interim_path}{uid}"
        if not os.path.exists(path):
            os.makedirs(path)

        # Get features from each user
        sample = features_df[features_df[user_id] == uid][features]

        # Return if not enough data
        if len(sample) < min_samples:
            continue

        # PCA and save fig
        umap_embedding = umap.UMAP(
            min_dist=0.1, n_components=2, random_state=232, n_jobs=1, metric="euclidean"
        ).fit_transform(sample)

        #        labels = HDBSCAN(min_cluster_size=min_samples, min_samples=5, cluster_selection_epsilon=0.1).fit_predict(sample)

        # Function to calculate K-means with silhouette score for cluster validation
        def calculate_kmeans(data, max_k=10):
            scores = []
            models = []

            for k in range(2, max_k + 1):
                kmeans = KMeans(n_clusters=k, random_state=42)
                labels = kmeans.fit_predict(data)
                score = silhouette_score(data, labels)
                scores.append(score)
                models.append(kmeans)
                print(f"Silhouette Score for k={k}: {score:.4f}")

            # Select the model with the highest silhouette score
            best_idx = np.argmax(scores)
            best_kmeans = models[best_idx]
            print(f"Best K: {best_idx+2} with Silhouette Score: {scores[best_idx]:.4f}")
            return best_kmeans

        # Calculate the best K-means model
        best_kmeans = calculate_kmeans(sample)
        cluster_centers = best_kmeans.cluster_centers_
        labels = best_kmeans.labels_

        # Calculate the distances from each point to each cluster center
        distances = euclidean_distances(sample, cluster_centers)

        # Get the minimum distance for each point
        min_distances = np.min(distances, axis=1)

        # Determine a threshold for outlier detection - using 95th percentile as cutoff
        threshold = np.percentile(min_distances, 95)
        outlier_mask = min_distances > threshold
        outlier_indices = np.where(outlier_mask)[0]  # Get indices of outliers
        print(outlier_indices)
        labels[outlier_indices] = "-1"
        sample["cluster"] = labels

        sample.to_csv(
            f"{path}/all_features_cluster.csv",
            index=False,
        )

        # Create a plot using seaborn for better aesthetics
        plt.figure(figsize=(10, 6))  # create a figure and an axes object

        plt.scatter(
            umap_embedding[:, 0],
            umap_embedding[:, 1],
            c=labels,
            cmap="viridis",
            s=50,
            alpha=0.6,
            edgecolors="w",
        )
        plt.scatter(
            umap_embedding[outlier_indices, 0],
            umap_embedding[outlier_indices, 1],
            s=100,
            color="red",
            label="Outliers",
            alpha=0.7,
        )

        plt.legend()
        # Save the figure
        plt.savefig(f"{path}/PCA_plot.png")


if __name__ == "__main__":
    main()
