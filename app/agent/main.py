import argparse
import logging
import yaml

from agent.config import AgentConfig
from agent.capture import CameraCapture
from agent.tracker import PeopleTracker
from agent.crossing import CrossingDetector
from agent.display import draw_overlays, show_frame, cleanup
from agent.sender import send_or_queue, start_retry_thread

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def main():
    """Run the edge detection agent's main loop.

    Loads configuration, initializes the YOLO tracker and crossing
    detector, then continuously reads camera frames to detect people
    and report line-crossing events to the backend server.  Events
    that fail to send are queued locally and retried in a background
    thread.

    Use ``--show`` to open a live OpenCV window displaying the camera
    feed with crossing line and bounding-box overlays.

    Raises:
        RuntimeError: If the configured camera source cannot be opened.
    """
    parser = argparse.ArgumentParser(description="People counter detection agent")
    parser.add_argument("--show", action="store_true", help="Show live detection window")
    args = parser.parse_args()

    config = AgentConfig.load()
    log.info("Config loaded: camera_source=%s, camera_id=%s", config.camera_source, config.camera_id)
    log.info("Current config:\n%s", yaml.dump(vars(config), default_flow_style=False))
    tracker = PeopleTracker(config)
    detector = CrossingDetector(config.line_start, config.line_end)
    start_retry_thread(config)

    with CameraCapture(config.camera_source) as cam:
        log.info("Camera opened, starting detection loop")
        while True:
            frame = cam.read_frame()
            if frame is None:
                log.warning("Failed to read frame, skipping")
                continue

            people = tracker.track(frame)
            events = detector.update(people)

            for event in events:
                sent = send_or_queue(config, event["direction"])
                status = "sent" if sent else "queued"
                log.info(
                    "Crossing: person %d → %s (%s)",
                    event["id"], event["direction"], status,
                )

            if args.show:
                draw_overlays(frame, config.line_start, config.line_end, people)
                if not show_frame(frame):
                    log.info("Display window closed")
                    break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Shutting down")
    finally:
        cleanup()
