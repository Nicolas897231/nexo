import { Bell, Edit, Plus, Trash2 } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";

const rules = ["Tope de arriendo", "Ahorro minimo", "Limite de ocio", "Meta prioritaria", "Gasto inusual"];
const templates = ["Ahorro minimo", "Limite de ocio", "Meta prioritaria", "Tope de arriendo"];

export default function RulesPage() {
  return (
    <main className="page">
      <PageHeader title="Mis reglas financieras" description="Crea reglas personalizadas para mantener tus finanzas bajo control." actions={<button className="btn primary" type="button"><Plus size={18} /> Nueva regla</button>} />
      <section className="grid two" style={{ gridTemplateColumns: "1fr 360px" }}>
        <div className="grid">
          <article className="card pad">
            <h2 className="card-title">Crea una nueva regla</h2>
            <div className="card pad" style={{ marginTop: 18 }}>
              <div className="form-grid" style={{ gridTemplateColumns: ".8fr 1fr .6fr .6fr 1fr auto" }}>
                <strong>Cuando</strong>
                <select className="select"><option>Arriendo</option><option>Ahorro</option></select>
                <select className="select"><option>&gt;</option><option>&lt;</option></select>
                <input className="input" value="30" readOnly />
                <select className="select"><option>% del ingreso</option></select>
                <button className="icon-button" type="button">×</button>
              </div>
              <button className="btn" style={{ marginTop: 14 }} type="button"><Plus size={16} /> Agregar condicion</button>
              <hr style={{ border: 0, borderTop: "1px solid var(--border)", margin: "22px 0" }} />
              <div className="form-grid" style={{ gridTemplateColumns: ".8fr 1fr 2fr auto" }}>
                <strong>Entonces</strong>
                <select className="select"><option>Mostrar alerta</option></select>
                <input className="input" value="Tu arriendo supera el 30% de tu ingreso mensual." readOnly />
                <button className="icon-button" type="button">×</button>
              </div>
            </div>
            <div className="action-card" style={{ marginTop: 18 }}>
              <Bell className="primary-text" />
              <strong>Cuando Arriendo &gt; 30% del ingreso, entonces mostrar alerta.</strong>
              <button className="btn primary" type="button">Guardar regla</button>
            </div>
          </article>
          <article className="card pad">
            <h2 className="card-title">Reglas activas</h2>
            <table className="table">
              <tbody>
                {rules.map((rule, index) => (
                  <tr key={rule}>
                    <td><strong>{rule}</strong><p className="muted small">Control automatico</p></td>
                    <td>{index === 0 ? "Arriendo > 30%" : "Condicion segura"}</td>
                    <td>Mostrar alerta</td>
                    <td><span className={`badge ${index === 2 ? "warning" : "success"}`}>{index === 2 ? "Pausada" : "Activa"}</span></td>
                    <td><button className="icon-button" type="button"><Edit size={16} /></button> <button className="icon-button" type="button"><Trash2 size={16} /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>
        </div>
        <aside className="grid">
          <article className="card pad">
            <h2 className="card-title">Plantillas de reglas</h2>
            {templates.map((template) => <div className="action-card" key={template}><strong>{template}</strong><span>›</span></div>)}
          </article>
          <article className="card pad">
            <h2 className="card-title">Personalizacion</h2>
            <p className="muted">Tema de color y widgets se sincronizan con Configuracion.</p>
          </article>
        </aside>
      </section>
    </main>
  );
}
