import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from backend.config import get_settings

class RateLimiter:
    def __init__(self):
        self.events = defaultdict(deque)

    def check(self, client_id: str):
        settings = get_settings()
        now = time.time()
        q = self.events[client_id]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= settings.rate_limit_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again shortly.")
        q.append(now)

rate_limiter = RateLimiter()

async def optional_api_key(request: Request):
    settings = get_settings()
    if not settings.api_key:
        return
    provided = request.headers.get("X-API-Key", "")
    if provided != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
