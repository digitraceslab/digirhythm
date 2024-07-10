import polars as pl
from util import timing
from config import PATHS
import sqlite3
import niimpy
import pandas as pd 
raw_path = "/m/cs/work/luongn1/digirhythm/data/raw/"

@timing
def convert_screen_tess_aware(path):
  
    df = (
        pl.read_csv(path, schema_overrides={"snapshot_id": pl.String}).with_columns(
            pl.col("local_time")
            .str.replace(r"\..*$", "")
            .str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S"),
            pl.col("phone_lock").map_dict({"lock": 2, "unlock": 3}),
            (pl.col("snapshot_id") + "d").alias("device"),
        )
    ).rename(
        {"snapshot_id": "user", "local_time": "datetime", "phone_lock": "screen_status"}
    )

    return df

@timing
def convert_call_tess_aware(path):

    mapper = {1: 'incoming', 2: 'outgoing', 3: 'missed'}
    df = (
        pl.read_csv(path, schema_overrides={"snapshot_id": pl.String}).with_columns(
            pl.col("type").replace(mapper)
            
        )
    ).rename(
        {"snapshot_id": "user", "local_time": "datetime", "type": "call_type", "duration": "call_duration", "number": "trace"}
    )

    return df

@timing
def convert_dtu_aware(path):
    df = (
        pl.read_csv(path, schema_overrides={"new_id": pl.String}).with_columns(
            (pl.col("new_id") + "d").alias("device")
        )
    ).rename({"new_id": "user", "new_timestamp": "time", "screen_on": "screen_status"})

    return df


# Static path
tess_lock_path = PATHS["tesserae"]["phonelock"]
screen_tess_aware = convert_screen_tess_aware(tess_lock_path)
screen_tess_aware.write_parquet(raw_path + "tesserae/tess_aware_screen.parquet" )

# dtu_screen_path = PATHS["dtu"]["screen"]
# screen_dtu_aware = convert_dtu_aware(dtu_screen_path)
# screen_dtu_aware.write_parquet(raw_path + "dtu/dtu_aware_screen.parquet")

#call = niimpy.read_sqlite(PATHS["mmm-control"]["awarecalls"], table='AwareCalls')
#print(call.head())

#df = convert_call_tess_aware(PATHS["tesserae"]["call"])
#df.write_parquet(raw_path + "tesserae/tesserae_aware_call.parquet")