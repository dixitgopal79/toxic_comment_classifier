from collections import Counter
from typing import Dict, List

LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

class MetricsService:
    def summarize(self, rows: List[dict]) -> Dict:
        if not rows:
            return {
                "total": 0,
                "toxic": 0,
                "safe": 0,
                "toxic_rate": 0,
                "label_counts": {label: 0 for label in LABELS},
                "risk_counts": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
            }

        toxic = sum(bool(r.get("overall_toxic")) for r in rows)
        label_counts = Counter()
        risk_counts = Counter()
        for row in rows:
            risk_counts[row.get("risk_level", "LOW")] += 1
            for label, value in row.get("labels", {}).items():
                if value:
                    label_counts[label] += 1

        return {
            "total": len(rows),
            "toxic": toxic,
            "safe": len(rows) - toxic,
            "toxic_rate": round(toxic / len(rows) * 100, 2),
            "label_counts": {label: label_counts[label] for label in LABELS},
            "risk_counts": {
                level: risk_counts[level] for level in ["LOW", "MEDIUM", "HIGH"]
            },
        }
