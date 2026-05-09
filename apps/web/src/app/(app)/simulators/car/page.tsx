"use client";

import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { SimulatorTabs } from "@/components/simulators/simulator-tabs";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney, normalizeMoney } from "@/lib/money";
import { convertSimulationToGoal, simulateCar, type SimulationResult } from "@/services/api/simulations.api";

export default function CarSimulatorPage() {
  const [income, setIncome] = useState("4250000");
  const [vehicle, setVehicle] = useState("45000000");
  const [down, setDown] = useState("9000000");
  const [monthlyRate, setMonthlyRate] = useState("0.010000");
  const [term, setTerm] = useState(60);
  const [insurance, setInsurance] = useState("1440000");
  const [fuel, setFuel] = useState("300000");
  const [maintenance, setMaintenance] = useState("1200000");
  const [parking, setParking] = useState("200000");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const simulate = useMutation({
    mutationFn: () => simulateCar({
      monthly_net_income: normalizeMoney(income),
      vehicle_price: normalizeMoney(vehicle),
      down_payment: normalizeMoney(down),
      monthly_rate: monthlyRate,
      term_months: term,
      insurance_monthly: normalizeMoney(insurance),
      fuel_monthly: normalizeMoney(fuel),
      maintenance_monthly: normalizeMoney(maintenance),
      parking_monthly: normalizeMoney(parking),
    }),
    onSuccess: setResult,
  });
  const convert = useMutation({ mutationFn: () => convertSimulationToGoal(String(result?.simulation_id)) });
  return (
    <main className="page">
      <PageHeader title="Simulador: Comprar carro" description="Calcula cuota, gastos asociados y viabilidad." actions={<Link className="btn primary" href="/goals/new">Crear nueva meta</Link>} />
      <SimulatorTabs active="/simulators/car" />
      <section className="grid two" style={{ marginTop: 18 }}>
        <form className="card pad" onSubmit={(event) => { event.preventDefault(); simulate.mutate(); }}>
          <h2 className="card-title">Datos del vehiculo</h2>
          <div className="form-grid" style={{ marginTop: 18 }}>
            <Input label="Ingreso mensual" value={income} setValue={setIncome} />
            <Input label="Valor del vehiculo" value={vehicle} setValue={setVehicle} />
            <Input label="Cuota inicial" value={down} setValue={setDown} />
            <label className="field"><span>Plazo del credito</span><input className="input" type="number" value={term} onChange={(event) => setTerm(Number(event.target.value))} /></label>
            <label className="field"><span>Tasa mensual decimal</span><input className="input" value={monthlyRate} onChange={(event) => setMonthlyRate(event.target.value)} /></label>
            <Input label="Seguro mensual" value={insurance} setValue={setInsurance} />
            <Input label="Combustible mensual" value={fuel} setValue={setFuel} />
            <Input label="Mantenimiento mensual" value={maintenance} setValue={setMaintenance} />
            <Input label="Parqueadero mensual" value={parking} setValue={setParking} />
          </div>
          <button className="btn primary" style={{ marginTop: 18 }} type="submit">Simular carro</button>
        </form>
        <article className="grid">
          <div className="grid two">
            <Result title="Cuota mensual estimada" value={String(result?.monthly_payment ?? "0.00")} tone="primary" />
            <Result title="Costo mensual total" value={String(result?.monthly_total_car_cost ?? "0.00")} tone="success" />
            <Result title="Monto financiado" value={String(result?.financed_amount ?? "0.00")} tone="warning" />
            <Result title="Gastos extra mensuales" value={String(result?.monthly_extra_costs ?? "0.00")} tone="purple" />
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
