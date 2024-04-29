import numpy as np


## Outliers detection method
def boxplot(x):
    Q1 = np.percentile(x, 25)
    Q3 = np.percentile(x, 75)
    IQR = Q3 - Q1
    outlier_threshold_low = Q1 - 1.5 * IQR
    outlier_threshold_high = Q3 + 1.5 * IQR

    # Generating boolean mask for outliers
    outlier_mask = x < outlier_threshold_low
    return outlier_mask


def std_from_mean(x, threshold):
    mean = np.mean(x)
    std = np.std(x)

    # Generating boolean mask for outliers
    # Points are considered outliers if they are below (mean - threshold*std) or above (mean + threshold*std)
    outlier_mask = x < (mean - threshold * std)

    return outlier_mask


def CBLOF():
    pass
