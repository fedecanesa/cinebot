import ScrollReveal from "./ScrollReveal";
import { Pencil, Search, ThumbsUp } from "lucide-react";

const steps = [
  { icon: Pencil, num: "01", title: "Escribís lo que querés ver", desc: "Preguntá por películas, horarios o cines en lenguaje natural, como si le hablaras a alguien." },
  { icon: Search, num: "02", title: "CineBot busca y procesa", desc: "Consulta su base de conocimiento y la web para encontrar la información más relevante para vos." },
  { icon: ThumbsUp, num: "03", title: "Recibís una respuesta clara", desc: "Sin filtros, sin menús: una respuesta directa con las mejores opciones para que decidas rápido." },
];

const HowItWorksSection = () => (
  <section id="como-funciona" className="py-24 lg:py-32">
    <div className="container mx-auto px-4">
      <ScrollReveal>
        <p className="text-sm font-medium text-primary uppercase tracking-wider mb-3 text-center">Proceso</p>
        <h2 className="text-3xl sm:text-4xl font-bold text-center text-balance mb-16">
          Cómo funciona
        </h2>
      </ScrollReveal>

      <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
        {steps.map((s, i) => (
          <ScrollReveal key={i} delay={i * 0.1}>
            <div className="text-center">
              <div className="mx-auto h-14 w-14 rounded-2xl cinema-gradient flex items-center justify-center mb-5">
                <s.icon className="h-6 w-6 text-primary-foreground" />
              </div>
              <span className="text-xs font-mono text-primary/60 block mb-2">{s.num}</span>
              <h3 className="font-semibold text-lg mb-2">{s.title}</h3>
              <p className="text-sm text-muted-foreground text-pretty">{s.desc}</p>
            </div>
          </ScrollReveal>
        ))}
      </div>
    </div>
  </section>
);

export default HowItWorksSection;
