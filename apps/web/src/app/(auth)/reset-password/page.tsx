import Link from "next/link";

export default function ResetPasswordPage() {
  return (
    <main className="auth-shell">
      <section className="auth-hero"><h1>Nueva contraseña</h1><p>Usa una contraseña fuerte de minimo 12 caracteres.</p></section>
      <section className="auth-card">
        <div className="card pad">
          <h1>Restablecer contraseña</h1>
          <form className="grid">
            <label className="field"><span>Token</span><input className="input" /></label>
            <label className="field"><span>Nueva contraseña</span><input className="input" type="password" /></label>
            <Link className="btn primary" href="/login">Guardar contraseña</Link>
          </form>
        </div>
      </section>
    </main>
  );
}
