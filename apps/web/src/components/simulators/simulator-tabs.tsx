import { Car, Home, PiggyBank, Plane } from "lucide-react";
import Link from "next/link";

const tabs = [
  { href: "/simulators/saving", label: "Ahorrar", icon: PiggyBank },
  { href: "/simulators/living-alone", label: "Vivir solo", icon: Home },
  { href: "/simulators/car", label: "Comprar carro", icon: Car },
  { href: "/simulators/travel", label: "Viajar", icon: Plane },
];

export function SimulatorTabs({ active }: { active: string }) {
  return (
    <nav className="tabs" aria-label="Tipos de simulador">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        return (
          <Link key={tab.href} className={`tab ${active === tab.href ? "active" : ""}`} href={tab.href}>
            <Icon size={19} />
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
