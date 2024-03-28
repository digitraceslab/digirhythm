from config import PATHS
from .comm import *
from .screen import *
from .actigraph import *
from .location import *
from .battery import *
from .accelerometer import AccelerometerProcessor
from .application import ApplicationProcessor
import hydra
from omegaconf import DictConfig, OmegaConf

groups = ["mmm-bpd", "mmm-mdd", "mmm-bd", "mmm-control"]

DATA_PATH = "data/interim/momo/"


@hydra.main(version_base=None, config_path="../../../../config", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg.processor))

    sensor = cfg.processor.sensor
    frequency = cfg.processor.frequency

    dfs = []
    for group in groups:
        
        if sensor == "acti":
            processor = ActigraphProcessor(
                sensor_name="acti",
                path=PATHS[group]["actiwatchfull"],
                table="ActiwatchFull",
                group=group,
                frequency=frequency,
            )
        elif sensor == "screen":
            processor = ScreenProcessor(
                sensor_name="screen",
                path=PATHS[group]["awarescreen"],
                table="AwareScreen",
                group=group,
                batt_path=PATHS[group]["awarebattery"],
                frequency=frequency,
            )
        elif sensor == "sms":
            processor = SmsProcessor(
                sensor_name="sms",
                path=PATHS[group]["awaremessages"],
                table="AwareMessages",
                group=group,
                frequency=frequency,
            )
        elif sensor == "call":
            processor = CallProcessor(
                sensor_name="call",
                path=PATHS[group]["awarecalls"],
                table="AwareCalls",
                group=group,
                frequency=frequency,
            )
        elif sensor == "location":
            processor = LocationProcessor(
                sensor_name="location",
                path=PATHS[group]["location"],
                table="AwareLocation",
                group=group,
                frequency=frequency,
            )
        elif sensor == "battery":
            processor = BatteryProcessor(
                sensor_name="battery",
                path=PATHS[group]["awarebattery"],
                table="AwareBattery",
                group=group,
                frequency=frequency,
            )

        elif sensor == "accelerometer":
            processor = AccelerometerProcessor(
                sensor_name="accelerometer",
                path=PATHS[group]["awareaccelerometer"],
                table="AwareAccelerometer",
                group=group,
                frequency=frequency,
            )
        elif sensor == "application":
            processor = ApplicationProcessor(
                sensor_name="application",
                path=PATHS[group]["awareapplicationforeground"],
                batt_path=PATHS[group]["awarebattery"],
                screen_path=PATHS[group]["awarescreen"],
                table="AwareApplicationForeground",
                group=group,
                frequency=frequency,
            )

        else:
            raise ValueError(
                "Invalid processor type. Please choose for this list: [acti, screen, sms,or call, battery, accelerometer]"
            )

        data = processor.extract_features().reset_index()
        dfs.append(data)

    res = pd.concat(dfs)
    res.to_csv(f"{DATA_PATH}/{sensor}_{frequency}.csv", index=False)


if __name__ == "__main__":
    main()
