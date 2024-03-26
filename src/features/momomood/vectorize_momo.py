import pandas as pd
import glob
import os

import hydra

from omegaconf import DictConfig, OmegaConf

DATA_PATH = "data/processed/momo/"


class VectorizeMoMo:
    def __init__(self, frequency, directory_path="data/interim/momo/"):
        self.frequency = frequency
        self.directory_path = directory_path

    def load_and_merge_dfs(self, merge_key):
        # Initialize a variable to hold the merged DataFrame
        merged_df = None

        # Use glob to find all files in the directory
        files = glob.glob(os.path.join(self.directory_path, "*.csv"))

        # Filter files containing '4epochs' in their names
        filtered_files = [
            file for file in files if self.frequency in os.path.basename(file)
        ]

        # Loop over files and merge DataFrames
        for file in filtered_files:
            df = pd.read_csv(file, index_col=0)
            
            # If merged_df is not initialized, assign the first DataFrame to it
            if merged_df is None:
                merged_df = df
            else:
                # Merge the current DataFrame with the merged_df
                merged_df = pd.merge(
                    merged_df,
                    df,
                    on=merge_key,
                    how="inner",
                )

        return merged_df


def normalize_features(df, cols, groupby_cols):
    # Normalize specified features per user and create new columns

    for col in cols:

        # Check if feature already normalized
        if not col.endswith(':norm'):
            df[f"{col}:norm"] = df.groupby(groupby_cols)[col].transform(
                lambda x: (x - x.min()) / (x.max() - x.min())
            )

    return df



@hydra.main(version_base=None, config_path="../../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

    frequency = cfg.vectorize.frequency

    # Create an instance of the class
    vectorize_momo = VectorizeMoMo(frequency)

    # Load and merge DataFrames on a specified key
    merged_df = vectorize_momo.load_and_merge_dfs(merge_key=["user", "group", "date"])

    # Filter columns
    prefixes = ("user", "group", "device", "date", "location", "sms", "call", "screen", "application")
    cols = [col for col in merged_df.columns if col.startswith(prefixes)]
    filtered_df = merged_df.copy()[cols]
    
    # Some post-processing
    # Reduce dist total to km
    # Identify columns that start with 'location:dist_total'
    location_dist_columns = [
        col
        for col in filtered_df.columns
        if col.startswith(("location:dist_total", "location:max_dist_home"))
    ]

    # Get distance in kilometers
    filtered_df[location_dist_columns] = filtered_df[location_dist_columns] / 1000

    # Convert time at home by dividing n_home bins by total bins
    filtered_df["location:proportion_home"] = filtered_df["location:n_home"] / filtered_df["location:n_bins"]

    # Normalize feature
    norm_cols = [col for col in filtered_df.columns if col.startswith(("location", "sms", "call", "screen", "application"))]
    filtered_df = normalize_features(filtered_df, norm_cols, ['user', 'group', 'device'])


    # Now, merged_df contains all data merged from the files based on the merge_key
    filtered_df.to_csv(DATA_PATH + f"vector_momo_{frequency}.csv")
    filtered_df.to_pickle(DATA_PATH + f"vector_momo_{frequency}.pkl")


if __name__ == "__main__":
    main()
