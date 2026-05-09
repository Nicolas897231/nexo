"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Grid2X2, Plus, Trash2 } from "lucide-react";
import Link from "next/link";
import { GoalCard } from "@/components/goals/goal-card";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney } from "@/lib/money";
import { deleteGoal, listGoals } from "@/services/api/goals.api";

export default function GoalsPage() {
  const queryClient = useQueryClient();
  const { data: goals = [], isLoading } = useQuery({ queryKey: ["goals"], queryFn: listGoals });
  const deleteMutation = useMutation({
    mutationFn: deleteGoal,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["goals"] }),
  });
  const totalTarget = goals.reduce((sum, goal) => sum + Number(goal.target_amount), 0);
  const totalSaved = goals.reduce((sum, goal) => sum + Number(goal.current_amount), 0);

  return (
    <main className="page">
      <PageHeader
        title="Mis metas"
        description="Aqui tienes un resumen del progreso de tus metas financieras reales."
        actions={
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button className="btn" type="button"><Grid2X2 size={18} /> Vista tarjetas</button>
            <Link className="btn primary" href="/goals/new"><Plus size={18} /> Crear nueva meta</Link>
          </div>
        }
      />
      <nav className="tabs" style={{ marginBottom: 22 }}>
        {["Todas", "Ahorro", "Estilo de vida", "Transporte", "Viajes"].map((tab, index) => (
          <button className={`tab ${index === 0 ? "active" : ""}`} key={tab} type="button">{tab}</button>
        ))}
      </nav>
      {isLoading ? (
        <div className="skeleton" style={{ height: 280 }} />
      ) : goals.length ? (
        <section className="grid" style={{ gridTemplateColumns: "repeat(4, minmax(240px, 1fr))" }}>
          {goals.map((goal) => <GoalCard goal={goal} key={goal.id} />)}
        </section>
      ) : (
        <EmptyState
          title="Aun no tienes metas"
          description="Crea tu primera meta para empezar a medir ahorro y progreso."
          action={<Link className="btn primary" href="/goals/new">Crear meta</Link>}
        />
      )}
      <section className="grid three" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Resumen de prioridades</h2>
          <div className="grid" style={{ marginTop: 16 }}>
            {goals.map((goal, index) => {
              const progress = Number(goal.target_amount) > 0 ? Math.round((Number(goal.current_amount) / Number(goal.target_amount)) * 100) : 0;
              return (
                <div className="action-card" key={goal.id}>
                  <strong>{index + 1}. {goal.name}</strong>
                  <span className="badge success">{goal.status}</span>
                  <strong>{progress}%</strong>
                </div>
              );
            })}
          </div>
        </article>
        <article className="card pad">
          <h2 className="card-title">Acciones</h2>
          <div className="grid" style={{ marginTop: 16 }}>
            {goals.map((goal) => (
              <button className="action-card" key={goal.id} type="button" onClick={() => deleteMutation.mutate(goal.id)}>
                <strong>Eliminar {goal.name}</strong>
                <Trash2 className="danger-text" />
              </button>
            ))}
          </div>
        </article>
        <article className="card pad">
          <h2 className="card-title">Proximos hitos</h2>
          {goals.map((goal) => (
            <div key={goal.id} style={{ borderLeft: "3px solid var(--primary)", padding: "10px 0 10px 18px" }}>
              <strong>{goal.name}</strong>
              <p className="muted small">{goal.target_date || "Sin fecha"} · aporte sugerido {formatMoney(goal.monthly_contribution)}</p>
            </div>
          ))}
        </article>
      </section>
      <section className="card pad" style={{ marginTop: 18 }}>
        <div className="grid kpi">
          <div><p className="muted">Metas activas</p><h2>{goals.length}</h2></div>
          <div><p className="muted">Total metas</p><h2>{formatMoney(totalTarget.toFixed(2))}</h2></div>
          <div><p className="muted">Total ahorrado</p><h2>{formatMoney(totalSaved.toFixed(2))}</h2></div>
          <div><p className="muted">Avance global</p><h2>{totalTarget > 0 ? Math.round((totalSaved / totalTarget) * 100) : 0}%</h2></div>
        </div>
      </section>
    </main>
  );
}
