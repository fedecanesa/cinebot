import { Button } from "@/components/ui/button";
import { Film } from "lucide-react";
import { Link } from "react-router-dom";

const Navbar = () => (
  <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
    <div className="container mx-auto flex h-16 items-center justify-between px-4">
      <div className="flex items-center gap-2">
        <Film className="h-6 w-6 text-primary" />
        <span className="text-lg font-bold tracking-tight">CineBot</span>
      </div>
      <Button variant="hero" size="sm" asChild>
        <Link to="/chat">Probar el chat</Link>
      </Button>
    </div>
  </nav>
);

export default Navbar;
