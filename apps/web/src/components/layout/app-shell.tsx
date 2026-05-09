"use client";

import {
  Bell,
  Calculator,
  ChevronDown,
  ChevronsLeft,
  Goal,
  LayoutDashboard,
  Menu,
  Moon,
  Search,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sun,
  TrendingUpDown,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentType, ReactNode } from "react";
import { useTheme } from "@/features/settings/theme-store";

const navigation = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/movements", label: "Movimientos", icon: TrendingUpDown },
  { href: "/goals", label: "Metas", icon: Goal },
  { href: "/simulators/living-alone", label: "Simuladores", icon: Calculator },
  { href: "/rules", label: "Reglas", icon: ShieldCheck },
  { href: "/reports", label: "Reportes", icon: SlidersHorizontal },
  { href: "/settings", label: "Configuracion", icon: Settings },
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Navegacion principal">
        <Link className="brand" href="/dashboard">
          <span className="brand-mark" aria-hidden>
            <span />
            <span />
            <span />
          </span>
          <strong>NexoVia</strong>
        </Link>
        <nav className="nav-list">
          {navigation.map((item) => (
            <NavItem key={item.href} {...item} />
          ))}
        </nav>
        <button className="sidebar-footer icon-button" type="button" title="Colapsar menu">
          <ChevronsLeft size={18} />
          <span>Colapsar</span>
        </button>
      </aside>
      <div className="main-column">
        <Topbar />
        {children}
      </div>
    </div>
  );
}

function NavItem({
  href,
  label,
  icon: Icon,
}: {
  href: string;
  label: string;
  icon: ComponentType<{ size?: number }>;
}) {
  const pathname = usePathname();
  const active = pathname === href || (href.includes("simulators") && pathname.startsWith("/simulators"));
  return (
    <Link className={`nav-item ${active ? "active" : ""}`} href={href}>
      <Icon size={24} />
      <span>{label}</span>
    </Link>
  );
}

function Topbar() {
  const { mode, setMode } = useTheme();
  return (
    <header className="topbar">
      <button className="icon-button" type="button" title="Abrir menu">
        <Menu size={24} />
      </button>
      <label className="search-box">
        <Search size={20} />
        <input
          aria-label="Buscar"
          placeholder="Buscar movimientos, metas, simuladores..."
          type="search"
        />
        <span className="badge">⌘ K</span>
      </label>
      <div className="topbar-actions">
        <div className="theme-toggle" aria-label="Cambiar tema">
          <Sun size={17} />
          <button
            className="switch"
            type="button"
            aria-label="Alternar modo oscuro"
            onClick={() => setMode(mode === "dark" ? "light" : "dark")}
          />
          <Moon size={17} />
        </div>
        <Link className="icon-button" href="/notifications" title="Notificaciones">
          <Bell size={22} />
          <span className="badge danger">3</span>
        </Link>
        <span className="avatar" aria-hidden>
          AG
        </span>
        <span className="muted">Hola, Andres</span>
        <ChevronDown size={18} />
      </div>
    </header>
  );
}
