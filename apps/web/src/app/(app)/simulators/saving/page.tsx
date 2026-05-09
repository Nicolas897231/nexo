"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { SimulatorTabs } from "@/components/simulators/simulator-tabs";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney, normalizeMoney } from "@/lib/money";
import { convertSimulationToGoal, simulateSavings, type SimulationResult } from "@/services/api/simulations.api";

export default function SavingSimulatorPage() {
  const [income, setIncome] = useState("4250000");
  const [target, setTarget] = useState("6000000");
  const [current, setCurrent] = useState("1200000");
  const [monthly, setMonthly] = useState("500000");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const simulate = useMutation({
    mutationFn: () => simulateSavings({ monthly_net_income: normalizeMoney(income), target_amount: normalizeMoney(target), current_amount: normalizeMoney(current), monthly_contribution: normalizeMoney(monthly) }),
    onSuccess: setResult,
  });
  const convert = useMutation({ mutationFn: () => convertSimulationToGoal(String(result?.simulation_id)) });
  return (
    <main className="page">
      <PageHeader title="Simulador: Ahorrar" description="Calcula cuanto ahorrar, en cuanto tiempo y bajo que estrategia." />
      <SimulatorTabs active="/simulators/saving" />
      <section className="grid two" style={{ marginTop: 18 }}>
        <form className="card pad" onSubmit={(event) => { event.preventDefault(); simulate.mutate(); }}>
          <h2 className="card-title">Configura tu meta</h2>
          <div className="form-grid" style={{ marginTop: 18 }}>
            <Input label="Ingreso mensual" value={income} setValue={setIncome} />
            <Input label="Monto objetivo" value={target} setValue={setTarget} />
            <Input label="Ahorro actual" value={current} setValue={setCurrent} />
            <Input label="Aporte mensual" value={monthly} setValue={setMonthly} />
          </div>
          <button className="btn primary" style={{ marginTop: 18 }} type="submit">Simular ahorro</button>
        </form>
        <article className="grid">
          <div className="card pad"><p className="muted">Monto pendiente</p><h2 className="primary-text">{formatMoney(String(result?.pending_amount ?? "0.00"))}</h2></div>
          <div className="card pad"><p className="muted">Meses requeridos</p><h2 className="success-text">{String(result?.months_required ?? "-")}</h2></div>
          <div className="card pad"><p className="muted">Viabilidad</p><h2 className="success-text">{result ? "Simulacion guardada" : "Pendiente"}</h2></div>
          {result ? <button className="btn primary" type="button" onClick={() => convert.mutate()}>Convertir en meta</button> : null}
        </article>
      </section>
    </main>
  );
}

function Input({ label, value, setValue }: { label: string; value: string; setValue: (value: string) => void }) {
  return <label className="field"><span>{label}</span><input className="input" inputMode="numeric" value={value} onChange={(event) => setValue(event.target.value)} /></label>;
}
