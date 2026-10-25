import React from 'react';
import { Eye, Hand, ShieldCheck, Video } from 'lucide-react';
import type { ApplicationState } from '../types';

interface CameraHUDProps {
  state: ApplicationState;
  currentGesture: string;
  confidence: number;
}

export const CameraHUD: React.FC<CameraHUDProps> = ({
  state,
  currentGesture,
  confidence,
}) => {
  const isDetecting = state === 'running';

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }} id="camera-hud-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff' }}>Vision Pipeline HUD</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
            Real-time hand tracking and YCrCb segmentation feed
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <Video size={16} color="var(--accent-cyan)" />
          <span>640 x 480 @ 30 FPS</span>
        </div>
      </div>

      {/* Main Video View Box */}
      <div className="camera-view-box" id="hud-camera-box">
        {/* HUD Grid & Reticles */}
        <div className="hud-overlay" />
        <div className="hud-corner hud-corner-tl" />
        <div className="hud-corner hud-corner-tr" />
        <div className="hud-corner hud-corner-bl" />
        <div className="hud-corner hud-corner-br" />

        {/* Hand Bounding Box Target */}
        {isDetecting ? (
          <div className="hand-target-box">
            <Hand size={48} color={currentGesture !== 'nothing' ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.25)'} />
            <div style={{
              position: 'absolute',
              bottom: '-28px',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.75rem',
              color: 'var(--accent-cyan)',
              background: 'rgba(6, 182, 212, 0.15)',
              padding: '2px 8px',
              borderRadius: '4px',
              border: '1px solid rgba(6, 182, 212, 0.4)',
            }}>
              TRACKING REGION
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-dim)', zIndex: 2 }}>
            <Eye size={40} style={{ opacity: 0.3, marginBottom: '0.5rem' }} />
            <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>Engine Standby</p>
            <p style={{ fontSize: '0.78rem' }}>Start engine to begin gesture recognition</p>
          </div>
        )}

        {/* Live Gesture Detection Floating Badge */}
        {isDetecting && currentGesture !== 'nothing' && (
          <div style={{
            position: 'absolute',
            top: '20px',
            left: '20px',
            background: 'rgba(11, 15, 25, 0.85)',
            border: '1px solid var(--accent-cyan)',
            backdropFilter: 'blur(8px)',
            borderRadius: '10px',
            padding: '0.6rem 1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            boxShadow: '0 0 20px var(--accent-cyan-glow)',
            animation: 'slide-in 0.2s ease',
          }} id="active-gesture-hud-badge">
            <ShieldCheck size={20} color="var(--accent-cyan)" />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                Detected Gesture
              </div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>
                {currentGesture.replace('_', ' ').toUpperCase()}
              </div>
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '1rem',
              fontWeight: 700,
              color: 'var(--accent-emerald)',
              marginLeft: '0.5rem',
            }}>
              {(confidence * 100).toFixed(0)}%
            </div>
          </div>
        )}
      </div>

      {/* Confidence Bar */}
      <div style={{ marginTop: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.4rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Detection Confidence Gauge</span>
          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
            {(confidence * 100).toFixed(1)}%
          </span>
        </div>
        <div style={{
          width: '100%',
          height: '6px',
          background: 'rgba(255, 255, 255, 0.08)',
          borderRadius: '999px',
          overflow: 'hidden',
        }}>
          <div style={{
            width: `${Math.min(100, Math.max(0, confidence * 100))}%`,
            height: '100%',
            background: 'linear-gradient(90deg, var(--accent-cyan), var(--accent-emerald))',
            borderRadius: '999px',
            transition: 'width 0.15s ease',
          }} />
        </div>
      </div>
    </div>
  );
};
