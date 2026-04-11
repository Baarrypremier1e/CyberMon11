"""
Async Event Bus — fire-and-forget dispatch (no bottleneck)
"""
import asyncio
import logging

logger = logging.getLogger("event_bus")

class EventBus:
    def __init__(self):
        self._subscribers = []
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=50000)

    def subscribe(self, callback):
        self._subscribers.append(callback)

    async def publish(self, event: dict):
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            pass  # Drop oldest on overflow

    async def dispatch(self):
        """Fire-and-forget — never blocks on subscriber completion."""
        while True:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                for cb in self._subscribers:
                    asyncio.create_task(cb(event))   # ← fire and forget
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Bus dispatch error: {e}")

event_bus = EventBus()
