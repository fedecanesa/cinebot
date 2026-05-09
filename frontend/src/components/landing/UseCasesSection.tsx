import ScrollReveal from "./ScrollReveal";
import { MessageSquare } from "lucide-react";

const cases = [
  "Quiero ver una peli hoy",
  "¿Qué hay en cartelera?",
  "¿Dónde pasan Dune 2?",
  "¿Qué me recomendás para esta noche?",
];

const UseCasesSection = () => (
  <section className="py-24 lg:py-32">
    <div className="container mx-auto px-4">
      <ScrollReveal>
        <p className="text-sm font-medium text-primary uppercase tracking-wider mb-3 text-center">Casos de uso</p>
        <h2 className="text-3xl sm:text-4xl font-bold text-center text-balance mb-12">
          Preguntale lo que quieras
        </h2>
      </ScrollReveal>

      <div className="flex flex-wrap justify-center gap-3 max-w-2xl mx-auto">
        {cases.map((c, i) => (
          <ScrollReveal key={i} delay={i * 0.08}>
            <div className="flex items-center gap-2 rounded-full border border-border bg-card px-5 py-3 hover:border-primary/40 transition-colors duration-300 cursor-default">
              <MessageSquare className="h-4 w-4 text-primary shrink-0" />
              <span className="text-sm font-medium">"{c}"</span>
            </div>
          </ScrollReveal>
        ))}
      </div>
    </div>
  </section>
);

export default UseCasesSection;
