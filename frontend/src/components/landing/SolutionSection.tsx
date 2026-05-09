import ScrollReveal from "./ScrollReveal";
import { Clapperboard, Clock, MapPin, Sparkles } from "lucide-react";

const cards = [
  { icon: Clapperboard, title: "Ver cartelera", desc: "Películas disponibles hoy en tu zona" },
  { icon: Clock, title: "Comparar horarios", desc: "Funciones lado a lado para que elijas rápido" },
  { icon: MapPin, title: "Encontrar cines", desc: "Ubicaciones y salas con disponibilidad" },
  { icon: Sparkles, title: "Recibir sugerencias", desc: "Recomendaciones según tus preferencias" },
];

const SolutionSection = () => (
  <section className="py-24 lg:py-32 relative">
    <div className="container mx-auto px-4">
      <ScrollReveal>
        <p className="text-sm font-medium text-primary uppercase tracking-wider mb-3 text-center">La solución</p>
        <h2 className="text-3xl sm:text-4xl font-bold text-center text-balance mb-4">
          Todo en una conversación
        </h2>
        <p className="text-muted-foreground text-center max-w-lg mx-auto mb-16">
          CineBot centraliza la búsqueda de películas en un chat simple e inteligente.
        </p>
      </ScrollReveal>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 max-w-5xl mx-auto">
        {cards.map((c, i) => (
          <ScrollReveal key={i} delay={i * 0.08}>
            <div className="group rounded-xl border border-border bg-card p-6 text-center h-full hover:border-primary/30 hover:cinema-glow-sm transition-all duration-300">
              <div className="mx-auto h-12 w-12 rounded-xl cinema-surface flex items-center justify-center mb-4 group-hover:scale-105 transition-transform duration-300">
                <c.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-1.5">{c.title}</h3>
              <p className="text-sm text-muted-foreground">{c.desc}</p>
            </div>
          </ScrollReveal>
        ))}
      </div>
    </div>
  </section>
);

export default SolutionSection;
