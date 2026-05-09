import { RegisterForm } from "@/features/auth/register-form";

export default function RegisterPage() {
  return (
    <main className="auth-shell">
      <section className="auth-hero"><h1>Empieza con NexoVia</h1><p>Crea tu cuenta y configura tu primer plan financiero.</p></section>
      <section className="auth-card">
        <div className="card pad">
          <h1>Crear cuenta</h1>
          <RegisterForm />
        </div>
      </section>
    </main>
  );
}
