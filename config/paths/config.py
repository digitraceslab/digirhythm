import configparser
import os

#################### PATHS ####################
cwd = os.path.dirname(__file__)
config_ini = os.path.join(cwd, "config.ini")

config = configparser.ConfigParser()
config.read(config_ini)

# Create a dictionary to hold the paths
paths = {
    "mmm-bd": {},
    "mmm-bpd": {},
    "mmm-control": {},
    "mmm-mdd": {},
    "pilot-control": {},
    "pilot-patient": {},
    "processed": {},
}

# Get the sample data path
sample_data_path = config.get("root", "data")
pilot_data_path = config.get("root", "pilot_data")
print(sample_data_path)

# Get the paths for mmm-bd
pilot_control_paths = config["pilot-control"]
for key in pilot_control_paths:
    paths["pilot-control"][key] = pilot_data_path + pilot_control_paths[key]
paths["pilot-control"]["location"] = (
    config.get("root", "pilot_location_data") + pilot_control_paths["Location"]
)

# Get the paths for mmm-bd
pilot_patient_paths = config["pilot-patient"]
for key in pilot_patient_paths:
    paths["pilot-patient"][key] = pilot_data_path + pilot_patient_paths[key]
paths["pilot-patient"]["location"] = (
    config.get("root", "pilot_location_data") + pilot_patient_paths["Location"]
)

# Get the paths for mmm-bd
mmm_bd_paths = config["mmm-bd"]
for key in mmm_bd_paths:
    paths["mmm-bd"][key] = sample_data_path + mmm_bd_paths[key]
paths["mmm-bd"]["location"] = (
    config.get("root", "location_data") + mmm_bd_paths["Location"]
)

# Get the paths for mmm-bpd
mmm_bpd_paths = config["mmm-bpd"]
for key in mmm_bpd_paths:
    paths["mmm-bpd"][key] = sample_data_path + mmm_bpd_paths[key]
paths["mmm-bpd"]["location"] = (
    config.get("root", "location_data") + mmm_bpd_paths["Location"]
)

# Get the paths for mmm-control
mmm_control_paths = config["mmm-control"]
for key in mmm_control_paths:
    paths["mmm-control"][key] = sample_data_path + mmm_control_paths[key]
paths["mmm-control"]["location"] = (
    config.get("root", "location_data") + mmm_control_paths["Location"]
)

# Get the paths for mmm-mdd
mmm_mdd_paths = config["mmm-mdd"]
for key in mmm_mdd_paths:
    paths["mmm-mdd"][key] = sample_data_path + mmm_mdd_paths[key]
paths["mmm-mdd"]["location"] = (
    config.get("root", "location_data") + mmm_mdd_paths["Location"]
)

# Processed data path
processed_data_path = config.get("processed", "data")

processed_comm_paths = config["comm"]
for key in processed_comm_paths:
    paths["processed"][key] = processed_data_path + processed_comm_paths[key]

processed_batt_paths = config["batt"]
for key in processed_batt_paths:
    paths["processed"][key] = processed_data_path + processed_batt_paths[key]

processed_screen_paths = config["screen"]
for key in processed_screen_paths:
    paths["processed"][key] = processed_data_path + processed_screen_paths[key]


# Export the paths dictionary
PATHS = paths
