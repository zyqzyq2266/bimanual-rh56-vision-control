from __future__ import annotations

import argparse
import time
from collections.abc import Sequence
from pathlib import Path

from hand_tracking.app import TrackingApp, default_model_path
from hand_tracking.config import TrackingConfig
from hand_tracking.rh56 import RH56Serial


class DualTrackingApp:
    """Route mirrored camera labels to independent left and right controllers."""

    def __init__(
        self,
        left_config: TrackingConfig,
        right_config: TrackingConfig,
        left_controller,
        right_controller,
    ) -> None:
        self.left = TrackingApp(left_config, left_controller)
        self.right = TrackingApp(right_config, right_controller)

    def process_hand(self, handedness: str, landmarks: Sequence[Sequence[float]], now: float) -> None:
        # A mirrored selfie image labels the physical left hand as Right.
        if handedness == "Right":
            self.left.process_landmarks(landmarks, now)
        elif handedness == "Left":
            self.right.process_landmarks(landmarks, now)

    def process_missing(self, seen_labels: set[str]) -> None:
        if "Right" not in seen_labels:
            self.left.process_landmarks(None, 0.0)
        if "Left" not in seen_labels:
            self.right.process_landmarks(None, 0.0)

    def handle_key(self, key: int) -> bool:
        left_exit = self.left.handle_key(key)
        right_exit = self.right.handle_key(key)
        return left_exit or right_exit


def setup_window(cv2) -> None:
    window_name = "RH56 Dual-Hand Tracking"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)


def _draw_overlay(frame, app: DualTrackingApp) -> None:
    import cv2

    cv2.putText(frame, f"Left hand / COM3: {app.left.status}", (16, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
    cv2.putText(frame, f"Right hand / COM4: {app.right.status}", (16, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 180, 0), 2)
    cv2.putText(frame, "Space: open both hands | Esc: exit", (16, 86), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def run_camera(app: DualTrackingApp, camera_index: int, model_path: Path | None = None) -> None:
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    model_path = model_path or default_model_path()
    if not model_path.is_file():
        raise FileNotFoundError(f"HandLandmarker model not found: {model_path}")
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        raise RuntimeError(f"cannot open camera index {camera_index}")
    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        min_tracking_confidence=0.6,
    )
    landmarker = vision.HandLandmarker.create_from_options(options)
    setup_window(cv2)
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                raise RuntimeError("camera frame capture failed")
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            result = landmarker.detect_for_video(image, int(time.monotonic() * 1000))
            seen_labels: set[str] = set()
            for hand_landmarks, categories in zip(result.hand_landmarks, result.handedness):
                handedness = categories[0].category_name
                seen_labels.add(handedness)
                height, width = frame.shape[:2]
                for point in hand_landmarks:
                    cv2.circle(frame, (int(point.x * width), int(point.y * height)), 3, (0, 255, 255), -1)
                app.process_hand(handedness, [(point.x, point.y, point.z) for point in hand_landmarks], time.monotonic())
            app.process_missing(seen_labels)
            _draw_overlay(frame, app)
            cv2.imshow("RH56 Dual-Hand Tracking", frame)
            if app.handle_key(cv2.waitKey(1) & 0xFF):
                return
    finally:
        landmarker.close()
        camera.release()
        cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="Track two hands and control two RH56 devices.")
    parser.add_argument("--left-config", required=True, help="Left-hand YAML or JSON configuration")
    parser.add_argument("--right-config", required=True, help="Right-hand YAML or JSON configuration")
    parser.add_argument("--camera", type=int, default=0, help="OpenCV camera index")
    parser.add_argument("--no-serial", action="store_true", help="Preview camera tracking without opening COM ports")
    args = parser.parse_args()
    left_config = TrackingConfig.load(args.left_config)
    right_config = TrackingConfig.load(args.right_config)

    class PreviewController:
        def set_angles(self, values: list[int]) -> None:
            return None

    left_controller = PreviewController() if args.no_serial else RH56Serial(left_config.serial_port, left_config.baudrate, left_config.hand_id)
    right_controller = PreviewController() if args.no_serial else RH56Serial(right_config.serial_port, right_config.baudrate, right_config.hand_id)
    if not args.no_serial:
        left_controller.open()
        try:
            right_controller.open()
        except Exception:
            left_controller.close()
            raise
    try:
        run_camera(DualTrackingApp(left_config, right_config, left_controller, right_controller), args.camera)
    finally:
        if not args.no_serial:
            right_controller.close()
            left_controller.close()


if __name__ == "__main__":
    main()
