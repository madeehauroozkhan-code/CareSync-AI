import { useState, useEffect, useRef } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const WS_URL = API_BASE_URL.replace(/^http/, "ws") + "/ws/live-feed";

export function useLiveFeed() {
  const [events, setEvents] = useState([]);
  const wsRef = useRef(null);
  
  useEffect(() => {
    function connect() {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Keep only the last 200 events to prevent memory bloat
          setEvents(prev => [...prev.slice(-199), data]);
        } catch (err) {
          console.error("Failed to parse websocket message", err);
        }
      };
      
      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
      };
      
      ws.onclose = () => {
        console.log("WebSocket disconnected. Reconnecting in 3s...");
        setTimeout(connect, 3000);
      };
    }
    
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.onclose = null; // Prevent reconnect loop
        wsRef.current.close();
      }
    };
  }, []);

  return events;
}
