from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AgentConfig:
    camera_source: str | int
    server_url: str
    camera_id: str
    line_start: tuple[int, int]
    line_end: tuple[int, int]
    yolo_model: str = "yolov8n.pt"
    yolo_confidence: float = 0.4

    @classmethod
    def load(cls, path: str | Path = None) -> "AgentConfig":
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
        )