import pandas as pd
import glob
import os


class VectorizeMoMo:
    def __init__(self, directory_path="data/interim/momo/"):
        self.directory_path = directory_path

    def load_and_merge_dfs(self, merge_key):
        # Initialize a variable to hold the merged DataFrame
        merged_df = None

        # Use glob to find all files in the directory
        files = glob.glob(os.path.join(self.directory_path, "*.csv"))

        # Loop over files and merge DataFrames
        for file in files:
            df = pd.read_csv(file)

            # If merged_df is not initialized, assign the first DataFrame to it
            if merged_df is None:
                merged_df = df
            else:
                # Merge the current DataFrame with the merged_df
                merged_df = pd.merge(merged_df, df, on=merge_key, how="inner")

        return merged_df


# Create an instance of the class
vectorize_momo = VectorizeMoMo()

# Load and merge DataFrames on a specified key
# Replace 'key_column' with the actual column name(s) you want to merge on
merged_df = vectorize_momo.load_and_merge_dfs(merge_key=["user", "group", "date"])
print(merged_df.columns)

# Now, merged_df contains all data merged from the files based on the merge_key
