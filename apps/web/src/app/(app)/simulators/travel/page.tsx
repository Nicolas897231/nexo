import { SimulatorTabs } from "@/components/simulators/simulator-tabs";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney } from "@/lib/money";

export default function TravelSimulatorPage() {
  return (
    <main className="page">
      <PageHeader title="Simulador: Viajar" description="Planifica tu viaje ideal y descubre cuanto necesitas ahorrar." />
      <SimulatorTabs active="/simulators/travel" />
      <section className="grid two" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Configura tu viaje</h2>
          {["Destino", "Fecha del viaje", "Presupuesto total estimado", "Vuelos", "Hospedaje", "Alimentacion", "Actividades", "Extras", "Ahorro mensual disponible", "Ahorros ya acumulados"].map((label, index) => (
            <label className="field" key={label} style={{ marginBottom: 12 }}>
              <span>{label}</span>
              <input className="input" value={index === 0 ? "Europa - 15 dias" : index === 1 ? "15 Oct 2025" : "$800.000"} readOnly />
            </label>
          ))}
        </article>
        <article className="grid">
          <div className="grid two">
            <Result title="Meta total" value="5400000.00" tone="primary" />
            <Result title="Aporte mensual recomendado" value="1018000.00" tone="success" />
            <Result title="Fecha estimada del viaje" text="15 Oct 2025" tone="primary" />
            <Result title="Probabilidad de llegar" text="86%" tone="purple" />
            <Result title="Semaforo de viabilidad" text="Viable" tone="success" />
            <div className="card pad"><h2 className="card-title">Resumen de recomendacion</h2><p>Con tu ahorro actual lograras tu viaje 23 dias antes de la fecha planeada.</p></div>
          </div>
          <article className="card pad">
            <h2 className="card-title">Progreso de tu meta: Viajar</h2>
            <div className="progress"><span style={{ width: "53%", background: "var(--success)" }} /></div>
            <p className="success-text"><strong>$2.850.000</strong> ahorrado · faltan $2.550.000</p>
          </article>
        </article>
      </section>
    </main>
  );
}

function Result({ title, value, text, tone }: { title: string; value?: string; text?: string; tone: string }) {
  return <div className="card pad"><p className="muted">{title}</p><h2 className={`${tone}-text`}>{text ?? formatMoney(value ?? "0.00")}</h2></div>;
}
