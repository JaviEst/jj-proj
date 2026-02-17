from __future__ import annotations

import socket
import subprocess
import sys
import time
from contextlib import closing

import httpx
import pytest

pytestmark = pytest.mark.e2e_backend


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_ready(base_url: str, timeout_s: float = 20.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            response = httpx.get(f"{base_url}/health", timeout=1.0)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    raise TimeoutError("Backend did not start in time")


def test_backend_http_stack_e2e() -> None:
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "asset_ltv.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        _wait_for_ready(base_url)

        health = httpx.get(f"{base_url}/health", timeout=5.0)
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}

        invalid = httpx.post(
            f"{base_url}/v1/analyze",
            json={
                "asset": "BTC",
                "source": "stooq",
                "symbol": "btcusd",
                "entry_ltv": 0.5,
                "liquidation_ltv": 0.7,
                "margin_call_ltv": 0.7,
                "safety_buffer": 0.05,
            },
            timeout=5.0,
        )
        assert invalid.status_code == 400

        metrics = httpx.get(f"{base_url}/metrics", timeout=5.0)
        assert metrics.status_code == 200
        assert "# HELP" in metrics.text
    finally:
        process.terminate()
        process.wait(timeout=10)
