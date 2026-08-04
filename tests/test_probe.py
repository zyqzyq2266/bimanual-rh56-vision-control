from hand_tracking.probe import find_responding_ids


class FakeSerial:
    def __init__(self) -> None:
        self.writes: list[bytes] = []
        self._responses = [b"", b"\xeb\x90\x02\x00"]

    def reset_input_buffer(self) -> None:
        return None

    def write(self, packet: bytes) -> None:
        self.writes.append(packet)

    def read(self, size: int) -> bytes:
        return self._responses.pop(0)


def test_find_responding_ids_reports_only_devices_that_reply():
    serial = FakeSerial()

    responses = find_responding_ids(serial, ids=[1, 2], pause_seconds=0)

    assert responses == {2: b"\xeb\x90\x02\x00"}
    assert serial.writes[0][2] == 1
    assert serial.writes[1][2] == 2
