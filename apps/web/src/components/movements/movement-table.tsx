import { Trash2, TrendingDown, TrendingUp } from "lucide-react";
import { formatMoney } from "@/lib/money";
import type { Category } from "@/services/api/catalogs.api";
import type { Movement } from "@/services/api/movements.api";

export function MovementTable({
  movements,
  onDelete,
  categories = [],
}: {
  movements: Movement[];
  onDelete?: (id: string) => void;
  categories?: Category[];
}) {
  const categoryById = new Map(categories.map((category) => [category.id, category.name]));
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
            <tr key={movement.id}>
              <td>{movement.transaction_date}</td>
              <td>{movement.type === "income" ? <TrendingUp className="success-text" /> : <TrendingDown className="danger-text" />}</td>
              <td><strong>{movement.description || "Sin descripcion"}</strong></td>
              <td>{categoryById.get(movement.category_id ?? "") ?? (movement.type === "income" ? "Ingreso" : "Gasto")}</td>
              <td>-</td>
              <td>{movement.is_fixed ? "Recurrente" : "Unico"}</td>
              <td className={movement.type === "income" ? "success-text" : "danger-text"}><strong>{formatMoney(movement.amount, movement.currency_code)}</strong></td>
              <td><span className="badge success">Completado</span></td>
              <td>
                <button className="icon-button" type="button" title="Eliminar" onClick={() => onDelete?.(movement.id)}>
                  <Trash2 size={18} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
