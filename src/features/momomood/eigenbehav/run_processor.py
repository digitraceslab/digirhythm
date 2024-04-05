from config import PATHS
from .eigen_process import EigenbehavProcessor
import hydra
from omegaconf import DictConfig, OmegaConf
import pandas as pd

# groups = ["mmm-bpd", "mmm-mdd", "mmm-bd", "mmm-control"]
groups = ["mmm-control", "mmm-mdd"]

DATA_PATH = "data/interim/momo/"

# @hydra.main(version_base=None, config_path="../../../../config", config_name="config")
# def main(cfg: DictConfig):


def main():
    dfs = []
    rule = "5T"
    for group in groups:
        processor = EigenbehavProcessor(
            path=PATHS[group]["awareapplicationforeground"],
            batt_path=PATHS[group]["awarebattery"],
            screen_path=PATHS[group]["awarescreen"],
            table="AwareApplicationForeground",
            group=group,
            rule=rule,
        )

        data = processor.extract_features()
        dfs.append(data)

    res = pd.concat(dfs)
    print(res.head())
    res.to_csv(
        f"/m/cs/work/luongn1/digirhythm/data/interim/momo/application_{rule}.csv",
        index=False,
    )


#    res.to_csv(f"{DATA_PATH}/{sensor}_{frequency}.csv", index=False)

if __name__ == "__main__":
    main()
