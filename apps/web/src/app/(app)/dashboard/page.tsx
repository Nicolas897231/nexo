import { ArrowRight, Car, Goal, Plus, WalletCards } from "lucide-react";
import Link from "next/link";
import { BalanceChart, CategoryDonut, SavingsBars } from "@/components/dashboard/charts";
import { MetricCard } from "@/components/dashboard/metric-card";
import { GoalCard } from "@/components/goals/goal-card";
import { PageHeader } from "@/components/ui/page-header";
import { goals, kpis, recommendations } from "@/data/mock-data";

export default function DashboardPage() {
  return (
    <main className="page">
      <PageHeader
        title="Dashboard"
        description="Tu centro de mando financiero para decidir mejor cada mes."
      />
      <section className="grid kpi">
        {kpis.map((kpi) => (
          <MetricCard key={kpi.label} {...kpi} tone={kpi.tone as "success" | "danger" | "primary"} />
        ))}
        <article className="card metric-card">
          <p className="muted">Meta principal</p>
          <h3>Viaje a Europa</h3>
          <div className="progress"><span style={{ width: "65%", background: "var(--purple)" }} /></div>
          <p className="purple-text" style={{ fontSize: 28, fontWeight: 800, textAlign: "right" }}>65%</p>
          <p className="muted small">$6.500.000 / $10.000.000 · 30 dic 2025</p>
        </article>
      </section>

      <section className="grid dashboard" style={{ marginTop: 18 }}>
        <article className="card pad">
          <div className="card-header">
            <h2 className="card-title">Evolucion de saldo</h2>
            <button className="icon-button" type="button">⋮</button>
          </div>
          <BalanceChart />
          <div className="tabs" style={{ gridTemplateColumns: "repeat(6, 1fr)" }}>
            {["7D", "1M", "3M", "6M", "1A", "Todo"].map((item) => (
              <button className={`tab ${item === "6M" ? "active" : ""}`} key={item} type="button">{item}</button>
            ))}
          </div>
        </article>
        <article className="card pad">
          <div className="card-header">
            <h2 className="card-title">Gastos por categoria</h2>
            <button className="icon-button" type="button">⋮</button>
          </div>
          <CategoryDonut />
          <Link className="btn" style={{ marginTop: 20, width: "100%" }} href="/reports">Ver detalle de categorias <ArrowRight size={18} /></Link>
        </article>
        <article className="card pad">
          <div className="card-header">
            <h2 className="card-title">Ahorro mensual</h2>
            <button className="icon-button" type="button">⋮</button>
          </div>
          <SavingsBars />
          <Link className="btn" style={{ marginTop: 20, width: "100%" }} href="/reports">Ver reporte completo <ArrowRight size={18} /></Link>
        </article>
      </section>

      <section className="grid two" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Avance de metas</h2>
          <div className="grid three" style={{ marginTop: 18 }}>
            {goals.slice(0, 3).map((goal) => <GoalCard key={goal.name} goal={goal} />)}
          </div>
        </article>
        <article className="card pad">
          <h2 className="card-title">Recomendaciones para ti</h2>
          <div className="grid" style={{ marginTop: 18 }}>
            {recommendations.map((item) => (
              <div className="action-card" key={item.title}>
                <div>
                  <strong>{item.title}</strong>
                  <p className="muted small">{item.detail}</p>
                </div>
                <strong className={`${item.tone}-text`}>{item.value}</strong>
              </div>
            ))}
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
