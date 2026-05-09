import { Download } from "lucide-react";
import { BalanceChart, CategoryDonut, SavingsBars } from "@/components/dashboard/charts";
import { PageHeader } from "@/components/ui/page-header";
import { categoryDistribution, goals, recommendations } from "@/data/mock-data";
import { formatMoney } from "@/lib/money";

export default function ReportsPage() {
  return (
    <main className="page">
      <PageHeader title="Reportes y analisis" description="Explora el rendimiento de tus finanzas con reportes detallados y comparativos." actions={<button className="btn primary" type="button"><Download size={18} /> Exportar</button>} />
      <section className="form-grid" style={{ gridTemplateColumns: "1.2fr 1fr 1fr 1fr", marginBottom: 18 }}>
        <input className="input" value="1 jul 2024 - 30 jul 2025" readOnly />
        <select className="select"><option>Categorias: Todas</option></select>
        <select className="select"><option>Metas: Todas</option></select>
        <select className="select"><option>Tipo: Resumen general</option></select>
      </section>
      <nav className="tabs" style={{ marginBottom: 18 }}>
        {["Resumen", "Flujo de caja", "Gastos", "Ingresos", "Metas", "Comparativo", "Personalizado"].map((tab, index) => <button className={`tab ${index === 0 ? "active" : ""}`} key={tab} type="button">{tab}</button>)}
      </nav>
      <section className="grid three">
        <article className="card pad"><h2 className="card-title">Ingresos vs. Egresos</h2><BalanceChart /></article>
        <article className="card pad"><h2 className="card-title">Distribucion por categoria</h2><CategoryDonut /></article>
        <article className="card pad"><h2 className="card-title">Ahorro por mes</h2><SavingsBars /></article>
      </section>
      <section className="grid three" style={{ marginTop: 18 }}>
        <article className="card pad"><h2 className="card-title">Cumplimiento de metas</h2>{goals.slice(0, 3).map((goal) => <div className="action-card" key={goal.name}><strong>{goal.name}</strong><span>{goal.progress}%</span></div>)}</article>
        <article className="card pad"><h2 className="card-title">Resumen del periodo</h2>{categoryDistribution.slice(0, 4).map(([name, value]) => <div className="action-card" key={name}><span>{name}</span><strong>{formatMoney(value)}</strong></div>)}</article>
        <article className="card pad"><h2 className="card-title">Insights rapidos</h2>{recommendations.map((item) => <div className="action-card" key={item.title}><strong>{item.title}</strong><span>›</span></div>)}</article>
      </section>
    </main>
  );
}
