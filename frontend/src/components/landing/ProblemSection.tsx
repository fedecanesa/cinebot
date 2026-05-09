import ScrollReveal from "./ScrollReveal";
import { Globe, Clock, Layers } from "lucide-react";

const problems = [
  { icon: Globe, title: "Múltiples sitios", desc: "Buscar una película implica entrar a múltiples sitios web y apps diferentes." },
  { icon: Clock, title: "Tiempo perdido", desc: "Comparar horarios, salas y cines lleva más tiempo del que debería." },
  { icon: Layers, title: "Información dispersa", desc: "La información está fragmentada y no hay un lugar que lo unifique." },
];

const ProblemSection = () => (
  <section className="py-24 lg:py-32 relative">
    <div className="container mx-auto px-4">
      <ScrollReveal>
        <p className="text-sm font-medium text-primary uppercase tracking-wider mb-3 text-center">El problema</p>
        <h2 className="text-3xl sm:text-4xl font-bold text-center text-balance mb-16 max-w-2xl mx-auto">
          Elegir una película no debería ser tan difícil
        </h2>
      </ScrollReveal>

      <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        {problems.map((p, i) => (
          <ScrollReveal key={i} delay={i * 0.1}>
            <div className="rounded-xl border border-border bg-card p-6 h-full hover:border-primary/30 transition-colors duration-300">
              <div className="h-10 w-10 rounded-lg cinema-gradient flex items-center justify-center mb-4">
                <p.icon className="h-5 w-5 text-primary-foreground" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{p.title}</h3>
              <p className="text-sm text-muted-foreground text-pretty">{p.desc}</p>
            </div>
          </ScrollReveal>
        ))}
      </div>
    </div>
  </section>
);

export default ProblemSection;
