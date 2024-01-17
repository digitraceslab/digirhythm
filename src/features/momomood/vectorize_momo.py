import numpy as np
import pandas as pd
from datetime import timedelta
import pytz


class VectorizeMoMo:

    """
    Add customized behaviours here as well
    """

    def __init__(self, activity_df, sleep_df):
        self.activity_df = activity_df
        self.sleep_df = sleep_df
