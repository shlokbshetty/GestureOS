import React from 'react';
import {
  AppWindow,
  XSquare,
  PlayCircle,
  Volume2,
  Volume1,
  ArrowUpCircle,
  ArrowDownCircle,
  Camera,
  Hand,
  type LucideIcon,
} from 'lucide-react';
import type { GestureMetadata } from '../types';

interface GestureCardsProps {
  gestures: Record<string, GestureMetadata>;
  activeGesture: string;
}

const GESTURE_ICONS: Record<string, LucideIcon> = {
  app_switch: AppWindow,
  close_window: XSquare,
  play_pause: PlayCircle,
  volume_up: Volume2,
  volume_down: Volume1,
  scroll_up: ArrowUpCircle,
  scroll_down: ArrowDownCircle,
  screenshot: Camera,
  nothing: Hand,
};

export const GestureCards: React.FC<GestureCardsProps> = ({
  gestures,
  activeGesture,
}) => {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1.5rem' }} id="gesture-library-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff' }}>Gesture Library</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
            Active AI gesture classifiers and corresponding Windows keybindings
          </p>
        </div>
      </div>

      <div className="gestures-grid">
        {Object.entries(gestures).map(([key, meta]) => {
          const IconComponent = GESTURE_ICONS[key] || Hand;
          const isActive = activeGesture === key && key !== 'nothing';

          return (
            <div
              key={key}
              id={`gesture-card-${key}`}
              className={`gesture-card ${isActive ? 'active-detected' : ''}`}
              style={{ opacity: meta.enabled ? 1 : 0.4 }}
            >
              <div className="gesture-icon-box">
                <IconComponent size={22} color={isActive ? 'var(--accent-cyan)' : 'inherit'} />
              </div>
              <div className="gesture-card-title">{meta.display_name}</div>
              <div className="gesture-card-action">
                {meta.action === 'keyboard_shortcut' && meta.params?.keys?.join('+').toUpperCase()}
                {meta.action === 'keyboard_key' && meta.params?.key?.toUpperCase()}
                {meta.action === 'media_key' && meta.params?.key?.replace('_', ' ').toUpperCase()}
                {meta.action === 'mouse_scroll' && (meta.params?.units > 0 ? 'SCROLL UP' : 'SCROLL DOWN')}
                {meta.action === 'none' && 'IDLE'}
              </div>

              {/* Cooldown badge */}
              <div style={{
                marginTop: '0.5rem',
                fontSize: '0.68rem',
                color: 'var(--text-dim)',
                background: 'rgba(255, 255, 255, 0.04)',
                padding: '2px 6px',
                borderRadius: '4px',
              }}>
                {meta.cooldown_ms}ms CD
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
