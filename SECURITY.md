# Security Policy (`SECURITY.md`)

## 1. Supported Versions

Because GestureOS synthesizes operating system keyboard and mouse events (`pynput`, `pyautogui`) and exposes a local FastAPI control server (`127.0.0.1:5000`), security patches are prioritized on the active release line:

| Version | Supported | Python Compatibility | Status |
| :--- | :--- | :--- | :--- |
| `` | Yes | Python `3.10` – `3.12` | Active Production Release |


---

## 2. Security Model & Deployment Boundaries

- **Local Loopback Binding (`127.0.0.1`)**: By default, `backend/main.py` and `backend/api_server.py` bind exclusively to `127.0.0.1:5000` so that LAN/WAN hosts cannot invoke `/api/start`, `/api/config`, or `/api/gestures/{gesture_name}` to trigger arbitrary virtual HID keystrokes. Do **not** bind `--host 0.0.0.0` on untrusted networks without placing an authenticated reverse proxy in front of the service.
- **No External Frame Transmission**: All webcam frames (`640x480` BGR) are processed in-memory by `SkinDetector` and `OptimizedGestureModel` and immediately garbage-collected. No video frames or images are persisted to disk or transmitted over the network.
- **Constrained Keybinding Map**: `WindowsController._get_key_object()` (`backend/controller.py`) restricts synthesized keys to an explicit allowlist of modifier, navigation, function (`f1`-`f12`), media, and control keys. Arbitrary shell command execution is never permitted through `config.json` or REST updates.

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability in GestureOS (such as arbitrary key injection, path traversal in configuration loading, or unauthorized cross-origin WebSocket hijacking):

1. **Do NOT open a public GitHub issue.**
2. Email **shettyshlok87@gmail.com** (or contact the repository maintainer via GitHub Private Vulnerability Reporting) with the subject `[SECURITY] GestureOS Vulnerability Report`.
3. Include:
   - Affected component (`backend/api_server.py`, `backend/controller.py`, `backend/utils/config.py`, etc.)
   - Step-by-step proof-of-concept (PoC) reproduction instructions
   - Potential impact and suggested remediation (if available)

---

## 4. Disclosure & Response Timeline

| Stage | Target SLA | Description |
| :--- | :--- | :--- |
| **Initial Acknowledgment** | Within **48 hours** | Confirmation of receipt and assignment of a tracking ID |
| **Triage & Validation** | Within **5 business days** | Reproduction of the issue and severity assessment (CVSS v3.1) |
| **Patch Development** | Within **14 days** | Fix implementation, regression test addition in `pytest`, and review |
| **Coordinated Disclosure** | Upon release | Publication of patched release and credit in `CHANGELOG.md` |
