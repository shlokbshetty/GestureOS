import type { CameraStatus, ConfigData, GestureMetadata, SystemStatus, ActionLogEntry } from '../types';

const BASE_URL = '/api';

export async function fetchStatus(): Promise<SystemStatus> {
  const res = await fetch(`${BASE_URL}/status`);
  if (!res.ok) throw new Error('Failed to fetch status');
  return res.json();
}

export async function startEngine(): Promise<{ success: boolean; state: string }> {
  const res = await fetch(`${BASE_URL}/start`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to start engine');
  return res.json();
}

export async function stopEngine(): Promise<{ success: boolean; state: string }> {
  const res = await fetch(`${BASE_URL}/stop`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to stop engine');
  return res.json();
}

export async function pauseEngine(): Promise<{ success: boolean; state: string }> {
  const res = await fetch(`${BASE_URL}/pause`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to pause engine');
  return res.json();
}

export async function resumeEngine(): Promise<{ success: boolean; state: string }> {
  const res = await fetch(`${BASE_URL}/resume`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to resume engine');
  return res.json();
}

export async function fetchConfig(): Promise<ConfigData> {
  const res = await fetch(`${BASE_URL}/config`);
  if (!res.ok) throw new Error('Failed to fetch configuration');
  return res.json();
}

export async function updateConfig(data: Partial<ConfigData>): Promise<{ success: boolean; config: ConfigData }> {
  const res = await fetch(`${BASE_URL}/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update configuration');
  return res.json();
}

export async function updateGesture(name: string, data: Partial<GestureMetadata>): Promise<any> {
  const res = await fetch(`${BASE_URL}/gestures/${name}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update gesture: ${name}`);
  return res.json();
}

export async function fetchLogs(limit: number = 50): Promise<ActionLogEntry[]> {
  const res = await fetch(`${BASE_URL}/logs?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch action logs');
  return res.json();
}

export async function clearLogs(): Promise<{ success: boolean }> {
  const res = await fetch(`${BASE_URL}/logs`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to clear action logs');
  return res.json();
}

export async function fetchCameraStatus(): Promise<CameraStatus> {
  const res = await fetch(`${BASE_URL}/camera-status`);
  if (!res.ok) throw new Error('Failed to fetch camera status');
  return res.json();
}
