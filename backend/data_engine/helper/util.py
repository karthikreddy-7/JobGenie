# helper/util.py
import datetime
import uuid
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

def generate_id(text):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, text))
