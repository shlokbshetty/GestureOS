import React from 'react';
import { Sliders, ToggleLeft, ToggleRight } from 'lucide-react';
import type { GestureMetadata } from '../types';

interface ConfigPanelProps {
  confidenceThreshold: number;
  smoothingFrames: number;
  gestures: Record<string, GestureMetadata>;
  onThresholdChange: (val: number) => void;
  onSmoothingChange: (val: number) => void;
  onToggleGesture: (name: string, enabled: boolean) => void;
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({
  confidenceThreshold,
  smoothingFrames,
  gestures,
  onThresholdChange,
  onSmoothingChange,
  onToggleGesture,
}) => {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }} id="config-panel">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Sliders size={18} color="var(--accent-cyan)" />
        <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff' }}>Engine Tuning</h2>
      </div>

      {/* Confidence Threshold Slider */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.4rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Confidence Filter</span>
          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', fontWeight: 600 }}>
            {(confidenceThreshold * 100).toFixed(0)}%
          </span>
        </div>
        <input
          id="slider-confidence-threshold"
          type="range"
          min="50"
          max="95"
          value={Math.round(confidenceThreshold * 100)}
          onChange={(e) => onThresholdChange(Number(e.target.value) / 100)}
          style={{ width: '100%', accentColor: 'var(--accent-cyan)', cursor: 'pointer' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>
          <span>50% (Loose)</span>
          <span>95% (Strict)</span>
        </div>
      </div>

      {/* Smoothing Frames Slider */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.4rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Smoothing Window</span>
          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', fontWeight: 600 }}>
            {smoothingFrames} frames
          </span>
        </div>
        <input
          id="slider-smoothing-frames"
          type="range"
          min="5"
          max="40"
          value={smoothingFrames}
          onChange={(e) => onSmoothingChange(Number(e.target.value))}
          style={{ width: '100%', accentColor: 'var(--accent-cyan)', cursor: 'pointer' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>
          <span>5 (Fastest)</span>
          <span>40 (Max Stability)</span>
        </div>
      </div>

      {/* Gesture Enable/Disable Toggles */}
      <div>
        <h3 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.65rem' }}>
          Active Gesture Interception
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', maxHeight: '220px', overflowY: 'auto' }}>
          {Object.entries(gestures).map(([name, meta]) => {
            if (name === 'nothing') return null;
            return (
              <div
                key={name}
                id={`toggle-row-${name}`}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.45rem 0.65rem',
                  background: 'var(--bg-card-glass)',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                }}
              >
                <span>{meta.display_name}</span>
                <button
                  id={`btn-toggle-${name}`}
                  onClick={() => onToggleGesture(name, !meta.enabled)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    color: meta.enabled ? 'var(--accent-emerald)' : 'var(--text-dim)',
                    display: 'flex',
                    alignItems: 'center',
                  }}
                  title={meta.enabled ? 'Disable Gesture' : 'Enable Gesture'}
                >
                  {meta.enabled ? <ToggleRight size={22} /> : <ToggleLeft size={22} />}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
