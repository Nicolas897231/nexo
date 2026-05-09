"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Lock, Mail, Moon, RotateCcw, Shield, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { useTheme } from "@/features/settings/theme-store";
import { currencyOptions, getPaydayOption, paydayOptions } from "@/lib/options";
import { changePassword } from "@/services/api/auth.api";
import { updateFinancialProfile } from "@/services/api/financial-profile.api";
import { getMe, getPreferences, updatePreferences, updateProfile } from "@/services/api/users.api";

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { accent, compact, mode, setAccent, setCompact, setMode } = useTheme();
  const { data: me } = useQuery({ queryKey: ["me"], queryFn: getMe });
  const { data: preferences } = useQuery({ queryKey: ["preferences"], queryFn: getPreferences });
  const [city, setCity] = useState("");
  const [currencyCode, setCurrencyCode] = useState("COP");
  const [paydayOption, setPaydayOption] = useState("biweekly_15_30");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!me) return;
    setCity(me.profile.city ?? "");
    setCurrencyCode(me.profile.currency_code ?? "COP");
    setPaydayOption(getPaydayOption(me.profile.income_frequency, me.profile.paydays));
  }, [me]);

  useEffect(() => {
    if (!preferences) return;
    if (preferences.theme_mode === "light" || preferences.theme_mode === "dark") setMode(preferences.theme_mode);
    if (preferences.accent_color === "blue" || preferences.accent_color === "ocean" || preferences.accent_color === "night") {
      setAccent(preferences.accent_color);
    }
  }, [preferences, setAccent, setMode]);

  const saveProfileMutation = useMutation({
    mutationFn: async () => {
      const option = paydayOptions.find((item) => item.value === paydayOption) ?? paydayOptions[2];
      const profilePayload = {
        city,
        currency_code: currencyCode,
        income_frequency: option.frequency,
        payday: option.paydays[0],
        paydays: [...option.paydays],
      };
      await updateProfile(profilePayload);
      return updateFinancialProfile(profilePayload);
    },
    onSuccess: async () => {
      setStatus("Preferencias guardadas.");
      await queryClient.invalidateQueries({ queryKey: ["me"] });
    },
    onError: () => setStatus("No pudimos guardar tus preferencias."),
  });

  const saveVisualPreferences = useMutation({
    mutationFn: () => updatePreferences({ theme_mode: mode, accent_color: accent }),
    onSuccess: () => setStatus("Apariencia guardada."),
    onError: () => setStatus("No pudimos guardar la apariencia."),
  });

  const changePasswordMutation = useMutation({
    mutationFn: () => changePassword({ current_password: currentPassword, new_password: newPassword }),
    onSuccess: () => {
      setCurrentPassword("");
      setNewPassword("");
      setStatus("Contraseña actualizada.");
    },
    onError: () => setStatus("No pudimos cambiar la contraseña. Verifica la contraseña actual."),
  });

  const fullName = `${me?.profile.first_name ?? ""} ${me?.profile.last_name ?? ""}`.trim() || "Usuario";
  const initials = `${me?.profile.first_name?.[0] ?? me?.email?.[0] ?? "U"}${me?.profile.last_name?.[0] ?? ""}`.toUpperCase();

  return (
    <main className="page">
      <PageHeader title="Configuracion" description="Personaliza tu experiencia en NexoVia y administra tu cuenta." />
      <section className="grid two">
        <article className="card pad">
          <h2 className="card-title">Perfil</h2>
          <div className="metric-row" style={{ marginTop: 20 }}>
            <span className="avatar">{initials}</span>
            <div><h2>{fullName}</h2><p className="muted">{me?.email}</p><span className="badge success">Cuenta activa</span></div>
          </div>
          <div className="form-grid" style={{ marginTop: 24 }}>
            <label className="field">
              <span>Ciudad</span>
              <input className="input" value={city} onChange={(event) => setCity(event.target.value)} />
            </label>
            <label className="field">
              <span>Moneda principal</span>
              <select className="select" value={currencyCode} onChange={(event) => setCurrencyCode(event.target.value)}>
                {currencyOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
            </label>
            <label className="field">
              <span>Dias de pago</span>
              <select className="select" value={paydayOption} onChange={(event) => setPaydayOption(event.target.value)}>
                {paydayOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
            </label>
            <label className="field">
              <span>Zona horaria</span>
              <select className="select" value="America/Bogota" disabled><option>America/Bogota</option></select>
            </label>
          </div>
          <button className="btn primary" style={{ marginTop: 16 }} type="button" onClick={() => saveProfileMutation.mutate()}>
            Guardar perfil
          </button>
        </article>
        <article className="card pad">
          <h2 className="card-title">Preferencias visuales</h2>
          <div className="grid three" style={{ marginTop: 18 }}>
            {["blue", "ocean", "night"].map((item) => <button className={`card pad ${accent === item ? "active" : ""}`} key={item} onClick={() => setAccent(item as "blue" | "ocean" | "night")} type="button"><strong>{item === "blue" ? "Azul" : item === "ocean" ? "Oceano" : "Noche suave"}</strong><p className="primary-text">● ● ●</p></button>)}
          </div>
          <div className="action-card" style={{ marginTop: 18 }}><Moon /><strong>Modo oscuro</strong><button className="switch" onClick={() => setMode(mode === "dark" ? "light" : "dark")} type="button" /></div>
          <div className="action-card" style={{ marginTop: 12 }}><Sun /><strong>Modo compacto</strong><button className="switch" onClick={() => setCompact(!compact)} type="button" /></div>
          <button className="btn primary" style={{ marginTop: 16 }} type="button" onClick={() => saveVisualPreferences.mutate()}>
            Guardar apariencia
          </button>
          {status ? <p className="badge success" style={{ marginTop: 16 }}>{status}</p> : null}
        </article>
      </section>
      <section className="grid two" style={{ marginTop: 18 }}>
        <article className="card pad">
          <h2 className="card-title">Widgets del dashboard</h2>
          {["Evolucion de saldo", "Gastos por categoria", "Ahorro mensual"].map((item) => <div className="action-card" key={item}><strong>{item}</strong><span className="badge success">Disponible</span></div>)}
          <button className="btn" style={{ marginTop: 14 }} type="button" onClick={() => { window.localStorage.removeItem("nexovia.hidden-widgets"); setStatus("Widgets restablecidos."); }}><RotateCcw size={18} /> Restablecer al diseño por defecto</button>
        </article>
        <article className="card pad">
          <h2 className="card-title">Notificaciones</h2>
          {["Notificaciones por correo", "Alertas de metas", "Alertas de presupuesto", "Novedades del producto"].map((item) => <div className="action-card" key={item}><Mail /><strong>{item}</strong><button className="switch" type="button" /></div>)}
        </article>
        <article className="card pad">
          <h2 className="card-title">Privacidad y seguridad</h2>
          <div className="grid" style={{ marginTop: 12 }}>
            <label className="field"><span>Contraseña actual</span><input className="input" type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} /></label>
            <label className="field"><span>Nueva contraseña</span><input className="input" type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} /></label>
            <button className="btn" type="button" disabled={changePasswordMutation.isPending || newPassword.length < 12} onClick={() => changePasswordMutation.mutate()}><Lock size={18} /> Cambiar contraseña</button>
            <div className="action-card"><Shield /><strong>Autenticacion en dos pasos</strong><span className="badge warning">Pendiente backend</span></div>
            <div className="action-card"><Shield /><strong>Sesiones activas</strong><span className="badge success">Rotacion segura</span></div>
          </div>
        </article>
        <article className="card pad">
          <h2 className="card-title">Preferencias generales</h2>
          {["Inicio de sesion automatico", "Recordatorios de actividad", "Formato de numeros", "Exportaciones"].map((item) => <div className="action-card" key={item}><strong>{item}</strong><span>›</span></div>)}
        </article>
      </section>
    </main>
  );
}
