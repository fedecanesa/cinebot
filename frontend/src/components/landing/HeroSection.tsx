import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { MessageSquare, Film, Clock, MapPin } from "lucide-react";

const chatMessages = [
  { role: "user" as const, text: "¿Qué hay para ver hoy?" },
  { role: "bot" as const, text: "Hoy podés ver: Dune 2, Kung Fu Panda 4, Godzilla x Kong" },
  { role: "user" as const, text: "Quiero ver Dune 2" },
];

const movies = [
  { title: "Dune 2", time: "18:30", cinema: "Cinemark" },
  { title: "Kung Fu Panda 4", time: "16:00", cinema: "Hoyts" },
  { title: "Godzilla x Kong", time: "20:15", cinema: "Cinépolis" },
];

const HeroSection = () => (
  <section className="relative min-h-screen flex items-center pt-16 overflow-hidden">
    {/* Background glow */}
    <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-primary/8 blur-[120px] animate-pulse-glow pointer-events-none" />

    <div className="container mx-auto px-4 py-20 lg:py-32">
      <div className="grid lg:grid-cols-2 gap-16 items-center">
        {/* Left: Copy */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/5 px-4 py-1.5 text-sm text-primary mb-6">
            <Film className="h-3.5 w-3.5" />
            Asistente de cine con IA
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-balance leading-[1.08] mb-6">
            Encontrá qué ver en el cine,{" "}
            <span className="cinema-gradient-text">en segundos</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-lg text-pretty mb-8">
            CineBot te ayuda a descubrir películas, comparar funciones y elegir la mejor opción sin navegar múltiples páginas.
          </p>
          <div className="flex flex-wrap gap-4">
            <Button variant="hero" size="xl" asChild>
              <a href="#demo">
                <MessageSquare className="h-5 w-5" />
                Probar el chat
              </a>
            </Button>
            <Button variant="heroOutline" size="xl" asChild>
              <a href="#como-funciona">Cómo funciona</a>
            </Button>
          </div>
        </motion.div>

        {/* Right: Mock UI */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
          className="relative"
        >
          <div className="rounded-2xl border border-border bg-card p-1 cinema-glow">
            {/* Chat mock */}
            <div className="rounded-xl bg-background p-4 space-y-3">
              <div className="flex items-center gap-2 pb-3 border-b border-border">
                <div className="h-8 w-8 rounded-full cinema-gradient flex items-center justify-center">
                  <MessageSquare className="h-4 w-4 text-primary-foreground" />
                </div>
                <span className="font-semibold text-sm">CineBot</span>
                <span className="ml-auto text-xs text-muted-foreground">en línea</span>
              </div>

              {chatMessages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + i * 0.3, duration: 0.4 }}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                      msg.role === "user"
                        ? "cinema-gradient text-primary-foreground rounded-br-md"
                        : "cinema-surface text-foreground rounded-bl-md"
                    }`}
                  >
                    {msg.text}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Movie list */}
            <div className="p-4 space-y-2 border-t border-border">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">Cartelera</p>
              {movies.map((m, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: 12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.4 + i * 0.15, duration: 0.35 }}
                  className="flex items-center justify-between rounded-lg cinema-surface p-3 hover:bg-secondary/80 transition-colors"
                >
                  <span className="font-medium text-sm">{m.title}</span>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{m.time}</span>
                    <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{m.cinema}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  </section>
);

export default HeroSection;
