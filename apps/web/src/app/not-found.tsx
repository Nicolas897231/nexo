import Link from "next/link";
import { EmptyState } from "@/components/ui/empty-state";

export default function NotFound() {
  return (
    <main className="page">
      <EmptyState
        title="Pagina no encontrada"
        description="La ruta que intentas abrir no existe o cambio de ubicacion."
        action={<Link className="btn primary" href="/dashboard">Ir al dashboard</Link>}
      />
    </main>
  );
}
