import Link from "next/link";

export default function ForgotPasswordPage() {
  return (
    <main className="auth-shell">
      <section className="auth-hero"><h1>Recupera tu acceso</h1><p>Te mostraremos siempre un mensaje seguro sin revelar si el correo existe.</p></section>
      <section className="auth-card">
        <div className="card pad">
          <h1>Recuperar contraseña</h1>
          <label className="field"><span>Email</span><input className="input" type="email" /></label>
          <button className="btn primary" style={{ marginTop: 18, width: "100%" }} type="button">Enviar instrucciones</button>
          <Link className="primary-text" href="/login">Volver a login</Link>
        </div>
      </section>
    </main>
  );
}
