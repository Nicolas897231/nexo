"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, Minus, Plus, WalletCards } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { MetricCard } from "@/components/dashboard/metric-card";
import { MovementTable } from "@/components/movements/movement-table";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { formatMoney, normalizeMoney } from "@/lib/money";
import { paymentMethods } from "@/lib/options";
import { listCategories } from "@/services/api/catalogs.api";
import { getDashboardSummary } from "@/services/api/dashboard.api";
import { createMovement, deleteMovement, listMovements } from "@/services/api/movements.api";

function currentMonthDate() {
  return `${new Date().toISOString().slice(0, 8)}01`;
}

export default function MovementsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const drawerOpen = searchParams.get("drawer") === "create";
  const isIncome = searchParams.get("type") !== "expense";
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [description, setDescription] = useState("");
  const [isFixed, setIsFixed] = useState(false);
  const [categoryId, setCategoryId] = useState("");
  const [subcategoryId, setSubcategoryId] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("bank_transfer");
  const [error, setError] = useState<string | null>(null);

  const month = useMemo(currentMonthDate, []);
  const movementsQuery = useQuery({ queryKey: ["movements"], queryFn: listMovements });
  const categoriesQuery = useQuery({ queryKey: ["categories"], queryFn: listCategories });
  const summaryQuery = useQuery({ queryKey: ["dashboard-summary", month], queryFn: () => getDashboardSummary(month) });
  const categories = categoriesQuery.data ?? [];
  const parentCategories = categories.filter((category) => category.kind === (isIncome ? "income" : "expense") && !category.parent_id);
  const childCategories = categories.filter((category) => category.parent_id === categoryId);

  const createMutation = useMutation({
    mutationFn: () =>
      createMovement({
        movement_type: isIncome ? "income" : "expense",
        amount: normalizeMoney(amount),
        transaction_date: date,
        category_id: subcategoryId || categoryId || null,
        description,
        is_fixed: isFixed,
        metadata: { payment_method: paymentMethod },
      }),
    onSuccess: async () => {
      setAmount("");
      setDescription("");
      await queryClient.invalidateQueries({ queryKey: ["movements"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      router.push("/movements");
    },
    onError: () => setError("No pudimos guardar el movimiento. Revisa el monto y la fecha."),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteMovement,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["movements"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const allMovements = movementsQuery.data ?? [];
  const q = (searchParams.get("q") ?? "").trim().toLowerCase();
  const movements = q
    ? allMovements.filter((movement) => (movement.description ?? "").toLowerCase().includes(q))
    : allMovements;
  const summary = summaryQuery.data;

  return (
    <main className="page">
      <PageHeader
        title="Movimientos"
        description="Gestiona y revisa todos tus ingresos y egresos reales."
        actions={
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <Link className="btn success" href="/movements?drawer=create&type=income"><Plus size={18} /> Registrar ingreso</Link>
            <Link className="btn danger" href="/movements?drawer=create&type=expense"><Minus size={18} /> Registrar gasto</Link>
          </div>
        }
      />
      <section className="grid kpi">
        <MetricCard label="Total ingresos" value={summary?.total_income ?? "0.00"} tone="success" delta="mes actual" />
        <MetricCard label="Total egresos" value={summary?.total_expenses ?? "0.00"} tone="danger" delta="mes actual" />
        <MetricCard label="Balance neto" value={summary?.available_cashflow ?? "0.00"} tone="primary" delta="disponible" />
        <article className="card metric-card">
          <div className="metric-row">
            <span className="metric-icon" style={{ background: "var(--purple)" }}><WalletCards /></span>
            <div><p className="muted">Movimientos</p><h2>{movements.length}</h2><p className="muted small">Registrados en tu cuenta</p></div>
          </div>
        </article>
      </section>
      <section className="card pad" style={{ marginTop: 18 }}>
        <div className="card-header">
          <h2 className="card-title">Historial</h2>
          <button className="btn" type="button" onClick={() => window.print()}><Download size={18} /> Exportar</button>
        </div>
        {movementsQuery.isLoading ? (
          <div className="skeleton" style={{ height: 220 }} />
        ) : movements.length ? (
          <MovementTable movements={movements} categories={categories} onDelete={(id) => deleteMutation.mutate(id)} />
        ) : (
          <EmptyState
            title="Aun no tienes movimientos"
            description="Registra tu primer ingreso o gasto para activar tus reportes."
            action={<Link className="btn primary" href="/movements?drawer=create&type=income">Registrar ingreso</Link>}
          />
        )}
      </section>
      {drawerOpen ? (
        <section
          aria-label="Registrar movimiento"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 50,
            display: "grid",
            gridTemplateColumns: "1fr minmax(420px, 720px)",
            background: "rgba(8, 20, 43, .42)",
          }}
        >
          <div />
          <form
            className="drawer-panel"
            onSubmit={(event) => {
              event.preventDefault();
              setError(null);
              createMutation.mutate();
            }}
          >
            <div className="card-header">
              <div>
                <h2>Registrar movimiento</h2>
                <p className="muted">Agrega un ingreso o gasto en segundos.</p>
              </div>
              <Link className="icon-button" href="/movements">×</Link>
            </div>
            <div className="tabs" style={{ gridTemplateColumns: "1fr 1fr", marginBottom: 18 }}>
              <Link className={`tab ${isIncome ? "active" : ""}`} href="/movements?drawer=create&type=income">Ingresar ingreso</Link>
              <Link className={`tab ${!isIncome ? "active" : ""}`} href="/movements?drawer=create&type=expense">Registrar gasto</Link>
            </div>
            <div className="form-grid">
              <label className="field"><span>Monto *</span><input className="input" inputMode="numeric" placeholder="Ej. 2500000" value={amount} onChange={(event) => setAmount(event.target.value)} required /></label>
              <label className="field"><span>Fecha *</span><input className="input" type="date" value={date} onChange={(event) => setDate(event.target.value)} required /></label>
              <label className="field">
                <span>Categoria *</span>
                <select className="select" value={categoryId} onChange={(event) => { setCategoryId(event.target.value); setSubcategoryId(""); }}>
                  <option value="">Selecciona una categoria</option>
                  {parentCategories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
                </select>
              </label>
              <label className="field">
                <span>Subcategoria</span>
                <select className="select" value={subcategoryId} onChange={(event) => setSubcategoryId(event.target.value)}>
                  <option value="">Sin subcategoria</option>
                  {childCategories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
                </select>
              </label>
              <label className="field">
                <span>Metodo</span>
                <select className="select" value={paymentMethod} onChange={(event) => setPaymentMethod(event.target.value)}>
                  {paymentMethods.map((method) => <option key={method.value} value={method.value}>{method.label}</option>)}
                </select>
              </label>
            </div>
            <label className="field" style={{ marginTop: 14 }}><span>Descripcion / Nota</span><textarea className="textarea" maxLength={120} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Ej. Salario de julio, supermercado, transporte." /></label>
            <label style={{ display: "flex", gap: 10, marginTop: 14 }}>
              <input checked={isFixed} onChange={(event) => setIsFixed(event.target.checked)} type="checkbox" />
              Movimiento recurrente
            </label>
            <article className="card pad" style={{ marginTop: 18, background: isIncome ? "var(--success-soft)" : "var(--danger-soft)" }}>
              <h3>Resumen e impacto</h3>
              <p className={isIncome ? "success-text" : "danger-text"}>{isIncome ? "+" : "-"} {formatMoney(normalizeMoney(amount))}</p>
              <p className="muted">{isIncome ? "Aumenta tu saldo disponible" : "Reduce tu saldo disponible"}</p>
            </article>
            {error ? <p className="badge danger" style={{ marginTop: 16 }}>{error}</p> : null}
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 24 }}>
              <Link className="btn" href="/movements">Cancelar</Link>
              <button className="btn primary" disabled={createMutation.isPending} type="submit">Guardar {isIncome ? "ingreso" : "gasto"}</button>
            </div>
          </form>
        </section>
      ) : null}
    </main>
  );
}
