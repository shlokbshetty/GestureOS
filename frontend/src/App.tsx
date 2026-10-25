import React, { useEffect, useState, useCallback } from 'react';
import { Header } from './components/Header';
import { ControlPanel } from './components/ControlPanel';
import { CameraHUD } from './components/CameraHUD';
import { GestureCards } from './components/GestureCards';
import { ActionLogFeed } from './components/ActionLogFeed';
import { ConfigPanel } from './components/ConfigPanel';
import { useWebSocket } from './hooks/useWebSocket';
import type { WebSocketEvent } from './hooks/useWebSocket';
import {
  fetchStatus,
  fetchConfig,
  fetchLogs,
  fetchCameraStatus,
  startEngine,
  stopEngine,
  pauseEngine,
  resumeEngine,
  updateConfig,
  updateGesture,
  clearLogs,
} from './services/api';
import type { ActionLogEntry, ApplicationState, CameraStatus, GestureMetadata } from './types';

export const App: React.FC = () => {
  const [state, setState] = useState<ApplicationState>('stopped');
  const [uptimeSeconds, setUptimeSeconds] = useState<number>(0);
  const [totalActions, setTotalActions] = useState<number>(0);
  const [currentGesture, setCurrentGesture] = useState<string>('nothing');
  const [confidence, setConfidence] = useState<number>(0.0);
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.70);
  const [smoothingFrames, setSmoothingFrames] = useState<number>(20);
  const [gestures, setGestures] = useState<Record<string, GestureMetadata>>({});
  const [logs, setLogs] = useState<ActionLogEntry[]>([]);
  const [cameraStatus, setCameraStatus] = useState<CameraStatus>({
    connected: false,
    running: false,
    fps_target: 30,
    inference_latency_ms: 0.2,
    frame_count: 0,
  });

  // Handle incoming real-time WebSocket events
  const handleWebSocketEvent = useCallback((event: WebSocketEvent) => {
    if (event.type === 'gesture_detected') {
      setCurrentGesture(event.data.gesture);
      setConfidence(event.data.confidence);
      
      // Auto-clear gesture badge after 1.5s of no updates
      setTimeout(() => {
        setCurrentGesture('nothing');
        setConfidence(0);
      }, 1500);
    } else if (event.type === 'state_changed') {
      setState(event.data.new_state);
    } else if (event.type === 'action_executed') {
      setLogs((prev) => [event.data, ...prev.slice(0, 49)]);
      setTotalActions((c) => c + 1);
    } else if (event.type === 'connection_established') {
      if (event.data?.state) {
        setState(event.data.state);
      }
    }
  }, []);

  const { isConnected } = useWebSocket(handleWebSocketEvent);

  // Initial Data Fetching
  const loadInitialData = async () => {
    try {
      const [statusData, configData, logsData, camData] = await Promise.all([
        fetchStatus(),
        fetchConfig(),
        fetchLogs(50),
        fetchCameraStatus(),
      ]);

      setState(statusData.state);
      setUptimeSeconds(statusData.uptime_seconds);
      setTotalActions(statusData.total_actions);
      setCurrentGesture(statusData.current_gesture || 'nothing');

      setGestures(configData.gestures || {});
      setConfidenceThreshold(configData.confidence_threshold || 0.70);
      setSmoothingFrames(configData.smoothing_frames || 20);

      setLogs(logsData || []);
      setCameraStatus(camData);
    } catch (err) {
      console.warn('API service not available yet (mocking default state):', err);
    }
  };

  useEffect(() => {
    loadInitialData();
    const interval = setInterval(() => {
      fetchStatus().then((s) => {
        setState(s.state);
        setUptimeSeconds(s.uptime_seconds);
        setTotalActions(s.total_actions);
      }).catch(() => {});
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // Handlers
  const handleStart = async () => {
    const res = await startEngine();
    setState(res.state as ApplicationState);
  };

  const handleStop = async () => {
    const res = await stopEngine();
    setState(res.state as ApplicationState);
    setCurrentGesture('nothing');
    setConfidence(0);
  };

  const handlePause = async () => {
    const res = await pauseEngine();
    setState(res.state as ApplicationState);
  };

  const handleResume = async () => {
    const res = await resumeEngine();
    setState(res.state as ApplicationState);
  };

  const handleThresholdChange = async (val: number) => {
    setConfidenceThreshold(val);
    await updateConfig({ confidence_threshold: val });
  };

  const handleSmoothingChange = async (val: number) => {
    setSmoothingFrames(val);
    await updateConfig({ smoothing_frames: val });
  };

  const handleToggleGesture = async (name: string, enabled: boolean) => {
    setGestures((prev) => ({
      ...prev,
      [name]: { ...prev[name], enabled },
    }));
    await updateGesture(name, { enabled });
  };

  const handleClearLogs = async () => {
    await clearLogs();
    setLogs([]);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }} id="app-root">
      <Header
        state={state}
        latencyMs={cameraStatus.inference_latency_ms || 0.2}
        cameraConnected={cameraStatus.connected}
        wsConnected={isConnected}
      />

      <main className="dashboard-grid">
        {/* Left Column: Lifecycle & Tuning */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <ControlPanel
            state={state}
            uptimeSeconds={uptimeSeconds}
            totalActions={totalActions}
            fps={cameraStatus.fps_target || 30}
            onStart={handleStart}
            onStop={handleStop}
            onPause={handlePause}
            onResume={handleResume}
          />

          <ConfigPanel
            confidenceThreshold={confidenceThreshold}
            smoothingFrames={smoothingFrames}
            gestures={gestures}
            onThresholdChange={handleThresholdChange}
            onSmoothingChange={handleSmoothingChange}
            onToggleGesture={handleToggleGesture}
          />
        </section>

        {/* Center Column: Camera HUD & Gesture Library */}
        <section style={{ display: 'flex', flexDirection: 'column' }}>
          <CameraHUD
            state={state}
            currentGesture={currentGesture}
            confidence={confidence}
          />

          <GestureCards
            gestures={gestures}
            activeGesture={currentGesture}
          />
        </section>

        {/* Right Column: Live Action Stream */}
        <section style={{ display: 'flex', flexDirection: 'column' }}>
          <ActionLogFeed
            logs={logs}
            onClear={handleClearLogs}
          />
        </section>
      </main>
    </div>
  );
};

export default App;
