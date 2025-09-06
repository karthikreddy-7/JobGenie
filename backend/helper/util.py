import datetime
import pandas as pd


def safe_str(val):
    if val is None:
        return "Unavailable"
    if isinstance(val, float) and pd.isna(val):
        return "Unavailable"
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.isoformat()
    if not isinstance(val, str):
        return str(val)
    return val