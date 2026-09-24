import hashlib
import time
from collections import deque
from threading import Lock


# Maximum requests allowed during the window.
MAX_REQUESTS = 30

# Window size in seconds.
WINDOW_SECONDS = 60


class RateLimiter:
    def __init__(
        self,
        max_requests: int = MAX_REQUESTS,
        window_seconds: int = WINDOW_SECONDS,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        self.requests: dict[str, deque[float]] = {}
        self.lock = Lock()

    @staticmethod
    def _key_identifier(client_key: str) -> str:
        """Return a non-sensitive identifier for an API key."""
        return hashlib.sha256(
            client_key.encode("utf-8")
        ).hexdigest()

    def allow(self, client_key: str) -> bool:
        now = time.time()
        identifier = self._key_identifier(client_key)

        with self.lock:
            timestamps = self.requests.get(identifier)

            if timestamps is None:
                timestamps = deque()
                self.requests[identifier] = timestamps

            # Remove requests outside the current window.
            while timestamps and timestamps[0] <= now - self.window_seconds:
                timestamps.popleft()

            # Remove stale client entries so memory does not grow forever.
            if not timestamps:
                self.requests.pop(identifier, None)
                timestamps = deque()
                self.requests[identifier] = timestamps

            if len(timestamps) >= self.max_requests:
                return False

            timestamps.append(now)
            return True

    def reset(self):
        with self.lock:
            self.requests.clear()


rate_limiter = RateLimiter()