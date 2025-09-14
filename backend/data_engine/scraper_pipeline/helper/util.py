# helper/util.py
import uuid

def safe_str(value):
    return str(value) if value is not None else ""

def generate_id(text):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, text))
