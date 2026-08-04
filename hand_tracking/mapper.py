from __future__ import annotations

import math
from collections.abc import Sequence


Point = Sequence[float]
FINGER_CURL_GAIN = 13.0
THUMB_FULL_FLEX_ANGLE = 70.0


def _angle(a: Point, b: Point, c: Point) -> float:
    first = tuple(a[index] - b[index] for index in range(3))
    second = tuple(c[index] - b[index] for index in range(3))
    first_length = math.sqrt(sum(value * value for value in first))
    second_length = math.sqrt(sum(value * value for value in second))
    if first_length == 0 or second_length == 0:
        return 180.0
    cosine = sum(first[index] * second[index] for index in range(3)) / (first_length * second_length)
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def _curl(landmarks: Sequence[Point], mcp: int, pip: int, dip: int, tip: int) -> int:
    angle = (_angle(landmarks[mcp], landmarks[pip], landmarks[dip]) + _angle(landmarks[pip], landmarks[dip], landmarks[tip])) / 2
    return max(0, min(1000, round((180.0 - angle) * FINGER_CURL_GAIN)))


def _thumb_curl(landmarks: Sequence[Point]) -> int:
    thumb_angle = _angle(landmarks[2], landmarks[3], landmarks[4])
    return max(0, min(1000, round((thumb_angle - THUMB_FULL_FLEX_ANGLE) * 1000.0 / (180.0 - THUMB_FULL_FLEX_ANGLE))))


def _thumb_rotation(landmarks: Sequence[Point]) -> int:
    """Map the signed thumb-base spread from the palm plane to 0..1000."""
    palm_x = landmarks[5][0] - landmarks[17][0]
    palm_y = landmarks[5][1] - landmarks[17][1]
    thumb_x = landmarks[2][0] - landmarks[1][0]
    thumb_y = landmarks[2][1] - landmarks[1][1]
    cross = palm_x * thumb_y - palm_y * thumb_x
    dot = palm_x * thumb_x + palm_y * thumb_y
    spread_degrees = math.degrees(math.atan2(cross, dot))
    return max(0, min(1000, round((spread_degrees + 90.0) * 1000.0 / 180.0)))


def map_left_hand(landmarks: Sequence[Point], invert_axes: Sequence[bool]) -> list[int]:
    """Map 21 MediaPipe left-hand landmarks to RH56's six-axis order."""
    if len(landmarks) != 21:
        raise ValueError("expected 21 hand landmarks")
    if len(invert_axes) != 6:
        raise ValueError("expected six inversion flags")
    angles = [
        _curl(landmarks, 17, 18, 19, 20),
        _curl(landmarks, 13, 14, 15, 16),
        _curl(landmarks, 9, 10, 11, 12),
        _curl(landmarks, 5, 6, 7, 8),
        _thumb_curl(landmarks),
        _thumb_rotation(landmarks),
    ]
    return [1000 - value if invert_axes[index] else value for index, value in enumerate(angles)]
