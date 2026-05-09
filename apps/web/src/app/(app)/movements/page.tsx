import { Download, Filter, Minus, Plus } from "lucide-react";
import Link from "next/link";
import { CategoryDonut } from "@/components/dashboard/charts";
import { MetricCard } from "@/components/dashboard/metric-card";
import { MovementTable } from "@/components/movements/movement-table";
import { PageHeader } from "@/components/ui/page-header";
import { kpis, movements } from "@/data/mock-data";

export default async function MovementsPage({
  searchParams,
}: {
  searchParams?: Promise<{ drawer?: string; type?: string }>;
}) {
  const params = await searchParams;
  const drawerOpen = params?.drawer === "create";
  const isIncome = params?.type !== "expense";
  return (
    <main className="page">
      <PageHeader
        title="Movimientos"
        description="Gestiona y revisa todos tus ingresos y egresos."
        actions={
          <div style={{ display: "flex", gap: 12 }}>
            <Link className="btn success" href="/movements?drawer=create&type=income"><Plus size={18} /> Registrar ingreso</Link>
            <Link className="btn danger" href="/movements?drawer=create&type=expense"><Minus size={18} /> Registrar gasto</Link>
          </div>
        }
      />
      <section className="grid kpi">
        {kpis.map((kpi) => <MetricCard key={kpi.label} {...kpi} tone={kpi.tone as "success" | "danger" | "primary"} />)}
        <article className="card metric-card">
          <div className="metric-row">
            <span className="metric-icon" style={{ background: "var(--purple)" }}><Filter /></span>
            <div><p className="muted">Filtros activos</p><h2>3 filtros</h2><Link className="primary-text" href="/movements">Limpiar filtros</Link></div>
          </div>
        </article>
      </section>
      <section className="grid two" style={{ marginTop: 18, gridTemplateColumns: "1fr 340px" }}>
        <article className="card pad">
          <div className="form-grid" style={{ gridTemplateColumns: "1fr .6fr .6fr .6fr 1fr auto" }}>
            <input className="input" value="1 Jul 2025 - 31 Jul 2025" readOnly aria-label="Rango de fechas" />
            <select className="select" aria-label="Tipo"><option>Todos</option><option>Ingresos</option><option>Gastos</option></select>
            <select className="select" aria-label="Categoria"><option>Todas</option></select>
            <select className="select" aria-label="Meta"><option>Todas</option></select>
            <input className="input" placeholder="Buscar en movimientos..." />
            <button className="btn" type="button"><Download size={18} /> Exportar</button>
          </div>
          <div style={{ marginTop: 22 }}><MovementTable /></div>
          <div className="card-header" style={{ marginTop: 18 }}>
            <span className="muted small">Mostrando 1 a {movements.length} de 42 movimientos</span>
            <div style={{ display: "flex", gap: 8 }}>
              {[1, 2, 3, 4, 5].map((page) => <button className={`btn ${page === 1 ? "primary" : ""}`} key={page} type="button">{page}</button>)}
            </div>
          </div>
        </article>
        <aside className="grid">
          <article className="card pad">
            <h2 className="card-title">Resumen rapido</h2>
            <p className="muted">Promedio diario ingresos <strong className="success-text">$137.100</strong></p>
            <p className="muted">Promedio diario egresos <strong className="danger-text">$93.200</strong></p>
            <p className="muted">Mayor ingreso <strong className="success-text">$2.500.000</strong></p>
          </article>
          <article className="card pad">
            <h2 className="card-title">Gastos por categoria</h2>
            <CategoryDonut />
          </article>
        </aside>
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
          <aside className="drawer-panel">
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
              <label className="field"><span>Monto *</span><input className="input" placeholder="$ 0" /></label>
              <label className="field"><span>Fecha *</span><input className="input" value="30 jul 2025" readOnly /></label>
              <label className="field"><span>Categoria *</span><select className="select"><option>Selecciona una categoria</option></select></label>
              <label className="field"><span>Subcategoria</span><select className="select"><option>Selecciona una subcategoria</option></select></label>
            </div>
            <label className="field" style={{ marginTop: 14 }}><span>Meta asociada</span><select className="select"><option>Buscar o seleccionar una meta</option></select></label>
            <label className="field" style={{ marginTop: 14 }}><span>Metodo *</span><select className="select"><option>Selecciona metodo de pago o cuenta</option></select></label>
            <label className="field" style={{ marginTop: 14 }}><span>Descripcion / Nota</span><textarea className="textarea" maxLength={120} placeholder="Ej. Salario de julio, bono por proyecto." /></label>
            <article className="card pad" style={{ marginTop: 18, background: isIncome ? "var(--success-soft)" : "var(--danger-soft)" }}>
              <h3>Resumen e impacto</h3>
              <p className={isIncome ? "success-text" : "danger-text"}>{isIncome ? "+" : "-"} $0</p>
              <p className="muted">{isIncome ? "Aumenta tu saldo disponible" : "Reduce tu saldo disponible"}</p>
            </article>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 24 }}>
              <Link className="btn" href="/movements">Cancelar</Link>
              <button className="btn" type="button">Guardar y nuevo</button>
              <button className="btn primary" type="button">Guardar {isIncome ? "ingreso" : "gasto"}</button>
            </div>
          </aside>
        </section>
      ) : null}
    </main>
  );
}
