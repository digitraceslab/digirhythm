from config import PATHS
from .activity import *

import hydra
from omegaconf import DictConfig, OmegaConf

DATA_PATH = "data/interim/corona/"


@hydra.main(version_base=None, config_path="../../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

    sensor = cfg.corona.sensor
    frequency = cfg.corona.frequency
    
    if sensor == "activity":
        processor = ActivityProcessor(
            sensor_name="steps",
            path=PATHS["corona"]["activity"],
            frequency=frequency,
        )
    else:
        raise ValueError(
            "Invalid processor type. Please choose for this list: [acti, screen, sms,or call, battery, accelerometer]"
        )
        
    data = processor.extract_features().reset_index()
    data.to_csv(f"{DATA_PATH}/{sensor}_{frequency}.csv", index=False)

if __name__ == "__main__":
    main()
