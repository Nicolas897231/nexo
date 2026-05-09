"use client";

import { Lock, Mail, Moon, RotateCcw, Shield, Sun } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { useTheme } from "@/features/settings/theme-store";

export default function SettingsPage() {
  const { accent, compact, mode, setAccent, setCompact, setMode } = useTheme();
  return (
    <main className="page">
      <PageHeader title="Configuracion" description="Personaliza tu experiencia en NexoVia y administra tu cuenta." />
      <section className="grid two">
        <article className="card pad">
          <h2 className="card-title">Perfil</h2>
          <div className="metric-row" style={{ marginTop: 20 }}>
            <span className="avatar">AG</span>
            <div><h2>Andres Gomez</h2><p className="muted">andres.gomez@email.com</p><span className="badge success">Cuenta verificada</span></div>
          </div>
          <div className="form-grid" style={{ marginTop: 24 }}>
            <select className="select"><option>USD - Dolar estadounidense</option><option>COP - Peso colombiano</option></select>
            <select className="select"><option>Español (ES)</option></select>
            <select className="select"><option>(GMT-05:00) Bogota, Lima, Quito</option></select>
          </div>
        </article>
        <article className="card pad">
          <h2 className="card-title">Preferencias visuales</h2>
          <div className="grid three" style={{ marginTop: 18 }}>
            {["blue", "ocean", "night"].map((item) => <button className={`card pad ${accent === item ? "active" : ""}`} key={item} onClick={() => setAccent(item as any)} type="button"><strong>{item === "blue" ? "Azul" : item === "ocean" ? "Oceano" : "Noche suave"}</strong><p className="primary-text">● ● ●</p></button>)}
          </div>
          <div className="action-card" style={{ marginTop: 18 }}><Moon /><strong>Modo oscuro</strong><button className="switch" onClick={() => setMode(mode === "dark" ? "light" : "dark")} type="button" /></div>
          <div className="action-card" style={{ marginTop: 12 }}><Sun /><strong>Modo compacto</strong><button className="switch" onClick={() => setCompact(!compact)} type="button" /></div>
        </article>
      </section>
      <section className="grid two" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Widgets del dashboard</h2>
          {["Evolucion de saldo", "Gastos por categoria", "Ahorro mensual", "Avance de metas", "Recomendaciones para ti"].map((item) => <div className="action-card" key={item}><strong>{item}</strong><button className="switch" type="button" /></div>)}
          <button className="btn" style={{ marginTop: 14 }} type="button"><RotateCcw size={18} /> Restablecer al diseño por defecto</button>
        </article>
        <article className="card pad">
          <h2 className="card-title">Notificaciones</h2>
          {["Notificaciones por correo", "Alertas de metas", "Alertas de presupuesto", "Novedades del producto"].map((item) => <div className="action-card" key={item}><Mail /><strong>{item}</strong><button className="switch" type="button" /></div>)}
        </article>
        <article className="card pad">
          <h2 className="card-title">Privacidad y seguridad</h2>
          {["Cambiar contraseña", "Autenticacion en dos pasos", "Sesiones activas"].map((item, index) => <div className="action-card" key={item}>{index === 0 ? <Lock /> : <Shield />}<strong>{item}</strong><span>›</span></div>)}
        </article>
        <article className="card pad">
          <h2 className="card-title">Preferencias generales</h2>
          {["Inicio de sesion automatico", "Recordatorios de actividad", "Formato de numeros", "Exportaciones"].map((item) => <div className="action-card" key={item}><strong>{item}</strong><span>›</span></div>)}
        </article>
      </section>
    </main>
  );
}
