from config import PATHS
from .comm import *
from .screen import *
from .actigraph import *
from .location import *
import hydra
from omegaconf import DictConfig, OmegaConf

group = "mmm-control"


@hydra.main(version_base=None, config_path="../../../../config", config_name="sensor")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

    sensor = cfg.processor.sensor
    time_bin = cfg.processor.time_bin

    # Processor execution based on command line argument
    if sensor == "acti":
        acti_processor = ActigraphProcessor(
            path=PATHS[group]["actiwatchfull"], table="ActiwatchFull", group=group
        )
        data = acti_processor.extract_features(time_bin=time_bin).reset_index()
    elif sensor == "screen":
        screen_processor = ScreenProcessor(
            path=PATHS[group]["awarescreen"],
            table="AwareScreen",
            group=group,
            batt_path=PATHS[group]["awarebattery"],
        )
        data = screen_processor.extract_features(time_bin=time_bin).reset_index()
    elif sensor == "sms":
        sms_processor = SmsProcessor(
            path=PATHS[group]["awaremessages"], table="AwareMessages", group=group
        )
        data = sms_processor.extract_features(time_bin=time_bin).reset_index()
    elif sensor == "call":
        call_processor = CallProcessor(
            path=PATHS[group]["awarecalls"], table="AwareCalls", group=group
        )
        data = call_processor.extract_features(time_bin=time_bin).reset_index()
    elif sensor == "location":
        loc_processor = LocationProcessor(
            path=PATHS[group]["location"], table="AwareLocation", group=group
        )
        data = loc_processor.extract_features(time_bin=time_bin).reset_index()
    else:
        raise ValueError(
            "Invalid processor type. Please choose: acti, screen, sms, or call"
        )


if __name__ == "__main__":
    main()
