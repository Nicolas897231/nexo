import { CheckCircle2 } from "lucide-react";
import { SimulatorTabs } from "@/components/simulators/simulator-tabs";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney } from "@/lib/money";

export default function LivingAloneSimulatorPage() {
  const fields = [
    ["Ciudad", "Medellin"],
    ["Arriendo estimado", "$1.600.000"],
    ["Deposito", "$1.600.000"],
    ["Servicios publicos", "$180.000"],
    ["Alimentacion", "$450.000"],
    ["Transporte", "$120.000"],
    ["Internet y celular", "$100.000"],
    ["Muebles iniciales", "$2.500.000"],
    ["Fondo de emergencia", "$3.200.000"],
  ];
  return (
    <main className="page">
      <PageHeader title="Simulador: Vivir solo" description="Calcula cuanto necesitas para independizarte y mantener tu estilo de vida." actions={<button className="btn" type="button">Reiniciar simulacion</button>} />
      <SimulatorTabs active="/simulators/living-alone" />
      <section className="grid two" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Configura tu escenario</h2>
          {fields.map(([label, value], index) => (
            <div className="range-row" key={label}><strong>{label}</strong>{index === 0 ? <select className="select" defaultValue={value}><option>{value}</option></select> : <><input type="range" defaultValue={60} /><input className="input" value={value} readOnly /></>}</div>
          ))}
        </article>
        <article className="grid">
          <div className="grid two">
            <Result title="Costo inicial de mudanza" value="7080000.00" tone="purple" />
            <Result title="Costo mensual de sostenimiento" value="2450000.00" tone="primary" />
            <Result title="Arriendo recomendado" text="$1.550.000 - $1.800.000" tone="success" />
            <Result title="Ingreso minimo recomendado" value="3500000.00" tone="warning" />
            <div className="card pad"><p className="muted">Semaforo de viabilidad</p><h2 className="success-text"><CheckCircle2 /> Viable</h2><p>Tu plan es financieramente viable.</p></div>
            <Result title="Ahorro mensual sugerido" value="1250000.00" tone="success" />
          </div>
          <article className="card pad">
            <h2 className="card-title">Plan para alcanzar tu meta</h2>
            <div className="stepper">{["Define tu plan", "Empieza a ahorrar", "Fondo completo", "Mudanza"].map((step, index) => <div className={`step ${index < 2 ? "done" : ""}`} key={step}><span className="step-dot">{index + 1}</span><strong>{step}</strong></div>)}</div>
          </article>
        </article>
      </section>
    </main>
  );
}

function Result({ title, value, text, tone }: { title: string; value?: string; text?: string; tone: string }) {
  return <div className="card pad"><p className="muted">{title}</p><h2 className={`${tone}-text`}>{text ?? formatMoney(value ?? "0.00")}</h2></div>;
}
