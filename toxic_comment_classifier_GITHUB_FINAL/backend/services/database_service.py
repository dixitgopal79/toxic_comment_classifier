from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError
from backend.config import get_settings

class DatabaseService:
    def __init__(self):
        settings = get_settings()
        self.client = None
        self.db = None
        self.collection = None
        try:
            self.client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=1500)
            self.client.admin.command("ping")
            self.db = self.client[settings.mongodb_db]
            self.collection = self.db.predictions
            self.collection.create_index([("created_at", DESCENDING)])
            self.collection.create_index("request_id", unique=True)
            self.collection.create_index("overall_toxic")
            self.collection.create_index("feedback.correct")
            # Keep demo history for 30 days. MongoDB TTL indexes expire documents automatically.
            self.collection.create_index(
                "created_at",
                expireAfterSeconds=30 * 24 * 60 * 60,
                name="prediction_retention_30d"
            )
            self.connected = True
        except Exception:
            self.connected = False

    def save_prediction(self, doc: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        try:
            self.collection.insert_one(doc)
            return True
        except PyMongoError:
            return False

    def history(self, limit: int = 100, toxic_only: Optional[bool] = None) -> List[Dict]:
        if not self.connected:
            return []
        query = {}
        if toxic_only is not None:
            query["overall_toxic"] = toxic_only
        return list(
            self.collection.find(query, {"_id": 0})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )

    def stats(self) -> Dict[str, Any]:
        if not self.connected:
            return {"connected": False}
        total = self.collection.count_documents({})
        toxic = self.collection.count_documents({"overall_toxic": True})
        feedback_total = self.collection.count_documents({"feedback": {"$exists": True}})
        feedback_correct = self.collection.count_documents({"feedback.correct": True})
        return {
            "connected": True,
            "total_predictions": total,
            "toxic_predictions": toxic,
            "non_toxic_predictions": max(total - toxic, 0),
            "toxic_rate": round((toxic / total) * 100, 2) if total else 0,
            "feedback_count": feedback_total,
            "feedback_correct": feedback_correct,
            "feedback_accuracy": round((feedback_correct / feedback_total) * 100, 2) if feedback_total else None,
        }

    def save_feedback(self, request_id: str, correct: bool, note: str):
        if not self.connected:
            return False
        result = self.collection.update_one(
            {"request_id": request_id},
            {"$set": {"feedback": {"correct": correct, "note": note, "updated_at": datetime.now(timezone.utc)}}}
        )
        return result.modified_count > 0

    def close(self):
        if self.client:
            self.client.close()
