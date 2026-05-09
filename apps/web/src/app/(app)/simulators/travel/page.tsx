"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { SimulatorTabs } from "@/components/simulators/simulator-tabs";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney, normalizeMoney } from "@/lib/money";
import { convertSimulationToGoal, simulateTravel, type SimulationResult } from "@/services/api/simulations.api";

export default function TravelSimulatorPage() {
  const [destination, setDestination] = useState("Europa - 15 dias");
  const [date, setDate] = useState("");
  const [income, setIncome] = useState("4250000");
  const [flights, setFlights] = useState("1600000");
  const [lodging, setLodging] = useState("1800000");
  const [food, setFood] = useState("900000");
  const [extras, setExtras] = useState("700000");
  const [current, setCurrent] = useState("1200000");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const simulate = useMutation({
    mutationFn: () => simulateTravel({ monthly_net_income: normalizeMoney(income), destination, travel_date: date || null, flights_amount: normalizeMoney(flights), lodging_amount: normalizeMoney(lodging), food_amount: normalizeMoney(food), extras_amount: normalizeMoney(extras), current_amount: normalizeMoney(current) }),
    onSuccess: setResult,
  });
  const convert = useMutation({ mutationFn: () => convertSimulationToGoal(String(result?.simulation_id)) });
  return (
    <main className="page">
      <PageHeader title="Simulador: Viajar" description="Planifica tu viaje ideal y descubre cuanto necesitas ahorrar." />
      <SimulatorTabs active="/simulators/travel" />
      <section className="grid two" style={{ marginTop: 18 }}>
        <form className="card pad" onSubmit={(event) => { event.preventDefault(); simulate.mutate(); }}>
          <h2 className="card-title">Configura tu viaje</h2>
          <div className="form-grid" style={{ marginTop: 18 }}>
            <label className="field"><span>Destino</span><input className="input" value={destination} onChange={(event) => setDestination(event.target.value)} /></label>
            <label className="field"><span>Fecha del viaje</span><input className="input" type="date" value={date} onChange={(event) => setDate(event.target.value)} /></label>
            <Input label="Ingreso mensual" value={income} setValue={setIncome} />
            <Input label="Vuelos" value={flights} setValue={setFlights} />
            <Input label="Hospedaje" value={lodging} setValue={setLodging} />
            <Input label="Alimentacion" value={food} setValue={setFood} />
            <Input label="Actividades y extras" value={extras} setValue={setExtras} />
            <Input label="Ahorros acumulados" value={current} setValue={setCurrent} />
          </div>
          <button className="btn primary" style={{ marginTop: 18 }} type="submit">Simular viaje</button>
        </form>
        <article className="grid">
          <div className="grid two">
            <Result title="Meta total" value={String(result?.total_cost ?? "0.00")} tone="primary" />
            <Result title="Pendiente" value={String(result?.pending_amount ?? "0.00")} tone="warning" />
            <Result title="Aporte mensual recomendado" value={String(result?.required_monthly ?? "0.00")} tone="success" />
            <div className="card pad"><p className="muted">Meses disponibles</p><h2 className="purple-text">{String(result?.months_until_trip ?? "-")}</h2></div>
          </div>
          {result ? <button className="btn primary" type="button" onClick={() => convert.mutate()}>Convertir en meta</button> : null}
        </article>
      </section>
    </main>
  );
}

function Input({ label, value, setValue }: { label: string; value: string; setValue: (value: string) => void }) {
  return <label className="field"><span>{label}</span><input className="input" inputMode="numeric" value={value} onChange={(event) => setValue(event.target.value)} /></label>;
}

function Result({ title, value, tone }: { title: string; value: string; tone: string }) {
  return <div className="card pad"><p className="muted">{title}</p><h2 className={`${tone}-text`}>{formatMoney(value)}</h2></div>;
}
