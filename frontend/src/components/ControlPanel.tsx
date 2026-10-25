import React, { useState } from 'react';
import { Play, Pause, Square, RefreshCw, Clock, Zap, Target } from 'lucide-react';
import type { ApplicationState } from '../types';

interface ControlPanelProps {
  state: ApplicationState;
  uptimeSeconds: number;
  totalActions: number;
  fps: number;
  onStart: () => Promise<void>;
  onStop: () => Promise<void>;
  onPause: () => Promise<void>;
  onResume: () => Promise<void>;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({
  state,
  uptimeSeconds,
  totalActions,
  fps,
  onStart,
  onStop,
  onPause,
  onResume,
}) => {
  const [loading, setLoading] = useState<boolean>(false);

  const formatUptime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAction = async (action: () => Promise<void>) => {
    setLoading(true);
    try {
      await action();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }} id="control-panel">
      <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.4rem', color: '#ffffff' }}>
        Control Center
      </h2>
      <p style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginBottom: '1.25rem' }}>
        Manage engine lifecycle and gesture interception
      </p>

      {/* Button Controls */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {state === 'stopped' ? (
          <button
            id="btn-start"
            className="btn-primary btn-start"
            disabled={loading}
            onClick={() => handleAction(onStart)}
          >
            {loading ? <RefreshCw size={18} className="spin" /> : <Play size={18} />}
            <span>Start Gesture Engine</span>
          </button>
        ) : (
          <button
            id="btn-stop"
            className="btn-primary btn-stop"
            disabled={loading}
            onClick={() => handleAction(onStop)}
          >
            {loading ? <RefreshCw size={18} className="spin" /> : <Square size={18} />}
            <span>Stop Engine</span>
          </button>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <button
            id="btn-pause"
            className="btn-primary btn-pause"
            disabled={loading || state !== 'running'}
            onClick={() => handleAction(onPause)}
          >
            <Pause size={16} />
            <span>Pause</span>
          </button>

          <button
            id="btn-resume"
            className="btn-primary"
            style={{
              background: 'rgba(30, 41, 59, 0.8)',
              borderColor: 'rgba(56, 189, 248, 0.4)',
              color: 'var(--accent-cyan)',
            }}
            disabled={loading || state !== 'paused'}
            onClick={() => handleAction(onResume)}
          >
            <Play size={16} />
            <span>Resume</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="metrics-row">
        <div className="metric-pill" id="uptime-pill">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
            <Clock size={12} color="var(--text-dim)" />
            <span className="metric-label">Uptime</span>
          </div>
          <div className="metric-value">{formatUptime(uptimeSeconds)}</div>
        </div>

        <div className="metric-pill" id="actions-pill">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
            <Zap size={12} color="var(--text-dim)" />
            <span className="metric-label">Actions</span>
          </div>
          <div className="metric-value">{totalActions}</div>
        </div>

        <div className="metric-pill" id="fps-pill">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
            <Target size={12} color="var(--text-dim)" />
            <span className="metric-label">Target FPS</span>
          </div>
          <div className="metric-value">{fps}</div>
        </div>
      </div>
    </div>
  );
};
