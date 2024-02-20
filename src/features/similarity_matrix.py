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
    "call:incoming_count:morning:norm",
    "call:incoming_count:afternoon:norm",
    "call:incoming_count:evening:norm",
    "call:incoming_count:night:norm",
    "call:incoming_count:sum",
    
    "call:outgoing_count:morning:norm",
    "call:outgoing_count:afternoon:norm",
    "call:outgoing_count:evening:norm",
    "call:outgoing_count:night:norm",
    "call:outgoing_count:sum",
    
    "call:incoming_duration_total:morning:norm",
    "call:incoming_duration_total:afternoon:norm",
    "call:incoming_duration_total:evening:norm",
    "call:incoming_duration_total:night:norm",
    "call:incoming_duration_total:sum",
    
    "call:outgoing_duration_total:morning:norm",
    "call:outgoing_duration_total:afternoon:norm",
    "call:outgoing_duration_total:evening:norm",
    "call:outgoing_duration_total:night:norm",
    "call:outgoing_duration_total:sum",
    
    # SMS
    "sms:incoming_count:morning:norm",
    "sms:incoming_count:afternoon:norm",
    "sms:incoming_count:evening:norm",
    "sms:incoming_count:night:norm",
    "sms:incoming_count:sum",
    
    "sms:outgoing_count:morning:norm",
    "sms:outgoing_count:afternoon:norm",
    "sms:outgoing_count:evening:norm",
    "sms:outgoing_count:night:norm",
    "sms:outgoing_count:sum",
]

# Compute matrix for each user
for user in df.user.unique():
    sample = df[df.user == user]

    # Reindex the DataFrame to include all dates in the range, filling missing ones
    #    date_range = pd.date_range(start=sample.index.min(), end=sample.index.max(), freq='D')
    #    sample = sample.reindex(date_range)

    # Selecting relevant features for similarity calculation
    sample = sample[selected_features]
    features = sample.values
    
    # Compute the cosine similarity
    similarity = cosine_similarity(features)

    # Convert to DataFrame
    similarity_df = pd.DataFrame(similarity)

    # Save
    similarity_df.to_csv(DATA_PATH + f"similarity_{user}.csv")
