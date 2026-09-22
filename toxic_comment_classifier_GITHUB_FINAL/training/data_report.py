import json
from pathlib import Path
from training.data_checks import validate_dataset

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "raw" / "train.csv"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

report = validate_dataset(DATA)
out = REPORTS / "data_report.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps(report, indent=2))
