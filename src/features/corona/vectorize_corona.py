import pandas as pd
import glob
import os

import hydra

from omegaconf import DictConfig, OmegaConf

DATA_PATH = "data/processed/corona/"


class VectorizeCorona:
    def __init__(self, frequency, directory_path="data/interim/corona/"):
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


@hydra.main(version_base=None, config_path="../../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

    frequency = cfg.vectorize.frequency

    # Create an instance of the class
    vectorize_momo = VectorizeCorona(frequency)

    # Load and merge DataFrames on a specified key
    merged_df = vectorize_momo.load_and_merge_dfs(merge_key=["subject_id", "date"])

    # Now, merged_df contains all data merged from the files based on the merge_key
    merged_df.to_csv(DATA_PATH + f"vector_corona_{frequency}.csv")
    merged_df.to_pickle(DATA_PATH + f"vector_corona_{frequency}.pkl")


if __name__ == "__main__":
    main()
