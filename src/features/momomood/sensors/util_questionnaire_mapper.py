# -*- coding: utf-8 -*-

# MOMO-MOOD mapper

# Map answer's id against numerical values
BG_ANSWER_MAP = {
    "bg_education": {
        # Below university / college level
        "0": 0,
        "1": 0,
        "2": 0,
        # University level
        "3": 1,
        "4": 1,
    },
    "children": {
        # No child
        "ei": 0,
        "1": 1,
        "2": 1,
        "3": 1,
        "4": 1,
    },
    "work": {
        # Sick leave or unemployed
        "0": 0,
        "1": 0,
        "2": 0,
        "4": 0,
        "5": 0,
        # Student or working
        "3": 1,
        "6": 1,
        "7": 1,
    },
    "habitation": {
        # Alone
        "0": 0,
        # With someone else/shared apartment
        "1": 1,
        "2": 1,
        "3": 1,
    },
}
