import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys

np.set_printoptions(threshold=sys.maxsize)

DATA_PATH = "data/processed/momo/similarity_matrix/"
fp = "data/processed/momo/vector_momo.pkl"
df = pd.read_pickle(fp)

df.date = pd.to_datetime(df.date)
df.sort_values(by=["user", "date"], inplace=True)
df.set_index("date", inplace=True)

selected_features = [
    # Location
    "location:dist_total:morning",
    "location:dist_total:afternoon",
    "location:dist_total:evening",
    "location:dist_total:night",
    # Call
    "call:incoming_count:morning",
    "call:incoming_count:afternoon",
    "call:incoming_count:evening",
    "call:incoming_count:night",
    "call:outgoing_count:morning",
    "call:outgoing_count:afternoon",
    "call:outgoing_count:evening",
    "call:outgoing_count:night",
    "call:incoming_duration_total:morning",
    "call:incoming_duration_total:afternoon",
    "call:incoming_duration_total:evening",
    "call:incoming_duration_total:night",
    "call:outgoing_duration_total:morning",
    "call:outgoing_duration_total:afternoon",
    "call:outgoing_duration_total:evening",
    "call:outgoing_duration_total:night",
    # SMS
    "sms:incoming_count:morning",
    "sms:incoming_count:afternoon",
    "sms:incoming_count:evening",
    "sms:incoming_count:night",
    "sms:outgoing_count:morning",
    "sms:outgoing_count:afternoon",
    "sms:outgoing_count:evening",
    "sms:outgoing_count:night",
]

# Compute matrix for each user
for user in df.user.unique():
    sample = df[df.user == user]

    # Reindex the DataFrame to include all dates in the range, filling missing ones
    #    date_range = pd.date_range(start=sample.index.min(), end=sample.index.max(), freq='D')
    #    sample = sample.reindex(date_range)

    # Selecting the relevant features for cosine similarity calculation
    sample = sample[selected_features]
    features = sample.values

    # Compute the cosine similarity
    similarity = cosine_similarity(features)

    # Convert to DataFrame
    similarity_df = pd.DataFrame(similarity)

    # Save
    similarity_df.to_csv(DATA_PATH + f"similarity_{user}.csv")
