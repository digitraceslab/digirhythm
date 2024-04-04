from config import PATHS
from .activity import ActivityProcessor
from .sleep import SleepProcessor
from .hrv import HRVProcessor
from .survey import SurveyProcessor

import hydra
from omegaconf import DictConfig, OmegaConf

DATA_PATH = "data/interim/corona/"


@hydra.main(version_base=None, config_path="../../../../config", config_name="config")
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
    elif sensor == "sleep":
        processor = SleepProcessor(
            sensor_name="sleep",
            path=PATHS["corona"]["sleep"],
            frequency=frequency,
        )
    elif sensor == "hrv":
        processor = HRVProcessor(
            sensor_name="hrv",
            path=PATHS["corona"]["nightly_recharge_summary"],
            frequency=frequency,
        )
    elif sensor == "survey":
        processor = SurveyProcessor(
            sensor_name="survey",
            path=PATHS["corona"]["raw_surveys"],
            frequency=frequency,
        )
    else:
        raise ValueError(
            "Invalid processor type. Please choose for this list: [acti, screen, sms,or call, battery, accelerometer, survey]"
        )

    data = processor.extract_features()
    data.to_csv(f"{DATA_PATH}/{sensor}_{frequency}.csv", index=False)


if __name__ == "__main__":
    main()
