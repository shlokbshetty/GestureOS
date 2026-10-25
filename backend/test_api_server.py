"""
Tests for APIServer REST endpoints and WebSocket functionality.
"""

from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.api_server import APIServer
from backend.state_manager import ApplicationState


class DummyEngine:
    def __init__(self):
        self.confidence_threshold = 0.70
        self.smoothing_frames = 20
        self.running = False
        self.camera = None
        self.fps_target = 30
        self.inference_latency = 12.5
        self.frame_count = 100

    def get_frame_count(self):
        return self.frame_count


class DummyRegistry:
    def __init__(self):
        self.gestures = {
            "volume_up": {
                "action": "media_key",
                "params": {"key": "volume_up"},
                "cooldown_ms": 200,
                "enabled": True,
                "display_name": "Volume Up",
            }
        }

    def get_all_gestures(self):
        return self.gestures.copy()

    def get_gesture_metadata(self, name):
        return self.gestures.get(name)

    def update_gesture(self, name, updates):
        if name in self.gestures:
            self.gestures[name].update(updates)
            return True
        return False


class DummyStateManager:
    def __init__(self):
        self.state = ApplicationState.STOPPED
        self.action_log = [
            {"gesture": "volume_up", "action": "media_key", "timestamp": 123456.0, "success": True}
        ]

    def get_status(self):
        return {
            "state": self.state.value,
            "current_gesture": "nothing",
            "last_action": None,
            "uptime_seconds": 10.0,
            "total_actions": len(self.action_log),
            "timestamp": 123456.0,
        }

    def start(self):
        if self.state == ApplicationState.STOPPED:
            self.state = ApplicationState.RUNNING
            return True
        return False

    def stop(self):
        self.state = ApplicationState.STOPPED
        return True

    def pause(self):
        if self.state == ApplicationState.RUNNING:
            self.state = ApplicationState.PAUSED
            return True
        return False

    def resume(self):
        if self.state == ApplicationState.PAUSED:
            self.state = ApplicationState.RUNNING
            return True
        return False

    def get_action_log(self, limit=100):
        return self.action_log[:limit]

    def clear_action_log(self):
        self.action_log.clear()


@pytest.fixture
def api_server():
    engine = DummyEngine()
    registry = DummyRegistry()
    state_mgr = DummyStateManager()
    server = APIServer(state_mgr, engine, registry)
    return server


@pytest.fixture
def client(api_server):
    return TestClient(api_server.app)


def test_get_status(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == "stopped"
    assert "uptime_seconds" in data


def test_start_and_stop_lifecycle(client):
    # Start
    res_start = client.post("/api/start")
    assert res_start.status_code == 200
    assert res_start.json()["state"] == "running"

    # Start again should conflict (409)
    res_start_again = client.post("/api/start")
    assert res_start_again.status_code == 409

    # Pause
    res_pause = client.post("/api/pause")
    assert res_pause.status_code == 200
    assert res_pause.json()["state"] == "paused"

    # Resume
    res_resume = client.post("/api/resume")
    assert res_resume.status_code == 200
    assert res_resume.json()["state"] == "running"

    # Stop
    res_stop = client.post("/api/stop")
    assert res_stop.status_code == 200
    assert res_stop.json()["state"] == "stopped"


def test_get_and_update_config(client, api_server):
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert data["confidence_threshold"] == 0.70
    assert data["smoothing_frames"] == 20
    assert "volume_up" in data["gestures"]

    # Update config
    update_res = client.post(
        "/api/config",
        json={"confidence_threshold": 0.85, "smoothing_frames": 25},
    )
    assert update_res.status_code == 200
    assert api_server.engine.confidence_threshold == 0.85
    assert api_server.engine.smoothing_frames == 25


def test_gestures_endpoints(client):
    res = client.get("/api/gestures")
    assert res.status_code == 200
    data = res.json()
    assert "volume_up" in data

    # Update gesture
    put_res = client.put(
        "/api/gestures/volume_up",
        json={"enabled": False, "cooldown_ms": 350},
    )
    assert put_res.status_code == 200
    assert put_res.json()["gesture"]["enabled"] is False
    assert put_res.json()["gesture"]["cooldown_ms"] == 350


def test_logs_endpoints(client):
    res = client.get("/api/logs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) == 1
    assert logs[0]["gesture"] == "volume_up"

    # Clear logs
    del_res = client.delete("/api/logs")
    assert del_res.status_code == 200
    assert client.get("/api/logs").json() == []


def test_camera_status(client):
    res = client.get("/api/camera-status")
    assert res.status_code == 200
    data = res.json()
    assert data["connected"] is False
    assert data["fps_target"] == 30
    assert data["inference_latency_ms"] == 12.5


def test_websocket_stream(client):
    with client.websocket_connect("/ws") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "connection_established"
        assert msg["data"]["state"] == "stopped"

        # Ping
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"
