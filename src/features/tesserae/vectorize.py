import pandas as pd
import glob
import os
import hydra
from omegaconf import DictConfig, OmegaConf
from functools import reduce

DATA_PATH = "data/processed/tesserae/"


class VectorizeTesserae:
    def __init__(self, directory_path="data/interim/tesserae/"):
        self.directory_path = directory_path

    def load_and_merge_dfs(self, merge_keys):
        # Use glob to find all CSV files in the directory
        files = glob.glob(os.path.join(self.directory_path, "*.csv"))

        result = None

        full_filenames = [
            "application_14ds.csv",
            "application_4epochs.csv",
            "application_7ds.csv",
            "call_14ds.csv",
            "call_4epochs.csv",
            "call_7ds.csv",
            "location_14ds.csv",
            "location_4epochs.csv",
            "location_7ds.csv",
            "screen_14ds.csv",
            "screen_4epochs.csv",
            "screen_7ds.csv",
            "sms_14ds.csv",
            "sms_4epochs.csv",
            "sms_7ds.csv",
            "PHQ9_scores.csv",
        ]

        filenames = ["call_4epochs.csv", "screen_4epochs.csv"]

        # Loop over files and merge DataFrames
        for f in filenames:
            file = os.path.join(self.directory_path, f)
            print(file)
            df = pd.read_csv(file, dtype={"user": "str"}, parse_dates=["date"])

            print(df.date.unique())
            if result is None:
                result = df.copy()
            else:
                result = result.merge(df, on=["user", "date"])

        for col in result.columns:
            print(col)
        return result


@hydra.main(version_base=None, config_path="../../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

    vectorize = VectorizeTesserae()
    merged_df = vectorize.load_and_merge_dfs(merge_keys=["user", "date"])

    # Save the data in CSV and Pickle format
    merged_df.to_csv(os.path.join(DATA_PATH, "all_features.csv"), index=False)
    merged_df.to_pickle(os.path.join(DATA_PATH, "all_features.pkl"))


if __name__ == "__main__":
    main()
