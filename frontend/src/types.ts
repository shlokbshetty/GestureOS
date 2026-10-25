export type ApplicationState = 'stopped' | 'starting' | 'running' | 'pausing' | 'paused' | 'stopping';

export interface GestureMetadata {
  action: string;
  params: Record<string, any>;
  cooldown_ms: number;
  enabled: boolean;
  display_name: string;
  icon?: string;
  description: string;
}

export interface ActionLogEntry {
  gesture: string;
  action: string;
  confidence: number;
  timestamp: number;
  success: boolean;
}

export interface SystemStatus {
  state: ApplicationState;
  current_gesture: string;
  last_action: ActionLogEntry | null;
  uptime_seconds: number;
  total_actions: number;
  timestamp: number;
}

export interface CameraStatus {
  connected: boolean;
  running: boolean;
  fps_target: number;
  inference_latency_ms: number;
  frame_count: number;
}

export interface ConfigData {
  gestures: Record<string, GestureMetadata>;
  confidence_threshold: number;
  smoothing_frames: number;
}
