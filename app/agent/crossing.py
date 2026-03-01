import time


class SpatialDeduplicator:
    """Suppress duplicate crossing events from tracker ID switches.

    Records accepted crossings as (position, timestamp, direction) tuples
    and rejects new events that occur at a similar position, within a time
    window, and in the same direction.
    """

    def __init__(self, time_window: float = 2.0, radius_factor: float = 1.2):
        self.time_window = time_window
        self.radius_factor = radius_factor
        self._recent: list[tuple[float, float, float, str]] = []

    def is_duplicate(self, x: float, y: float, bbox_width: float, direction: str) -> bool:
        now = time.monotonic()
        radius = bbox_width * self.radius_factor
        self._recent = [r for r in self._recent if now - r[2] <= self.time_window]
        for rx, ry, _rt, rd in self._recent:
            if rd == direction and ((x - rx) ** 2 + (y - ry) ** 2) <= radius ** 2:
                return True
        self._recent.append((x, y, now, direction))
        return False


class CrossingDetector:
    """Detect when tracked people cross a virtual line in the frame.

    Uses a cross-product sign change between consecutive frames to
    determine if a person moved from one side of the line to the other.
    A per-person cooldown prevents duplicate events caused by jitter
    near the line.

    Args:
        line_start: ``(x, y)`` pixel coordinate of the line's start.
        line_end: ``(x, y)`` pixel coordinate of the line's end.
    """

    COOLDOWN_SECONDS = 3.0

    def __init__(self, line_start: tuple[int, int], line_end: tuple[int, int]):
        self.line_start = line_start
        self.line_end = line_end
        self._previous_sides: dict[int, float] = {}
        self._last_crossing: dict[int, float] = {}
        self._dedup = SpatialDeduplicator()

    def _side(self, point: tuple[float, float]) -> float:
        """Cross product to determine which side of the line a point is on."""
        dx = self.line_end[0] - self.line_start[0]
        dy = self.line_end[1] - self.line_start[1]
        px = point[0] - self.line_start[0]
        py = point[1] - self.line_start[1]
        return dx * py - dy * px

    def update(self, people: list[dict]) -> list[dict]:
        """Process a new frame's tracked people and emit crossing events.

        Compares each person's current side of the line with their
        previous side. A sign change (respecting the cooldown) produces
        an ``"entry"`` or ``"exit"`` event. People who disappear from
        the frame have their tracking state cleaned up automatically.

        Args:
            people: List of dicts with ``"id"`` (int) and ``"center"``
                (tuple of floats), as returned by
                :meth:`PeopleTracker.track`.

        Returns:
            List of crossing event dicts, each containing:
                - ``"id"`` — the person's tracking ID.
                - ``"direction"`` — ``"entry"`` or ``"exit"``.
        """
        events = []
        current_ids = set()

        for person in people:
            pid = person["id"]
            current_ids.add(pid)
            side = self._side(person["center"])

            if pid in self._previous_sides:
                prev = self._previous_sides[pid]
                now = time.monotonic()
                cooldown_ok = (now - self._last_crossing.get(pid, 0)) > self.COOLDOWN_SECONDS

                if cooldown_ok:
                    direction = None
                    if prev > 0 and side <= 0:
                        direction = "entry"
                    elif prev < 0 and side >= 0:
                        direction = "exit"
                    if direction is not None:
                        cx, cy = person["center"]
                        x1, _y1, x2, _y2 = person["bbox"]
                        if not self._dedup.is_duplicate(cx, cy, x2 - x1, direction):
                            events.append({"id": pid, "direction": direction})
                        self._last_crossing[pid] = now

            self._previous_sides[pid] = side

        # Clean up IDs that left the frame
        gone = set(self._previous_sides) - current_ids
        for pid in gone:
            del self._previous_sides[pid]
            self._last_crossing.pop(pid, None)

        return events
