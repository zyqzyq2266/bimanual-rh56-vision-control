from hand_tracking.config import TrackingConfig
from hand_tracking.dual_app import DualTrackingApp, setup_window


class FakeController:
    def __init__(self) -> None:
        self.commands: list[list[int]] = []

    def set_angles(self, values: list[int]) -> None:
        self.commands.append(values)


def _config(port: str, open_value: int) -> TrackingConfig:
    return TrackingConfig(
        serial_port=port,
        open_pose=[open_value] * 6,
        deadband=0,
        motion_scale=1.0,
    )


def test_mirrored_left_and_right_labels_route_to_independent_hands(monkeypatch):
    monkeypatch.setattr("hand_tracking.app.map_left_hand", lambda landmarks, invert_axes: [111] * 6)
    left_controller = FakeController()
    right_controller = FakeController()
    app = DualTrackingApp(
        left_config=_config("COM3", 300),
        right_config=_config("COM4", 700),
        left_controller=left_controller,
        right_controller=right_controller,
    )

    app.process_hand("Right", [(0.0, 0.0, 0.0)] * 21, now=0.0)
    app.process_hand("Left", [(0.0, 0.0, 0.0)] * 21, now=0.0)

    assert left_controller.commands == [[111] * 6]
    assert right_controller.commands == [[111] * 6]


def test_unknown_label_does_not_control_either_hand():
    left_controller = FakeController()
    right_controller = FakeController()
    app = DualTrackingApp(
        left_config=_config("COM3", 300),
        right_config=_config("COM4", 700),
        left_controller=left_controller,
        right_controller=right_controller,
    )

    app.process_hand("Unknown", [(0.0, 0.0, 0.0)] * 21, now=0.0)

    assert left_controller.commands == []
    assert right_controller.commands == []


def test_space_opens_both_hands():
    left_controller = FakeController()
    right_controller = FakeController()
    app = DualTrackingApp(
        left_config=_config("COM3", 300),
        right_config=_config("COM4", 700),
        left_controller=left_controller,
        right_controller=right_controller,
    )

    assert app.handle_key(ord(" ")) is False

    assert left_controller.commands == [[300] * 6]
    assert right_controller.commands == [[700] * 6]


def test_setup_window_creates_a_resizable_hd_window():
    class FakeCv2:
        WINDOW_NORMAL = 0

        def __init__(self) -> None:
            self.named: tuple[str, int] | None = None
            self.size: tuple[str, int, int] | None = None

        def namedWindow(self, name: str, mode: int) -> None:
            self.named = (name, mode)

        def resizeWindow(self, name: str, width: int, height: int) -> None:
            self.size = (name, width, height)

    cv2 = FakeCv2()

    setup_window(cv2)

    assert cv2.named == ("RH56 Dual-Hand Tracking", cv2.WINDOW_NORMAL)
    assert cv2.size == ("RH56 Dual-Hand Tracking", 1280, 720)
