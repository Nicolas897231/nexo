import { SimulatorTabs } from "@/components/simulators/simulator-tabs";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney } from "@/lib/money";

export default function CarSimulatorPage() {
  const fields = [
    ["Valor del vehiculo", "$45.000.000"],
    ["Cuota inicial", "20%"],
    ["Plazo del credito", "60 meses"],
    ["Tasa de interes (EA)", "12,50%"],
    ["Seguro todo riesgo", "3,20%"],
    ["Impuestos y tramites", "$600.000/año"],
    ["Mantenimiento", "$1.200.000/año"],
    ["Parqueadero", "$200.000/mes"],
  ];
  return (
    <main className="page">
      <PageHeader title="Mis metas" description="Define tus objetivos y simula como alcanzarlos." actions={<button className="btn primary" type="button">Crear nueva meta</button>} />
      <SimulatorTabs active="/simulators/car" />
      <section className="grid two" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Simulador: Comprar carro</h2>
          {fields.map(([label, value]) => <div className="range-row" key={label}><strong>{label}</strong><input type="range" defaultValue={55} /><input className="input" value={value} readOnly /></div>)}
          <p className="muted small">Los calculos son estimados y pueden variar segun la entidad financiera y tu perfil crediticio.</p>
        </article>
        <article className="grid">
          <div className="grid two">
            <Result title="Cuota mensual estimada" value="1152000.00" tone="primary" />
            <Result title="Costo mensual total del carro" value="1832000.00" tone="success" />
            <Result title="Rango saludable" text="Hasta $1.900.000" tone="warning" />
            <Result title="Semaforo de viabilidad" text="Viable" tone="success" />
          </div>
          <article className="card pad">
            <h2 className="card-title">Ahorrar vs financiar</h2>
            <table className="table"><tbody>{["Valor del vehiculo", "Cuota inicial", "Tiempo para tenerlo", "Cuota mensual", "Intereses pagados"].map((row) => <tr key={row}><td>{row}</td><td>Financiar ahora</td><td>Ahorrar y comprar</td></tr>)}</tbody></table>
          </article>
        </article>
      </section>
    </main>
  );
}

function Result({ title, value, text, tone }: { title: string; value?: string; text?: string; tone: string }) {
  return <div className="card pad"><p className="muted">{title}</p><h2 className={`${tone}-text`}>{text ?? formatMoney(value ?? "0.00")}</h2></div>;
}
