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
import { usePathname, useRouter } from "next/navigation";
import type { ComponentType, ReactNode } from "react";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTheme } from "@/features/settings/theme-store";
import { logout } from "@/services/api/auth.api";
import { listAlerts } from "@/services/api/alerts.api";
import { getMe } from "@/services/api/users.api";

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
  const [collapsed, setCollapsed] = useState(false);
  useEffect(() => {
    setCollapsed(window.localStorage.getItem("nexovia.sidebar-collapsed") === "true");
  }, []);
  function toggleCollapsed() {
    const next = !collapsed;
    setCollapsed(next);
    window.localStorage.setItem("nexovia.sidebar-collapsed", String(next));
  }
  return (
    <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
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
        <button className="sidebar-footer icon-button" type="button" title="Colapsar menu" onClick={toggleCollapsed}>
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
  const router = useRouter();
  const [search, setSearch] = useState("");
  const { data: me } = useQuery({ queryKey: ["me"], queryFn: getMe });
  const { data: alerts = [] } = useQuery({ queryKey: ["alerts"], queryFn: listAlerts });
  const firstName = me?.profile.first_name || me?.email?.split("@")[0] || "Usuario";
  const initials = `${me?.profile.first_name?.[0] ?? me?.email?.[0] ?? "U"}${me?.profile.last_name?.[0] ?? ""}`.toUpperCase();

  async function handleLogout() {
    await logout().catch(() => undefined);
    router.push("/login");
    router.refresh();
  }

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
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && search.trim()) {
              router.push(`/movements?q=${encodeURIComponent(search.trim())}`);
            }
          }}
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
          {alerts.length ? <span className="badge danger">{alerts.length}</span> : null}
        </Link>
        <span className="avatar" aria-hidden>
          {initials}
        </span>
        <Link className="muted" href="/settings">Hola, {firstName}</Link>
        <button className="icon-button" type="button" title="Cerrar sesion" onClick={handleLogout}>
          <ChevronDown size={18} />
        </button>
      </div>
    </header>
  );
}
