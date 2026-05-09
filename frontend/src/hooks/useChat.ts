import { useState, useCallback } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function getOrCreateSessionId(): string {
  const key = "cinebot_session_id";
  const stored = localStorage.getItem(key);
  if (stored) return stored;
  const id = crypto.randomUUID();
  localStorage.setItem(key, id);
  return id;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const sessionId = getOrCreateSessionId();

  const sendMessage = useCallback(async (content: string) => {
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content, session_id: sessionId }),
      });

      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = await res.json();
      const reply = data.response ?? data.message ?? JSON.stringify(data);

      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: reply },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Ups, no pude conectarme con el servidor. Intentá de nuevo.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  return { messages, isLoading, sendMessage };
}
