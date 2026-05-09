import { Bell, CheckCheck } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";

const notifications = [
  ["Meta", "Tu viaje a Europa alcanzo 65% de progreso.", "Hace 10 min"],
  ["Regla", "Tu gasto en ocio esta cerca del limite definido.", "Hace 2 h"],
  ["Seguridad", "Se inicio sesion desde un dispositivo nuevo.", "Ayer"],
  ["Sistema", "Nuevo reporte mensual disponible.", "2 dias"],
];

export default function NotificationsPage() {
  return (
    <main className="page">
      <PageHeader title="Notificaciones" description="Alertas de reglas, metas y seguridad en un solo lugar." actions={<button className="btn primary" type="button"><CheckCheck size={18} /> Marcar todo como leido</button>} />
      <section className="card pad">
        <div className="tabs" style={{ marginBottom: 18 }}>
          {["Todas", "Metas", "Reglas", "Seguridad", "Sistema"].map((tab, index) => <button className={`tab ${index === 0 ? "active" : ""}`} key={tab} type="button">{tab}</button>)}
        </div>
        <div className="grid">
          {notifications.map(([type, message, time]) => (
            <article className="action-card" key={message}>
              <Bell className="primary-text" />
              <div><strong>{type}</strong><p className="muted">{message}</p></div>
              <span className="muted">{time}</span>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
