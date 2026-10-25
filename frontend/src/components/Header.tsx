import React from 'react';
import { Camera, Cpu, Radio, Sparkles } from 'lucide-react';
import type { ApplicationState } from '../types';

interface HeaderProps {
  state: ApplicationState;
  latencyMs: number;
  cameraConnected: boolean;
  wsConnected: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  state,
  latencyMs,
  cameraConnected,
  wsConnected,
}) => {
  const getStatusClass = () => {
    switch (state) {
      case 'running':
        return 'status-running';
      case 'paused':
        return 'status-paused';
      default:
        return 'status-stopped';
    }
  };

  return (
    <header className="header-container" id="app-header">
      <div className="logo-wrapper">
        <div className="logo-icon">
          <Sparkles size={22} color="#ffffff" />
        </div>
        <div>
          <h1 className="logo-title" id="app-title">GestureOS</h1>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', letterSpacing: '0.04em' }}>
            INTELLIGENT VISION AUTOMATION ENGINE
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* Latency Pill */}
        <div className="system-status-chip" title="Inference Latency" id="latency-chip">
          <Cpu size={15} color="var(--accent-cyan)" />
          <span style={{ fontFamily: 'var(--font-mono)' }}>{latencyMs.toFixed(1)} ms</span>
        </div>

        {/* Camera Status */}
        <div className="system-status-chip" title="Camera Hardware Status" id="camera-chip">
          <Camera size={15} color={cameraConnected ? 'var(--accent-emerald)' : 'var(--text-dim)'} />
          <span>{cameraConnected ? 'Camera Active' : 'Camera Idle'}</span>
        </div>

        {/* WebSocket Stream Indicator */}
        <div className="system-status-chip" title="Real-Time WebSocket Stream" id="ws-chip">
          <Radio size={15} color={wsConnected ? 'var(--accent-cyan)' : 'var(--accent-rose)'} />
          <span>{wsConnected ? 'LIVE FEED' : 'OFFLINE'}</span>
        </div>

        {/* System State Pill */}
        <div className="system-status-chip" id="system-state-chip">
          <div className={`status-dot ${getStatusClass()}`} />
          <span style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {state}
          </span>
        </div>
      </div>
    </header>
  );
};
