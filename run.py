"""
GestureOS Unified Product Launcher.

Orchestrates the entire product stack with a single command:
1. Bootstraps the FastAPI REST & WebSocket backend service (port 5000)
2. Waits for backend health verification
3. Starts the modern React/Vite frontend dashboard (port 3000)
4. Opens the browser to http://localhost:3000
5. Manages unified lifecycle and graceful shutdown on Ctrl+C / SIGINT
"""

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"


def check_backend_health(url: str = "http://127.0.0.1:5000/api/status", timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="GestureOS Product Launcher")
    parser.add_argument("--backend-only", action="store_true", help="Launch only the backend service")
    parser.add_argument("--frontend-only", action="store_true", help="Launch only the frontend dashboard")
    parser.add_argument("--mock", action="store_true", help="Run with simulated mock vision engine")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    parser.add_argument("--port", type=int, default=5000, help="Backend port (default: 5000)")
    parser.add_argument("--frontend-port", type=int, default=3000, help="Frontend port (default: 3000)")
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("  GestureOS — Next-Generation AI Hand Gesture Control System")
    print("=" * 65 + "\n")

    processes = []

    def cleanup(signum=None, frame=None):
        print("\n[GestureOS Launcher] Shutting down all services...")
        for p in processes:
            if p.poll() is None:
                try:
                    p.terminate()
                    p.wait(timeout=2)
                except Exception:
                    p.kill()
        print("[GestureOS Launcher] All processes stopped. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    python_executable = sys.executable

    # 1. Start Backend
    if not args.frontend_only:
        backend_cmd = [python_executable, "-m", "backend.main", "--port", str(args.port)]
        if args.mock:
            backend_cmd.append("--mock")

        print(f"[Launcher] Starting Backend service on port {args.port}...")
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        processes.append(backend_proc)

        # Wait for backend to be ready
        print("[Launcher] Awaiting backend healthcheck confirmation...", end="", flush=True)
        ready = False
        for _ in range(30):
            if check_backend_health(f"http://127.0.0.1:{args.port}/api/status", timeout=0.5):
                ready = True
                break
            time.sleep(0.3)
            print(".", end="", flush=True)

        if ready:
            print(" [READY]")
        else:
            print(" [TIMEOUT WARNING: continuing anyway]")

    # 2. Start Frontend
    if not args.backend_only and FRONTEND_DIR.exists():
        print(f"[Launcher] Starting Frontend dashboard on port {args.frontend_port}...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        frontend_proc = subprocess.Popen(
            [npm_cmd, "run", "dev", "--", "--port", str(args.frontend_port)],
            cwd=str(FRONTEND_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        processes.append(frontend_proc)
        time.sleep(1.5)

        target_url = f"http://localhost:{args.frontend_port}"
        print(f"\n GestureOS Dashboard active at: {target_url}")
        print(f" REST API & WebSocket active at: http://localhost:{args.port}\n")

        if not args.no_browser:
            print("[Launcher] Launching default web browser...")
            webbrowser.open(target_url)

    print("[Launcher] GestureOS is running! Press Ctrl+C at any time to stop.\n")

    # Monitor processes
    try:
        while True:
            for p in processes:
                if p.poll() is not None:
                    print(f"[Launcher Warning] A managed process exited with code {p.returncode}")
                    cleanup()
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
