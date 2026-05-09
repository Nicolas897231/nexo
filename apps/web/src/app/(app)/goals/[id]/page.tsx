"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney, normalizeMoney } from "@/lib/money";
import { addGoalContribution, getGoal } from "@/services/api/goals.api";

export default function GoalDetailPage() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [amount, setAmount] = useState("");
  const { data: goal } = useQuery({ queryKey: ["goal", params.id], queryFn: () => getGoal(params.id) });
  const contribution = useMutation({
    mutationFn: () => addGoalContribution(params.id, { amount: normalizeMoney(amount), contribution_date: new Date().toISOString().slice(0, 10) }),
    onSuccess: async () => {
      setAmount("");
      await queryClient.invalidateQueries({ queryKey: ["goal", params.id] });
      await queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });
  if (!goal) return <main className="page"><div className="skeleton" style={{ height: 260 }} /></main>;
  const progress = Number(goal.target_amount) > 0 ? Math.min(Math.round((Number(goal.current_amount) / Number(goal.target_amount)) * 100), 100) : 0;
  return (
    <main className="page">
      <PageHeader title={goal.name} description="Consulta el plan, aportes e impacto de esta meta." />
      <section className="grid two">
        <article className="card pad">
          <h2>{formatMoney(goal.current_amount)} de {formatMoney(goal.target_amount)}</h2>
          <div className="progress"><span style={{ width: `${progress}%` }} /></div>
          <p className="muted">Estado: {goal.status} · Fecha estimada: {goal.target_date || "Sin fecha"}</p>
          <div className="stepper" style={{ marginTop: 30 }}>
            {["Definida", "En progreso", "En camino", "Meta alcanzada"].map((step, index) => (
              <div className={`step ${index <= Math.floor(progress / 34) ? "done" : ""}`} key={step}><span className="step-dot">{index + 1}</span><strong>{step}</strong></div>
            ))}
          </div>
        </article>
        <form className="card pad" onSubmit={(event) => { event.preventDefault(); contribution.mutate(); }}>
          <h2 className="card-title">Agregar aporte</h2>
          <label className="field" style={{ marginTop: 16 }}><span>Monto</span><input className="input" inputMode="numeric" value={amount} onChange={(event) => setAmount(event.target.value)} /></label>
          <button className="btn primary" style={{ marginTop: 16 }} type="submit">Guardar aporte</button>
        </form>
      </section>
    </main>
  );
}
