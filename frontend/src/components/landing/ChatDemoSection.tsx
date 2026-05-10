import { useState, useEffect, useRef } from "react";
import ScrollReveal from "./ScrollReveal";
import { MessageSquare, Send } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ChatMsg {
  role: "user" | "assistant";
  text: string;
}

const GREETING: ChatMsg = {
  role: "assistant",
  text: "¡Hola! Soy CineBot. Preguntame sobre películas, horarios o cines y te ayudo a elegir.",
};

const ChatDemoSection = () => {
  const [messages, setMessages] = useState<ChatMsg[]>([GREETING]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
  const [sessionId] = useState(() => crypto.randomUUID());

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    const userMsg: ChatMsg = { role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = await res.json();
      const reply = data.response ?? data.message ?? JSON.stringify(data);

      setMessages((prev) => [...prev, { role: "assistant", text: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "No pude conectarme con el servidor. Intentá de nuevo." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <section id="demo" className="py-24 lg:py-32 relative">
      <div className="container mx-auto px-4">
        <ScrollReveal>
          <p className="text-sm font-medium text-primary uppercase tracking-wider mb-3 text-center">Demo en vivo</p>
          <h2 className="text-3xl sm:text-4xl font-bold text-center text-balance mb-4">
            Probalo ahora mismo
          </h2>
          <p className="text-muted-foreground text-center max-w-lg mx-auto mb-12">
            Escribí cualquier pregunta sobre películas o cines y respondemos al instante.
          </p>
        </ScrollReveal>

        <ScrollReveal>
          <div className="max-w-lg mx-auto rounded-2xl border border-border bg-card cinema-glow overflow-hidden flex flex-col h-[480px]">
            {/* Header */}
            <div className="flex items-center gap-3 p-4 border-b border-border shrink-0">
              <div className="h-9 w-9 rounded-full cinema-gradient flex items-center justify-center">
                <MessageSquare className="h-4 w-4 text-primary-foreground" />
              </div>
              <div>
                <p className="font-semibold text-sm">CineBot</p>
                <p className="text-xs text-muted-foreground">Asistente de cine</p>
              </div>
              <span className="ml-auto text-xs text-primary/70 font-medium">en línea</span>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              <AnimatePresence initial={false}>
                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm whitespace-pre-line ${
                        msg.role === "user"
                          ? "cinema-gradient text-primary-foreground rounded-br-md"
                          : "cinema-surface text-foreground rounded-bl-md"
                      }`}
                    >
                      {msg.text}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {isLoading && (
                <div className="flex justify-start">
                  <div className="cinema-surface rounded-2xl rounded-bl-md px-4 py-3">
                    <div className="flex gap-1 items-center h-4">
                      <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:-0.3s]" />
                      <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:-0.15s]" />
                      <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-border shrink-0">
              <div className="flex items-center gap-2 rounded-xl cinema-surface px-4 py-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Preguntá sobre películas, horarios o cines..."
                  className="flex-1 bg-transparent outline-none text-sm placeholder:text-muted-foreground"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSend}
                  disabled={isLoading || !input.trim()}
                  className="text-primary hover:opacity-70 disabled:opacity-50 transition-opacity"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
};

export default ChatDemoSection;
