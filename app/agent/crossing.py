import time


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
                    if prev > 0 and side <= 0:
                        events.append({"id": pid, "direction": "entry"})
                        self._last_crossing[pid] = now
                    elif prev < 0 and side >= 0:
                        events.append({"id": pid, "direction": "exit"})
                        self._last_crossing[pid] = now

            self._previous_sides[pid] = side

        # Clean up IDs that left the frame
        gone = set(self._previous_sides) - current_ids
        for pid in gone:
            del self._previous_sides[pid]
            self._last_crossing.pop(pid, None)

        return events
