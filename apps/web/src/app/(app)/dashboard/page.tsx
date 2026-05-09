"use client";

import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Car, Goal, WalletCards } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { BalanceChart, CategoryDonut, SavingsBars } from "@/components/dashboard/charts";
import { MetricCard } from "@/components/dashboard/metric-card";
import { GoalCard } from "@/components/goals/goal-card";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { getDashboardSummary } from "@/services/api/dashboard.api";
import { listGoals } from "@/services/api/goals.api";

function currentMonthDate() {
  return `${new Date().toISOString().slice(0, 8)}01`;
}

export default function DashboardPage() {
  const [hiddenWidgets, setHiddenWidgets] = useState<string[]>([]);
  useEffect(() => {
    setHiddenWidgets(JSON.parse(window.localStorage.getItem("nexovia.hidden-widgets") ?? "[]"));
  }, []);
  function hideWidget(widget: string) {
    const next = [...new Set([...hiddenWidgets, widget])];
    setHiddenWidgets(next);
    window.localStorage.setItem("nexovia.hidden-widgets", JSON.stringify(next));
  }
  function isVisible(widget: string) {
    return !hiddenWidgets.includes(widget);
  }
  const month = currentMonthDate();
  const { data: summary, isLoading: summaryLoading } = useQuery({ queryKey: ["dashboard-summary", month], queryFn: () => getDashboardSummary(month) });
  const { data: goals = [], isLoading: goalsLoading } = useQuery({ queryKey: ["goals"], queryFn: listGoals });
  const mainGoal = goals[0];
  const mainProgress = mainGoal && Number(mainGoal.target_amount) > 0 ? Math.round((Number(mainGoal.current_amount) / Number(mainGoal.target_amount)) * 100) : 0;

  return (
    <main className="page">
      <PageHeader
        title="Dashboard"
        description="Tu centro de mando financiero con datos reales de tu cuenta."
      />
      <section className="grid kpi">
        <MetricCard label="Ingresos del mes" value={summary?.total_income ?? "0.00"} tone="success" delta="mes actual" />
        <MetricCard label="Egresos del mes" value={summary?.total_expenses ?? "0.00"} tone="danger" delta="mes actual" />
        <MetricCard label="Ahorro disponible" value={summary?.available_cashflow ?? "0.00"} tone="primary" delta="balance" />
        <article className="card metric-card">
          <p className="muted">Meta principal</p>
          {mainGoal ? (
            <>
              <h3>{mainGoal.name}</h3>
              <div className="progress"><span style={{ width: `${mainProgress}%`, background: "var(--purple)" }} /></div>
              <p className="purple-text" style={{ fontSize: 28, fontWeight: 800, textAlign: "right" }}>{mainProgress}%</p>
              <p className="muted small">{mainGoal.current_amount} / {mainGoal.target_amount} · {mainGoal.target_date || "Sin fecha"}</p>
            </>
          ) : (
            <p className="muted">Crea una meta para ver tu avance.</p>
          )}
        </article>
      </section>

      <section className="grid dashboard" style={{ marginTop: 18 }}>
        {isVisible("balance") ? <article className="card pad">
          <div className="card-header">
            <h2 className="card-title">Evolucion de saldo</h2>
            <button className="icon-button" type="button" onClick={() => hideWidget("balance")}>×</button>
          </div>
          {summaryLoading ? <div className="skeleton" style={{ height: 210 }} /> : <BalanceChart />}
        </article> : null}
        {isVisible("categories") ? <article className="card pad">
          <div className="card-header">
            <h2 className="card-title">Gastos por categoria</h2>
            <button className="icon-button" type="button" onClick={() => hideWidget("categories")}>×</button>
          </div>
          <CategoryDonut total={summary?.total_expenses ?? "0.00"} items={[["Gastos registrados", summary?.total_expenses ?? "0.00", summary?.total_expenses === "0.00" ? "0%" : "100%"]]} />
          <Link className="btn" style={{ marginTop: 20, width: "100%" }} href="/reports">Ver detalle de categorias <ArrowRight size={18} /></Link>
        </article> : null}
        {isVisible("savings") ? <article className="card pad">
          <div className="card-header">
            <h2 className="card-title">Ahorro mensual</h2>
            <button className="icon-button" type="button" onClick={() => hideWidget("savings")}>×</button>
          </div>
          <SavingsBars values={[Number(summary?.available_cashflow ?? 0) > 0 ? 85 : 12]} />
          <Link className="btn" style={{ marginTop: 20, width: "100%" }} href="/reports">Ver reporte completo <ArrowRight size={18} /></Link>
        </article> : null}
      </section>

      <section className="grid two" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Avance de metas</h2>
          {goalsLoading ? (
            <div className="skeleton" style={{ height: 220, marginTop: 18 }} />
          ) : goals.length ? (
            <div className="grid three" style={{ marginTop: 18 }}>
              {goals.slice(0, 3).map((goal) => <GoalCard key={goal.id} goal={goal} />)}
            </div>
          ) : (
            <EmptyState title="Sin metas todavia" description="Crea tu primera meta para que el dashboard tenga contexto." action={<Link className="btn primary" href="/goals/new">Crear meta</Link>} />
          )}
        </article>
        <article className="card pad">
          <h2 className="card-title">Recomendaciones para ti</h2>
          <div className="grid" style={{ marginTop: 18 }}>
            <div className="action-card">
              <div>
                <strong>{Number(summary?.available_cashflow ?? 0) >= 0 ? "Mantén tu balance positivo" : "Reduce gastos este mes"}</strong>
                <p className="muted small">Basado en tus ingresos, egresos y metas registradas.</p>
              </div>
              <Link className="btn" href="/rules">Crear regla</Link>
            </div>
            <div className="action-card">
              <div>
                <strong>Actualiza tus movimientos</strong>
                <p className="muted small">Entre mas registros tengas, mejores seran tus simulaciones.</p>
              </div>
              <Link className="btn" href="/movements?drawer=create&type=expense">Registrar</Link>
            </div>
          </div>
        </article>
      </section>

      <section className="card pad" style={{ marginTop: 18 }}>
        <h2 className="card-title">Acciones rapidas</h2>
        <div className="grid quick-actions" style={{ marginTop: 18 }}>
          <Link className="action-card" href="/movements?drawer=create&type=income"><WalletCards className="success-text" /> Registrar ingreso <ArrowRight /></Link>
          <Link className="action-card" href="/movements?drawer=create&type=expense"><WalletCards className="danger-text" /> Registrar gasto <ArrowRight /></Link>
          <Link className="action-card" href="/goals/new"><Goal className="purple-text" /> Crear meta <ArrowRight /></Link>
          <Link className="action-card" href="/simulators/car"><Car className="primary-text" /> Simular carro <ArrowRight /></Link>
        </div>
      </section>
    </main>
  );
}
