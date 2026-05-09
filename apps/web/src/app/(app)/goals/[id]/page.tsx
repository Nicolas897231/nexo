import { PageHeader } from "@/components/ui/page-header";
import { goals, recommendations } from "@/data/mock-data";
import { formatMoney } from "@/lib/money";

export default async function GoalDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const goal = goals.find((item) => item.type === id) ?? goals[0];
  return (
    <main className="page">
      <PageHeader title={goal.name} description="Consulta el plan, aportes e impacto de esta meta." actions={<button className="btn primary" type="button">Agregar aporte</button>} />
      <section className="grid two">
        <article className="card pad">
          <h2>{formatMoney(goal.saved)} de {formatMoney(goal.target)}</h2>
          <div className="progress"><span style={{ width: `${goal.progress}%` }} /></div>
          <p className="muted">Estado: {goal.status} · Fecha estimada: {goal.date}</p>
          <div className="stepper" style={{ marginTop: 30 }}>
            {["Definida", "En progreso", "En camino", "Meta alcanzada"].map((step, index) => (
              <div className={`step ${index < 2 ? "done" : ""}`} key={step}><span className="step-dot">{index + 1}</span><strong>{step}</strong></div>
            ))}
          </div>
        </article>
        <article className="card pad">
          <h2 className="card-title">Recomendaciones</h2>
          {recommendations.map((item) => (
            <div className="action-card" key={item.title}><strong>{item.title}</strong><span className={`${item.tone}-text`}>{item.value}</span></div>
          ))}
        </article>
      </section>
    </main>
  );
}
