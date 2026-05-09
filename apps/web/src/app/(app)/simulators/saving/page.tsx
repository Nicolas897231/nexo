import { SimulatorTabs } from "@/components/simulators/simulator-tabs";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney } from "@/lib/money";

export default function SavingSimulatorPage() {
  return (
    <main className="page">
      <PageHeader title="Simulador: Ahorrar" description="Calcula cuanto ahorrar, en cuanto tiempo y bajo que estrategia." />
      <SimulatorTabs active="/simulators/saving" />
      <section className="grid two" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Configura tu meta</h2>
          {[
            ["Monto objetivo", "$6.000.000"],
            ["Ahorro actual", "$1.200.000"],
            ["Aporte mensual", "$500.000"],
            ["Fecha objetivo", "31 dic 2026"],
          ].map(([label, value]) => (
            <div className="range-row" key={label}><strong>{label}</strong><input type="range" defaultValue={65} /><input className="input" value={value} readOnly /></div>
          ))}
        </article>
        <article className="grid">
          <div className="card pad"><p className="muted">Fecha estimada</p><h2 className="primary-text">Oct 2026</h2></div>
          <div className="card pad"><p className="muted">Aporte recomendado</p><h2 className="success-text">{formatMoney("480000.00")}</h2></div>
          <div className="card pad"><p className="muted">Semaforo de viabilidad</p><h2 className="success-text">Viable</h2><p>Tu plan luce alcanzable.</p></div>
        </article>
      </section>
    </main>
  );
}
