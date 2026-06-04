import io
import sys

from app.core.logging import configure_console_encoding


class ReconfigurableStream(io.StringIO):
    def __init__(self):
        super().__init__()
        self.reconfigure_calls: list[dict] = []

    def reconfigure(self, **kwargs):
        self.reconfigure_calls.append(kwargs)


def test_configure_console_encoding_sets_utf8_with_replacement(monkeypatch):
    stdout = ReconfigurableStream()
    stderr = ReconfigurableStream()
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", stderr)

    configure_console_encoding()

    assert stdout.reconfigure_calls == [{"encoding": "utf-8", "errors": "replace"}]
    assert stderr.reconfigure_calls == [{"encoding": "utf-8", "errors": "replace"}]
