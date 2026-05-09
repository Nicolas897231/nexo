"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { normalizeMoney } from "@/lib/money";
import { currencyOptions, paydayOptions } from "@/lib/options";
import { updateFinancialProfile } from "@/services/api/financial-profile.api";
import { updateProfile } from "@/services/api/users.api";

export default function OnboardingPage() {
  const router = useRouter();
  const [city, setCity] = useState("Bogota");
  const [currencyCode, setCurrencyCode] = useState("COP");
  const [monthlyIncome, setMonthlyIncome] = useState("");
  const [paydayOption, setPaydayOption] = useState("biweekly_15_30");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      const option = paydayOptions.find((item) => item.value === paydayOption) ?? paydayOptions[2];
      const payload = {
        city,
        currency_code: currencyCode,
        monthly_income: normalizeMoney(monthlyIncome),
        income_frequency: option.frequency,
        payday: option.paydays[0],
        paydays: [...option.paydays],
      };
      await updateProfile({
        city,
        currency_code: currencyCode,
        income_frequency: option.frequency,
        payday: option.paydays[0],
        paydays: [...option.paydays],
      });
      return updateFinancialProfile(payload);
    },
    onSuccess: () => router.push("/dashboard"),
    onError: () => setError("No pudimos guardar tu perfil financiero. Revisa los datos e intenta de nuevo."),
  });

  return (
    <main className="page" style={{ maxWidth: 1080, margin: "0 auto" }}>
      <PageHeader title="Onboarding financiero" description="Completa tu perfil para activar dashboard, metas y recomendaciones reales." />
      <section className="card pad">
        <div className="stepper">
          {["Perfil", "Ingresos", "Pagos", "Listo"].map((step, index) => (
            <div className={`step ${index === 0 ? "active" : ""}`} key={step}>
              <span className="step-dot">{index + 1}</span>
              <strong>{step}</strong>
            </div>
          ))}
        </div>
      </section>
      <form
        className="card pad"
        style={{ marginTop: 18 }}
        onSubmit={(event) => {
          event.preventDefault();
          setError(null);
          mutation.mutate();
        }}
      >
        <h2>Perfil financiero</h2>
        <div className="form-grid">
          <label className="field">
            <span>Ciudad</span>
            <input className="input" value={city} onChange={(event) => setCity(event.target.value)} required />
          </label>
          <label className="field">
            <span>Moneda principal</span>
            <select className="select" value={currencyCode} onChange={(event) => setCurrencyCode(event.target.value)}>
              {currencyOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Ingreso mensual aproximado</span>
            <input className="input" inputMode="numeric" placeholder="Ej. 4250000" value={monthlyIncome} onChange={(event) => setMonthlyIncome(event.target.value)} required />
          </label>
          <label className="field">
            <span>Dias de pago</span>
            <select className="select" value={paydayOption} onChange={(event) => setPaydayOption(event.target.value)}>
              {paydayOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>
        </div>
        {error ? <p className="badge danger" style={{ marginTop: 16 }}>{error}</p> : null}
        <button className="btn primary" style={{ marginTop: 18 }} disabled={mutation.isPending} type="submit">
          {mutation.isPending ? "Guardando..." : "Completar onboarding"}
        </button>
      </form>
    </main>
  );
}
