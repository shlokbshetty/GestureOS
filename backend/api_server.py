"""
FastAPI REST API and WebSocket Server for GestureOS.

Provides HTTP REST endpoints for dashboard control and monitoring,
and WebSocket streaming for real-time gesture, state, and action events.

Requirements: 5.0, 6.2, 13.0, 16.7
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from backend.utils.logger import get_logger


class ConfigUpdateRequest(BaseModel):
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    smoothing_frames: Optional[int] = Field(None, ge=1, le=100)
    gestures: Optional[Dict[str, Dict[str, Any]]] = None


class GestureUpdateRequest(BaseModel):
    action: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    cooldown_ms: Optional[int] = Field(None, ge=0)
    enabled: Optional[bool] = None
    display_name: Optional[str] = None
    description: Optional[str] = None


class APIServer:
    """
    FastAPI server providing REST endpoints and WebSocket event streaming.
    
    Attributes:
        state_manager: StateManager instance
        engine: GestureEngine instance
        registry: GestureRegistry instance
        logger: Logger instance
        port: Server port (default 5000)
        app: FastAPI application instance
        websocket_clients: Set of connected WebSocket clients
    """
    
    def __init__(
        self,
        state_manager: Any,
        engine: Any,
        registry: Any,
        logger: Optional[logging.Logger] = None,
        host: str = "127.0.0.1",
        port: int = 5000,
    ):
        self.state_manager = state_manager
        self.engine = engine
        self.registry = registry
        self.logger = logger or get_logger("api_server")
        self.host = host
        self.port = port
        
        self.websocket_clients: Set[WebSocket] = set()
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.server: Optional[uvicorn.Server] = None
        
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            self.loop = asyncio.get_running_loop()
            self.logger.info("API server event loop initialized")
            yield

        self.app = FastAPI(
            title="GestureOS API Server",
            description="Control and monitoring REST API & WebSocket service",
            version="1.0.0",
            lifespan=lifespan,
        )
        
        self.setup_middleware()
        self.setup_routes()
    
    def setup_middleware(self) -> None:
        """Configure CORS middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self) -> None:
        """Define REST and WebSocket endpoints."""
        
        @self.app.get("/api/status")
        async def get_status():
            try:
                return self.state_manager.get_status()
            except Exception as e:
                self.logger.error(f"Error fetching status: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.post("/api/start")
        async def start():
            try:
                success = self.state_manager.start()
                curr_state = (
                    self.state_manager.state.value
                    if hasattr(self.state_manager.state, "value")
                    else str(self.state_manager.state)
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Cannot start from state '{curr_state}'",
                    )
                return {"success": True, "state": curr_state}
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Start failed: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.post("/api/stop")
        async def stop():
            try:
                success = self.state_manager.stop()
                curr_state = (
                    self.state_manager.state.value
                    if hasattr(self.state_manager.state, "value")
                    else str(self.state_manager.state)
                )
                return {"success": success, "state": curr_state}
            except Exception as e:
                self.logger.error(f"Stop failed: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.post("/api/pause")
        async def pause():
            try:
                success = self.state_manager.pause()
                curr_state = (
                    self.state_manager.state.value
                    if hasattr(self.state_manager.state, "value")
                    else str(self.state_manager.state)
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Cannot pause from state '{curr_state}'",
                    )
                return {"success": True, "state": curr_state}
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Pause failed: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.post("/api/resume")
        async def resume():
            try:
                success = self.state_manager.resume()
                curr_state = (
                    self.state_manager.state.value
                    if hasattr(self.state_manager.state, "value")
                    else str(self.state_manager.state)
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Cannot resume from state '{curr_state}'",
                    )
                return {"success": True, "state": curr_state}
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Resume failed: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.get("/api/config")
        async def get_config():
            try:
                return {
                    "gestures": self.registry.get_all_gestures(),
                    "confidence_threshold": getattr(self.engine, "confidence_threshold", 0.70),
                    "smoothing_frames": getattr(self.engine, "smoothing_frames", 20),
                }
            except Exception as e:
                self.logger.error(f"Failed to get config: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.post("/api/config")
        async def update_config(payload: ConfigUpdateRequest):
            try:
                if payload.confidence_threshold is not None:
                    self.engine.confidence_threshold = payload.confidence_threshold
                    self.logger.info(f"Updated confidence_threshold to {payload.confidence_threshold}")
                
                if payload.smoothing_frames is not None:
                    self.engine.smoothing_frames = payload.smoothing_frames
                    self.logger.info(f"Updated smoothing_frames to {payload.smoothing_frames}")
                
                if payload.gestures is not None:
                    for gesture_name, updates in payload.gestures.items():
                        self.registry.update_gesture(gesture_name, updates)
                    self.logger.info(f"Updated gestures configuration: {list(payload.gestures.keys())}")
                
                return {
                    "success": True,
                    "config": {
                        "gestures": self.registry.get_all_gestures(),
                        "confidence_threshold": getattr(self.engine, "confidence_threshold", 0.70),
                        "smoothing_frames": getattr(self.engine, "smoothing_frames", 20),
                    },
                }
            except Exception as e:
                self.logger.error(f"Failed to update config: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.get("/api/gestures")
        async def get_gestures():
            try:
                return self.registry.get_all_gestures()
            except Exception as e:
                self.logger.error(f"Failed to get gestures: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.put("/api/gestures/{gesture_name}")
        async def update_gesture(gesture_name: str, payload: GestureUpdateRequest):
            try:
                updates = {k: v for k, v in payload.model_dump().items() if v is not None}
                if not updates:
                    return {"success": True, "gesture": self.registry.get_gesture_metadata(gesture_name)}
                
                success = self.registry.update_gesture(gesture_name, updates)
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Gesture '{gesture_name}' not found",
                    )
                return {"success": True, "gesture": self.registry.get_gesture_metadata(gesture_name)}
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to update gesture '{gesture_name}': {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.get("/api/logs")
        async def get_logs(limit: int = 100):
            try:
                return self.state_manager.get_action_log(limit=limit)
            except Exception as e:
                self.logger.error(f"Failed to get logs: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.delete("/api/logs")
        async def clear_logs():
            try:
                self.state_manager.clear_action_log()
                return {"success": True, "message": "Action logs cleared"}
            except Exception as e:
                self.logger.error(f"Failed to clear logs: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.get("/api/camera-status")
        async def get_camera_status():
            try:
                camera = getattr(self.engine, "camera", None)
                camera_opened = False
                if camera is not None:
                    try:
                        camera_opened = camera.isOpened()
                    except Exception:
                        camera_opened = False
                
                return {
                    "connected": camera_opened,
                    "running": getattr(self.engine, "running", False),
                    "fps_target": getattr(self.engine, "fps_target", 30),
                    "inference_latency_ms": getattr(self.engine, "inference_latency", 0.0),
                    "frame_count": (
                        self.engine.get_frame_count()
                        if hasattr(self.engine, "get_frame_count")
                        else getattr(self.engine, "frame_count", 0)
                    ),
                }
            except Exception as e:
                self.logger.error(f"Failed to get camera status: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.websocket_clients.add(websocket)
            self.logger.info(f"WebSocket client connected. Total clients: {len(self.websocket_clients)}")
            
            # Send initial state immediately
            try:
                await websocket.send_text(
                    json.dumps({
                        "type": "connection_established",
                        "data": self.state_manager.get_status(),
                        "timestamp": time.time(),
                    })
                )
            except Exception as e:
                self.logger.warning(f"Error sending welcome packet: {e}")
            
            try:
                while True:
                    data = await websocket.receive_text()
                    try:
                        msg = json.loads(data)
                        if msg.get("type") == "ping":
                            await websocket.send_text(json.dumps({"type": "pong", "timestamp": time.time()}))
                    except Exception:
                        pass
            except WebSocketDisconnect:
                self.logger.info("WebSocket client disconnected")
            except Exception as e:
                self.logger.warning(f"WebSocket error: {e}")
            finally:
                self.websocket_clients.discard(websocket)
                self.logger.info(f"Remaining WebSocket clients: {len(self.websocket_clients)}")
    
    def broadcast_event(self, event_type: str, data: Any) -> None:
        """
        Broadcast an event to all connected WebSocket clients.
        
        Thread-safe: Can be called from any worker thread.
        
        Args:
            event_type: Event identifier (e.g. 'gesture_detected', 'state_changed')
            data: Arbitrary event payload
        """
        payload = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": time.time(),
        })
        
        # Coroutine for broadcasting
        async def _send_all():
            disconnected = set()
            for client in list(self.websocket_clients):
                try:
                    await client.send_text(payload)
                except Exception:
                    disconnected.add(client)
            for dead in disconnected:
                self.websocket_clients.discard(dead)
        
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(_send_all(), self.loop)
        else:
            try:
                # If current thread has a running loop, create task directly
                curr_loop = asyncio.get_event_loop()
                if curr_loop.is_running():
                    curr_loop.create_task(_send_all())
            except RuntimeError:
                pass
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Run the FastAPI application via uvicorn (blocking).
        
        Args:
            host: Host interface (default '127.0.0.1')
            port: Port number (default 5000)
        """
        h = host or self.host
        p = port or self.port
        self.logger.info(f"Starting API Server on {h}:{p}")
        
        config = uvicorn.Config(app=self.app, host=h, port=p, log_level="info")
        self.server = uvicorn.Server(config)
        self.server.run()
    
    def shutdown(self) -> None:
        """Gracefully shut down the server."""
        self.logger.info("Shutting down API server...")
        if self.server:
            self.server.should_exit = True
