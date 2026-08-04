from __future__ import annotations

import argparse
import time
from collections.abc import Iterable

import serial

from hand_tracking.rh56 import build_read_packet


ACTUAL_ANGLES_ADDRESS = 1546
ACTUAL_ANGLES_LENGTH = 12


def find_responding_ids(serial_port, ids: Iterable[int], pause_seconds: float = 0.03) -> dict[int, bytes]:
    responses: dict[int, bytes] = {}
    for hand_id in ids:
        serial_port.reset_input_buffer()
        serial_port.write(build_read_packet(hand_id, ACTUAL_ANGLES_ADDRESS, ACTUAL_ANGLES_LENGTH))
        if pause_seconds:
            time.sleep(pause_seconds)
        response = serial_port.read(64)
        if response:
            responses[hand_id] = response
    return responses


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only RH56 device-ID probe. It does not move the hand.")
    parser.add_argument("--port", default="COM4", help="USB-RS485 port to probe")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--timeout", type=float, default=0.03, help="Seconds to wait for each reply")
    args = parser.parse_args()

    with serial.Serial(args.port, args.baudrate, timeout=args.timeout) as port:
        responses = find_responding_ids(port, range(1, 255), pause_seconds=args.timeout)
    if not responses:
        print(f"No RH56 response on {args.port} at {args.baudrate} baud.")
        return 1
    for hand_id, response in responses.items():
        print(f"RH56 response: port={args.port} hand_id={hand_id} bytes={response.hex(' ')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
