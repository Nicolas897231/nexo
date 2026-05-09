import { LoginForm } from "@/features/auth/login-form";

export default function LoginPage() {
  return (
    <main className="auth-shell">
      <section className="auth-hero">
        <div className="brand"><span className="brand-mark"><span /><span /><span /></span><strong>NexoVia</strong></div>
        <h1 style={{ fontSize: 52, margin: 0 }}>Decide mejor con tus metas financieras claras.</h1>
        <p style={{ fontSize: 20 }}>Organiza ingresos, egresos, ahorro y simulaciones desde un dashboard seguro.</p>
      </section>
      <section className="auth-card">
        <div className="card pad">
          <h1>Iniciar sesion</h1>
          <p className="muted">Accede a tu panel financiero.</p>
          <LoginForm />
        </div>
      </section>
    </main>
  );
}
