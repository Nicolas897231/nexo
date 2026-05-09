import { Calendar, Car, Home, PiggyBank, Plane } from "lucide-react";
import Link from "next/link";
import { formatMoney } from "@/lib/money";
import type { Goal } from "@/services/api/goals.api";

const iconByType = {
  saving: PiggyBank,
  live_alone: Home,
  buy_car: Car,
  travel: Plane,
};

const simulatorHrefByType = {
  saving: "/simulators/saving",
  live_alone: "/simulators/living-alone",
  buy_car: "/simulators/car",
  travel: "/simulators/travel",
};

const toneByType = {
  saving: "success",
  live_alone: "primary",
  buy_car: "purple",
  travel: "warning",
};

export function GoalCard({ goal }: { goal: Goal }) {
  const Icon = iconByType[goal.goal_type] ?? PiggyBank;
  const target = Number(goal.target_amount);
  const current = Number(goal.current_amount);
  const progress = target > 0 ? Math.min(Math.round((current / target) * 100), 100) : 0;
  const tone = toneByType[goal.goal_type] ?? "primary";
  const label = goal.status === "completed" ? "Completada" : goal.status === "paused" ? "Pausada" : "Activa";
  return (
    <article className="card pad goal-card">
      <div className="card-header">
        <span className="metric-icon" style={{ background: tone === "warning" ? "var(--warning)" : `var(--${tone})` }}>
          <Icon size={25} />
        </span>
        <span className={`badge ${goal.status === "paused" ? "warning" : goal.status === "not_viable" ? "danger" : "success"}`}>
          {label}
        </span>
      </div>
      <div>
        <h3>{goal.name}</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <div>
            <p className="muted small">Meta</p>
            <strong className={`${tone}-text`} style={{ fontSize: 22 }}>{formatMoney(goal.target_amount)}</strong>
          </div>
          <div>
            <p className="muted small">Ahorrado</p>
            <strong>{formatMoney(goal.current_amount)}</strong>
          </div>
        </div>
      </div>
      <div>
        <div className="progress"><span style={{ width: `${progress}%`, background: tone === "warning" ? "var(--warning)" : `var(--${tone})` }} /></div>
        <p className={`${tone}-text`} style={{ textAlign: "right", fontWeight: 800 }}>{progress}%</p>
      </div>
      <p className="muted"><Calendar size={16} /> Fecha estimada<br /><strong>{goal.target_date || "Sin fecha"}</strong></p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <Link className="btn" href={`/goals/${goal.id}`}>Ver detalle</Link>
        <Link className="btn primary" href={simulatorHrefByType[goal.goal_type]}>Simular</Link>
      </div>
    </article>
  );
}
