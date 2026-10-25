import { useEffect, useRef, useState } from 'react';

export interface WebSocketEvent {
  type: string;
  data: any;
  timestamp: number;
}

export function useWebSocket(onEvent?: (event: WebSocketEvent) => void) {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    let active = true;

    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/ws`;

      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!active) return;
          setIsConnected(true);
        };

        ws.onmessage = (messageEvent) => {
          if (!active) return;
          try {
            const parsed: WebSocketEvent = JSON.parse(messageEvent.data);
            if (onEvent) {
              onEvent(parsed);
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };

        ws.onclose = () => {
          if (!active) return;
          setIsConnected(false);
          // Try reconnecting in 2.5 seconds
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, 2500);
        };

        ws.onerror = (err) => {
          console.warn('WebSocket connection error:', err);
          ws.close();
        };
      } catch (err) {
        console.warn('WebSocket init failed:', err);
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 3000);
      }
    }

    connect();

    return () => {
      active = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [onEvent]);

  return { isConnected };
}
