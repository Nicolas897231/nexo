import { MoreVertical, TrendingDown, TrendingUp } from "lucide-react";
import { movements } from "@/data/mock-data";
import { formatMoney } from "@/lib/money";

export function MovementTable() {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Tipo</th>
            <th>Descripcion</th>
            <th>Categoria</th>
            <th>Meta</th>
            <th>Metodo</th>
            <th>Monto</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {movements.map((movement) => (
            <tr key={`${movement.date}-${movement.description}`}>
              <td>{movement.date}</td>
              <td>{movement.type === "income" ? <TrendingUp className="success-text" /> : <TrendingDown className="danger-text" />}</td>
              <td><strong>{movement.description}</strong></td>
              <td>{movement.category}</td>
              <td>{movement.goal}</td>
              <td>{movement.method}</td>
              <td className={movement.type === "income" ? "success-text" : "danger-text"}><strong>{formatMoney(movement.amount)}</strong></td>
              <td><span className={`badge ${movement.status === "Pendiente" ? "warning" : "success"}`}>{movement.status}</span></td>
              <td><button className="icon-button" type="button" title="Abrir acciones"><MoreVertical size={18} /></button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
