import pandas as pd
import glob
import os
import hydra
from omegaconf import DictConfig, OmegaConf
from functools import reduce

DATA_PATH = "data/processed/momo/"


class VectorizeMoMo:
    def __init__(self, directory_path="data/interim/momo/"):
        self.directory_path = directory_path

    def load_and_merge_dfs(self, merge_keys):
        # Use glob to find all CSV files in the directory
        files = glob.glob(os.path.join(self.directory_path, "*.csv"))
        excluded_files = ["survey_all.csv"]

        result = None

        # Loop over files and merge DataFrames
        for file in files:
            filename = os.path.basename(file)

            if filename not in excluded_files:
                df = pd.read_csv(file)

                if result is None:
                    result = df
                else:
                    if not set(merge_keys).issubset(df.columns):
                        abc = ["user", "group", "date"]
                        print("nomerge", filename)
                    else:
                        abc = merge_keys
                        print("merge", filename)

                    if filename == "PHQ9_scores.csv":
                        result = result.merge(df, how="left", on=abc)
                    else:
                        result = result.merge(df, how="outer", on=abc)
        return result


@hydra.main(version_base=None, config_path="../../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

    vectorize_momo = VectorizeMoMo()
    merged_df = vectorize_momo.load_and_merge_dfs(
        merge_keys=["user", "device", "group", "date"]
    )

    # Filter columns to save based on prefix
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
        "accelerometer",
    )

    # Filter columns based on prefixes
    cols = [col for col in merged_df.columns if col.startswith(prefixes)]
    filtered_df = merged_df[cols]

    print(filtered_df.shape())
    # Save the data in CSV and Pickle format
    filtered_df.to_csv(os.path.join(DATA_PATH, "all_features.csv"))
    filtered_df.to_pickle(os.path.join(DATA_PATH, "all_features.pkl"))


if __name__ == "__main__":
    main()
