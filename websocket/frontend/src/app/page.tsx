'use client';


import { useEffect, useRef, useState } from "react";

export default function Home() {
  const socketRef = useRef<WebSocket | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [outgoing, setOutgoing] = useState<string>("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    // Build ws/wss URL based on current page for local dev
    const protocol = "ws";
    const host = "192.168.1.211";
    const port = 8000; // backend port
    const wsUrl = `${protocol}://${host}:${port}/ws/chat/lobby/`;
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      // Send a test message so the server echoes it back
      // try {
      //   socket.send(JSON.stringify({ message: "hello from client" }));
      // } catch (_) {}
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log(data);
        // Backend consumer sends { message: string }
        setMessages((prev) => [...prev, data]);
      } catch (err) {
        // Non-JSON or unexpected payload
        setMessages((prev) => [...prev, { message: String(event.data) }]);
      }
    };

    socket.onerror = (ev) => {
      setMessages((prev) => [...prev, { message: "WebSocket error" }]);
    };

    socket.onclose = () => {
      setMessages((prev) => [...prev, { message: "WebSocket closed" }]);
    };

    return () => {
      socket.close();
      socketRef.current = null;
    };
  }, [mounted]);

  if (!mounted) return null;

  const send = () => {
    const payload = { message: outgoing || "ping" };
    try {
      socketRef.current?.send(JSON.stringify(payload));
      setOutgoing("");
    } catch {}
  };

  return (
    <div suppressHydrationWarning className="grid grid-cols-12 grid-rows-12 min-h-screen place-items-center">
      <div className="col-start-3 col-span-8 flex items-center justify-center row-span-2">
        <span className="text-sm font-bold">Event listener</span>
      </div>
      <div className="col-start-3 col-span-8 border-2 border-gray-300 h-full w-full row-span-10 bg-white p-3 space-y-2 overflow-auto">
        {messages.length > 0 ? (
          messages.map((item: any, idx: number) => (
            <div className="flex items-center justify-between text-sm font-bold text-black" key={idx}>
              <span>{item.task_id ?? "message"}</span>
              <span>{item.progress ?? item.message}</span>
            </div>
          ))
        ) : (
          <span className="flex items-center justify-center text-sm font-bold text-black">No data</span>
        )}
      </div>
      <div className="col-start-3 col-span-8 row-span-1 w-full flex items-center gap-2 p-3">
        <input
          className="flex-1 border border-gray-300 px-2 py-1 text-black bg-white"
          value={outgoing}
          onChange={(e) => setOutgoing(e.target.value)}
          placeholder="Type a message..."
          onKeyDown={(e) => { if (e.key === "Enter") send(); }}
        />
        <button
          className="px-3 py-1 bg-blue-600 text-white font-semibold"
        >
          Send
        </button>
      </div>
    </div>
  );
};
