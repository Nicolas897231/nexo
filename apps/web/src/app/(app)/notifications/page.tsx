"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCheck } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { listAlerts, markAlertRead } from "@/services/api/alerts.api";

export default function NotificationsPage() {
  const queryClient = useQueryClient();
  const { data: alerts = [], isLoading } = useQuery({ queryKey: ["alerts"], queryFn: listAlerts });
  const markMutation = useMutation({
    mutationFn: markAlertRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts"] }),
  });

  function markAll() {
    alerts.forEach((alert) => markMutation.mutate(alert.id));
  }

  return (
    <main className="page">
      <PageHeader title="Notificaciones" description="Alertas de reglas, metas y seguridad en un solo lugar." actions={<button className="btn primary" type="button" onClick={markAll}><CheckCheck size={18} /> Marcar todo como leido</button>} />
      <section className="card pad">
        <div className="tabs" style={{ marginBottom: 18 }}>
          {["Todas", "Metas", "Reglas", "Seguridad", "Sistema"].map((tab, index) => <button className={`tab ${index === 0 ? "active" : ""}`} key={tab} type="button">{tab}</button>)}
        </div>
        {isLoading ? <div className="skeleton" style={{ height: 180 }} /> : alerts.length ? (
          <div className="grid">
            {alerts.map((alert) => (
              <article className="action-card" key={alert.id}>
                <Bell className={alert.severity === "danger" ? "danger-text" : alert.severity === "warning" ? "warning-text" : "primary-text"} />
                <div><strong>{alert.alert_type}</strong><p className="muted">{alert.message}</p></div>
                <button className="btn" type="button" onClick={() => markMutation.mutate(alert.id)}>Marcar leida</button>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState title="Sin notificaciones" description="Cuando tus reglas o metas generen alertas apareceran aqui." />
        )}
      </section>
    </main>
  );
}
