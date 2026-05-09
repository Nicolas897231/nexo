import { Calendar, Car, Home, PiggyBank, Plane } from "lucide-react";
import Link from "next/link";
import { formatMoney } from "@/lib/money";

const iconByType = {
  saving: PiggyBank,
  "living-alone": Home,
  car: Car,
  travel: Plane,
};

export function GoalCard({ goal }: { goal: any }) {
  const Icon = iconByType[goal.type as keyof typeof iconByType] ?? PiggyBank;
  return (
    <article className="card pad goal-card">
      <div className="card-header">
        <span className="metric-icon" style={{ background: goal.tone === "warning" ? "var(--warning)" : `var(--${goal.tone})` }}>
          <Icon size={25} />
        </span>
        <span className={`badge ${goal.status === "En riesgo" ? "danger" : goal.status === "Viable" ? "success" : "warning"}`}>
          {goal.status}
        </span>
      </div>
      <div>
        <h3>{goal.name}</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <div>
            <p className="muted small">Meta</p>
            <strong className={`${goal.tone}-text`} style={{ fontSize: 22 }}>{formatMoney(goal.target)}</strong>
          </div>
          <div>
            <p className="muted small">Ahorrado</p>
            <strong>{formatMoney(goal.saved)}</strong>
          </div>
        </div>
      </div>
      <div>
        <div className="progress"><span style={{ width: `${goal.progress}%`, background: goal.tone === "warning" ? "var(--warning)" : `var(--${goal.tone})` }} /></div>
        <p className={`${goal.tone}-text`} style={{ textAlign: "right", fontWeight: 800 }}>{goal.progress}%</p>
      </div>
      <p className="muted"><Calendar size={16} /> Fecha estimada<br /><strong>{goal.date}</strong></p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <Link className="btn" href={`/goals/${goal.type}`}>Ver detalle</Link>
        <Link className="btn primary" href={`/simulators/${goal.type}`}>Simular</Link>
      </div>
    </article>
  );
}
