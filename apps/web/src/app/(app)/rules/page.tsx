"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, Edit, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { createUserRule, deleteUserRule, listRuleTemplates, listUserRules, updateUserRule } from "@/services/api/rules.api";

const fields = [
  ["monthly_available", "Disponible mensual"],
  ["savings_rate", "Tasa de ahorro"],
  ["debt_payment_ratio", "Deuda / ingreso"],
  ["housing_cost_ratio", "Vivienda / ingreso"],
  ["car_total_monthly_ratio", "Carro / ingreso"],
  ["goal_progress_ratio", "Progreso de meta"],
];

const operators = [
  ["gt", ">"],
  ["gte", ">="],
  ["lt", "<"],
  ["lte", "<="],
  ["eq", "="],
];

export default function RulesPage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("Alerta financiera");
  const [field, setField] = useState("monthly_available");
  const [operator, setOperator] = useState("lt");
  const [value, setValue] = useState("0.00");
  const [message, setMessage] = useState("Revisa esta condicion financiera.");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { data: rules = [] } = useQuery({ queryKey: ["rules"], queryFn: listUserRules });
  const { data: templates = [] } = useQuery({ queryKey: ["rule-templates"], queryFn: listRuleTemplates });

  const createMutation = useMutation({
    mutationFn: () =>
      editingId
        ? updateUserRule(editingId, {
            name,
            scope: "general",
            condition_json: { fact: field, operator, value },
            action_json: { status: "WARN", severity: "WARNING", message, suggestions: ["Revisa tus movimientos recientes."] },
            priority: 100,
          })
        : createUserRule({
        name,
        scope: "general",
        condition_json: { fact: field, operator, value },
        action_json: { status: "WARN", severity: "WARNING", message, suggestions: ["Revisa tus movimientos recientes."] },
        priority: 100,
      }),
    onSuccess: async () => {
      setError(null);
      setEditingId(null);
      await queryClient.invalidateQueries({ queryKey: ["rules"] });
    },
    onError: () => setError("No pudimos crear la regla. Revisa campo, operador y valor."),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteUserRule,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rules"] }),
  });

  const toggleMutation = useMutation({
    mutationFn: (rule: { id: string; is_active: boolean }) => updateUserRule(rule.id, { is_active: !rule.is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rules"] }),
  });

  return (
    <main className="page">
      <PageHeader title="Mis reglas financieras" description="Crea reglas personalizadas sin codigo dinamico ni eval." actions={<button className="btn primary" type="button" onClick={() => createMutation.mutate()}><Plus size={18} /> {editingId ? "Actualizar regla" : "Guardar regla"}</button>} />
      <section className="grid two" style={{ gridTemplateColumns: "1fr 360px" }}>
        <div className="grid">
          <article className="card pad">
            <h2 className="card-title">Crea una nueva regla</h2>
            <div className="card pad" style={{ marginTop: 18 }}>
              <div className="form-grid" style={{ gridTemplateColumns: ".8fr 1fr .6fr .7fr" }}>
                <strong>Cuando</strong>
                <select className="select" value={field} onChange={(event) => setField(event.target.value)}>
                  {fields.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
                <select className="select" value={operator} onChange={(event) => setOperator(event.target.value)}>
                  {operators.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
                <input className="input" value={value} onChange={(event) => setValue(event.target.value)} />
              </div>
              <hr style={{ border: 0, borderTop: "1px solid var(--border)", margin: "22px 0" }} />
              <div className="form-grid" style={{ gridTemplateColumns: ".8fr 1fr 2fr" }}>
                <strong>Entonces</strong>
                <select className="select" value="alert" disabled><option>Mostrar alerta</option></select>
                <input className="input" value={message} onChange={(event) => setMessage(event.target.value)} />
              </div>
            </div>
            <label className="field" style={{ marginTop: 14 }}><span>Nombre de la regla</span><input className="input" value={name} onChange={(event) => setName(event.target.value)} /></label>
            {error ? <p className="badge danger" style={{ marginTop: 16 }}>{error}</p> : null}
            <div className="action-card" style={{ marginTop: 18 }}>
              <Bell className="primary-text" />
              <strong>Cuando {fields.find(([key]) => key === field)?.[1]} {operators.find(([key]) => key === operator)?.[1]} {value}, mostrar alerta.</strong>
              <button className="btn primary" type="button" disabled={createMutation.isPending} onClick={() => createMutation.mutate()}>{editingId ? "Actualizar regla" : "Guardar regla"}</button>
            </div>
          </article>
          <article className="card pad">
            <h2 className="card-title">Reglas activas</h2>
            <table className="table">
              <tbody>
                {rules.map((rule) => (
                  <tr key={rule.id}>
                    <td><strong>{rule.name}</strong><p className="muted small">Prioridad {rule.priority}</p></td>
                    <td>{String(rule.condition_json.fact ?? rule.condition_json.field)} {String(rule.condition_json.operator)} {String(rule.condition_json.value ?? "")}</td>
                    <td>{String(rule.action_json.message ?? rule.action_json.user_message ?? "Mostrar alerta")}</td>
                    <td><button className={`badge ${rule.is_active ? "success" : "warning"}`} type="button" onClick={() => toggleMutation.mutate(rule)}>{rule.is_active ? "Activa" : "Pausada"}</button></td>
                    <td><button className="icon-button" type="button" title="Editar" onClick={() => {
                      setEditingId(rule.id);
                      setName(rule.name);
                      setField(String(rule.condition_json.fact ?? rule.condition_json.field ?? "monthly_available"));
                      setOperator(String(rule.condition_json.operator ?? "lt"));
                      setValue(String(rule.condition_json.value ?? "0.00"));
                      setMessage(String(rule.action_json.message ?? rule.action_json.user_message ?? "Revisa esta condicion financiera."));
                    }}><Edit size={16} /></button> <button className="icon-button" type="button" title="Eliminar" onClick={() => deleteMutation.mutate(rule.id)}><Trash2 size={16} /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>
        </div>
        <aside className="grid">
          <article className="card pad">
            <h2 className="card-title">Plantillas de reglas</h2>
            {templates.map((template) => <button className="action-card" key={template.id} type="button" onClick={() => setName(template.name)}><strong>{template.name}</strong><span>›</span></button>)}
          </article>
          <article className="card pad">
            <h2 className="card-title">Seguridad</h2>
            <p className="muted">Las reglas validan campos, operadores y acciones permitidas en backend. No se ejecuta codigo enviado por el usuario.</p>
          </article>
        </aside>
      </section>
    </main>
  );
}
