import { useEffect, useRef, useState } from 'react';
import { ProtocolEventDTO } from '../types';
import { api } from '../api/client';

export function useWebSocketEvents(bufferSize: number = 100) {
  const [events, setEvents] = useState<ProtocolEventDTO[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let reconnectTimeout: any;

    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/events/ws/stream`;

      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          if (isPaused) return;
          try {
            const data: ProtocolEventDTO = JSON.parse(event.data);
            setEvents((prev) => [data, ...prev.slice(0, bufferSize - 1)]);
          } catch (e) {
            console.error('Failed to parse WebSocket event:', e);
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          // Try reconnect in 3s
          reconnectTimeout = setTimeout(connect, 3000);
        };

        ws.onerror = () => {
          setIsConnected(false);
          ws.close();
        };
      } catch (e) {
        setIsConnected(false);
        reconnectTimeout = setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [bufferSize, isPaused]);

  // Polling fallback if WS is not connected
  useEffect(() => {
    if (isConnected || isPaused) return;

    const fetchFallback = async () => {
      try {
        const res = await api.getEvents(bufferSize);
        if (res.events) {
          setEvents(res.events);
        }
      } catch (e) {
        // Silent error handling for polling fallback
      }
    };

    fetchFallback();
    const interval = setInterval(fetchFallback, 2000);
    return () => clearInterval(interval);
  }, [isConnected, isPaused, bufferSize]);

  return { events, isConnected, isPaused, setIsPaused, clearEvents: () => setEvents([]) };
}
