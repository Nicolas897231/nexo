import { Grid2X2, Plus } from "lucide-react";
import Link from "next/link";
import { GoalCard } from "@/components/goals/goal-card";
import { PageHeader } from "@/components/ui/page-header";
import { goals, recommendations } from "@/data/mock-data";
import { formatMoney } from "@/lib/money";

export default function GoalsPage() {
  return (
    <main className="page">
      <PageHeader
        title="Mis metas"
        description="Aqui tienes un resumen del progreso de tus metas financieras."
        actions={
          <div style={{ display: "flex", gap: 12 }}>
            <button className="btn" type="button"><Grid2X2 size={18} /> Ver como lista</button>
            <Link className="btn primary" href="/goals/new"><Plus size={18} /> Crear nueva meta</Link>
          </div>
        }
      />
      <nav className="tabs" style={{ marginBottom: 22 }}>
        {["Todas", "Ahorro", "Estilo de vida", "Transporte", "Viajes", "Hogar", "Educacion"].map((tab, index) => (
          <button className={`tab ${index === 0 ? "active" : ""}`} key={tab} type="button">{tab}</button>
        ))}
      </nav>
      <section className="grid" style={{ gridTemplateColumns: "repeat(4, minmax(240px, 1fr))" }}>
        {goals.map((goal) => <GoalCard goal={goal} key={goal.name} />)}
      </section>
      <section className="grid three" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Resumen de prioridades</h2>
          <div className="grid" style={{ marginTop: 16 }}>
            {goals.map((goal, index) => (
              <div className="action-card" key={goal.name}>
                <strong>{index + 1}. {goal.name}</strong>
                <span className={`badge ${goal.status === "En riesgo" ? "danger" : goal.status === "Viable" ? "success" : "warning"}`}>{goal.status}</span>
                <strong>{goal.progress}%</strong>
              </div>
            ))}
          </div>
        </article>
        <article className="card pad">
          <h2 className="card-title">Recomendaciones para ti</h2>
          <div className="grid" style={{ marginTop: 16 }}>
            {recommendations.map((item) => (
              <div className="action-card" key={item.title}>
                <div><strong>{item.title}</strong><p className="muted small">{item.detail}</p></div>
                <span>›</span>
              </div>
            ))}
          </div>
        </article>
        <article className="card pad">
          <h2 className="card-title">Proximos hitos</h2>
          {goals.map((goal) => (
            <div key={goal.name} style={{ borderLeft: "3px solid var(--primary)", padding: "10px 0 10px 18px" }}>
              <strong>{goal.name}</strong>
              <p className="muted small">{goal.date} · llega a {goal.progress + 20}% de tu meta</p>
            </div>
          ))}
        </article>
      </section>
      <section className="card pad" style={{ marginTop: 18 }}>
        <div className="grid kpi">
          <div><p className="muted">Metas activas</p><h2>4</h2></div>
          <div><p className="muted">Total metas</p><h2>{formatMoney("64860000.00")}</h2></div>
          <div><p className="muted">Total ahorrado</p><h2>{formatMoney("26796000.00")}</h2></div>
          <div><p className="muted">Fecha promedio</p><h2>Mar 2027</h2></div>
        </div>
      </section>
    </main>
  );
}
