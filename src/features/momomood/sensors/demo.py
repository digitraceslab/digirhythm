import sys

import pandas as pd
from config import PATHS
from .comm import *
from .screen import *
from .actigraph import *


group = "mmm-control"

#acti_processor = ActigraphProcessor(path=PATHS[group]['actiwatchfull'], table="ActiwatchFull", group=group)
#acti = acti_processor.extract_features(time_bin = '1H').reset_index()


screen_processor = ScreenProcessor(path=PATHS[group]["awarescreen"],table="AwareScreen",group=group,batt_path=PATHS[group]["awarebattery"]
)
screen_processor.extract_features(time_bin="1H").reset_index()

sms_processor = SmsProcessor(path=PATHS[group]['awaremessages'], table="AwareMessages", group=group)
sms = sms_processor.extract_features(time_bin = '1H').reset_index()

call_processor = CallProcessor(path=PATHS[group]['awarecalls'], table="AwareCalls", group=group)
call = call_processor.extract_features(time_bin = '1H').reset_index()
# me = call.merge(sms, on=['user', 'date'], how='outer').fillna(0)
