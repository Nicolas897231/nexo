"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Car, Home, PiggyBank, Plane } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { normalizeMoney } from "@/lib/money";
import { createGoal, type GoalType } from "@/services/api/goals.api";

const options: { icon: typeof PiggyBank; type: GoalType; title: string; text: string }[] = [
  { icon: PiggyBank, type: "saving", title: "Ahorrar", text: "Fondo, reserva o compra futura." },
  { icon: Home, type: "live_alone", title: "Vivir solo", text: "Independencia con costos reales." },
  { icon: Car, type: "buy_car", title: "Comprar carro", text: "Cuota saludable y gastos asociados." },
  { icon: Plane, type: "travel", title: "Viajar", text: "Presupuesto, fecha y aporte mensual." },
];

export default function NewGoalPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [goalType, setGoalType] = useState<GoalType>("saving");
  const [name, setName] = useState("Ahorrar");
  const [targetAmount, setTargetAmount] = useState("");
  const [currentAmount, setCurrentAmount] = useState("0");
  const [monthlyContribution, setMonthlyContribution] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      createGoal({
        goal_type: goalType,
        name,
        target_amount: normalizeMoney(targetAmount),
        current_amount: normalizeMoney(currentAmount),
        monthly_contribution: normalizeMoney(monthlyContribution),
        target_date: targetDate || undefined,
        priority: 3,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["goals"] });
      router.push("/goals");
    },
    onError: () => setError("No pudimos crear la meta. Revisa los montos y la fecha."),
  });

  return (
    <main className="page">
      <PageHeader title="Crear nueva meta" description="Define tu objetivo y guarda una meta real en tu cuenta." />
      <section className="card pad">
        <div className="stepper">
          {["Tipo", "Datos", "Aporte", "Confirmacion"].map((step, index) => (
            <div className={`step ${index === 0 ? "active" : ""}`} key={step}><span className="step-dot">{index + 1}</span><strong>{step}</strong></div>
          ))}
        </div>
      </section>
      <section className="grid four" style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 18, marginTop: 18 }}>
        {options.map((item) => {
          const Icon = item.icon;
          return (
            <button
              className={`card pad ${goalType === item.type ? "active" : ""}`}
              key={item.type}
              type="button"
              style={{ textAlign: "left", borderColor: goalType === item.type ? "var(--primary)" : undefined }}
              onClick={() => {
                setGoalType(item.type);
                setName(item.title);
              }}
            >
              <Icon className="primary-text" size={34} />
              <h2>{item.title}</h2>
              <p className="muted">{item.text}</p>
            </button>
          );
        })}
      </section>
      <form
        className="card pad"
        style={{ marginTop: 18 }}
        onSubmit={(event) => {
          event.preventDefault();
          setError(null);
          mutation.mutate();
        }}
      >
        <h2>Datos de la meta</h2>
        <div className="form-grid">
          <label className="field"><span>Nombre</span><input className="input" value={name} onChange={(event) => setName(event.target.value)} required /></label>
          <label className="field"><span>Monto objetivo</span><input className="input" inputMode="numeric" placeholder="Ej. 6500000" value={targetAmount} onChange={(event) => setTargetAmount(event.target.value)} required /></label>
          <label className="field"><span>Ahorrado actualmente</span><input className="input" inputMode="numeric" placeholder="Ej. 500000" value={currentAmount} onChange={(event) => setCurrentAmount(event.target.value)} /></label>
          <label className="field"><span>Aporte mensual planeado</span><input className="input" inputMode="numeric" placeholder="Ej. 300000" value={monthlyContribution} onChange={(event) => setMonthlyContribution(event.target.value)} /></label>
          <label className="field"><span>Fecha objetivo</span><input className="input" type="date" value={targetDate} onChange={(event) => setTargetDate(event.target.value)} /></label>
        </div>
        {error ? <p className="badge danger" style={{ marginTop: 16 }}>{error}</p> : null}
        <button className="btn primary" style={{ marginTop: 18 }} disabled={mutation.isPending} type="submit">
          {mutation.isPending ? "Guardando..." : "Crear meta"}
        </button>
      </form>
    </main>
  );
}
