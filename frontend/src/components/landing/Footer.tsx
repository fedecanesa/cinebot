import { Film } from "lucide-react";

const Footer = () => (
  <footer className="border-t border-border py-10">
    <div className="container mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-2">
        <Film className="h-5 w-5 text-primary" />
        <span className="font-semibold">CineBot</span>
      </div>
      <div className="text-center space-y-1">
        <p className="text-sm text-muted-foreground">
          Proyecto de IA conversacional · Canezza Studios
        </p>
        <p className="text-xs text-muted-foreground/50">
          CineBot informa y recomienda. No reserva asientos ni vende entradas.
        </p>
      </div>
    </div>
  </footer>
);

export default Footer;
