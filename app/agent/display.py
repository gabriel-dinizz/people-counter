import cv2

WINDOW_NAME = "People Counter"
LINE_COLOR = (0, 255, 0)
BOX_COLOR = (255, 180, 0)
TEXT_COLOR = (255, 255, 255)


def draw_overlays(frame, line_start, line_end, people):
    """Draw crossing line and bounding boxes with IDs on the frame."""
    cv2.line(frame, line_start, line_end, LINE_COLOR, 2)

    for person in people:
        x1, y1, x2, y2 = person["bbox"]
        pid = person["id"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOR, 2)
        cv2.putText(
            frame, f"ID {pid}", (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2,
        )

    return frame


def show_frame(frame):
    """Display frame in an OpenCV window. Returns False if user wants to quit."""
    cv2.imshow(WINDOW_NAME, frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:
        return False
    if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
        return False
    return True


def cleanup():
    cv2.destroyAllWindows()
