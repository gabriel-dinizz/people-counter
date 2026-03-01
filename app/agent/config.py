from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AgentConfig:
    """Configuration for the edge detection agent.

    Attributes:
        camera_source: Device index (int) or video file / RTSP URL (str).
        server_url: Base URL of the backend API (e.g. ``http://localhost:8000``).
        camera_id: Unique identifier for this camera, sent with every event.
        line_start: ``(x, y)`` pixel coordinate of the crossing line's start.
        line_end: ``(x, y)`` pixel coordinate of the crossing line's end.
        yolo_model: YOLOv8 model filename or path.
        yolo_confidence: Minimum detection confidence threshold (0–1).
    """

    camera_source: str | int
    server_url: str
    camera_id: str
    line_start: tuple[int, int]
    line_end: tuple[int, int]
    yolo_model: str = "yolov8n.pt"
    yolo_confidence: float = 0.4
    tracker_config: str = "botsort.yaml"

    @classmethod
    def load(cls, path: str | Path = None) -> "AgentConfig":
        """Load agent configuration from a YAML file.

        Args:
            path: Path to the YAML config file. Defaults to
                ``config.yaml`` in the same directory as this module.

        Returns:
            A fully populated ``AgentConfig`` instance.

        Raises:
            FileNotFoundError: If *path* does not exist.
            KeyError: If required keys are missing from the YAML file.
        """
        if path is None:
            path = Path(__file__).parent / "config.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(
            camera_source=data["camera_source"],
            server_url=data["server_url"],
            camera_id=data["camera_id"],
            line_start=tuple(data["line"]["start"]),
            line_end=tuple(data["line"]["end"]),
            yolo_model=data.get("yolo_model", "yolov8n.pt"),
            yolo_confidence=data.get("yolo_confidence", 0.4),
            tracker_config=data.get("tracker_config", "botsort.yaml"),
        )
