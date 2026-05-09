"use client";

import { useQuery } from "@tanstack/react-query";
import { Download } from "lucide-react";
import { BalanceChart, CategoryDonut, SavingsBars } from "@/components/dashboard/charts";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney } from "@/lib/money";
import { getDashboardSummary } from "@/services/api/dashboard.api";
import { listGoals } from "@/services/api/goals.api";

function currentMonthDate() {
  return `${new Date().toISOString().slice(0, 8)}01`;
}

export default function ReportsPage() {
  const month = currentMonthDate();
  const { data: summary } = useQuery({ queryKey: ["dashboard-summary", month], queryFn: () => getDashboardSummary(month) });
  const { data: goals = [] } = useQuery({ queryKey: ["goals"], queryFn: listGoals });
  return (
    <main className="page">
      <PageHeader title="Reportes y analisis" description="Explora el rendimiento de tus finanzas con reportes reales." actions={<button className="btn primary" type="button" onClick={() => window.print()}><Download size={18} /> Exportar</button>} />
      <nav className="tabs" style={{ marginBottom: 18 }}>
        {["Resumen", "Flujo de caja", "Gastos", "Ingresos", "Metas"].map((tab, index) => <button className={`tab ${index === 0 ? "active" : ""}`} key={tab} type="button">{tab}</button>)}
      </nav>
      <section className="grid three">
        <article className="card pad"><h2 className="card-title">Ingresos vs. Egresos</h2><BalanceChart /></article>
        <article className="card pad"><h2 className="card-title">Distribucion por categoria</h2><CategoryDonut total={summary?.total_expenses ?? "0.00"} items={[["Gastos registrados", summary?.total_expenses ?? "0.00", "100%"]]} /></article>
        <article className="card pad"><h2 className="card-title">Ahorro por mes</h2><SavingsBars values={[Number(summary?.available_cashflow ?? 0) > 0 ? 80 : 10]} /></article>
      </section>
      <section className="grid three" style={{ marginTop: 18 }}>
        <article className="card pad"><h2 className="card-title">Cumplimiento de metas</h2>{goals.slice(0, 3).map((goal) => <div className="action-card" key={goal.id}><strong>{goal.name}</strong><span>{Number(goal.target_amount) > 0 ? Math.round((Number(goal.current_amount) / Number(goal.target_amount)) * 100) : 0}%</span></div>)}</article>
        <article className="card pad"><h2 className="card-title">Resumen del periodo</h2>{[
          ["Ingresos", summary?.total_income ?? "0.00"],
          ["Egresos", summary?.total_expenses ?? "0.00"],
          ["Disponible", summary?.available_cashflow ?? "0.00"],
        ].map(([name, value]) => <div className="action-card" key={name}><span>{name}</span><strong>{formatMoney(value)}</strong></div>)}</article>
        <article className="card pad"><h2 className="card-title">Insights rapidos</h2><div className="action-card"><strong>{Number(summary?.available_cashflow ?? 0) >= 0 ? "Balance positivo" : "Balance en riesgo"}</strong><span>›</span></div></article>
      </section>
    </main>
  );
}
