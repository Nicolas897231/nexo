import Link from "next/link";
import { PageHeader } from "@/components/ui/page-header";

export default function OnboardingPage() {
  return (
    <main className="page" style={{ maxWidth: 1080, margin: "0 auto" }}>
      <PageHeader title="Onboarding financiero" description="Completa cuatro pasos para activar tu dashboard." />
      <section className="card pad">
        <div className="stepper">
          {["Perfil", "Ingresos", "Gastos y deudas", "Meta inicial"].map((step, index) => <div className={`step ${index === 0 ? "active" : ""}`} key={step}><span className="step-dot">{index + 1}</span><strong>{step}</strong></div>)}
        </div>
      </section>
      <section className="card pad" style={{ marginTop: 18 }}>
        <h2>Perfil financiero</h2>
        <div className="form-grid">
          <input className="input" placeholder="Ciudad" />
          <input className="input" placeholder="Moneda principal" />
          <input className="input" placeholder="Ingreso mensual" />
          <input className="input" placeholder="Dia de pago" />
        </div>
        <Link className="btn primary" style={{ marginTop: 18 }} href="/dashboard">Completar onboarding</Link>
      </section>
    </main>
  );
}
