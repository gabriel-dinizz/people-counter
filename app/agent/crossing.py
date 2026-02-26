import time


class CrossingDetector:
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
