import os
from os.path import isfile, join
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys

import hydra
from omegaconf import DictConfig, OmegaConf

import re

np.set_printoptions(threshold=sys.maxsize)

DATA_PATH = "data/processed/momo/similarity_matrix/"
# dir = "data/processed/momo/similarity_matrix/"
# files = [f for f in os.listdir(dir) if isfile(join(dir, f))]


def similarity_matrix(sample, uid):
    """
    Return dictionary of similarity matrix
    """

    # Reindex the DataFrame to include all dates in the range, filling missing ones
    #    date_range = pd.date_range(start=sample.index.min(), end=sample.index.max(), freq='D')
    #    sample = sample.reindex(date_range)

    # Compute the cosine similarity
    similarity = cosine_similarity(sample.values)

    # Convert to DataFrame
    similarity_df = pd.DataFrame(similarity)

    return similarity_df


def is_sufficient_data(similarity_matrix, kernel_size):
    return similarity_matrix.shape[0] >= kernel_size * 2


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


def calculate_baseline(df, si_max, kernel_size):
    """
    Get the region with highest SI, then average
    """

    region = df.iloc[si_max : si_max + kernel_size]
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


@hydra.main(version_base=None, config_path="../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

    frequency = cfg.baseline_rhythm.frequency
    # features = cfg.baseline_rhythm.features
    kernel_size = cfg.baseline_rhythm.kernel_size

    fp = f"data/processed/momo/vector_momo_{frequency}.csv"

    features_df = pd.read_csv(fp)
    features_df.dropna(inplace=True)

    # Regex pattern to match strings starting with 'call' or 'sms' and ending with 'norm' or 'sum'
    if frequency == '4epochs':
        pattern = r"^(call|sms)"
    else:
        pattern = r"^(call|sms).*:(norm|total)$"
    # Filtering the list
    features = [f for f in features_df.columns if re.match(pattern, f)]
    print(features_df[features])

    res = {}
    for uid in features_df.user.unique():
        sample = features_df[features_df.user == uid][features]

        sm = similarity_matrix(sample, uid)

        if is_sufficient_data(sm, kernel_size) == False:
            continue

        # Save to csv
        sm.to_csv(DATA_PATH + f"{frequency}/similarity_{uid}.csv")

        si_score = stability_score(sm, kernel_size)
        si_max = largest_stability_score(si_score)

        baseline = calculate_baseline(sample, si_max, kernel_size)

        similarity_baseline = similarity_against_baseline(sample, baseline)

        res[uid] = similarity_baseline

    # Save to csv
    res_df = pd.DataFrame.from_dict(res, orient="index")
    res_df.to_csv(DATA_PATH + f"similarity_baseline_{frequency}.csv")


if __name__ == "__main__":
    main()
