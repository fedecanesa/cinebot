import ScrollReveal from "./ScrollReveal";
import { Zap, Target, Smartphone, MessageCircle } from "lucide-react";

const benefits = [
  { icon: Zap, title: "Ahorro de tiempo", desc: "Encontrá tu película en segundos, no en minutos." },
  { icon: Target, title: "Decisión más rápida", desc: "Información clara para elegir sin vueltas." },
  { icon: Smartphone, title: "Experiencia simple", desc: "Solo un chat. Sin menús, filtros ni complicaciones." },
  { icon: MessageCircle, title: "Interacción natural", desc: "Hablale como a un amigo que sabe de cine." },
];

const BenefitsSection = () => (
  <section className="py-24 lg:py-32">
    <div className="container mx-auto px-4">
      <ScrollReveal>
        <p className="text-sm font-medium text-primary uppercase tracking-wider mb-3 text-center">Beneficios</p>
        <h2 className="text-3xl sm:text-4xl font-bold text-center text-balance mb-16">
          ¿Por qué usar CineBot?
        </h2>
      </ScrollReveal>

      <div className="grid sm:grid-cols-2 gap-5 max-w-3xl mx-auto">
        {benefits.map((b, i) => (
          <ScrollReveal key={i} delay={i * 0.08}>
            <div className="flex items-start gap-4 rounded-xl border border-border bg-card p-5 hover:border-primary/30 transition-colors duration-300">
              <div className="h-10 w-10 rounded-lg cinema-surface flex items-center justify-center shrink-0">
                <b.icon className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">{b.title}</h3>
                <p className="text-sm text-muted-foreground">{b.desc}</p>
              </div>
            </div>
          </ScrollReveal>
        ))}
      </div>
    </div>
  </section>
);

export default BenefitsSection;
