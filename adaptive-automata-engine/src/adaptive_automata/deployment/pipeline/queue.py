"""
Bounded Event Queue with Backpressure Handling.
"""

from collections import deque
import threading
from typing import Any, Generic, TypeVar

from adaptive_automata.deployment.config.settings import BackpressurePolicy

T = TypeVar("T")


class BoundedEventQueue(Generic[T]):
    """
    Thread-safe Bounded Queue implementing explicit backpressure policies:
    - DROP_OLDEST: Evict oldest items when queue capacity is reached.
    - DROP_NEWEST: Reject incoming item when capacity is reached.
    - BLOCK: Block producer until capacity opens up.
    - SAMPLE: Accept every Nth item under high load.
    """

    def __init__(
        self,
        max_size: int = 5000,
        policy: BackpressurePolicy = BackpressurePolicy.DROP_OLDEST,
    ) -> None:
        self.max_size = max_size
        self.policy = policy
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)
        self._queue: deque[T] = deque()
        self.dropped_count: int = 0
        self._sample_counter: int = 0

    def put(self, item: T, timeout: float | None = None) -> bool:
        """
        Put item onto the queue applying backpressure policy.
        Returns True if item was added, False if dropped.
        """
        with self._lock:
            if len(self._queue) >= self.max_size:
                if self.policy == BackpressurePolicy.DROP_OLDEST:
                    if self._queue:
                        self._queue.popleft()
                        self.dropped_count += 1
                elif self.policy == BackpressurePolicy.DROP_NEWEST:
                    self.dropped_count += 1
                    return False
                elif self.policy == BackpressurePolicy.SAMPLE:
                    self._sample_counter += 1
                    if self._sample_counter % 5 != 0:
                        self.dropped_count += 1
                        return False
                    if self._queue:
                        self._queue.popleft()
                elif self.policy == BackpressurePolicy.BLOCK:
                    while len(self._queue) >= self.max_size:
                        if not self._not_full.wait(timeout=timeout):
                            self.dropped_count += 1
                            return False

            self._queue.append(item)
            self._not_empty.notify()
            return True

    def get(self, timeout: float | None = None) -> T | None:
        """
        Get next item from queue, blocking until available or timeout.
        """
        with self._lock:
            while not self._queue:
                if not self._not_empty.wait(timeout=timeout):
                    return None
            item = self._queue.popleft()
            self._not_full.notify()
            return item

    def qsize(self) -> int:
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        with self._lock:
            return len(self._queue) == 0
