import { Button } from "@/components/ui/button";
import ScrollReveal from "./ScrollReveal";
import { MessageSquare } from "lucide-react";
import { Link } from "react-router-dom";

const CTASection = () => (
  <section className="py-24 lg:py-32 relative">
    <div className="absolute inset-0 bg-primary/[0.03]" />
    <div className="container mx-auto px-4 relative">
      <ScrollReveal>
        <div className="text-center max-w-xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-balance mb-4">
            ¿Qué vas a ver este fin de semana?
          </h2>
          <p className="text-muted-foreground mb-8">
            Abrí el chat y en segundos tenés opciones claras. Sin buscar en múltiples sitios.
          </p>
          <Button variant="hero" size="xl" asChild>
            <Link to="/chat">
              <MessageSquare className="h-5 w-5" />
              Probar el chat
            </Link>
          </Button>
        </div>
      </ScrollReveal>
    </div>
  </section>
);

export default CTASection;
