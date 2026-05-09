import ScrollReveal from "./ScrollReveal";
import { Check, X } from "lucide-react";

const does = [
  "Mostrar películas en cartelera",
  "Listar funciones y horarios",
  "Sugerir opciones según preferencias",
  "Guiar la decisión de compra",
];

const doesnt = [
  "Reserva de asientos",
  "Compra de entradas",
  "Integración con sistemas de cine",
];

const ScopeSection = () => (
  <section className="py-24 lg:py-32">
    <div className="container mx-auto px-4">
      <ScrollReveal>
        <p className="text-sm font-medium text-primary uppercase tracking-wider mb-3 text-center">Alcance del MVP</p>
        <h2 className="text-3xl sm:text-4xl font-bold text-center text-balance mb-16">
          Qué hace CineBot en esta versión
        </h2>
      </ScrollReveal>

      <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
        <ScrollReveal delay={0}>
          <div className="rounded-xl border border-primary/20 bg-card p-6 h-full">
            <h3 className="font-semibold text-lg mb-4 text-primary">✓ Lo que hace</h3>
            <ul className="space-y-3">
              {does.map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <Check className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                  <span className="text-foreground/90">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </ScrollReveal>

        <ScrollReveal delay={0.1}>
          <div className="rounded-xl border border-border bg-card p-6 h-full">
            <h3 className="font-semibold text-lg mb-4 text-muted-foreground">✗ Todavía no</h3>
            <ul className="space-y-3">
              {doesnt.map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <X className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </ScrollReveal>
      </div>
    </div>
  </section>
);

export default ScopeSection;
