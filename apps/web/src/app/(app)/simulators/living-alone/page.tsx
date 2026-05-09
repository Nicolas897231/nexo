"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { SimulatorTabs } from "@/components/simulators/simulator-tabs";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney, normalizeMoney } from "@/lib/money";
import { convertSimulationToGoal, simulateLivingAlone, type SimulationResult } from "@/services/api/simulations.api";

export default function LivingAloneSimulatorPage() {
  const [values, setValues] = useState({
    monthly_net_income: "4250000",
    rent_amount: "1600000",
    utilities_amount: "180000",
    food_amount: "450000",
    transport_amount: "120000",
    internet_amount: "100000",
    personal_basics_amount: "250000",
    moving_initial_cost: "2500000",
    emergency_fund_amount: "3200000",
  });
  const [result, setResult] = useState<SimulationResult | null>(null);
  const simulate = useMutation({
    mutationFn: () => simulateLivingAlone(Object.fromEntries(Object.entries(values).map(([key, value]) => [key, normalizeMoney(value)]))),
    onSuccess: setResult,
  });
  const convert = useMutation({ mutationFn: () => convertSimulationToGoal(String(result?.simulation_id)) });
  return (
    <main className="page">
      <PageHeader title="Simulador: Vivir solo" description="Calcula cuanto necesitas para independizarte y mantener tu estilo de vida." actions={<button className="btn" type="button" onClick={() => setResult(null)}>Reiniciar simulacion</button>} />
      <SimulatorTabs active="/simulators/living-alone" />
      <section className="grid two" style={{ marginTop: 18 }}>
        <form className="card pad" onSubmit={(event) => { event.preventDefault(); simulate.mutate(); }}>
          <h2 className="card-title">Configura tu escenario</h2>
          <div className="form-grid" style={{ marginTop: 18 }}>
            {Object.entries(values).map(([key, value]) => (
              <label className="field" key={key}><span>{labelFor(key)}</span><input className="input" inputMode="numeric" value={value} onChange={(event) => setValues((current) => ({ ...current, [key]: event.target.value }))} /></label>
            ))}
          </div>
          <button className="btn primary" style={{ marginTop: 18 }} type="submit">Simular vivir solo</button>
        </form>
        <article className="grid">
          <div className="grid two">
            <Result title="Costo inicial de mudanza" value={String(result?.moving_initial_cost ?? "0.00")} tone="purple" />
            <Result title="Costo mensual" value={String(result?.monthly_living_cost ?? "0.00")} tone="primary" />
            <Result title="Fondo requerido" value={String(result?.emergency_fund_required ?? "0.00")} tone="success" />
            <div className="card pad"><p className="muted">Semaforo</p><h2 className="success-text">{result ? "Calculado" : "Pendiente"}</h2></div>
          </div>
          {result ? <button className="btn primary" type="button" onClick={() => convert.mutate()}>Convertir en meta</button> : null}
        </article>
      </section>
    </main>
  );
}

function labelFor(key: string) {
  const labels: Record<string, string> = {
    monthly_net_income: "Ingreso mensual",
    rent_amount: "Arriendo",
    utilities_amount: "Servicios publicos",
    food_amount: "Alimentacion",
    transport_amount: "Transporte",
    internet_amount: "Internet y celular",
    personal_basics_amount: "Gastos personales",
    moving_initial_cost: "Costo de mudanza",
    emergency_fund_amount: "Fondo de emergencia actual",
  };
  return labels[key] ?? key;
}

function Result({ title, value, tone }: { title: string; value: string; tone: string }) {
  return <div className="card pad"><p className="muted">{title}</p><h2 className={`${tone}-text`}>{formatMoney(value)}</h2></div>;
}
