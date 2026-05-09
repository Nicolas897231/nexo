import { Car, CheckCircle2, Home, PiggyBank, Plane } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";

const options = [
  { icon: PiggyBank, title: "Ahorrar", text: "Fondo, reserva o compra futura." },
  { icon: Home, title: "Vivir solo", text: "Independencia con costos reales." },
  { icon: Car, title: "Comprar carro", text: "Cuota saludable y gastos asociados." },
  { icon: Plane, title: "Viajar", text: "Presupuesto, fecha y aporte mensual." },
];

export default function NewGoalPage() {
  return (
    <main className="page">
      <PageHeader title="Crear nueva meta" description="Define tu objetivo y revisa el esfuerzo mensual antes de guardarlo." />
      <section className="card pad">
        <div className="stepper">
          {["Tipo", "Datos", "Simulacion", "Confirmacion"].map((step, index) => (
            <div className={`step ${index === 0 ? "active" : ""}`} key={step}><span className="step-dot">{index + 1}</span><strong>{step}</strong></div>
          ))}
        </div>
      </section>
      <section className="grid four" style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 18, marginTop: 18 }}>
        {options.map((item) => {
          const Icon = item.icon;
          return (
            <button className="card pad" key={item.title} type="button" style={{ textAlign: "left" }}>
              <Icon className="primary-text" size={34} />
              <h2>{item.title}</h2>
              <p className="muted">{item.text}</p>
              <span className="badge success"><CheckCircle2 size={14} /> Listo para simular</span>
            </button>
          );
        })}
      </section>
    </main>
  );
}
