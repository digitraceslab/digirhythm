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
                merged_df = merged_df.merge(
                    df,
                    on=merge_key,
                    how="outer",
                )
                print(merged_df)
                
        merged_df.to_csv('dfm.csv')
        return merged_df


def normalize_features(df, cols, groupby_cols):
    # Normalize specified features per user and create new columns

    for col in cols:
        # Check if feature is already normalized
        if not col.endswith(":norm"):
            temp_frame = df.copy()
            # df[f"{col}:norm"] = df.groupby(groupby_cols)[col].transform(lambda x: (x - x.min()) / (x.max() - x.min()))
            temp_frame[f"{col}:norm"] = df.groupby(groupby_cols)[col].transform(
                lambda x: (x - x.min()) / (x.max() - x.min())
            )
            df = pd.concat([df, temp_frame[f"{col}:norm"]], axis=1)

    return df


def filter_users_with_insufficient_data(df, threshold=0.8):
    """
    Filter out users with less than the given threshold of non-missing observations.

    Parameters:
    df (DataFrame): The input data frame containing a 'user' column and observations.
    threshold (float): The minimum proportion of non-missing observations required to keep a user.

    Returns:
    DataFrame: A filtered data frame with users meeting the data sufficiency threshold.
    """

    # Define a custom filter function
    def sufficient_data(group):
        # Calculate the proportion of non-missing observations for each user
        proportion_non_missing = (
            group.notnull().mean().mean()
        )  # mean() twice: once for columns, once across resulting series
        print(proportion_non_missing)
        return proportion_non_missing >= threshold

    print("Before filter:", len(df.user.unique()))
    # Apply the filter function after grouping by 'user'
    filtered_df = df.groupby("user").filter(sufficient_data)
    print("After filter:", len(filtered_df.user.unique()))
    return filtered_df


@hydra.main(version_base=None, config_path="../../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

    frequency = cfg.vectorize.frequency

    # Create an instance of the class
    vectorize_momo = VectorizeMoMo(frequency)

    # Load and merge DataFrames on a specified key
    merged_df = vectorize_momo.load_and_merge_dfs(merge_key=["user", "group", "date"])

    # Filter columns
    prefixes = (
        "user",
        "group",
        "device",
        "date",
        "location",
        "sms",
        "call",
        "screen",
        "application",
    )
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


    # Normalize feature
    norm_cols = [
        col
        for col in filtered_df.columns
        if col.startswith(("location", "sms", "call", "screen", "application"))
    ]
    
    filtered_df = (
        filtered_df

        # Normalize features
        .pipe(normalize_features, norm_cols, ["user", "group"])

        # Filter users with at least 80% non-missing data
      #  .pipe(filter_users_with_insufficient_data, 0.8)
    )
    
    # Now, merged_df contains all data merged from the files based on the merge_key
    filtered_df.to_csv(DATA_PATH + f"vector_momo_{frequency}.csv")
    filtered_df.to_pickle(DATA_PATH + f"vector_momo_{frequency}.pkl")


if __name__ == "__main__":
    main()

    