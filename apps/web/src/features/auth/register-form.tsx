"use client";

import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";
import { ApiClientError } from "@/lib/api-client";
import { login, register } from "@/services/api/auth.api";

export function RegisterForm() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (password !== confirmPassword) {
      setError("Las contrasenas no coinciden.");
      return;
    }
    if (password.length < 12) {
      setError("La contrasena debe tener minimo 12 caracteres.");
      return;
    }
    if (!acceptedTerms) {
      setError("Debes aceptar los terminos.");
      return;
    }
    setLoading(true);
    try {
      await register({ full_name: fullName, email, password, accepted_terms: acceptedTerms });
      await login({ email, password, remember_device: true });
      router.push("/onboarding");
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiClientError
          ? `${err.message}${err.traceId ? ` Codigo: ${err.traceId}` : ""}`
          : "No pudimos crear la cuenta.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="grid" onSubmit={onSubmit}>
      <label className="field">
        <span>Nombre completo</span>
        <input className="input" required value={fullName} onChange={(event) => setFullName(event.target.value)} />
      </label>
      <label className="field">
        <span>Email</span>
        <input className="input" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
      </label>
      <label className="field">
        <span>Contrasena</span>
        <input className="input" type="password" required value={password} onChange={(event) => setPassword(event.target.value)} />
      </label>
      <label className="field">
        <span>Confirmar contrasena</span>
        <input className="input" type="password" required value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} />
      </label>
      <label>
        <input checked={acceptedTerms} onChange={(event) => setAcceptedTerms(event.target.checked)} type="checkbox" /> Acepto terminos y condiciones
      </label>
      {error ? <p className="badge danger">{error}</p> : null}
      <button className="btn primary" disabled={loading} type="submit">
        {loading ? "Creando..." : "Crear cuenta"}
      </button>
    </form>
  );
}
