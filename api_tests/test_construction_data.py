from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "construction_layer.csv"
REQUIRED_COLUMNS = [
    "project_name",
    "street",
    "from_street",
    "to_street",
    "start_date",
    "end_date",
    "start_time",
