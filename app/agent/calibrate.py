import cv2
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"

points = []


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 2:
        points.append((x, y))
        print(f"Point {len(points)}: ({x}, {y})")
        if len(points) == 2:
            print("Line drawn. Press 's' to save, 'r' to reset, 'q' to quit.")


def main():
    """Launch an interactive GUI for defining the crossing line used by the people counter.

    Opens a live camera feed where the user clicks two points to define a
    crossing line. The line can then be persisted to ``config.yaml`` so
    the detection agent knows where to count crossings.

    Keyboard controls within the GUI window:
        s — save the current line to *config.yaml* and exit.
        r — discard selected points and start over.
        q / Escape — quit without saving.

    Raises:
        RuntimeError: If the camera source specified in *config.yaml*
            cannot be opened.
    """
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    print("=== Current config ===")
    print(yaml.dump(config, default_flow_style=False), end="")
    print("======================")

    cap = cv2.VideoCapture(config["camera_source"])
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera: {config['camera_source']}")

    cv2.namedWindow("Calibrate")
    cv2.setMouseCallback("Calibrate", on_mouse)

    print("=== Line Calibration ===")
    print("Click two points on the video to define the crossing line.")
    print("  s — save line to config.yaml")
    print("  r — reset points")
    print("  q — quit without saving")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        for pt in points:
            cv2.circle(frame, pt, 5, (0, 255, 0), -1)

        if len(points) == 2:
            cv2.line(frame, points[0], points[1], (0, 255, 0), 2)

        cv2.imshow("Calibrate", frame)
        key = cv2.waitKey(30) & 0xFF

        # Also quit if window is closed via X button
        if cv2.getWindowProperty("Calibrate", cv2.WND_PROP_VISIBLE) < 1:
            print("Window closed.")
            break

        if key == ord("q") or key == 27:  # q or Escape
            print("Quit without saving.")
            break

        if key == ord("r"):
            points.clear()
            print("Points reset. Click two new points.")

        if key == ord("s"):
            if len(points) < 2:
                print("Need two points before saving.")
            else:
                config["line"] = {
                    "start": list(points[0]),
                    "end": list(points[1]),
                }
                with open(CONFIG_PATH, "w") as f:
                    yaml.safe_dump(config, f, default_flow_style=False)
                print(f"\n=== Saved to {CONFIG_PATH} ===")
                print(f"  line start: {list(points[0])}")
                print(f"  line end:   {list(points[1])}")
                print("Run 'python -m agent.main' to start detection.")
                break

    cap.release()
    cv2.destroyAllWindows()
    print("Camera released. Done.")


if __name__ == "__main__":
    main()
