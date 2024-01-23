import sys

import pandas as pd
from config import PATHS
from .comm import *
from .screen import *
from .actigraph import *
import argparse

group = "mmm-control"


# Set up argument parser
parser = argparse.ArgumentParser(
    description="Process data using the specified processor."
)
parser.add_argument(
    "processor",
    type=str,
    help="The processor to use: acti, screen, sms, or call",
)

parser.add_argument("timebin", type=str, help="Time bin in hours (1H, 4H, 6H)")


# Parse arguments
args = parser.parse_args()

time_bin = args.timebin

# Processor execution based on command line argument
if args.processor == "acti":
    acti_processor = ActigraphProcessor(
        path=PATHS[group]["actiwatchfull"], table="ActiwatchFull", group=group
    )
    data = acti_processor.extract_features(time_bin=time_bin).reset_index()
elif args.processor == "screen":
    screen_processor = ScreenProcessor(
        path=PATHS[group]["awarescreen"],
        table="AwareScreen",
        group=group,
        batt_path=PATHS[group]["awarebattery"],
    )
    data = screen_processor.extract_features(time_bin=time_bin).reset_index()
elif args.processor == "sms":
    sms_processor = SmsProcessor(
        path=PATHS[group]["awaremessages"], table="AwareMessages", group=group
    )
    data = sms_processor.extract_features(time_bin=time_bin).reset_index()
elif args.processor == "call":
    call_processor = CallProcessor(
        path=PATHS[group]["awarecalls"], table="AwareCalls", group=group
    )
    data = call_processor.extract_features(time_bin=time_bin).reset_index()
else:
    raise ValueError(
        "Invalid processor type. Please choose: acti, screen, sms, or call"
    )

# Now you can use 'data' for further processing or analysis
