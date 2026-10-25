import React from 'react';
import { CheckCircle2, ListFilter, Trash2, XCircle } from 'lucide-react';
import type { ActionLogEntry } from '../types';

interface ActionLogFeedProps {
  logs: ActionLogEntry[];
  onClear: () => Promise<void>;
}

export const ActionLogFeed: React.FC<ActionLogFeedProps> = ({ logs, onClear }) => {
  const formatTime = (ts: number) => {
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString();
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }} id="action-log-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ListFilter size={18} color="var(--accent-cyan)" />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff' }}>Action Stream</h2>
        </div>

        <button
          id="btn-clear-logs"
          onClick={onClear}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-dim)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            fontSize: '0.78rem',
            padding: '4px 8px',
            borderRadius: '4px',
            transition: 'color 0.2s',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--accent-rose)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-dim)')}
          title="Clear Action History"
        >
          <Trash2 size={14} />
          <span>Clear</span>
        </button>
      </div>

      <div className="log-container" id="log-feed-list">
        {logs.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '2.5rem 0', fontSize: '0.85rem' }}>
            No actions executed yet. Perform hand gestures to see real-time triggers.
          </div>
        ) : (
          logs.map((entry, idx) => (
            <div key={`${entry.timestamp}-${idx}`} className="log-entry" id={`log-item-${idx}`}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                {entry.success ? (
                  <CheckCircle2 size={16} color="var(--accent-emerald)" />
                ) : (
                  <XCircle size={16} color="var(--accent-rose)" />
                )}
                <div>
                  <div className="log-gesture-name">
                    {entry.gesture.replace('_', ' ').toUpperCase()}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    Action: {entry.action}
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.78rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
                  {(entry.confidence * 100).toFixed(0)}%
                </div>
                <div className="log-time">{formatTime(entry.timestamp)}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
