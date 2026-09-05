import { useEffect, useState, useRef } from 'react';
import { ProtocolEventDTO } from '../types';
import { fetchEvents } from '../api/client';

interface UseWebSocketOptions {
  onEvent?: (event: ProtocolEventDTO) => void;
  url?: string;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  lastEvent: ProtocolEventDTO | null;
  reconnect: () => void;
}

export function useWebSocket({
  onEvent,
  url = 'ws://127.0.0.1:8000/events/ws/stream',
}: UseWebSocketOptions = {}): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastEvent, setLastEvent] = useState<ProtocolEventDTO | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const connect = () => {
    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setIsConnected(true);
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const parsed: ProtocolEventDTO = JSON.parse(event.data);
          setLastEvent(parsed);
          if (onEvent) onEvent(parsed);
        } catch (e) {
          console.error('Failed to parse WebSocket message JSON', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        startPollingFallback();
      };

      ws.onerror = (err) => {
        console.error('WebSocket connection error', err);
        ws.close();
      };

      wsRef.current = ws;
    } catch (err) {
      setIsConnected(false);
      startPollingFallback();
    }
  };

  const startPollingFallback = () => {
    if (pollIntervalRef.current) return;
    pollIntervalRef.current = setInterval(async () => {
      try {
        const events = await fetchEvents(5);
        if (events && events.length > 0) {
          const newest = events[0];
          setLastEvent(newest);
          if (onEvent) onEvent(newest);
        }
      } catch (err) {
        // Polling failed silently
      }
    }, 2000);
  };

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [url]);

  return {
    isConnected,
    lastEvent,
    reconnect: connect,
  };
}
