import time
from collections import defaultdict, deque
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

        self.requests = defaultdict(deque)
        self.lock = Lock()

    def allow(self, client_key: str) -> bool:
        now = time.time()

        with self.lock:
            timestamps = self.requests[client_key]

            # Remove requests outside the current window.
            while timestamps and timestamps[0] <= now - self.window_seconds:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                return False

            timestamps.append(now)
            return True

    def reset(self):
        with self.lock:
            self.requests.clear()


rate_limiter = RateLimiter()