import pandas as pd
from datetime import date

def first_of_month_from(x):
    ts = pd.to_datetime(x, errors="coerce")
    if pd.isna(ts):
        ts = pd.Timestamp.today()
    return ts.to_pydatetime().date().replace(day=1)
