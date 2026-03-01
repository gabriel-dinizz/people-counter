import cv2
import numpy as np


class CameraCapture:
    """Context-managed wrapper around ``cv2.VideoCapture``.

    Ensures the underlying capture device is properly released when the
    context exits, even if an exception occurs.

    Args:
        camera_source: Device index (int) or video file / RTSP URL (str).

    Raises:
        RuntimeError: If the capture device cannot be opened.
    """

    def __init__(self, camera_source: int | str):
        self.cap = cv2.VideoCapture(camera_source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera: {camera_source}")

    def read_frame(self) -> np.ndarray | None:
        """Read the next frame from the capture device.

        Returns:
            The captured frame as a NumPy array, or ``None`` if the
            read failed (e.g. end of file or device error).
        """
        ret, frame = self.cap.read()
        return frame if ret else None

    def release(self) -> None:
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False
