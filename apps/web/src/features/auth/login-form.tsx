"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";
import { ApiClientError } from "@/lib/api-client";
import { login } from "@/services/api/auth.api";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberDevice, setRememberDevice] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login({ email, password, remember_device: rememberDevice });
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiClientError
          ? `${err.message}${err.traceId ? ` Codigo: ${err.traceId}` : ""}`
          : "No pudimos iniciar sesion.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="grid" onSubmit={onSubmit}>
      <label className="field">
        <span>Email</span>
        <input
          className="input"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="andres@email.com"
        />
      </label>
      <label className="field">
        <span>Contrasena</span>
        <input
          className="input"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </label>
      <label>
        <input
          checked={rememberDevice}
          onChange={(event) => setRememberDevice(event.target.checked)}
          type="checkbox"
        />{" "}
        Recordar este dispositivo
      </label>
      {error ? <p className="badge danger">{error}</p> : null}
      <button className="btn primary" disabled={loading} type="submit">
        {loading ? "Iniciando..." : "Iniciar sesion"}
      </button>
      <Link className="primary-text" href="/forgot-password">
        Olvide mi contrasena
      </Link>
      <Link href="/register">Crear cuenta</Link>
    </form>
  );
}
