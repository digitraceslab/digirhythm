from .base import BaseCoronaProcessor
from dataclasses import dataclass
import pandas as pd
from pathlib import Path
from .util_questionnaire_mapper import *

DATA_PATH = "data/interim/corona/"

pd.set_option("future.no_silent_downcasting", True)


@dataclass
class SurveyProcessor:
    sensor_name: str
    frequency: str
    path: str
    data: pd.DataFrame = pd.DataFrame()

    def __post_init__(self) -> None:
        # Merge contents of all dicts into one
        col_id = {
            **phq2_map,
            **psqi_map,
            **pss10_map,
            **panas_map,
            **gad2_map,
            **big5_map,
            **ucla_3_items_map,
            **meq_map,
            **utils_map,
        }

        dfs = []
        for file in Path(self.path).glob("*.csv"):  # This will get all CSV files
            # Read each file and append to the list

            df = pd.read_csv(file, dtype={"user": str})
            # Drop empty subject_id
            df.dropna(subset="user", inplace=True)

            df = df.rename(columns=col_id)
            dfs.append(df)

        # Concatenate all DataFrames in the list
        self.data = pd.concat(dfs, ignore_index=True)

    def preprocess(self, df):
        df["time time"] = pd.to_datetime(df["time time"], format="%d.%m.%YT%H:%M:%S")
        df["date"] = df["time time"].dt.date
        return df

    def encode_categorical_data(self, df):
        encode = {
            "gender": {"male": 0, "female": 1},
            "occupation": {
                "service-staff-permanent-contract": 0,
                "service-staff-fixed-term-contract": 0,
                "academic-staff-fixed-term-contract": 1,
                "academic-staff-permanent-contract": 1,
            },
            "origin": {
                "finland": 0,
                "europe-except-finland": 1,
                "outside-of-europe": 1,
            },
        }
        df.replace(encode, inplace=True)
        df["children_at_home"] = df["children_at_home"].apply(
            lambda x: 1 if x > 0 else x
        )

        return df

    def convert_to_numerical_answer(
        self,
        df,
        answer_col="raw_answer",
        prefix=[
            "PSS",
            "PHQ",
            "GAD",
            "PSQI",
            "PANAS_NEG_During",
            "PANAS_POS_During",
            "PANAS_NEG_Pre",
            "PANAS_POS_Pre",
            "BIG5",
            "MEQ",
            "UCLA3",
        ],
        cum_score=False,
    ):
        """
        Insert doc
        Assuming a wide format dataframe

        :param cum_score: boolean. If true, sums the score and store in a column '{prefix}_sum'
        """

        res = []
        """
        Iterate through rows with the prefix
        """
        for pr in prefix:
            colname = [col for col in df.columns if col.startswith(pr)]
            if not colname:
                continue

            temp = df[colname].copy()

            if pr == "PSS":
                for col in colname:
                    if col in ["PSS10_1", "PSS10_2", "PSS10_3", "PSS10_8", "PSS10_9"]:
                        df[col] = df[col].replace(PSS_ANSWER_MAP)
                    else:
                        df[col] = df[col].replace(PSS_REVERT_ANSWER_MAP)

            if pr == "PHQ" or pr == "GAD":
                df[colname] = df[colname].replace(PHQ2_ANSWER_MAP)

            if pr == "PANAS_POS_Pre" or pr == "PANAS_NEG_Pre":
                df[colname] = df[colname].replace(PANAS_ANSWER_MAP)

            if pr == "PANAS_POS_During" or pr == "PANAS_NEG_During":
                df[colname] = df[colname].replace(PANAS_ANSWER_MAP)

            if pr == "PSQI":
                print(colname)
                df[colname] = df[colname].replace(PSQI_ANSWER_MAP)

            if pr == "UCLA3":
                df[colname] = df[colname].replace(UCLA_3_ITEM_MAP)

            if pr == "BIG5":
                for col in colname:
                    if col in [
                        "BIG5_Agreeableness_2",
                        "BIG5_Neuroticism_4",
                        "BIG5_Openness_5",
                        "BIG5_Extraversion_6",
                        "BIG5_Neuroticism_9",
                        "BIG5_Extraversion_11",
                        "BIG5_Agreeableness_12",
                        "BIG5_Conscientiousness_13",
                        "BIG5_Openness_15",
                    ]:
                        df[col] = df[col].replace(BIG5_ANSWER_MAP)
                    else:
                        df[col] = df[col].replace(BIG5_REVERT_ANSWER_MAP)

            if pr == "MEQ":
                # Manually calculate MEQ
                df["MEQ_1"] = df["MEQ_1"].replace(MEQ_1_ANSWER_MAP)
                df["MEQ_2"] = df["MEQ_2"].replace(MEQ_2_ANSWER_MAP)
                df["MEQ_3"] = df["MEQ_3"].replace(MEQ_3_ANSWER_MAP)
                df["MEQ_4"] = df["MEQ_4"].replace(MEQ_4_ANSWER_MAP)
                df["MEQ_5"] = df["MEQ_5"].replace(MEQ_5_ANSWER_MAP)

            df.to_csv("testsurvey.csv", index=False)
            if cum_score:
                if pr == "BIG5":
                    # Sum BIG-5 score
                    df["BIG5_Extraversion"] = (
                        df["BIG5_Extraversion_1R"]
                        + df["BIG5_Extraversion_6"]
                        + df["BIG5_Extraversion_11"]
                    )
                    df["BIG5_Agreeableness"] = (
                        df["BIG5_Agreeableness_2"]
                        + df["BIG5_Agreeableness_7R"]
                        + df["BIG5_Agreeableness_12"]
                    )
                    df["BIG5_Conscientiousness"] = (
                        df["BIG5_Conscientiousness_3R"]
                        + df["BIG5_Conscientiousness_8R"]
                        + df["BIG5_Conscientiousness_13"]
                    )
                    df["BIG5_Neuroticism"] = (
                        df["BIG5_Neuroticism_4"]
                        + df["BIG5_Neuroticism_9"]
                        + df["BIG5_Neuroticism_14R"]
                    )
                    df["BIG5_Openness"] = (
                        df["BIG5_Openness_5"]
                        + df["BIG5_Openness_10R"]
                        + df["BIG5_Openness_15"]
                    )
                else:
                    df[f"{pr}"] = df[colname].sum(axis=1)

            res.append(temp)
            del temp

        res = pd.concat(res)
        return df

    def fill_demographics(self, df):
        col = ["age", "gender", "occupation", "origin", "children_at_home",
               "BIG5_Extraversion", "BIG5_Agreeableness", "BIG5_Conscientiousness", "BIG5_Neuroticism",
               "BIG5_Openness"]
        df[col] = df[col].fillna(df.groupby(["subject_id"])[col].ffill())

        return df

    def extract_features(self):
        self.data.pipe(self.preprocess).pipe(
            self.convert_to_numerical_answer, cum_score=True
        ).pipe(self.encode_categorical_data).pipe(
            lambda df: df.sort_values(by=["subject_id", "date"], inplace=True)
        )

        self.data.pipe(self.fill_demographics)

        return self.data
